#!/usr/bin/env python3
"""bench_kb.py - lớp Python sinh keyframe của project benchmark, chạy SAU tools/bench_build.py.
Không viết lại bộ sinh keyframe: nạp scripts_v1/kb_apply.py rồi thay PLAN bằng tham số Ken Burns đọc từ shots.csv, và nạp GEO từ hai cột kx với ky khi bảng có sẵn hai cột đó, nhờ vậy mọi logic keyframe cùng bit 4096 và việc ghi đủ bốn file đều do kb_apply.py lo theo đường đã kiểm chứng.
SAU SCRIPT NÀY TUYỆT ĐỐI KHÔNG CHẠY THÊM LỆNH GHI NÀO CỦA CLI.
[KIEM: chua]
"""
import contextlib, csv, importlib.util, io, os, pathlib, sys, time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

proj = sys.argv[1]
csvf = pathlib.Path(sys.argv[2])
here = pathlib.Path(__file__).resolve().parents[1]
kbp = here / "scripts_v1" / "kb_apply.py"
if not kbp.exists():
    sys.exit("Khong thay %s" % kbp)

spec = importlib.util.spec_from_file_location("kb_apply", kbp)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

rows = list(csv.DictReader(csvf.open(encoding="utf-8")))
m.PLAN = {int(r["idx"]): (float(r["kb_s0"]), float(r["kb_s1"]),
                          float(r["kb_x0"]), float(r["kb_x1"]),
                          float(r["kb_y0"]), float(r["kb_y1"]),
                          "bench%03d" % int(r["idx"])) for r in rows}
print("Nap PLAN tu shots.csv: %d shot" % len(m.PLAN))
if rows and "kx" in rows[0] and "ky" in rows[0]:
    m.GEO = {int(r["idx"]): (float(r["kx"]), float(r["ky"])) for r in rows}
    print("Nap hinh hoc rieng tung shot: %d shot" % len(m.GEO))
else:
    print("CANH BAO: shots.csv khong co cot kx, ky -- dung hang so mac dinh")

sys.argv = ["kb_apply.py", proj]
buf = io.StringIO()
code = 0
t0 = time.time()
try:
    with contextlib.redirect_stdout(buf):
        m.main()
except SystemExit as e:
    code = e.code if isinstance(e.code, int) else 1
    print("EXIT MSG:", e.code)
except Exception as e:
    code = 99
    buf.write("\nNGOAI LE: %r\n" % (e,))
dt = time.time() - t0
log = buf.getvalue()

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\IT\capcut-lab\data"))
PERF = LAB / "perf"
PERF.mkdir(parents=True, exist_ok=True)
lf = PERF / ("bench_kb_%s.log" % time.strftime("%Y%m%d_%H%M%S"))
lf.write_text(log, encoding="utf-8")

keys = ("KY =", "track video", "main_timeline_id", "CANH BAO", "DUNG LAI",
        "vuot le", "check_flag bat bit", "ghi:", "Chi thay", "NGOAI LE", "XONG")
print("\n=== dong quan trong ===")
for ln in log.splitlines():
    if any(k in ln for k in keys):
        print(ln)

apply_lines = [l for l in log.splitlines() if l.strip().startswith("shot ")]
read_lines = [l for l in log.splitlines() if l.strip().split(" ")[0].isdigit()]
kf3 = sum(1 for l in read_lines if l.rstrip().endswith("kf=3"))
print("\n=== tong ket ===")
print("dong AP DUNG        : %d" % len(apply_lines))
print("dong DOC LAI        : %d" % len(read_lines))
print("segment co du kf=3  : %d" % kf3)
print("thoi gian           : %.1f giay" % dt)
print("log day du          : %s" % lf)
print("ma thoat kb_apply   : %s" % code)
if code:
    print("\n--- 20 dong cuoi cua log ---")
    print("\n".join(log.splitlines()[-20:]))
sys.exit(code)