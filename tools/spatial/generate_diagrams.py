#!/usr/bin/env python3
"""Generate deterministic text diagrams directly from authoritative layout data."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from .coordinates import section_local_to_global
    from .model import derive_functional_area_count, derive_room_families, load_spatial_data, room_cells
    from .navigation import find_path
except ImportError:
    from coordinates import section_local_to_global
    from model import derive_functional_area_count, derive_room_families, load_spatial_data, room_cells
    from navigation import find_path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "reports" / "diagrams"
LAYOUTS = ["day1", "east_day7", "east_day7_alternate", "west_day7", "west_day7_alternate"]
FAMILY_GLYPHS = {"rest": "R", "medical": "M", "food": "F", "storage": "S", "utility": "U", "workshop": "W", "operations": "O"}


def _grid(data: Any, layout: dict[str, Any]) -> str:
    width = data.station["camera_bounds"]["shelter_overview"]["max_x"] + 1
    rows = {(level, lane): [" "] * width for level in [1, 0] for lane in [0, 1, 2]}
    for section_id, section in data.station["sections"].items():
        state = layout["section_states"].get(section_id, {}).get("access", "blocked")
        glyph = "." if state == "operational" else "×"
        for local_x in range(section["width"]):
            for level in section["levels"]:
                for lane in section["allowed_depth_lanes"]:
                    global_cell = section_local_to_global(data.station, {"section_id": section_id, "level": level, "x": local_x, "lane": lane})
                    rows[(global_cell["level"], global_cell["lane"])][global_cell["x"]] = glyph
    for room in layout["rooms"]:
        if room["state"] not in {"operational", "upgraded", "repurposed", "impaired", "under_repair"}:
            continue
        glyph = FAMILY_GLYPHS[room["family_id"]].lower() if room.get("temporary_zone") else FAMILY_GLYPHS[room["family_id"]]
        for section_id, level, x, lane in room_cells(data.station, room):
            global_cell = section_local_to_global(data.station, {"section_id": section_id, "level": level, "x": x, "lane": lane})
            rows[(global_cell["level"], global_cell["lane"])][global_cell["x"]] = glyph
    for section in data.station["sections"].values():
        for feature in section["fixed_architecture"]:
            for cell_range in feature["cells"]:
                start = cell_range.get("x_start", cell_range.get("x", 0)); end = cell_range.get("x_end", cell_range.get("x", start))
                lanes = cell_range.get("lanes", [cell_range.get("lane", 0)])
                for x in range(start, end + 1):
                    for lane in lanes:
                        logical = section_local_to_global(data.station, {"section_id": section["section_id"], "level": cell_range.get("level", 0), "x": x, "lane": lane})
                        current = rows[(logical["level"], logical["lane"])][logical["x"]]
                        if current in {".", "×"}: rows[(logical["level"], logical["lane"])][logical["x"]] = "#"
    lines = [
        f"# {layout['display_name']}", "",
        "> Generated from the authoritative JSON. `×` is unavailable shell, `#` fixed railway structure; lowercase is temporary function.", "",
        "```text", "global x  0000000000111111111122222222223333333", "          0123456789012345678901234567890123456",
    ]
    for level in [1, 0]:
        for lane in [0, 1, 2]:
            lines.append(f"L{level} lane{lane}  {''.join(rows[(level, lane)])}".rstrip())
    lines += ["```", "", f"Derived areas: **{derive_functional_area_count(layout)}**", f"Families: **{len(derive_room_families(layout))}** ({', '.join(sorted(derive_room_families(layout)))})", "", "Legend: `R` Rest, `M` Medical, `F` Food, `S` Storage, `U` Utility, `W` Workshop, `O` Operations.", ""]
    return "\n".join(lines)


def _utility_diagram(data: Any) -> str:
    lines = ["# Utility Topology", "", "> Generated from canonical Day 7 layouts. No player-drawn wires or pipes are implied.", "", "```mermaid", "flowchart LR"]
    seen: set[tuple[str, str]] = set()
    for layout_id in ["east_day7", "west_day7"]:
        layout = data.layout(layout_id)
        lines.append(f"  subgraph {layout_id}[{layout['display_name']}]")
        for node in layout["utility_nodes"]:
            key = (layout_id, node["node_id"]); seen.add(key)
            lines.append(f"    {layout_id}_{node['node_id']}[\"{node['utility']}: {node['node_id']}\"]")
        for branch in layout["utility_branches"]:
            style = "-. isolated .->" if branch.get("isolated") else "-->"
            lines.append(f"    {layout_id}_{branch['source_node']} {style} {layout_id}_{branch['target_node']}")
        lines.append("  end")
    lines += ["```", ""]
    return "\n".join(lines)


def _emergency_routes(data: Any) -> str:
    lines = ["# Emergency Routes", "", "> Generated path-cell sequences; costs are logical proxies, not seconds.", ""]
    for layout_id in LAYOUTS:
        layout = data.layout(layout_id)
        starts = [layout["safety_checks"]["primary_medical"], layout["safety_checks"]["main_gate"]]
        lines += [f"## {layout['display_name']}", ""]
        for label, start in zip(["Medical → safe", "Gate → safe"], starts):
            result = find_path(data, layout, start, layout["safety_checks"]["safe_area"], "emergency_evacuation")
            route = " → ".join(f"{p['section_id']}:{p['x']}/{p['lane']}" for p in result.path)
            lines.append(f"- {label}: {'reachable' if result.found else result.failure_reason}; cost {result.cost}; {route}")
        lines.append("")
    return "\n".join(lines)


def _camera_regions(data: Any) -> str:
    lines = ["# Camera Focus Regions", "", "> Generated from room-instance camera contracts; framing never changes simulation state.", "", "| Layout | Room | Target | Min bounds | Max bounds | Occlusion group |", "|---|---|---|---|---|---|"]
    for layout_id in LAYOUTS:
        layout = data.layout(layout_id)
        for room in layout["rooms"]:
            camera = room.get("camera")
            if not camera: continue
            target = camera["focus_target"]
            lines.append(f"| {layout_id} | {room['instance_id']} | {target['section_id']}:{target['x']}/{target['lane']} | {camera['minimum_focus_bounds']} | {camera['maximum_focus_bounds']} | {camera['occlusion_group']} |")
    lines.append("")
    return "\n".join(lines)


def generated_files() -> dict[Path, str]:
    data = load_spatial_data()
    files = {OUTPUT / f"{layout_id}.md": _grid(data, data.layout(layout_id)) for layout_id in LAYOUTS}
    files[OUTPUT / "utility_topology.md"] = _utility_diagram(data)
    files[OUTPUT / "emergency_routes.md"] = _emergency_routes(data)
    files[OUTPUT / "camera_focus_regions.md"] = _camera_regions(data)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    files = generated_files(); mismatches: list[str] = []
    for path, content in files.items():
        expected = content.rstrip() + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected: mismatches.append(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True); path.write_text(expected, encoding="utf-8")
    if mismatches:
        for path in mismatches: print(f"STALE {path}")
        return 1
    print(f"DIAGRAMS {'CURRENT' if args.check else 'GENERATED'} files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
