#!/usr/bin/env python3
"""
dump_src.py - gom ma nguon 8 muc con thieu trong tai lieu thanh mot file.
Ghi ra <LAB>\perf\missing_src.txt de chep vao Phan X.
"""
import os, pathlib

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
OUT = LAB / "perf"
OUT.mkdir(parents=True, exist_ok=True)

ITEMS = [
    ("X.23", "grab_frames.py"),
    ("X.24", "tr_profile3.py"),
    ("X.25", "strip_filters.py"),
    ("X.28", "pack_vendor.ps1"),
    ("X.29", "parity_build.py"),
    ("X.30", "_vendor/setup_1_runtimes.ps1"),
    ("X.30", "_vendor/setup_2_capcut.ps1"),
    ("X.31", "_vendor/README_PARITY.txt"),
]

buf = []
tong = 0
print("%-6s %-34s %8s %6s" % ("muc", "file", "bytes", "dong"))
for muc, rel in ITEMS:
    p = LAB / rel
    if not p.exists():
        print("%-6s %-34s %s" % (muc, rel, "*** KHONG CO TREN DIA ***"))
        buf.append("\n\n########## %s  %s  -- KHONG CO TREN DIA ##########\n" % (muc, rel))
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    nl = t.count("\n") + 1
    tong += len(t)
    print("%-6s %-34s %8d %6d" % (muc, rel, p.stat().st_size, nl))
    buf.append("\n\n########## %s  %s  (%d dong) ##########\n" % (muc, rel, nl))
    buf.append(t)

(OUT / "missing_src.txt").write_text("".join(buf), encoding="utf-8")
print("\nTong ky tu: %d  (~%.0f KB)" % (tong, tong / 1024))
print("Da ghi: %s" % (OUT / "missing_src.txt"))
print("\nMo file do, chep noi dung gui lai. Neu qua dai thi gui lam 2-3 lan,")
print("uu tien theo thu tu: parity_build.py, strip_filters.py, tr_profile3.py,")
print("grab_frames.py, roi den cac file .ps1 va .txt.")