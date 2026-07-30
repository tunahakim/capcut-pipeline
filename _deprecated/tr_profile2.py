#!/usr/bin/env python3
"""
tr_profile2.py <video.mp4>
Lay mau tung FRAME (1/30s), luoi 32x32, danh gia theo HINH DANG chu khong theo dinh.
  cat cung   -> dung 1 dinh don doc, hai ben im lang
  transition -> nhieu buoc cao lien tiep, TRAI VA PHAI deu co
In kem do sang trung binh de bat khung toi (chu ky cua xoay 3D).
"""
import subprocess, pathlib, sys

VID = pathlib.Path(sys.argv[1])
FPS, HALF, GRID = 30.0, 0.30, 32
STEP = 1.0 / FPS

WINDOWS = [
    (60.000,  "DOI CHUNG giua shot 4"),
    (19.767,  "Cube        (PLACEHOLDER)"),
    (34.700,  "Page Turning"),
    (48.900,  "Glitch"),
    (72.733,  "Whirlpool"),
    (91.967,  "Split"),
    (106.700, "Flip II"),
    (132.733, "Shutter"),
]


def grid(t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.4f" % t, "-i", str(VID),
                        "-frames:v", "1", "-vf", "scale=%d:%d" % (GRID, GRID),
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    return r.stdout[:GRID * GRID * 3]


print("buoc = 1 frame (%.4fs), cua so +-%.2fs, luoi %dx%d\n" % (STEP, HALF, GRID, GRID))
n = int(HALF / STEP)
for center, label in WINDOWS:
    ts = [center + (i - n) * STEP for i in range(2 * n + 1)]
    gs = [grid(t) for t in ts]
    if any(len(g) != GRID * GRID * 3 for g in gs):
        print("  %-28s KHONG DOC DUOC DU KHUNG" % label); continue
    br = [sum(g) / len(g) for g in gs]
    ds = [sum(abs(gs[i][k] - gs[i + 1][k]) for k in range(len(gs[i]))) / len(gs[i])
          for i in range(len(gs) - 1)]
    mx = max(ds) or 1.0
    hi = [i for i, x in enumerate(ds) if x > mx * 0.15]
    left = sum(1 for i in hi if i < n - 1)
    right = sum(1 for i in hi if i > n)
    if len(hi) <= 2:
        verdict = "*** CAT CUNG (1 dinh don doc) ***"
    elif left >= 2 and right >= 2:
        verdict = "TRANSITION THAT"
    else:
        verdict = "*** NGHI VAN - lech mot ben ***"
    print("  %-28s max=%6.2f  buoc_cao=%2d (trai %d / phai %d)  sang_min=%5.1f  %s"
          % (label, mx, len(hi), left, right, min(br), verdict))
    print("       d : " + " ".join("%3.0f" % x for x in ds))
    print("       br: " + " ".join("%3.0f" % x for x in br))
    print()