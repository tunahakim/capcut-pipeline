#!/usr/bin/env python3
"""
bench_fixkb.py <shots.csv>
Kep bon cot kb_x/kb_y ve trong gioi han le, TINH TREN GIA TRI DA LAM TRON.
Ly do ton tai: sinh so trong bo nho thi hop le, nhung "%.6f" co the lam tron
LEN va day gia tri vuot mep. Chi cot kb_* bi sua; cac cot khac giu nguyen.
[KIEM: chua]
"""
import csv, math, pathlib, shutil, sys

CW, CH, IMG_W, IMG_H = 1920.0, 1080.0, 1376.0, 768.0
KY = (CW * IMG_H / IMG_W) / CH
f = pathlib.Path(sys.argv[1])
rows = list(csv.DictReader(f.open(encoding="utf-8")))
cols = list(rows[0].keys())


def q6(v):
    return float("%.6f" % v)


def clamp(v, lim):
    return math.copysign(math.floor(lim * 1e6) / 1e6, v) if abs(v) > lim else v


changed = []
for r in rows:
    s0, s1 = q6(float(r["kb_s0"])), q6(float(r["kb_s1"]))
    old = (r["kb_x0"], r["kb_y0"], r["kb_x1"], r["kb_y1"])
    x0 = clamp(q6(float(r["kb_x0"])), 1.0 - s0)
    y0 = clamp(q6(float(r["kb_y0"])), 1.0 - KY * s0)
    x1 = clamp(q6(float(r["kb_x1"])), 1.0 - s1)
    y1 = clamp(q6(float(r["kb_y1"])), 1.0 - KY * s1)
    new = ("%.6f" % x0, "%.6f" % y0, "%.6f" % x1, "%.6f" % y1)
    r["kb_s0"], r["kb_s1"] = "%.6f" % s0, "%.6f" % s1
    r["kb_x0"], r["kb_y0"], r["kb_x1"], r["kb_y1"] = new
    if new != old:
        changed.append((r["idx"], old, new))

bad = []
for r in rows:
    for s, x, y, tag in ((float(r["kb_s0"]), float(r["kb_x0"]), float(r["kb_y0"]), "dau"),
                         (float(r["kb_s1"]), float(r["kb_x1"]), float(r["kb_y1"]), "cuoi")):
        if abs(x) > 1.0 - s + 1e-9 or abs(y) > 1.0 - KY * s + 1e-9:
            bad.append("shot %s %s" % (r["idx"], tag))

print("KY = %.6f" % KY)
print("shot bi kep lai: %d" % len(changed))
for idx, o, n in changed[:10]:
    print("  shot %s  x0 %s->%s  y0 %s->%s  x1 %s->%s  y1 %s->%s"
          % (idx, o[0], n[0], o[1], n[1], o[2], n[2], o[3], n[3]))
if bad:
    sys.exit("VAN CON VI PHAM: %s" % bad[:10])

shutil.copy2(f, str(f) + ".bak")
with f.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
print("Da ghi lai %s  (ban goc: %s.bak)" % (f, f))
print("Kiem lai toan bo %d shot: KHONG con vi pham" % len(rows))