import json, pathlib
import os

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))

PROJ = pathlib.Path(r"C:\Users\anhlt\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\testV3")
SNAP = LAB / "snapshots"

b = json.loads((SNAP / "v3_before.json").read_text(encoding="utf-8"))
a = json.loads((SNAP / "v3_after.json").read_text(encoding="utf-8"))

print("=== TIMING: TRUOC vs SAU KHI CAPCUT LUU ===")
print("duration: %.4fs -> %.4fs" % (int(b["duration"]) / 1e6, int(a["duration"]) / 1e6))
worst = 0.0
for rb, ra in zip(b["rows"], a["rows"]):
    ds = (ra["start"] - rb["start"]) / 1000.0
    dd = (ra["dur"] - rb["dur"]) / 1000.0
    worst = max(worst, abs(ds))
    flag = "  <<< LECH QUA 1 FRAME" if abs(ds) > 33.4 else ""
    print("  %d %s start %10.4f -> %10.4f (d%+8.1fms)  dur d%+8.1fms%s"
          % (rb["n"], rb["id"], rb["start"] / 1e6, ra["start"] / 1e6, ds, dd, flag))
print(">>> Lech start lon nhat: %.1f ms  (1 frame = 33.3 ms)" % worst)
print(">>> KET LUAN:", "DAT - khong dich timeline" if worst <= 33.4 else "*** THAT BAI ***")

TID = json.loads((PROJ / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
d = json.loads((PROJ / "Timelines" / TID / "draft_content.json").read_text(encoding="utf-8"))

print("\n=== TRANSITION: CAPCUT DA RESOLVE CHUA ===")
for t in d["materials"].get("transitions", []):
    p = t.get("path", "")
    ok = pathlib.Path(p).exists() if p else False
    print("  %-16s dur=%d overlap=%s  path_ton_tai=%s"
          % (t.get("name"), t.get("duration"), t.get("is_overlap"), ok))
    if not ok:
        print("      path =", p or "(RONG)")

print("\n=== ANIMATION ===")
for m in d["materials"].get("material_animations", []):
    for an in m.get("animations", []):
        p = an.get("path", "")
        print("  %-4s %-10s start=%9d dur=%7d  path_ton_tai=%s"
              % (an.get("type"), an.get("name"), an.get("start"), an.get("duration"),
                 pathlib.Path(p).exists() if p else False))

print("\n=== SCALE/KEYFRAME CON NGUYEN KHONG ===")
vids = {m["id"]: m for m in d["materials"].get("videos", [])}
for i, s in enumerate(next(t for t in d["tracks"] if t.get("type") == "video")["segments"], 1):
    c = s.get("clip") or {}
    kf = [k.get("property_type") for k in (s.get("common_keyframes") or [])]
    print("  %d scale=%-6.3f flag=%-6s kf=%d %s"
          % (i, c.get("scale", {}).get("x", 0),
             vids.get(s.get("material_id"), {}).get("check_flag"), len(kf),
             "OK" if len(kf) == 3 else "*** THIEU ***"))