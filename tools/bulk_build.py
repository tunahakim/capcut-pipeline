"""bulk_build.py <project-dir> <thư-mục-ảnh> [số-shot=300] [độ-dài-mỗi-shot=12.0]
Dựng N shot bằng cách lặp vòng danh sách ảnh Shot_*.png và gọi capcut add-video từng lệnh một, mục đích đo tải của lớp ghi. Không thêm audio, không hiệu ứng.
Vào: project đã clone và thư mục ảnh. Ra: báo cáo JSON ở <CAPCUT_LAB>/perf/bulk_<N>_<dấu-thời-gian>.json gồm thời gian từng lệnh và kích thước draft_content.json theo mốc 25 shot.
Dừng ngay ở lệnh đầu tiên bị lỗi. Đã chạy ở n=10 và n=300 trên máy render.
[KIEM: du lieu that]
"""

import json, os, pathlib, subprocess, sys, time

PROJ = sys.argv[1]
SRC  = pathlib.Path(sys.argv[2])
N    = int(sys.argv[3]) if len(sys.argv) > 3 else 300
DUR  = float(sys.argv[4]) if len(sys.argv) > 4 else 12.0

LAB  = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\IT\capcut-lab\data"))
PERF = LAB / "perf"
PERF.mkdir(parents=True, exist_ok=True)

imgs = sorted(SRC.glob("Shot_*.png"))
if not imgs:
    sys.exit("Khong thay anh Shot_*.png trong %s" % SRC)
dc = pathlib.Path(PROJ) / "draft_content.json"
if not dc.exists():
    sys.exit("Khong thay %s" % dc)

def n(x):
    return ("%.3f" % x).rstrip("0").rstrip(".")

times, sizes = [], []
t0 = time.time()
print("bulk_build: %d shot x %.1fs = %.1f phut | %d anh nguon"
      % (N, DUR, N * DUR / 60.0, len(imgs)))

for i in range(N):
    img = imgs[i % len(imgs)]
    cmd = 'capcut add-video "%s" "%s" "%ss" "%ss" -q' % (PROJ, img, n(i * DUR), n(DUR))
    a = time.perf_counter()
    p = subprocess.run(cmd, shell=True, capture_output=True)
    b = time.perf_counter()
    if p.returncode != 0:
        print("LOI o shot %d:" % (i + 1))
        print((p.stdout + b"\n" + p.stderr).decode("utf-8", errors="replace")[:400])
        sys.exit(1)
    times.append(b - a)
    if i == 0 or (i + 1) % 25 == 0:
        mb = dc.stat().st_size / 1048576.0
        sizes.append((i + 1, mb))
        w = times[-25:]
        print("  %4d shot | lenh nay %5.2fs | tb 25 gan nhat %5.2fs | json %6.2f MB | da troi %5.1f phut"
              % (i + 1, times[-1], sum(w) / len(w), mb, (time.time() - t0) / 60.0))

tot = time.time() - t0
f10 = sum(times[:10]) / min(10, len(times))
l10 = sum(times[-10:]) / min(10, len(times))
print("\nXONG %d shot trong %.1f phut" % (N, tot / 60.0))
print("lenh dau %.2fs | lenh cuoi %.2fs | trung binh %.2fs"
      % (times[0], times[-1], sum(times) / len(times)))
print("tb 10 dau %.3fs | tb 10 cuoi %.3fs | TI LE %.2fx" % (f10, l10, (l10 / f10) if f10 else 0))
print("draft_content.json: %.2f MB" % (dc.stat().st_size / 1048576.0))

rep = {"n": N, "dur_each": DUR, "total_min": tot / 60.0,
       "t_first": times[0], "t_last": times[-1],
       "t_mean": sum(times) / len(times),
       "t_mean_first10": f10, "t_mean_last10": l10,
       "ratio_last_first": (l10 / f10) if f10 else None,
       "json_mb_final": dc.stat().st_size / 1048576.0,
       "checkpoints": [{"shot": s, "json_mb": m} for s, m in sizes],
       "times": [round(t, 4) for t in times]}
out = PERF / ("bulk_%d_%s.json" % (N, time.strftime("%Y%m%d_%H%M%S")))
out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
print("Da ghi:", out)