#!/usr/bin/env python3
"""find_ph.py <project-dir> - dinh vi moi chuoi ##_material_placeholder trong cay JSON. [KIEM: chua]"""
import json, pathlib, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROJ = pathlib.Path(sys.argv[1])
TID = json.loads((PROJ / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
NEEDLE = "##_material_placeholder"


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, path + "[%d]" % i)
    elif isinstance(node, str) and NEEDLE in node:
        yield path, node


for f in (PROJ / "draft_content.json", PROJ / "template-2.tmp",
          PROJ / "Timelines" / TID / "draft_content.json",
          PROJ / "Timelines" / TID / "template-2.tmp"):
    if not f.exists():
        continue
    raw = f.read_text(encoding="utf-8")
    print("\n=== %s  (%d lan trong text) ===" % (f.name, raw.count(NEEDLE)))
    for p, v in walk(json.loads(raw)):
        print("   %-70s = %s" % (p, v[:70]))