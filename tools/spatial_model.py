#!/usr/bin/env python3
"""SIGNAL 45 — engine-independent spatial, adjacency, access, and room-data model (Prompt 4, D-046/D-048).

ONE logical source of truth: SECTION -> BAY -> CELL (tools/data/station_sections.json).
Placement, room ownership, object footprints, utility reach, navigation, and save
data all reference the same cell addresses; a future renderer converts cells to
world transforms at draw time and stores nothing of its own.

This module is design evidence, not gameplay: it proves the slice layouts are
structurally consistent (placeable, navigable, evacuable, save-stable) and that
the blueprint/reservation arithmetic obeys its anti-exploit rules. It does NOT
prove the building system is fun — that is a playable-prototype question.

Enforcement boundary (D-048, honest): the validator executes the hard placement
rules (buildable zones, overlap, link protection, interaction clearance, room
compatibility, socket budgets, module attachment, hard restrictions, the
flood-fill no-sever/no-strand guard, trunk service, the reservation ledger).
Schema fields it records but does not yet consume (bays-as-count, environment
temperatures, camera frames, occupancy caps, damage-state ladders) are
recorded-for-later and say so in the docs.

All values PROVISIONAL. Deterministic; no wall-clock, no randomness.
"""

import copy
import json
import os
from collections import deque

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


SECTIONS = _load("station_sections.json")
FAMILIES = _load("room_families.json")
OBJECTS = _load("placeable_objects.json")

# behavior families every room accepts regardless of its socket list
UNIVERSAL_FAMILIES = {"barrier", "decoration", "story_object", "emergency_object", "comfort_object"}
# restrictions the validator executes; the rest are ADVISORY UI hints (config note)
HARD_RESTRICTIONS = {"interior_only", "portal_or_partition_gap_only", "tank_adjacent",
                     "needs_water_feature_or_tank_adjacent", "signal_box_only_in_slice",
                     "west_gallery_only_in_slice", "cistern_works_only_in_slice",
                     "common_areas", "carer_side_clear", "never_deconstruct",
                     "must_stay_reachable", "never_seals_last_path"}


def _rect_cells(rect):
    return [(rect["x"] + dx, rect["y"] + dy)
            for dy in range(rect["h"]) for dx in range(rect["w"])]


def _fixed_cells(sec, sid):
    """{(x, y): (type, walkable_when)}; overlapping fixed features are a data
    error (silent shadowing once hid a column under the kiosk row — D-048)."""
    out = {}
    for f in sec.get("fixed", []):
        cells = ([tuple(c) for c in f["cells"]] if "cells" in f
                 else [tuple(c) for c in _rect_cells(f["cells_rect"])])
        for c in cells:
            if c in out:
                raise ValueError("fixed-architecture overlap in %s at %s: %s vs %s"
                                 % (sid, c, out[c][0], f["type"]))
            out[c] = (f["type"], f["walkable_when"])
    return out


def rotate_footprint(w, h, cells, rot):
    if rot % 360 == 0:
        return w, h, list(cells)
    if rot % 360 == 90:
        return h, w, [(h - 1 - y, x) for (x, y) in cells]
    if rot % 360 == 180:
        return w, h, [(w - 1 - x, h - 1 - y) for (x, y) in cells]
    if rot % 360 == 270:
        return h, w, [(y, w - 1 - x) for (x, y) in cells]
    raise ValueError("rotation must be a multiple of 90")


class ValidationError(Exception):
    """Every rejection carries a specific, player-presentable reason (24 S5)."""


class Station:
    def __init__(self, data=SECTIONS):
        self.data = data
        self.sections = data["sections"]
        self.trunks = data["trunks"]
        self._fixed = {sid: _fixed_cells(s, sid) for sid, s in self.sections.items()}

    def in_grid(self, sid, c):
        w, h = self.sections[sid]["grid"]
        return 0 <= c[0] < w and 0 <= c[1] < h

    def fixed_at(self, sid, c):
        return self._fixed[sid].get(tuple(c))

    def buildable(self, sid, c):
        sec = self.sections[sid]
        c = tuple(c)
        if not self.in_grid(sid, c):
            return False
        for z in sec.get("buildable", []):
            if z["x"] <= c[0] < z["x"] + z["w"] and z["y"] <= c[1] < z["y"] + z["h"]:
                fx = self.fixed_at(sid, c)
                if fx is None:
                    return True
                if z.get("except_fixed", True):
                    return False
                return fx[1] == "interior"
        return False

    def link_cells(self, sid):
        cells = set()
        for l in self.sections[sid].get("vertical_links", []):
            cells |= {tuple(c) for c in l["cells"]}
        for e in self.sections[sid].get("entries", []):
            cells |= {tuple(c) for c in e["cells"]}
        return cells

    def fixed_type_cells(self, sid, ftype):
        return [c for c, (t, _) in self._fixed[sid].items() if t == ftype]


class Layout:
    """A concrete station state: rooms, objects, portal/link/trunk/door states."""

    def __init__(self, layout_data, station=None):
        self.station = station or Station()
        self.d = copy.deepcopy(layout_data)
        self.d.setdefault("door_states", {})
        self.rooms = {r["id"]: r for r in self.d["rooms"]}
        self.objects = {o["id"]: o for o in self.d["objects"]}

    # ---------------- geometry ----------------
    def room_cells(self, room_id):
        r = self.rooms[room_id]
        return [(r["section"], c) for c in _rect_cells(r["rect"])]

    def object_cells(self, obj):
        spec = OBJECTS["objects"][obj["type"]]
        w, h = spec["footprint"]
        w, h, _ = rotate_footprint(w, h, [], obj.get("rot", 0))
        px, py = obj["pos"]
        return [(px + dx, py + dy) for dy in range(h) for dx in range(w)]

    def object_interactions(self, obj):
        spec = OBJECTS["objects"][obj["type"]]
        w, h = spec["footprint"]
        _, _, cells = rotate_footprint(w, h, spec["interaction"], obj.get("rot", 0))
        px, py = obj["pos"]
        return [(px + x, py + y) for (x, y) in cells]

    def object_section(self, obj):
        if obj.get("section"):
            return obj["section"]
        return self.rooms[obj["room"]]["section"]

    def _blocking_cells(self, sid, ignore_obj=None):
        blocked = set()
        for o in self.objects.values():
            if o["id"] == (ignore_obj or ""):
                continue
            if self.object_section(o) != sid:
                continue
            spec = OBJECTS["objects"][o["type"]]
            blocks = spec["block_paths"]
            if o["type"] == "door_panel":
                blocks = self.d["door_states"].get(o["id"], "open") != "open"
            if blocks:
                blocked |= {tuple(c) for c in self.object_cells(o)}
        return blocked

    def _occupied_cells(self, sid, ignore_obj=None):
        occ = set()
        for o in self.objects.values():
            if o["id"] == (ignore_obj or ""):
                continue
            if self.object_section(o) == sid:
                occ |= {tuple(c) for c in self.object_cells(o)}
        return occ

    # ---------------- walkability & navigation ----------------
    def walkable(self, sid, c, ignore_obj=None):
        st = self.station
        c = tuple(c)
        if not st.in_grid(sid, c):
            return False
        fx = st.fixed_at(sid, c)
        if fx is not None:
            kind, when = fx
            if when == "never":
                return False
            if when == "open":
                if self.d.get("door_states", {}).get(kind, "open") != "open":
                    return False
        if c in self._blocking_cells(sid, ignore_obj=ignore_obj):
            return False
        return True

    def _edges(self):
        edges = []
        seen_links = set()
        for sid, sec in self.station.sections.items():
            for e in sec.get("entries", []):
                if e["to"] == "surface":
                    continue
                state = self.d["portal_states"].get(e["id"], e.get("state_day1"))
                if state not in ("open", "operational"):
                    continue
                other = e["to"]
                for oe in self.station.sections[other].get("entries", []):
                    if oe["id"] == e["id"] or oe["to"] == sid:
                        for a in e["cells"]:
                            for b in oe["cells"]:
                                edges.append(((sid, tuple(a)), (other, tuple(b))))
            for l in sec.get("vertical_links", []):
                if l["id"] in seen_links:
                    continue
                seen_links.add(l["id"])
                state = self.d["link_states"].get(l["id"], l.get("state_day1"))
                if state != "operational":
                    continue
                for a in l["cells"]:
                    for b in l["to_cells"]:
                        edges.append(((sid, tuple(a)), (l["to"], tuple(b))))
        return edges

    def reached_cells(self, start, ignore_obj=None):
        """Flood-fill: every (section, cell) reachable from start under current state."""
        start = (start[0], tuple(start[1]))
        if not self.walkable(*start, ignore_obj=ignore_obj):
            return set()
        jump = {}
        for a, b in self._edges():
            jump.setdefault(a, []).append(b)
            jump.setdefault(b, []).append(a)
        q = deque([start])
        seen = {start}
        while q:
            sid, c = q.popleft()
            nbrs = [(sid, (c[0] + 1, c[1])), (sid, (c[0] - 1, c[1])),
                    (sid, (c[0], c[1] + 1)), (sid, (c[0], c[1] - 1))]
            nbrs.extend(jump.get((sid, c), []))
            for n in nbrs:
                if n in seen:
                    continue
                if not self.walkable(n[0], n[1], ignore_obj=ignore_obj):
                    continue
                seen.add(n)
                q.append(n)
        return seen

    def path(self, start, goal, ignore_obj=None):
        start = (start[0], tuple(start[1]))
        goal = (goal[0], tuple(goal[1]))
        if not self.walkable(*start, ignore_obj=ignore_obj):
            return None
        jump = {}
        for a, b in self._edges():
            jump.setdefault(a, []).append(b)
            jump.setdefault(b, []).append(a)
        q = deque([(start, 0)])
        seen = {start}
        while q:
            (sid, c), dist = q.popleft()
            if (sid, c) == goal:
                return dist
            nbrs = [(sid, (c[0] + 1, c[1])), (sid, (c[0] - 1, c[1])),
                    (sid, (c[0], c[1] + 1)), (sid, (c[0], c[1] - 1))]
            nbrs.extend(jump.get((sid, c), []))
            for n in nbrs:
                if n in seen:
                    continue
                if not self.walkable(n[0], n[1], ignore_obj=ignore_obj):
                    continue
                seen.add(n)
                q.append((n, dist + 1))
        return None

    def access_cell(self, room_id, reached=None):
        """The room's doorstep: a walkable cell inside or adjacent to the room.
        When a reached-set is given (or computable from the muster point), prefer
        a cell that is actually connected — a walkable-but-enclosed pocket cell
        must never masquerade as the room's access (D-048)."""
        r = self.rooms[room_id]
        sid = r["section"]
        cells = [tuple(c) for c in _rect_cells(r["rect"])]
        candidates = [c for c in cells if self.walkable(sid, c)]
        for c in cells:
            for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
                if self.walkable(sid, n):
                    candidates.append(n)
        if not candidates:
            return None
        if reached is None:
            reached = self.reached_cells(self.muster())
        for c in candidates:
            if (sid, c) in reached:
                return (sid, c)
        return (sid, candidates[0])

    def muster(self):
        m = self.station.data["muster_point"]
        return (m["section"], tuple(m["cells"][0]))

    def reachable_from_muster(self, room_id):
        r = self.rooms[room_id]
        sid = r["section"]
        reached = self.reached_cells(self.muster())
        cells = [tuple(c) for c in _rect_cells(r["rect"])]
        for c in cells:
            if (sid, c) in reached:
                return True
            for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
                if (sid, n) in reached:
                    return True
        return False

    def _safe_targets(self):
        targets = []
        for safe in self.station.data["safe_areas"]:
            for l in self.station.sections[safe].get("vertical_links", []):
                targets += [(safe, tuple(c)) for c in l["cells"]]
            if safe == self.station.data["muster_point"]["section"]:
                targets.append((safe, tuple(self.station.data["muster_point"]["cells"][0])))
        return targets

    def emergency_path(self, room_id):
        """(shortest length to safety, alternates, spof_edges): alternates counts
        open edges whose single closure still leaves a route; spof_edges names the
        single points of failure (closing that one edge severs the room)."""
        a = self.access_cell(room_id)
        if a is None:
            return None, 0, []
        best = None
        for t in self._safe_targets():
            d = self.path(a, t)
            if d is not None and (best is None or d < best):
                best = d
        alternates, spof = 0, []
        if best is not None:
            state_keys = ([("portal_states", p) for p in self.d["portal_states"]]
                          + [("link_states", l) for l in self.d["link_states"]])
            for dct, key in state_keys:
                saved = self.d[dct][key]
                if saved not in ("open", "operational"):
                    continue
                try:
                    self.d[dct][key] = "closed"
                    still = any(self.path(a, t) is not None for t in self._safe_targets())
                finally:
                    self.d[dct][key] = saved
                if still:
                    alternates += 1
                else:
                    spof.append(key)
        return best, alternates, spof

    # ---------------- placement validation ----------------
    def validate_room(self, room):
        st = self.station
        sid = room["section"]
        fam = FAMILIES["slice_families"][room["family"]]
        cells = [tuple(c) for c in _rect_cells(room["rect"])]
        hard_cells = []
        for c in cells:
            if not st.in_grid(sid, c):
                raise ValidationError("footprint leaves the section: %s at %s" % (room["id"], (c,)))
            fx = st.fixed_at(sid, c)
            if fx and fx[1] == "never":
                continue   # rooms may span dead architecture; cells are unusable, not illegal
            if not st.buildable(sid, c):
                raise ValidationError("cell %s is not buildable (%s): outside a buildable zone"
                                     % (str(c), room["id"]))
            hard_cells.append(c)
        if not room.get("module_of") and room.get("form") != "temporary":
            # modules extend a parent; temporary zones are open-zone (no shell, no minimum)
            mw, mh = fam["min_footprint"]
            w, h = room["rect"]["w"], room["rect"]["h"]
            if not ((w >= mw and h >= mh) or (w >= mh and h >= mw)) or len(hard_cells) < mw * mh:
                raise ValidationError("footprint below the %s family minimum %dx%d: %s"
                                     % (room["family"], mw, mh, room["id"]))
        for other in self.rooms.values():
            if other["id"] == room["id"] or other["section"] != sid:
                continue
            overlap = set(cells) & {tuple(c) for c in _rect_cells(other["rect"])}
            if overlap:
                raise ValidationError("room overlap: %s and %s share %s"
                                     % (room["id"], other["id"], sorted(overlap)[0]))
        if room.get("module_of"):
            parent = self.rooms.get(room["module_of"])
            if parent is None:
                raise ValidationError("module %s attaches to a room that does not exist" % room["id"])
            if parent.get("module_of"):
                raise ValidationError("module %s must attach to a full room instance, "
                                     "not another module (no module chains — 22 S1)" % room["id"])
            if parent["section"] != sid:
                raise ValidationError("module %s must share its parent's section" % room["id"])
            pcells = {tuple(c) for c in _rect_cells(parent["rect"])}
            if not any(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a in cells for b in pcells):
                raise ValidationError("module %s does not touch its parent room %s "
                                     "(the Expand verb grows into the adjacent bay — 10 S5)"
                                     % (room["id"], room["module_of"]))
        if room.get("form") == "feature_built":
            feat = room.get("feature")
            fcells = st.fixed_type_cells(sid, feat)
            if not any(abs(a[0] - b[0]) + abs(a[1] - b[1]) <= 1 for a in cells for b in fcells):
                raise ValidationError("feature-built room %s is not at its anchor (%s)"
                                     % (room["id"], feat))
        if self.access_cell(room["id"]) is None:
            raise ValidationError("no door access: %s has no walkable doorstep" % room["id"])
        req = fam.get("required_utilities", {})
        if "power" in req and req["power"] not in ("self_or_grid",):
            node = st.sections[sid]["utility_node"]
            live = self.d["trunk_states"].get(node["trunk"],
                                             st.trunks[node["trunk"]]["state_day1"]) == "live"
            if not live and room.get("form") not in ("temporary",):
                raise ValidationError("no utility service: %s needs power but %s is dark "
                                     "(extend the trunk first — CONNECT)" % (room["id"], node["trunk"]))
        return True

    def _check_restrictions(self, obj, spec, sid, cells):
        st = self.station
        restr = set(spec.get("restrictions", [])) & HARD_RESTRICTIONS
        def near_fixed(types):
            anchors = []
            for t in types:
                anchors += st.fixed_type_cells(sid, t)
            return any(abs(a[0] - b[0]) + abs(a[1] - b[1]) <= 1 for a in cells for b in anchors)
        if "interior_only" in restr:
            rcells = set()
            for r in self.rooms.values():
                if r["section"] == sid:
                    rcells |= {tuple(c) for c in _rect_cells(r["rect"])}
            if not set(cells) <= rcells:
                raise ValidationError("%s is interior-only: place it inside a room" % obj["id"])
        if "portal_or_partition_gap_only" in restr:
            gap_ok = set(cells) <= st.link_cells(sid) or near_fixed(["airlock_doors"]) \
                     or any(self.objects[o]["type"] == "partition"
                            and abs(self.objects[o]["pos"][0] - cells[0][0])
                            + abs(self.objects[o]["pos"][1] - cells[0][1]) == 1
                            for o in self.objects if o != obj["id"])
            if not gap_ok:
                raise ValidationError("%s must hang in a portal or a partition gap" % obj["id"])
        if "tank_adjacent" in restr and not near_fixed(["emergency_tank"]):
            raise ValidationError("%s must sit beside the emergency tank" % obj["id"])
        if "needs_water_feature_or_tank_adjacent" in restr \
                and not near_fixed(["emergency_tank", "cistern_main", "drain_channel"]):
            raise ValidationError("%s needs a water feature or the tank beside it" % obj["id"])
        if "signal_box_only_in_slice" in restr and sid != "signal_box":
            raise ValidationError("%s belongs in the Signal Box in the slice" % obj["id"])
        if "west_gallery_only_in_slice" in restr and sid != "west_gallery":
            raise ValidationError("%s belongs in the West Gallery in the slice" % obj["id"])
        if "cistern_works_only_in_slice" in restr and obj.get("room") != "cistern_works":
            raise ValidationError("%s attaches to the Cistern Works in the slice" % obj["id"])
        if "common_areas" in restr:
            if sid not in self.station.data["safe_areas"] \
                    and not any(r["section"] == sid for r in self.rooms.values()):
                raise ValidationError("%s belongs in an inhabited common area" % obj["id"])
        if "carer_side_clear" in restr:
            inter = [tuple(c) for c in self.object_interactions(obj)]
            blocked = self._blocking_cells(sid, ignore_obj=obj["id"])
            clear = [c for c in inter if st.in_grid(sid, c)
                     and (st.fixed_at(sid, c) is None or st.fixed_at(sid, c)[1] != "never")
                     and c not in blocked]
            if len(clear) < len(inter):
                raise ValidationError("%s needs its carer side clear (every working cell open)"
                                     % obj["id"])

    def validate_object(self, obj):
        st = self.station
        spec = OBJECTS["objects"][obj["type"]]
        sid = self.object_section(obj)
        cells = [tuple(c) for c in self.object_cells(obj)]
        for c in cells:
            if not st.in_grid(sid, c):
                raise ValidationError("object %s leaves the section at %s" % (obj["id"], str(c)))
            fx = st.fixed_at(sid, c)
            if fx and fx[1] == "never":
                raise ValidationError("object %s overlaps fixed architecture (%s) at %s"
                                     % (obj["id"], fx[0], str(c)))
            if not st.buildable(sid, c) and not (fx and fx[1] in ("always", "open")
                                                 and not spec["block_paths"]):
                raise ValidationError("object %s is outside a buildable zone at %s"
                                     % (obj["id"], str(c)))
            if c in st.link_cells(sid) and spec["block_paths"]:
                raise ValidationError("object %s would block a stair/lift/portal cell at %s"
                                     % (obj["id"], str(c)))
        occ = self._occupied_cells(sid, ignore_obj=obj["id"])
        clash = set(cells) & occ
        if clash:
            raise ValidationError("those cells are occupied: %s collides at %s"
                                 % (obj["id"], sorted(clash)[0]))
        if obj.get("room"):
            r = self.rooms[obj["room"]]
            allowed = spec["rooms"]
            if "*" not in allowed and r["family"] not in allowed:
                raise ValidationError("%s does not belong in a %s room (%s)"
                                     % (obj["type"], r["family"], obj["id"]))
            rcells = {tuple(c) for c in _rect_cells(r["rect"])}
            for m in self.rooms.values():
                if m.get("module_of") == r["id"]:
                    rcells |= {tuple(c) for c in _rect_cells(m["rect"])}
            if not set(cells) <= rcells:
                raise ValidationError("object %s sticks out of its room %s" % (obj["id"], r["id"]))
            # socket budgets (22 S4): behavior family must be socketed; storage counted
            fam = FAMILIES["slice_families"][r["family"]]
            if spec["family"] not in UNIVERSAL_FAMILIES \
                    and spec["family"] not in fam.get("equipment_sockets", []):
                raise ValidationError("no %s socket in a %s room (%s)"
                                     % (spec["family"], r["family"], obj["id"]))
            if spec["family"] == "storage":
                count = sum(1 for o in self.objects.values()
                            if o.get("room") == r["id"] and o["id"] != obj["id"]
                            and OBJECTS["objects"][o["type"]]["family"] == "storage")
                if count + 1 > fam.get("storage_sockets", 99):
                    raise ValidationError("storage sockets full in %s (%d of %d)"
                                         % (r["id"], count + 1, fam.get("storage_sockets")))
        util = spec.get("utility") or ""
        if util.startswith("power") and not util.endswith(("_optional", "_storage", "storage")):
            node = st.sections[sid]["utility_node"]
            live = self.d["trunk_states"].get(node["trunk"],
                                             st.trunks[node["trunk"]]["state_day1"]) == "live"
            if not live:
                raise ValidationError("%s needs power but %s is dark (CONNECT first)"
                                     % (obj["id"], node["trunk"]))
        self._check_restrictions(obj, spec, sid, cells)
        inter = [tuple(c) for c in self.object_interactions(obj)]
        blocked = self._blocking_cells(sid, ignore_obj=obj["id"])
        clear = [c for c in inter
                 if st.in_grid(sid, c)
                 and (st.fixed_at(sid, c) is None or st.fixed_at(sid, c)[1] != "never")
                 and c not in blocked]
        if inter and not clear:
            raise ValidationError("no clear working side: every interaction cell of %s is blocked"
                                 % obj["id"])
        if spec["block_paths"] and inter:
            reached = self.reached_cells(self.muster(), ignore_obj=obj["id"])
            if not any((sid, c) in reached for c in clear):
                raise ValidationError("the working side of %s would be unreachable from the "
                                     "muster point" % obj["id"])
        return True

    def _stranded_objects(self, layout):
        """Objects whose every interaction cell is covered or unreached (all
        sections). An interaction cell counts as served if it — or a 4-neighbor
        (the bedside rule: reaching the bed's side is reaching the bed) — is in
        the muster flood-fill."""
        reached = layout.reached_cells(layout.muster())
        out = set()
        for o in layout.objects.values():
            inter = [tuple(c) for c in layout.object_interactions(o)]
            if not inter:
                continue
            sid = layout.object_section(o)
            st = layout.station
            blocked = layout._blocking_cells(sid, ignore_obj=o["id"])
            def served(c):
                if not st.in_grid(sid, c):
                    return False
                fx = st.fixed_at(sid, c)
                if fx and fx[1] == "never":
                    return False
                if c in blocked:
                    return False
                if (sid, c) in reached:
                    return True
                return any((sid, n) in reached
                           for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]),
                                     (c[0], c[1] + 1), (c[0], c[1] - 1)))
            if not any(served(c) for c in inter):
                out.add(o["id"])
        return out

    def validate_no_shelter_block(self, obj):
        """A placement is REFUSED (slice policy — no override) if it would sever an
        essential facility from the muster point, or strand ANY existing object —
        reachability, not mere cell coverage, is the criterion (never_seals_last_path
        / must_stay_reachable are data statements of this guard). Recovery is always
        named: remove the placement or open another route (CONNECT/ADAPT)."""
        before = self._stranded_objects(self)
        trial = self.copy()
        trial.objects[obj["id"]] = copy.deepcopy(obj)
        trial.d["objects"].append(copy.deepcopy(obj))
        for fac in self.d.get("essential_facilities", []):
            if not trial.reachable_from_muster(fac):
                raise ValidationError("refused: placing %s would cut off %s — open another "
                                     "route first (recovery via CONNECT/ADAPT)" % (obj["id"], fac))
        after = trial._stranded_objects(trial)
        newly = after - before - {obj["id"]}
        if newly:
            raise ValidationError("refused: placing %s would strand %s — its every working cell "
                                 "goes dark or unreachable" % (obj["id"], sorted(newly)[0]))
        return True

    # ---------------- mutation ----------------
    def copy(self):
        return Layout(self.d, station=self.station)

    def place_object(self, obj, check_shelter=True):
        self.validate_object(obj)
        if check_shelter:
            self.validate_no_shelter_block(obj)
        self.objects[obj["id"]] = obj
        self.d["objects"].append(obj)
        return True

    def remove_object(self, obj_id):
        self.objects.pop(obj_id)
        self.d["objects"] = [o for o in self.d["objects"] if o["id"] != obj_id]

    def move_object(self, obj_id, pos, rot=None):
        original = copy.deepcopy(self.objects[obj_id])
        moved = copy.deepcopy(original)
        moved["pos"] = list(pos)
        if rot is not None:
            moved["rot"] = rot
        self.remove_object(obj_id)
        try:
            self.place_object(moved)
        except ValidationError:
            self.place_object(original, check_shelter=False)
            raise
        return True

    def store_object(self, obj_id):
        """Deconstruct-to-store: the object leaves the floor intact (10 S4).
        Story objects can never be stored or deconstructed."""
        spec = OBJECTS["objects"][self.objects[obj_id]["type"]]
        if "never_deconstruct" in spec.get("restrictions", []) or spec.get("store_result") is None:
            raise ValidationError("%s is part of the station's story — it cannot be removed"
                                 % obj_id)
        o = self.objects[obj_id]
        self.remove_object(obj_id)
        o["stored"] = True
        return o

    def repurpose_room(self, room_id, new_family, new_specialization=None):
        """Validate-then-commit: the converted room must itself be legal; equipment
        the new family cannot socket is stored (never destroyed) and leaves the floor."""
        trial = self.copy()
        r2 = trial.rooms[room_id]
        old_family = r2["family"]
        displaced = []
        for o in list(trial.objects.values()):
            if o.get("room") == room_id:
                allowed = OBJECTS["objects"][o["type"]]["rooms"]
                fam_ok = "*" in allowed or new_family in allowed
                if not fam_ok:
                    displaced.append(o["id"])
                    trial.remove_object(o["id"])
        r2["family"] = new_family
        if new_specialization:
            r2["specialization"] = new_specialization
        r2["repurposed_from"] = r2.get("repurposed_from", old_family)
        trial.validate_room(r2)               # raises before anything commits
        stored = []
        for oid in displaced:
            stored.append(self.store_object(oid))
        r = self.rooms[room_id]
        r.update({k: r2[k] for k in ("family", "repurposed_from")})
        if new_specialization:
            r["specialization"] = new_specialization
        return [o["id"] for o in stored]

    def close_door(self, key):
        """Close a placed door/portal for isolation. Returns the facilities that
        become unreachable — the warn-before channel for state-change severance."""
        if key in self.objects and self.objects[key]["type"] == "door_panel":
            self.d["door_states"][key] = "closed"
        elif key in self.d["portal_states"]:
            self.d["portal_states"][key] = "closed"
        elif key in self.d["link_states"]:
            self.d["link_states"][key] = "closed"
        else:
            raise ValidationError("no door, portal, or link named %s" % key)
        return [f for f in self.d.get("essential_facilities", [])
                if not self.reachable_from_muster(f)]

    def open_door(self, key):
        if key in self.objects and self.objects[key]["type"] == "door_panel":
            self.d["door_states"][key] = "open"
        elif key in self.d["portal_states"]:
            self.d["portal_states"][key] = "open"
        elif key in self.d["link_states"]:
            self.d["link_states"][key] = "operational"
        else:
            raise ValidationError("no door, portal, or link named %s" % key)

    # ---------------- save / reload ----------------
    def to_dict(self):
        return copy.deepcopy(self.d)

    @classmethod
    def from_dict(cls, d, station=None):
        return cls(d, station=station)

    # ---------------- metrics ----------------
    def noise_distance(self, room_id):
        """Path distance from a room to the nearest very-high-noise source access
        (the Flywheel Vault's stair head) — the visible physical fact behind the
        rest-vs-noise adjacency (25 S3). Bigger is quieter."""
        a = self.access_cell(room_id)
        if a is None:
            return None
        noisy = []
        for sid, sec in self.station.sections.items():
            if sec.get("environment", {}).get("noise") == "very_high":
                for l in sec.get("vertical_links", []):
                    noisy.append((l["to"], tuple(l["to_cells"][0])))
        dists = [self.path(a, n) for n in noisy]
        dists = [d for d in dists if d is not None]
        return min(dists) if dists else None

    def backed_up_rooms(self):
        """Rooms with a battery bank in or adjacent — the backup-charge adjacency
        (25 S3); the survival model's battery bridge is its modeled effect."""
        out = []
        for o in self.objects.values():
            if o["type"] != "battery_bank":
                continue
            sid = self.object_section(o)
            cells = {tuple(c) for c in self.object_cells(o)}
            grown = set()
            for c in cells:
                for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1),
                          (c[0], c[1] - 1), c):
                    grown.add(n)
            for r in self.rooms.values():
                if r["section"] == sid and grown & {tuple(c) for c in _rect_cells(r["rect"])}:
                    out.append(r["id"])
        return sorted(set(out))

    def metrics(self):
        lengths = []
        areas = [r for r in self.rooms.values() if not r.get("module_of")]
        for i, a in enumerate(areas):
            for b in areas[i + 1:]:
                ca, cb = self.access_cell(a["id"]), self.access_cell(b["id"])
                if ca and cb:
                    d = self.path(ca, cb)
                    if d is not None:
                        lengths.append(d)
        essential = [self.path(self.muster(), self.access_cell(f))
                     for f in self.d.get("essential_facilities", [])
                     if self.access_cell(f)]
        med = [r["id"] for r in self.rooms.values() if r["family"] == "medical"]
        gate = ("scrubber_gate", (1, 1))
        entrance_to_medical = min([self.path(gate, self.access_cell(m)) for m in med
                                   if self.access_cell(m)] or [None],
                                  key=lambda x: (x is None, x))
        store = [r["id"] for r in self.rooms.values() if r["family"] == "storage"]
        work = [r["id"] for r in self.rooms.values() if r["family"] == "workshop"]
        s2w = (self.path(self.access_cell(store[0]), self.access_cell(work[0]))
               if store and work else None)
        rest = [r["id"] for r in self.rooms.values() if r["family"] == "rest"]
        spofs = {r["id"]: self.emergency_path(r["id"])[2] for r in areas}
        return {
            "avg_path": round(sum(lengths) / len(lengths), 1) if lengths else None,
            "longest_essential": max([e for e in essential if e is not None], default=None),
            "entrance_to_medical": entrance_to_medical,
            "storage_to_workshop": s2w,
            "noise_distance_rest": {r: self.noise_distance(r) for r in rest},
            "backed_up_rooms": self.backed_up_rooms(),
            "spof_edges": {k: v for k, v in spofs.items() if v},
        }


# ---------------- blueprint / reservation ledger (executable rules) ----------------
class MaterialsLedger:
    """The reservation arithmetic Prompt 3 declared rule-level (D-045), executable:
    preview never spends; save reserves nothing; activation reserves; delivered
    stages consume; cancel refunds ONLY the unconsumed reserve; deconstruct
    recovers 50% of consumed once. Every transition is state-guarded (D-048)."""

    def __init__(self, stock):
        self.stock = float(stock)
        self.projects = {}

    def _check(self):
        assert self.stock >= -1e-9, "stock went negative"
        for p in self.projects.values():
            assert p["reserved"] >= -1e-9 and p["consumed"] >= -1e-9

    def preview(self, pid, cost):
        return {"cost": cost, "affordable": cost <= self.stock}

    def save_blueprint(self, pid, cost):
        self.projects[pid] = {"cost": float(cost), "state": "blueprint",
                              "reserved": 0.0, "consumed": 0.0, "deconstructed": False}
        return self.projects[pid]

    def activate(self, pid):
        p = self.projects[pid]
        if p["state"] != "blueprint":
            raise ValidationError("only a saved blueprint can be activated")
        if p["cost"] > self.stock:
            raise ValidationError("insufficient materials: need %.0f, hold %.0f (the UI names "
                                 "the missing family — the anti-lie rule, 16 S1)"
                                 % (p["cost"], self.stock))
        self.stock -= p["cost"]
        p["reserved"] = p["cost"]
        p["state"] = "active"
        self._check()

    def deliver_stage(self, pid, fraction):
        p = self.projects[pid]
        if p["state"] != "active":
            raise ValidationError("no active project")
        if fraction <= 0:
            raise ValidationError("stage fraction must be positive")
        amt = min(p["reserved"], p["cost"] * fraction)
        p["reserved"] -= amt
        p["consumed"] += amt
        self._check()

    def cancel(self, pid):
        p = self.projects[pid]
        if p["state"] != "active":
            raise ValidationError("nothing to cancel")
        refund = p["reserved"]
        self.stock += refund
        p["reserved"] = 0.0
        p["state"] = "cancelled"
        self._check()
        return refund

    def complete(self, pid):
        p = self.projects[pid]
        if p["state"] != "active":
            raise ValidationError("only an active project can complete")
        p["consumed"] += p["reserved"]
        p["reserved"] = 0.0
        p["state"] = "complete"
        self._check()

    def deconstruct(self, pid):
        p = self.projects[pid]
        if p["state"] != "complete":
            raise ValidationError("only a completed installation can be deconstructed")
        if p["deconstructed"]:
            raise ValidationError("already deconstructed once — recovery is once per component")
        p["deconstructed"] = True
        recovered = 0.5 * p["consumed"]
        self.stock += recovered
        self._check()
        return recovered


def load_layout(name):
    return Layout(_load(os.path.join("layouts", name + ".json")))


def utility_headroom(layout):
    """Honest board proxy: sums utilities.json load values for load classes whose
    anchor objects are actually placed (base: scrubbers + lights). A consistency
    check against the survival model's board — not the week's arithmetic."""
    util = _load("utilities.json")
    loads = util["power"]["loads"]
    stabilized = any(r.get("upgrade") == "stabilized" for r in layout.rooms.values())
    gen = util["power"]["generation"]["stabilized" if stabilized else "partial"]
    demand = loads["scrubbers"] + loads["lights"]
    types = {o["type"] for o in layout.objects.values()}
    if {"radio_rig", "radio_rig_wired"} & types:
        demand += loads["radio"]
    if "hotplate_counter" in types:
        demand += loads["hotplate"]
    if "workbench" in types:
        demand += loads["tools"]
    if "comfort_lamp" in types:
        demand += loads["comfort_lighting"]
    if "pump_module" in types:
        demand += loads["cistern_pumps"]
    return gen - demand


def sheddable_load(layout):
    util = _load("utilities.json")
    loads, tier = util["power"]["loads"], util["power"]["tier_of"]
    types = {o["type"] for o in layout.objects.values()}
    total = 0
    if "comfort_lamp" in types:
        total += loads["comfort_lighting"]
    if "hotplate_counter" in types:
        total += loads["hotplate"]
    if "workbench" in types:
        total += loads["tools"]
    return total
