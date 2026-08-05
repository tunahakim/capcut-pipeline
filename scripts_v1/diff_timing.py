#!/usr/bin/env python3
"""diff_timing.py <snap-truoc> <snap-sau> [KIEM: du lieu that]"""
import json, pathlib, sys
import os

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))

SNAP = LAB / "snapshots"
b = json.loads((SNAP / (sys.argv[1] + ".json")).read_text(encoding="utf-8"))
a = json.loads((SNAP / (sys.argv[2] + ".json")).read_text(encoding="utf-8"))

print("=== TIMING: %s -> %s ===" % (sys.argv[1], sys.argv[2]))
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
print(">>> KET LUAN:", "DAT - khong dich timeline" if worst <= 33.4
      else "*** THAT BAI - PHAI DIEU TRA ***")