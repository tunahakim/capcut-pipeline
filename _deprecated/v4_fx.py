import json, pathlib, sys
import os

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))

PROJ = pathlib.Path(sys.argv[1])
SNAP = LAB / "snapshots"
TID = json.loads((PROJ / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
d = json.loads((PROJ / "Timelines" / TID / "draft_content.json").read_text(encoding="utf-8"))

try:
    b = json.loads((SNAP / "v3_v4_before.json").read_text(encoding="utf-8"))
    a = json.loads((SNAP / "v3_v4_after.json").read_text(encoding="utf-8"))
    print("=== TIMING TRUOC/SAU KHI CAPCUT LUU ===")
    worst = 0.0
    for rb, ra in zip(b["rows"], a["rows"]):
        ds = (ra["start"] - rb["start"]) / 1000.0
        worst = max(worst, abs(ds))
        print("  %d %s start %10.4f -> %10.4f (d%+7.1fms) dur d%+7.1fms"
              % (rb["n"], rb["id"], rb["start"]/1e6, ra["start"]/1e6, ds,
                 (ra["dur"]-rb["dur"])/1000.0))
    print(">>> lech lon nhat %.1f ms -> %s\n" % (worst, "DAT" if worst <= 33.4 else "*** THAT BAI ***"))
except Exception as e:
    print("(bo qua so sanh timing:", e, ")\n")

print("=== CAC BUCKET MATERIAL ===")
for k, v in sorted((d.get("materials") or {}).items()):
    if isinstance(v, list) and v:
        print("   %-24s %d" % (k, len(v)))

for bucket in ("video_effects", "effects", "filters"):
    arr = (d.get("materials") or {}).get(bucket) or []
    if not arr: continue
    print("\n" + "=" * 74)
    print("MATERIALS.%s  (%d)" % (bucket.upper(), len(arr)))
    print("=" * 74)
    for m in arr:
        print(json.dumps(m, ensure_ascii=False, indent=1))
        p = m.get("path", "")
        print("  >> path_ton_tai =", pathlib.Path(p).exists() if p else "PATH RONG")

print("\n" + "=" * 74)
print("TRACK EFFECT / FILTER")
print("=" * 74)
mats = {}
for bk, arr in (d.get("materials") or {}).items():
    if isinstance(arr, list):
        for m in arr:
            if isinstance(m, dict) and m.get("id"): mats[m["id"]] = (bk, m)
for t in d.get("tracks", []):
    if t.get("type") not in ("effect", "filter"): continue
    print("\n-- track type=%s name=%s  %d segment" % (t.get("type"), t.get("name"), len(t.get("segments", []))))
    for s in t.get("segments", []):
        tt = s.get("target_timerange") or {}
        print("   seg %s  start=%.3f dur=%.3f" % (str(s.get("id"))[:8],
              int(tt.get("start", 0))/1e6, int(tt.get("duration", 0))/1e6))
        bk, mo = mats.get(s.get("material_id"), ("MISSING", {}))
        print("     material bucket=%s name=%r" % (bk, mo.get("name")))
        for k in ("value", "intensity", "adjust_params", "apply_target_type", "formula_id"):
            if k in s: print("     seg.%s = %s" % (k, json.dumps(s[k], ensure_ascii=False)[:200]))