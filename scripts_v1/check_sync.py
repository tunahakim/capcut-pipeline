#!/usr/bin/env python3
"""check_sync.py <project-dir> <ten-snapshot> - kiem tra 4 file dong bo + chup timing. [KIEM: du lieu that]"""
import json, pathlib, sys
import os

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))

if len(sys.argv) < 3:
    sys.exit("Dung: python check_sync.py <project-dir> <ten-snapshot>")

PROJ = pathlib.Path(sys.argv[1]); TAG = sys.argv[2]
OUT = LAB / "snapshots"; OUT.mkdir(parents=True, exist_ok=True)
TID = json.loads((PROJ / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]

files = [PROJ / "draft_content.json", PROJ / "template-2.tmp",
         PROJ / "Timelines" / TID / "draft_content.json",
         PROJ / "Timelines" / TID / "template-2.tmp"]

print("=== DONG BO 4 FILE ===")
sigs = []
for f in files:
    if not f.exists():
        print(" %-27s KHONG TON TAI" % f.name); continue
    d = json.loads(f.read_text(encoding="utf-8"))
    cv = {c["id"] for c in d["materials"].get("canvases", []) if c.get("type") == "canvas_blur"}
    vids = {m["id"]: m for m in d["materials"].get("videos", [])}
    sc, fl, kf = [], [], []
    for s in next(t for t in d["tracks"] if t.get("type") == "video")["segments"]:
        sc.append(round((s.get("clip") or {}).get("scale", {}).get("x", 0), 3))
        m = vids.get(s.get("material_id"), {})
        star = "*" if any(r in cv for r in s.get("extra_material_refs", [])) else ""
        fl.append(str(m.get("check_flag", "?")) + star)
        kf.append(len(s.get("common_keyframes") or []))
    sigs.append((tuple(sc), tuple(fl), tuple(kf)))
    loc = "GOC " if f.parent == PROJ else "LONG"
    print(" %s %-22s scale=%s" % (loc, f.name, sc))
    print(" %27s flag=%s  kf=%s" % ("", fl, kf))
print(">>> 4 FILE GIONG NHAU:", "CO" if len(set(sigs)) == 1 else "*** KHONG ***")

d = json.loads(files[2].read_text(encoding="utf-8"))
mats = {}
for b, arr in (d.get("materials") or {}).items():
    if isinstance(arr, list):
        for m in arr:
            if isinstance(m, dict) and m.get("id"): mats[m["id"]] = b

print("\n=== TIMING (%s) ===  duration = %.4fs" % (TAG, int(d.get("duration", 0)) / 1e6))
rows = []
for i, s in enumerate(next(t for t in d["tracks"] if t.get("type") == "video")["segments"], 1):
    tt = s["target_timerange"]
    tags = sorted({mats.get(r, "") for r in s.get("extra_material_refs", [])}
                  & {"transitions", "material_animations"})
    rows.append({"n": i, "id": str(s["id"])[:8],
                 "start": int(tt["start"]), "dur": int(tt["duration"])})
    print("  %d %s start=%10.4f dur=%9.4f  %s"
          % (i, str(s["id"])[:8], int(tt["start"]) / 1e6, int(tt["duration"]) / 1e6,
             " ".join(t[:5] for t in tags)))

print("\n=== TRACK KHONG PHAI VIDEO/AUDIO ===")
for t in d["tracks"]:
    if t.get("type") in ("video", "audio"): continue
    for s in (t.get("segments") or []):
        bk = mats.get(s.get("material_id"), "MISSING")
        tt = s.get("target_timerange") or {}
        print("  %-7s bucket=%-14s %8.3f +%8.3f"
              % (t.get("type"), bk, int(tt.get("start", 0)) / 1e6, int(tt.get("duration", 0)) / 1e6))

(OUT / (TAG + ".json")).write_text(
    json.dumps({"duration": d.get("duration"), "rows": rows}, indent=1), encoding="utf-8")
print("\nDa luu snapshot:", OUT / (TAG + ".json"))