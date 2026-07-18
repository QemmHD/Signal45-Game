#!/usr/bin/env python3
"""SIGNAL 45 — engine-independent spatial, adjacency, access, and room-data model (Prompt 4, D-046).

ONE logical source of truth: SECTION -> BAY -> CELL (tools/data/station_sections.json).
Placement, room ownership, object footprints, utility reach, navigation, and save
data all reference the same cell addresses; a future renderer converts cells to
world transforms at draw time and stores nothing of its own.

This module is design evidence, not gameplay: it proves the slice layouts are
structurally consistent (placeable, navigable, evacuable, save-stable) and that
the blueprint/reservation arithmetic obeys its anti-exploit rules. It does NOT
prove the building system is fun — that is a playable-prototype question.

All values PROVISIONAL (D-046). Deterministic; no wall-clock, no randomness.
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


def _rect_cells(rect):
    return [(rect["x"] + dx, rect["y"] + dy)
            for dy in range(rect["h"]) for dx in range(rect["w"])]


def _fixed_cells(sec):
    """{(x, y): (type, walkable_when)} for a section definition."""
    out = {}
    for f in sec.get("fixed", []):
        cells = ([tuple(c) for c in f["cells"]] if "cells" in f
                 else [tuple(c) for c in _rect_cells(f["cells_rect"])])
        for c in cells:
            out[c] = (f["type"], f["walkable_when"])
    return out


def rotate_footprint(w, h, cells, rot):
    """Rotate a footprint and its relative cells in 90-degree steps."""
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
    """Every rejection carries a specific, player-presentable reason."""


class Station:
    def __init__(self, data=SECTIONS):
        self.data = data
        self.sections = data["sections"]
        self.trunks = data["trunks"]
        self._fixed = {sid: _fixed_cells(s) for sid, s in self.sections.items()}

    def in_grid(self, sid, c):
        w, h = self.sections[sid]["grid"]
        return 0 <= c[0] < w and 0 <= c[1] < h

    def fixed_at(self, sid, c):
        return self._fixed[sid].get(tuple(c))

    def buildable(self, sid, c):
        """A cell accepts room footprints / object placement."""
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
                # convertible shells (walkable_when=interior) accept rooms;
                # hard architecture (never/always/open) does not
                return fx[1] == "interior"
        return False

    def link_cells(self, sid):
        cells = set()
        for l in self.sections[sid].get("vertical_links", []):
            cells |= {tuple(c) for c in l["cells"]}
        for e in self.sections[sid].get("entries", []):
            cells |= {tuple(c) for c in e["cells"]}
        return cells


class Layout:
    """A concrete station state: rooms, objects, portal/link/trunk states."""

    def __init__(self, layout_data, station=None):
        self.station = station or Station()
        self.d = copy.deepcopy(layout_data)
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
            if OBJECTS["objects"][o["type"]]["block_paths"]:
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

    def _edges(self, ignore_obj=None):
        """Portal + vertical-link edges usable under current states."""
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

    def path(self, start, goal, ignore_obj=None):
        """BFS over cells; start/goal = (section, (x, y)). Returns path length or None."""
        start = (start[0], tuple(start[1]))
        goal = (goal[0], tuple(goal[1]))
        if not self.walkable(*start, ignore_obj=ignore_obj):
            # standing inside a non-blocking object is fine; a hard-blocked start is not
            return None
        jump = {}
        for a, b in self._edges(ignore_obj=ignore_obj):
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
                nsid, nc = n
                if not self.walkable(nsid, nc, ignore_obj=ignore_obj):
                    continue
                seen.add(n)
                q.append((n, dist + 1))
        return None

    def access_cell(self, room_id):
        """A walkable cell inside or adjacent to the room — its 'doorstep'."""
        r = self.rooms[room_id]
        sid = r["section"]
        cells = [tuple(c) for c in _rect_cells(r["rect"])]
        for c in cells:
            if self.walkable(sid, c):
                return (sid, c)
        for c in cells:
            for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
                if self.walkable(sid, n):
                    return (sid, n)
        return None

    def muster(self):
        m = self.station.data["muster_point"]
        return (m["section"], tuple(m["cells"][0]))

    def reachable_from_muster(self, room_id):
        a = self.access_cell(room_id)
        return a is not None and self.path(self.muster(), a) is not None

    def emergency_path(self, room_id):
        """Path from the room to any safe area; returns (length, alternates)."""
        a = self.access_cell(room_id)
        if a is None:
            return None, 0
        best = None
        for safe in self.station.data["safe_areas"]:
            sec = self.station.sections[safe]
            targets = []
            for l in sec.get("vertical_links", []):
                targets += [tuple(c) for c in l["cells"]]
            targets.append(tuple(self.station.data["muster_point"]["cells"][0])
                           if safe == self.station.data["muster_point"]["section"] else None)
            for t in [t for t in targets if t]:
                d = self.path(a, (safe, t))
                if d is not None and (best is None or d < best):
                    best = d
        alternates = 0
        if best is not None:
            # closing each currently-open portal/link one at a time: does an
            # alternative route to safety survive?
            for kind, key in ([("portal", p) for p in self.d["portal_states"]]
                              + [("link", l) for l in self.d["link_states"]]):
                saved = self.d["portal_states" if kind == "portal" else "link_states"][key]
                if saved not in ("open", "operational"):
                    continue
                self.d["portal_states" if kind == "portal" else "link_states"][key] = "closed"
                still = any(self.path(a, (s, tuple(l["cells"][0]))) is not None
                            for s in self.station.data["safe_areas"]
                            for l in self.station.sections[s].get("vertical_links", []))
                self.d["portal_states" if kind == "portal" else "link_states"][key] = saved
                if still:
                    alternates += 1
        return best, alternates

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
                continue   # rooms may span dead architecture (columns); cells are unusable, not illegal
            if not st.buildable(sid, c):
                raise ValidationError("cell %s is not buildable (%s): outside a buildable zone"
                                     % (str(c), room["id"]))
            hard_cells.append(c)
        if not room.get("module_of"):    # modules extend a parent; no family minimum
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
            if parent["section"] != sid:
                raise ValidationError("module %s must share its parent's section" % room["id"])
            pcells = {tuple(c) for c in _rect_cells(parent["rect"])}
            touching = any(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
                           for a in cells for b in pcells)
            if not touching:
                raise ValidationError("module %s does not touch its parent room %s "
                                     "(the Expand verb grows into the adjacent bay — 10 S5)"
                                     % (room["id"], room["module_of"]))
        if room.get("form") == "feature_built":
            feat = room.get("feature")
            fcells = [c for c, (t, _) in st._fixed[sid].items() if t == feat]
            near = any(abs(a[0] - b[0]) + abs(a[1] - b[1]) <= 1
                       for a in cells for b in fcells)
            if not near:
                raise ValidationError("feature-built room %s is not at its anchor (%s)"
                                     % (room["id"], feat))
        if self.access_cell(room["id"]) is None:
            raise ValidationError("no door access: %s has no walkable doorstep" % room["id"])
        req = fam.get("required_utilities", {})
        if "power" in req and req["power"] not in ("self_or_grid",):
            node = st.sections[sid]["utility_node"]
            trunk = st.trunks[node["trunk"]]
            live = self.d["trunk_states"].get(node["trunk"], trunk["state_day1"]) == "live"
            if not live and room.get("form") not in ("temporary",):
                raise ValidationError("no utility service: %s needs power but %s is dark "
                                     "(extend the trunk first — CONNECT)" % (room["id"], node["trunk"]))
        return True

    def validate_object(self, obj):
        st = self.station
        spec = OBJECTS["objects"][obj["type"]]
        sid = self.object_section(obj)
        cells = [tuple(c) for c in self.object_cells(obj)]
        for c in cells:
            if not st.in_grid(sid, c):
                raise ValidationError("object %s leaves the section at %s" % (obj["id"], str(c)))
            fx = st.fixed_at(sid, c)
            if fx and fx[1] in ("never",):
                raise ValidationError("object %s overlaps fixed architecture (%s) at %s"
                                     % (obj["id"], fx[0], str(c)))
            if c in st.link_cells(sid) and spec["block_paths"]:
                raise ValidationError("object %s would block a stair/lift/portal cell at %s"
                                     % (obj["id"], str(c)))
        occ = self._occupied_cells(sid, ignore_obj=obj["id"])
        clash = set(cells) & occ
        if clash:
            raise ValidationError("object overlap: %s collides at %s" % (obj["id"], sorted(clash)[0]))
        if obj.get("room"):
            r = self.rooms[obj["room"]]
            allowed = spec["rooms"]
            if "*" not in allowed and r["family"] not in allowed:
                raise ValidationError("%s does not belong in a %s room (%s)"
                                     % (obj["type"], r["family"], obj["id"]))
            rcells = {tuple(c) for c in _rect_cells(r["rect"])}
            mods = [m for m in self.rooms.values() if m.get("module_of") == r["id"]]
            for m in mods:
                rcells |= {tuple(c) for c in _rect_cells(m["rect"])}
            if not set(cells) <= rcells:
                raise ValidationError("object %s sticks out of its room %s" % (obj["id"], r["id"]))
        inter = [tuple(c) for c in self.object_interactions(obj)]
        blocked = self._blocking_cells(sid, ignore_obj=obj["id"])
        clear = [c for c in inter
                 if st.in_grid(sid, c)
                 and (st.fixed_at(sid, c) is None or st.fixed_at(sid, c)[1] != "never")
                 and c not in blocked]
        if inter and not clear:
            raise ValidationError("no clear interaction side: every working cell of %s is blocked"
                                 % obj["id"])
        if spec["block_paths"] and inter:
            reachable = any(self.path(self.muster(), (sid, c), ignore_obj=obj["id"]) is not None
                            for c in clear)
            if not reachable:
                raise ValidationError("interaction cells of %s are unreachable from the muster point"
                                     % obj["id"])
        return True

    def validate_no_shelter_block(self, obj):
        """A placement may never sever an essential facility from the muster point,
        and may never strand an existing working object (every workstation, bed,
        store, or utility module keeps at least one clear, reachable interaction
        cell) — furniture cannot silently make a functioning room unusable."""
        trial = self.copy()
        trial.objects[obj["id"]] = copy.deepcopy(obj)
        trial.d["objects"].append(copy.deepcopy(obj))
        for fac in self.d.get("essential_facilities", []):
            if not trial.reachable_from_muster(fac):
                raise ValidationError("placement of %s would cut off %s — severe confirmation "
                                     "required, recovery must exist" % (obj["id"], fac))
        sid = self.object_section(obj)
        st = self.station
        for o in self.objects.values():
            if self.object_section(o) != sid or o["id"] == obj["id"]:
                continue
            inter = [tuple(c) for c in self.object_interactions(o)]
            if not inter:
                continue
            blocked = trial._blocking_cells(sid, ignore_obj=o["id"])
            clear = [c for c in inter
                     if st.in_grid(sid, c)
                     and (st.fixed_at(sid, c) is None or st.fixed_at(sid, c)[1] != "never")
                     and c not in blocked]
            had_clear = any(
                c for c in inter
                if st.in_grid(sid, c)
                and (st.fixed_at(sid, c) is None or st.fixed_at(sid, c)[1] != "never")
                and c not in self._blocking_cells(sid, ignore_obj=o["id"]))
            if had_clear and not clear:
                raise ValidationError("placement of %s would strand %s — its every working cell "
                                     "goes dark (warned before confirm)" % (obj["id"], o["id"]))
        return True

    # ---------------- mutation used by tests ----------------
    def copy(self):
        c = Layout(self.d, station=self.station)
        return c

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
            self.place_object(original, check_shelter=False)   # move failed: object stays put
            raise
        return True

    def store_object(self, obj_id):
        """Deconstruct-to-store: the object leaves the floor intact (10 S4)."""
        spec = OBJECTS["objects"][self.objects[obj_id]["type"]]
        if spec.get("store_result") != "stored":
            raise ValidationError("%s cannot be stored" % obj_id)
        o = self.objects[obj_id]
        self.remove_object(obj_id)
        o["stored"] = True
        return o

    def repurpose_room(self, room_id, new_family, new_specialization=None):
        r = self.rooms[room_id]
        old = r["family"]
        incompatible = []
        for o in self.objects.values():
            if o.get("room") == room_id:
                allowed = OBJECTS["objects"][o["type"]]["rooms"]
                if "*" not in allowed and new_family not in allowed:
                    incompatible.append(o["id"])
        for oid in incompatible:
            self.objects[oid]["room"] = None
            self.objects[oid]["stored"] = True     # equipment stored, not destroyed (10 S4)
        r["family"] = new_family
        if new_specialization:
            r["specialization"] = new_specialization
        r["repurposed_from"] = r.get("repurposed_from", old)
        return incompatible

    # ---------------- save / reload ----------------
    def to_dict(self):
        return copy.deepcopy(self.d)

    @classmethod
    def from_dict(cls, d, station=None):
        return cls(d, station=station)

    # ---------------- metrics ----------------
    def metrics(self):
        pairs, lengths = [], []
        areas = [r for r in self.rooms.values() if not r.get("module_of")]
        for i, a in enumerate(areas):
            for b in areas[i + 1:]:
                ca, cb = self.access_cell(a["id"]), self.access_cell(b["id"])
                if ca and cb:
                    d = self.path(ca, cb)
                    if d is not None:
                        lengths.append(d)
                        pairs.append((a["id"], b["id"], d))
        essential = [self.path(self.muster(), self.access_cell(f))
                     for f in self.d.get("essential_facilities", [])
                     if self.access_cell(f)]
        med = [r["id"] for r in self.rooms.values() if r["family"] == "medical"]
        gate = ("scrubber_gate", (1, 1))
        entrance_to_medical = (self.path(gate, self.access_cell(med[0])) if med else None)
        store = [r["id"] for r in self.rooms.values() if r["family"] == "storage"]
        work = [r["id"] for r in self.rooms.values() if r["family"] == "workshop"]
        s2w = (self.path(self.access_cell(store[0]), self.access_cell(work[0]))
               if store and work else None)
        return {
            "avg_path": round(sum(lengths) / len(lengths), 1) if lengths else None,
            "longest_essential": max([e for e in essential if e is not None], default=None),
            "entrance_to_medical": entrance_to_medical,
            "storage_to_workshop": s2w,
            "pair_count": len(pairs),
        }


# ---------------- blueprint / reservation ledger (executable rules) ----------------
class MaterialsLedger:
    """The reservation arithmetic that Prompt 3 declared rule-level (D-045) is
    executable here: preview never spends; activation reserves; delivered stages
    consume; cancel refunds ONLY the unconsumed reserve; deconstruct recovers
    50% of consumed materials exactly once. Profit is structurally impossible."""

    def __init__(self, stock):
        self.stock = float(stock)
        self.projects = {}

    def _check(self):
        assert self.stock >= -1e-9, "stock went negative"
        for p in self.projects.values():
            assert p["reserved"] >= -1e-9 and p["consumed"] >= -1e-9

    def preview(self, pid, cost):
        return {"cost": cost, "affordable": cost <= self.stock}   # no side effects, ever

    def save_blueprint(self, pid, cost):
        self.projects[pid] = {"cost": float(cost), "state": "blueprint",
                              "reserved": 0.0, "consumed": 0.0, "deconstructed": False}
        return self.projects[pid]

    def activate(self, pid):
        p = self.projects[pid]
        if p["state"] != "blueprint":
            raise ValidationError("only a saved blueprint can be activated")
        if p["cost"] > self.stock:
            raise ValidationError("insufficient materials: need %.0f, hold %.0f (names its family "
                                 "in the UI — the anti-lie rule, 16 S1)" % (p["cost"], self.stock))
        self.stock -= p["cost"]
        p["reserved"] = p["cost"]
        p["state"] = "active"
        self._check()

    def deliver_stage(self, pid, fraction):
        p = self.projects[pid]
        if p["state"] != "active":
            raise ValidationError("no active project")
        amt = min(p["reserved"], p["cost"] * fraction)
        p["reserved"] -= amt
        p["consumed"] += amt
        self._check()

    def cancel(self, pid):
        p = self.projects[pid]
        if p["state"] != "active":
            raise ValidationError("nothing to cancel")
        refund = p["reserved"]                      # consumed stages never refund
        self.stock += refund
        p["reserved"] = 0.0
        p["state"] = "cancelled"
        self._check()
        return refund

    def complete(self, pid):
        p = self.projects[pid]
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
    """Node-level demand proxy vs generation (utilities.json) — a consistency
    check, not a power simulation (the survival model owns the week's arithmetic)."""
    util = _load("utilities.json")
    gen = util["power"]["generation"]["stabilized"]
    demand = 0
    for r in layout.rooms.values():
        fam = FAMILIES["slice_families"][r["family"]]
        if "power" in fam.get("required_utilities", {}):
            demand += 2
    for o in layout.objects.values():
        u = OBJECTS["objects"][o["type"]].get("utility") or ""
        if u.startswith("power"):
            demand += 2
    return gen - demand
