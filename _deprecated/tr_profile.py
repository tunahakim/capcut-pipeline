#!/usr/bin/env python3
"""
tr_profile.py <video.mp4>
Do muc bien dong giua cac khung lien tiep xuyen qua tung ranh gioi transition,
so voi mot cua so DOI CHUNG nam giua shot (khong co transition).
Dung luoi 8x8 nen bat duoc ca bien doi hinh hoc, khong chi doi mau.
"""
import subprocess, pathlib, sys

VID = pathlib.Path(sys.argv[1])
STEP, HALF, GRID = 0.05, 0.25, 8

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
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", str(VID),
                        "-frames:v", "1", "-vf", "scale=%d:%d" % (GRID, GRID),
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    return r.stdout[:GRID * GRID * 3]


def diff(a, b):
    if len(a) != len(b) or not a:
        return -1
    return sum(abs(a[i] - b[i]) for i in range(len(a))) / len(a)


print("cua so = tam +-%.2fs, buoc %.2fs, luoi %dx%d\n" % (HALF, STEP, GRID, GRID))
base = None
for center, label in WINDOWS:
    ts = [center - HALF + i * STEP for i in range(int(2 * HALF / STEP) + 1)]
    gs = [grid(t) for t in ts]
    ds = [diff(gs[i], gs[i + 1]) for i in range(len(gs) - 1)]
    ds = [x for x in ds if x >= 0]
    if not ds:
        print("  %-28s KHONG DOC DUOC" % label); continue
    mx, av = max(ds), sum(ds) / len(ds)
    if base is None:
        base = mx
        verdict = "<= moc nen"
    else:
        verdict = "CO TRANSITION" if mx > base * 2.5 else "*** khong khac nen -> CAT CUNG ***"
    print("  %-28s max=%6.2f  tb=%6.2f  x nen=%5.2f  %s"
          % (label, mx, av, mx / base if base else 0, verdict))
    print("       " + " ".join("%.0f" % x for x in ds))