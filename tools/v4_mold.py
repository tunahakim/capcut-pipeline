#!/usr/bin/env python3
"""
v4_mold.py <project-dir>
Boc khuon filter: in day du track + segment + material cua
  (A) filter do GUI tao  -> materials.effects        (DUNG)
  (B) filter do CLI tao  -> materials.video_effects  (LOI)
Diff hai material theo tung khoa, ghi khuon ra D:\\Test_tool\\mold_filter.json
"""
import json, pathlib, sys
import os

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))

PROJ = pathlib.Path(sys.argv[1])
OUT  = LAB / "mold_filter.json"
TID  = json.loads((PROJ / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
d    = json.loads((PROJ / "Timelines" / TID / "draft_content.json").read_text(encoding="utf-8"))

mats = {}
for bk, arr in (d.get("materials") or {}).items():
    if isinstance(arr, list):
        for m in arr:
            if isinstance(m, dict) and m.get("id"):
                mats[m["id"]] = (bk, m)

print("=" * 74)
print("TAT CA TRACK - moi truong tru segments")
print("=" * 74)
for t in d.get("tracks", []):
    meta = {k: v for k, v in t.items() if k != "segments"}
    print("\n-- type=%s  %d segment" % (t.get("type"), len(t.get("segments") or [])))
    print(json.dumps(meta, ensure_ascii=False, indent=1))

gui = cli = None
for t in d.get("tracks", []):
    for s in (t.get("segments") or []):
        bk, mo = mats.get(s.get("material_id"), ("?", {}))
        if mo.get("type") == "filter":
            if bk == "effects":
                gui = (t, s, mo)
            elif bk == "video_effects":
                cli = (t, s, mo)

for tag, trio in (("GUI (DUNG)", gui), ("CLI (LOI)", cli)):
    print("\n" + "=" * 74)
    print("SEGMENT FILTER - " + tag)
    print("=" * 74)
    if trio is None:
        print("  KHONG TIM THAY")
        continue
    t, s, m = trio
    print("track.type=%r id=%s flag=%s attribute=%s"
          % (t.get("type"), t.get("id"), t.get("flag"), t.get("attribute")))
    print(json.dumps(s, ensure_ascii=False, indent=1))

print("\n" + "=" * 74)
print("DIFF MATERIAL:  GUI(effects)  vs  CLI(video_effects)")
print("=" * 74)
ga = gui[2] if gui else {}
ca = cli[2] if cli else {}
for k in sorted(set(ga) | set(ca)):
    g = json.dumps(ga.get(k, "<<THIEU>>"), ensure_ascii=False)
    c = json.dumps(ca.get(k, "<<THIEU>>"), ensure_ascii=False)
    print("%s%-32s GUI=%-44s CLI=%s"
          % ("   " if g == c else ">> ", k, g[:44], c[:56]))

if gui:
    t, s, m = gui
    mold = {"track": {k: v for k, v in t.items() if k != "segments"},
            "segment": s, "material": m}
    OUT.write_text(json.dumps(mold, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nDa ghi khuon:", OUT)
else:
    print("\nKHONG co filter GUI -> khong ghi duoc khuon")