#!/usr/bin/env python3
"""
prod_shots.py - sinh shots.csv cho project san xuat that, timing khoa theo file audio.
Thay the tools/bench_shots.py. Khac biet chinh:
  - tong thoi luong lay tu ffprobe file audio, khong phai so tron tu bia
  - moc luu bang SO NGUYEN mili giay, luoi 100 ms, khong dung so thuc
  - kiem bien SAU khi lam tron, khong phai truoc
  - hinh hoc tinh theo TUNG anh (KX, KY), chap nhan moi kich thuoc va moi ti le
  - ghi luon hai cot kx, ky vao shots.csv de lop keyframe dung dung con so do
  - cot blur sinh theo luat hinh hoc, khong rai ngau nhien
"""
import argparse, csv, math, random, re, subprocess, sys
from pathlib import Path

CW, CH = 1920.0, 1080.0
GRID_MS = 100
S_LO, S_HI = 0.72, 0.92
TRANS = ["dissolve", "black-fade", "blur", "gradient-wipe", "dissolve-ii",
         "page-turning", "glitch", "whirlpool", "split", "flip-ii", "shutter"]
PATTERNS = [("in", 0, 0), ("flat", 1, 0), ("in", 1, 1), ("out", -1, 1),
            ("in", -1, -1), ("flat", 0, 1), ("in", 1, -1), ("out", 0, 0)]
COLS = ["idx", "image", "start_s", "dur_s", "transition", "blur", "intro", "outro",
        "kb_s0", "kb_s1", "kb_x0", "kb_x1", "kb_y0", "kb_y1", "kx", "ky"]


def probe_container(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def probe_decoded(p):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        return None
    h, mn, s = m[-1]
    return int(h) * 3600 + int(mn) * 60 + float(s)


def total_ms_from_audio(path, tail_ms):
    c = probe_container(path)
    d = probe_decoded(path)
    if c is None and d is None:
        sys.exit("ffprobe khong doc duoc audio: %s" % path)
    base = max(c or 0.0, d or 0.0)
    base_ms = int(math.ceil(base * 1000.0))
    total = int(math.ceil((base_ms + tail_ms) / float(GRID_MS))) * GRID_MS
    print("audio           : %s" % path)
    print("  container     : %s" % ("%.6f s" % c if c else "n/a"))
    print("  decoded       : %s" % ("%.6f s" % d if d else "n/a"))
    print("  audio_ms      : %d  (lay gia tri lon hon, ceil len mili giay)" % base_ms)
    print("  duoi co y     : %d ms" % tail_ms)
    print("  tong tren luoi: %d ms = %.1f s" % (total, total / 1000.0))
    print("  thua sau audio: %d ms" % (total - base_ms))
    return total, base_ms


def durations(rng, n, total_ds, dmin, dmax):
    if n * dmin > total_ds or n * dmax < total_ds:
        sys.exit("Khong the chia %d shot trong [%d,%d] ds cho tong %d ds"
                 % (n, dmin, dmax, total_ds))
    w = [rng.uniform(0.6, 1.4) for _ in range(n)]
    sw = sum(w)
    d = [min(dmax, max(dmin, int(round(total_ds * x / sw)))) for x in w]
    guard = 0
    while sum(d) != total_ds:
        guard += 1
        if guard > 400000:
            sys.exit("Khong hoi tu khi can bang do dai")
        diff = total_ds - sum(d)
        i = rng.randrange(n)
        if diff > 0 and d[i] < dmax:
            d[i] += 1
        elif diff < 0 and d[i] > dmin:
            d[i] -= 1
    return d


def kb_for(rng, i, kx_img, ky_img):
    kind, px, py = PATTERNS[i % len(PATTERNS)]
    amp = rng.uniform(0.06, 0.14)
    if kind == "in":
        s0 = rng.uniform(S_LO, S_HI - amp)
        s1 = s0 + amp
    elif kind == "out":
        s1 = rng.uniform(S_LO, S_HI - amp)
        s0 = s1 + amp
    else:
        s0 = s1 = rng.uniform(S_LO, S_HI)
    f = rng.uniform(0.45, 0.85)
    s0 = round(s0, 6)
    s1 = round(s1, 6)
    ax = min(1.0 - kx_img * s0, 1.0 - kx_img * s1) * f
    ay = min(1.0 - ky_img * s0, 1.0 - ky_img * s1) * f
    v = [round(-px * ax, 6), round(px * ax, 6), round(-py * ay, 6), round(py * ay, 6)]
    x0, x1, y0, y1 = v
    for s, x, y in ((s0, x0, y0), (s1, x1, y1)):
        if abs(x) > 1.0 - kx_img * s + 1e-9 or abs(y) > 1.0 - ky_img * s + 1e-9:
            sys.exit("shot %d vuot le SAU khi lam tron: s=%.6f x=%.6f y=%.6f kx=%.6f ky=%.6f"
                     % (i + 1, s, x, y, kx_img, ky_img))
    return s0, s1, x0, x1, y0, y1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images-csv", required=True)
    ap.add_argument("--assets-root", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--tail-ms", type=int, default=2000)
    ap.add_argument("--min-edge", type=int, default=800)
    ap.add_argument("--dmin-ms", type=int, default=0)
    ap.add_argument("--dmax-ms", type=int, default=0)
    ap.add_argument("--seed", type=int, default=731)
    a = ap.parse_args()

    rng = random.Random(a.seed)
    root = Path(a.assets_root)
    total_ms, audio_ms = total_ms_from_audio(Path(a.audio), a.tail_ms)
    if total_ms % GRID_MS:
        sys.exit("Tong khong nam tren luoi 100 ms")

    pool = []
    skipped = 0
    with open(a.images_csv, "r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            w, h = int(r["w"]), int(r["h"])
            if max(w, h) < a.min_edge:
                skipped += 1
                continue
            p = Path(r["path"])
            try:
                rel = p.relative_to(root).as_posix()
            except ValueError:
                rel = p.name
            pool.append({"rel": rel, "w": w, "h": h,
                         "kx": float(r["kx"]), "ky": float(r["ky"])})
    if not pool:
        sys.exit("Pool anh rong")
    rng.shuffle(pool)
    print("")
    print("anh             : %d dung duoc, %d bi loai vi canh dai < %d px"
          % (len(pool), skipped, a.min_edge))

    avg = total_ms / float(a.n)
    dmin = a.dmin_ms or int(max(3000, 0.5 * avg) // GRID_MS * GRID_MS)
    dmax = a.dmax_ms or int(min(1.8 * avg, 30000) // GRID_MS * GRID_MS)
    d_ds = durations(rng, a.n, total_ms // GRID_MS, dmin // GRID_MS, dmax // GRID_MS)

    rows = []
    t_ms = 0
    for i in range(a.n):
        img = pool[i % len(pool)]
        s0, s1, x0, x1, y0, y1 = kb_for(rng, i, img["kx"], img["ky"])
        smin = min(s0, s1)
        need_blur = (img["kx"] * smin < 1.0 - 1e-9) or (img["ky"] * smin < 1.0 - 1e-9)
        dur_ms = d_ds[i] * GRID_MS
        rows.append({
            "idx": i + 1, "image": img["rel"],
            "start_s": "%.3f" % (t_ms / 1000.0), "dur_s": "%.3f" % (dur_ms / 1000.0),
            "transition": rng.choice(TRANS) if i < a.n - 1 else "",
            "blur": 3 if need_blur else 0,
            "intro": "fade-in" if i == 0 else "",
            "outro": "fade-out" if i == a.n - 1 else "",
            "kb_s0": "%.6f" % s0, "kb_s1": "%.6f" % s1,
            "kb_x0": "%.6f" % x0, "kb_x1": "%.6f" % x1,
            "kb_y0": "%.6f" % y0, "kb_y1": "%.6f" % y1,
            "kx": "%.6f" % img["kx"], "ky": "%.6f" % img["ky"]})
        t_ms += dur_ms

    if t_ms != total_ms:
        sys.exit("Tong do dai %d ms khac muc tieu %d ms" % (t_ms, total_ms))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        wtr = csv.DictWriter(f, fieldnames=COLS)
        wtr.writeheader()
        wtr.writerows(rows)

    durs = [d * GRID_MS for d in d_ds]
    reused = a.n - len(set(r["image"] for r in rows))
    print("")
    print("shot            : %d" % a.n)
    print("do dai min/max  : %.1f s / %.1f s (bien %.1f .. %.1f)"
          % (min(durs) / 1000.0, max(durs) / 1000.0, dmin / 1000.0, dmax / 1000.0))
    print("tong            : %d ms, khop muc tieu: OK" % t_ms)
    print("moc cuoi        : %.3f s, audio het o %.3f s, thua %.3f s"
          % (t_ms / 1000.0, audio_ms / 1000.0, (t_ms - audio_ms) / 1000.0))
    kxs = [float(r["kx"]) for r in rows]
    kys = [float(r["ky"]) for r in rows]
    print("kx trong bang   : %.4f .. %.4f" % (min(kxs), max(kxs)))
    print("ky trong bang   : %.4f .. %.4f" % (min(kys), max(kys)))
    print("blur bat        : %d / %d shot" % (sum(1 for r in rows if r["blur"]), a.n))
    print("transition      : %d" % sum(1 for r in rows if r["transition"]))
    print("anh dung lai    : %d lan" % reused)
    print("")
    print("shots.csv       : %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())