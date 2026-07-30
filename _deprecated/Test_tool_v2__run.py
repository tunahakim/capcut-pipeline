#!/usr/bin/env python3
# D:\Test_tool\Test_tool_v2\run.py  (v2)
# Doc tham so tu args.txt (moi dong 1 tham so, UTF-8 khong BOM).
# Dong 1 = duong dan script .py, cac dong sau = argv.
import sys, pathlib, runpy

HERE = pathlib.Path(__file__).resolve().parent
f = HERE / "args.txt"
if not f.exists():
    sys.exit(f"Thieu {f}")

lines = [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
if not lines:
    sys.exit("args.txt rong")

script, args = lines[0], lines[1:]
print("SCRIPT:", script)
for i, a in enumerate(args, 1):
    print(f"  arg{i}: [{a}]")
if not pathlib.Path(script).exists():
    sys.exit(f"Khong thay script: {script}")

sys.argv = [script] + args
runpy.run_path(script, run_name="__main__")
