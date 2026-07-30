#!/usr/bin/env python3
"""
tr_profile3.py <video.mp4>
Doc LIEN TUC ca cua so bang MOT lenh ffmpeg -> het trung khung do tua.
Nguong lay tu 3 cua so NEN do ben trong shot (chi co Ken Burns).
"""
import subprocess, pathlib, sys

VID  = pathlib.Path(sys.argv[1])
GRID, SPAN = 32, 1.20
FSZ  = GRID * GRID * 3

WINDOWS = [
    (42.000,  "NEN giua shot 3"),
    (60.000,  "NEN giua shot 4"),
    (120.000, "NEN giua shot 7"),
    (19.767,  "Cube  (PLACEHOLDER)"),
    (34.700,  "Page Turning"),
    (48.900,  "Glitch"),
    (72.733,  "Whirlpool"),
    (91.967,  "Split"),
    (106.700, "Flip II"),
    (132.733, "Shutter"),
]


def frames(center):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.4f" % (center - SPAN / 2),
                        "-i", str(VID), "-t", "%.4f" % SPAN,
                        "-vf", "scale=%d:%d" % (GRID, GRID),
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    b = r.stdout
    return [b[i * FSZ:(i + 1) * FSZ] for i in range(len(b) // FSZ)]


out, base = [], 0.0
for c, label in WINDOWS:
    fs = frames(c)
    if len(fs) < 10:
        print("  %-24s CHI DOC DUOC %d KHUNG" % (label, len(fs))); continue
    ds = [sum(abs(fs[i][k] - fs[i + 1][k]) for k in range(FSZ)) / FSZ
          for i in range(len(fs) - 1)]
    br = [sum(f) / FSZ for f in fs]
    out.append((label, ds, br))
    if label.startswith("NEN"):
        base = max(base, max(ds))

thr = max(base * 3.0, 2.0)
print("moc nen = %.2f   nguong = %.2f   cua so %.2fs, luoi %dx%d\n"
      % (base, thr, SPAN, GRID, GRID))

for label, ds, br in out:
    n, mid = len(ds), len(ds) // 2
    hi = [i for i, x in enumerate(ds) if x > thr]
    left = sum(1 for i in hi if i < mid - 1)
    right = sum(1 for i in hi if i > mid)
    if not hi:
        v = "im lang"
    elif len(hi) <= 2:
        v = "*** CAT CUNG ***"
    elif left >= 2 and right >= 2:
        v = "TRANSITION THAT"
    else:
        v = "*** LECH MOT BEN -> nghi CAT CUNG ***"
    print("  %-24s max=%6.2f  vuot_nguong=%2d (trai %d / phai %d)  sang_min=%5.1f  %s"
          % (label, max(ds), len(hi), left, right, min(br), v))
    print("       d : " + " ".join("%3.0f" % x for x in ds))
    print("       t : " + " ".join("  ^" if i == mid else "   " for i in range(n)))
    print("       br: " + " ".join("%3.0f" % x for x in br))
    print()