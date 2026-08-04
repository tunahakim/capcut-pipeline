#!/usr/bin/env python3
"""strip_filters.py <project-dir> - go sach lop filter, giu nguyen moi thu khac. [KIEM: chua]"""
import json, pathlib, shutil, sys

PROJ = pathlib.Path(sys.argv[1])
TID = json.loads((PROJ / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
tg = [PROJ / "draft_content.json", PROJ / "template-2.tmp",
      PROJ / "Timelines" / TID / "draft_content.json",
      PROJ / "Timelines" / TID / "template-2.tmp"]
tg = [t for t in tg if t.exists()]
if len(tg) != 4:
    sys.exit("Chi thay %d/4 file dich" % len(tg))

d = json.loads(tg[0].read_text(encoding="utf-8"))
mats = d.setdefault("materials", {})

bad = set()
for bk in ("effects", "video_effects"):
    for m in (mats.get(bk) or []):
        if m.get("type") == "filter":
            bad.add(m["id"])
            print("  xoa material %s bucket=%-14s name=%r" % (m["id"][:8], bk, m.get("name")))
    mats[bk] = [m for m in (mats.get(bk) or []) if m["id"] not in bad]
if not bad:
    print("  khong co filter nao")

keep = []
for t in d.get("tracks", []):
    n0 = len(t.get("segments") or [])
    t["segments"] = [s for s in (t.get("segments") or []) if s.get("material_id") not in bad]
    if len(t["segments"]) != n0:
        print("  xoa %d segment khoi track type=%s" % (n0 - len(t["segments"]), t.get("type")))
    if not t["segments"] and t.get("type") in ("effect", "filter"):
        print("  xoa track rong type=%s" % t.get("type"))
        continue
    keep.append(t)
d["tracks"] = keep

payload = json.dumps(d, ensure_ascii=False)
json.loads(payload)
for t in tg:
    shutil.copy2(t, str(t) + ".prestrip")
    t.write_text(payload, encoding="utf-8")
    print("  ghi:", t.relative_to(PROJ))

d2 = json.loads((PROJ / "Timelines" / TID / "draft_content.json").read_text(encoding="utf-8"))
print()
for t in d2["tracks"]:
    print("  track type=%-7s %d segment" % (t.get("type"), len(t.get("segments") or [])))
print("XONG.")