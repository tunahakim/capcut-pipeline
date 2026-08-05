#!/usr/bin/env python3
"""
bench_shots.py - sinh shots.csv cho project benchmark va nhan ban anh nguon.

Muc dich: dac ta mot project ~60 phut du hieu ung de do suc may render.
Day la ban sinh shots.csv dau tien cua du an; luoc do cot o day la HOP DONG
dau vao tam thoi cho pipeline/ va la dich cho tools/shots_dump.py doc nguoc.

QUY TAC THOI GIAN - doc ky truoc khi sua:
  30 fps -> 1 frame = 33333.333... us, KHONG tron mili giay.
  capcut-cli nhan tham so giay voi 3 chu so thap phan.
  => Moc an toan = BOI SO CUA 0.1 GIAY = 3 frame = 100000 us chan.
  Moi moc sinh ra o day deu la boi so cua 0.1 giay. Don vi noi bo la "phan muoi giay".

Cach dung:
  python tools/bench_shots.py --src <thu-muc-anh> --assets <thu-muc-copy> --out <shots.csv>
[KIEM: mot lan]
"""
import argparse, csv, pathlib, random, shutil, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CW, CH = 1920.0, 1080.0
IMG_W, IMG_H = 1376.0, 768.0
KY = (CW * IMG_H / IMG_W) / CH

# 11 transition da xac minh tan dau ra MP4, tat ca is_overlap=false. KHONG co cube.
TRANS = ["dissolve", "black-fade", "blur", "gradient-wipe", "dissolve-ii",
         "page-turning", "glitch", "whirlpool", "split", "flip-ii", "shutter"]
# Chi hai slug animation da chay that trong parity_build.py. Mo rong sau khi liet ke enum.
INTRO = ["fade-in"]
OUTRO = ["fade-out"]

S_MIN, S_MAX = 0.72, 0.92
D_MIN_T, D_MAX_T = 60, 200          # phan muoi giay: 6.0s .. 20.0s


def lim_x(s):
    return 1.0 - s


def lim_y(s):
    return 1.0 - KY * s


def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--assets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--minutes", type=float, default=60.0)
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=20260731)
    ap.add_argument("--no-copy", action="store_true")
    a = ap.parse_args()

    src = pathlib.Path(a.src)
    assets = pathlib.Path(a.assets)
    out = pathlib.Path(a.out)
    imgs = sorted(src.glob("Shot_*.png"))
    if not imgs:
        sys.exit("Khong thay anh Shot_*.png trong %s" % src)

    total_t = int(round(a.minutes * 60 * 10))
    if not (D_MIN_T * a.n <= total_t <= D_MAX_T * a.n):
        sys.exit("Khong the chia %d phan muoi giay cho %d shot trong [%d,%d]"
                 % (total_t, a.n, D_MIN_T, D_MAX_T))

    rnd = random.Random(a.seed)
    d = [rnd.randint(D_MIN_T, D_MAX_T) for _ in range(a.n)]
    diff = total_t - sum(d)
    guard = 0
    while diff != 0:
        i = rnd.randrange(a.n)
        step = 1 if diff > 0 else -1
        if D_MIN_T <= d[i] + step <= D_MAX_T:
            d[i] += step
            diff -= step
        guard += 1
        if guard > 20000000:
            sys.exit("Khong hoi tu khi can bang tong thoi luong")

    rows, bad = [], []
    start_t = 0
    for i in range(a.n):
        idx = i + 1
        s0 = rnd.uniform(S_MIN, S_MAX)
        s1 = clamp(s0 + rnd.uniform(0.04, 0.16) * rnd.choice([1, -1]), S_MIN, S_MAX)
        if idx == 1:
            # PROBE BIEN co y: dat dung gioi han ly thuyet o ca hai dau.
            x0, y0 = lim_x(s0), -lim_y(s0)
            x1, y1 = -lim_x(s1), lim_y(s1)
        else:
            x0 = rnd.uniform(-1, 1) * 0.90 * lim_x(s0)
            y0 = rnd.uniform(-1, 1) * 0.90 * lim_y(s0)
            x1 = rnd.uniform(-1, 1) * 0.90 * lim_x(s1)
            y1 = rnd.uniform(-1, 1) * 0.90 * lim_y(s1)

        for tag, s, x, y in (("dau", s0, x0, y0), ("cuoi", s1, x1, y1)):
            if abs(x) > lim_x(s) + 1e-9 or abs(y) > lim_y(s) + 1e-9:
                bad.append("shot %d %s vuot le" % (idx, tag))

        rows.append({
            "idx": idx,
            "image": "bench_%04d.png" % idx,
            "start_s": "%.1f" % (start_t / 10.0),
            "dur_s": "%.1f" % (d[i] / 10.0),
            "transition": rnd.choice(TRANS) if idx < a.n else "",
            "blur": rnd.randint(1, 4) if rnd.random() < 0.50 else 0,
            "intro": rnd.choice(INTRO) if rnd.random() < 0.30 else "",
            "outro": rnd.choice(OUTRO) if rnd.random() < 0.30 else "",
            "kb_s0": "%.6f" % s0, "kb_s1": "%.6f" % s1,
            "kb_x0": "%.6f" % x0, "kb_x1": "%.6f" % x1,
            "kb_y0": "%.6f" % y0, "kb_y1": "%.6f" % y1,
        })
        start_t += d[i]

    if bad:
        for b in bad[:20]:
            print("  " + b)
        sys.exit("DUNG LAI: %d vi pham le, khong ghi gi ca" % len(bad))
    if start_t != total_t:
        sys.exit("Tong lech: %d vs %d phan muoi giay" % (start_t, total_t))

    out.parent.mkdir(parents=True, exist_ok=True)
    cols = ["idx", "image", "start_s", "dur_s", "transition", "blur", "intro", "outro",
            "kb_s0", "kb_s1", "kb_x0", "kb_x1", "kb_y0", "kb_y1"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    nbytes = 0
    if not a.no_copy:
        assets.mkdir(parents=True, exist_ok=True)
        for i in range(a.n):
            dst = assets / ("bench_%04d.png" % (i + 1))
            if not dst.exists():
                shutil.copy2(imgs[i % len(imgs)], dst)
            nbytes += dst.stat().st_size

    print("KY = %.6f" % KY)
    print("shot            : %d" % a.n)
    print("tong thoi luong : %.1f giay = %.2f phut  (khop dung: %s)"
          % (total_t / 10.0, total_t / 600.0, start_t == total_t))
    print("do dai shot     : min %.1fs  max %.1fs  tb %.2fs"
          % (min(d) / 10.0, max(d) / 10.0, sum(d) / 10.0 / a.n))
    print("moi moc la boi so cua 0.1 giay = 3 frame @30fps: DUNG theo cau truc so nguyen")
    print("transition      : %d shot co" % sum(1 for r in rows if r["transition"]))
    print("canvas blur     : %d shot co" % sum(1 for r in rows if r["blur"]))
    print("intro / outro   : %d / %d shot"
          % (sum(1 for r in rows if r["intro"]), sum(1 for r in rows if r["outro"])))
    print("anh nhan ban    : %d file, %.1f MB" % (0 if a.no_copy else a.n, nbytes / 1048576.0))
    print("shots.csv       : %s" % out)


if __name__ == "__main__":
    main()