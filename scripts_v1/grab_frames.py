#!/usr/bin/env python3
"""
grab_frames.py <video.mp4> [out-dir]
Trich khung hinh tai cac moc kiem chung, kem md5 va mau trung binh RGB.
  - md5 trung nhau  -> hai khung GIONG HET (dung de phat hien cat cung)
  - RGB trung binh  -> so sanh khach quan thay vi nhin bang mat
[KIEM: chua]
"""
import subprocess, pathlib, sys, os, hashlib

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
VID = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else LAB / "frames"
OUT.mkdir(parents=True, exist_ok=True)

if not VID.exists():
    sys.exit("Khong thay file: %s" % VID)

# Baseline sau quantization:
#  s1 0-19.767  s2 -34.700  s3 -48.900  s4 -72.733
#  s5 -91.967   s6 -106.700 s7 -132.733 s8 -168.733
MARKS = [
    (0.500,   "01_s1_dau_scale072"),      # keyframe scale 0.72 -> 0.86
    (19.200,  "02_s1_cuoi_scale086"),
    (19.500,  "03_cube_truoc"),           # Cube - TAI NGUYEN CHET
    (19.767,  "04_cube_giua"),
    (20.030,  "05_cube_sau"),
    (20.500,  "06_s2_dau_pan_trai"),      # keyframe position -0.15 -> +0.15
    (34.300,  "07_s2_cuoi_pan_phai"),
    (34.470,  "08_pageturn_truoc"),       # Page Turning - OK
    (34.700,  "09_pageturn_giua"),
    (34.930,  "10_pageturn_sau"),
    (49.400,  "11_s4_dau_scale092"),      # ZOOM OUT 0.92 -> 0.76
    (72.300,  "12_s4_cuoi_scale076"),
    (83.900,  "13_shot5_truoc"),          # cung Shot_005, khong con filter
    (84.800,  "14_shot5_sau"),
    (91.967,  "15_split_giua"),           # Split - OK
    (106.700, "16_flipii_giua"),          # Flip II - OK
    (107.300, "17_s7_combo"),             # combo animation shot 7
    (132.733, "18_shutter_giua"),         # Shutter - OK
    (168.000, "19_gan_cuoi"),
]

print("=== THONG TIN FILE ===")
p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height,r_frame_rate,nb_frames,codec_name",
                    "-show_entries", "format=duration,size,bit_rate",
                    "-of", "default=nw=1", str(VID)], capture_output=True)
print(p.stdout.decode("utf-8", errors="replace").strip())
print("  file: %s  (%.1f MB)" % (VID.name, VID.stat().st_size / 1048576))


def avg_rgb(t):
    """Mau trung binh toan khung: thu nho ve 1x1 pixel."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", str(VID),
                        "-frames:v", "1", "-vf", "scale=1:1", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True)
    b = r.stdout[:3]
    return tuple(b) if len(b) == 3 else (None, None, None)


print("\n=== TRICH KHUNG ===")
rows = []
for t, name in MARKS:
    out = OUT / (name + ".png")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % t,
                        "-i", str(VID), "-frames:v", "1", str(out)], capture_output=True)
    if not (out.exists() and out.stat().st_size > 0):
        print("  %8.3fs  %-24s *** LOI *** %s" % (t, name,
              r.stderr.decode("utf-8", errors="replace")[:120]))
        continue
    h = hashlib.md5(out.read_bytes()).hexdigest()
    rgb = avg_rgb(t)
    rows.append((t, name, h, rgb))
    print("  %8.3fs  %-24s md5=%s  RGB=%s" % (t, name, h[:10], rgb))

print("\n=== KHUNG GIONG HET NHAU (md5 trung) ===")
seen = {}
dup = False
for t, name, h, _ in rows:
    seen.setdefault(h, []).append(name)
for h, names in seen.items():
    if len(names) > 1:
        dup = True
        print("  %s  ->  %s" % (h[:10], names))
if not dup:
    print("  khong co cap nao giong het")

print("\n=== SO CAP DOI CHUNG ===")
D = {n: (t, h, rgb) for t, n, h, rgb in rows}


def cmp(a, b, hoi):
    if a not in D or b not in D:
        print("  THIEU KHUNG: %s hoac %s" % (a, b)); return
    ta, ha, ra = D[a]; tb, hb, rb = D[b]
    same = "GIONG HET" if ha == hb else "KHAC NHAU"
    d = sum(abs((ra[i] or 0) - (rb[i] or 0)) for i in range(3))
    print("  %-28s %-9s dRGB=%3d   %s" % (a + " vs " + b, same, d, hoi))


cmp("01_s1_dau_scale072", "02_s1_cuoi_scale086", "keyframe SCALE co render?")
cmp("11_s4_dau_scale092", "12_s4_cuoi_scale076", "keyframe SCALE (zoom OUT)?")
cmp("06_s2_dau_pan_trai", "07_s2_cuoi_pan_phai", "keyframe POSITION co render?")
cmp("03_cube_truoc", "05_cube_sau", "hai ben Cube - phai KHAC (2 anh khac nhau)")
cmp("03_cube_truoc", "04_cube_giua", "Cube: giong => CAT CUNG")
cmp("04_cube_giua", "05_cube_sau", "Cube: giong => CAT CUNG")
cmp("08_pageturn_truoc", "09_pageturn_giua", "Page Turning co render?")
cmp("09_pageturn_giua", "10_pageturn_sau", "Page Turning co render?")
cmp("13_shot5_truoc", "14_shot5_sau", "cung Shot_005, da go filter -> khac it la binh thuong")

print("\n=== KHUNG DEN / GAN DEN (tong RGB < 30) ===")
blk = [(n, rgb) for t, n, h, rgb in rows if rgb[0] is not None and sum(rgb) < 30]
for n, rgb in blk:
    print("  %-24s RGB=%s" % (n, rgb))
if not blk:
    print("  khong co")

print("\nDa ghi %d khung vao: %s" % (len(rows), OUT))