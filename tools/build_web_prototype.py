#!/usr/bin/env python3
"""Build the SIGNAL 45 web prototype.

Injects the authoritative spatial data (tools/data/*.json) into
web/index.template.html, replacing the __DATA_JSON__ token, and writes
web/index.html — a single self-contained file suitable for GitHub Pages
or artifact hosting. The template never carries data of its own; the
JSON files remain the single source of truth (D-046).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data"
TEMPLATE = ROOT / "web" / "index.template.html"
OUT = ROOT / "web" / "index.html"
TOKEN = "__DATA_JSON__"


def load(p: Path):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def build() -> Path:
    payload = {
        "sections": load(DATA / "station_sections.json"),
        "layouts": {
            "day1": load(DATA / "layouts" / "day1.json"),
            "east_day7": load(DATA / "layouts" / "east_day7.json"),
            "west_day7": load(DATA / "layouts" / "west_day7.json"),
        },
        "objects": load(DATA / "placeable_objects.json"),
        "families": load(DATA / "room_families.json"),
    }
    blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    # Guard against '</script>' sequences breaking the inline script tag.
    blob = blob.replace("</", "<\\/")

    html = TEMPLATE.read_text(encoding="utf-8")
    if TOKEN not in html:
        raise SystemExit(f"token {TOKEN} not found in {TEMPLATE}")
    if html.count(TOKEN) != 1:
        raise SystemExit(f"token {TOKEN} must appear exactly once in {TEMPLATE}")
    OUT.write_text(html.replace(TOKEN, blob), encoding="utf-8")
    return OUT


if __name__ == "__main__":
    out = build()
    print(f"wrote {out} ({out.stat().st_size:,} bytes)")
