import subprocess
import os
import sys

FFMPEG = os.path.join(
    os.path.expanduser("~"),
    r"AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0"
    r"\LocalCache\local-packages\Python313\site-packages\imageio_ffmpeg\binaries"
    r"\ffmpeg-win-x86_64-v7.1.exe"
)

W = 1280
H = 720
MARGIN = 0.12
BLUR = 40
ZOOM_PCT = 4
FPS = 30

shots = [
    ("Shot_001_IE3_Launch.png",            "00:00:00.260", "00:00:19.340"),
    ("Shot_002_CSS_Revolution.png",        "00:00:19.740", "00:00:34.090"),
    ("Shot_003_IE_Acclaimed.png",          "00:00:34.680", "00:00:48.220"),
    ("Shot_004_Browser_War_Shifts.png",    "00:00:48.880", "00:01:12.720"),
    ("Shot_005_IE3_Engineering_Team.png",  "00:01:12.720", "00:01:31.400"),
    ("Shot_006_Cost_Of_Success.png",       "00:01:31.960", "00:01:46.020"),
    ("Shot_007_Netscape_Communicator.png", "00:01:46.700", "00:02:12.460"),
    ("Shot_008_Netscape_Collapse.png",     "00:02:12.720", "00:02:48.720"),
]

def ts_to_sec(ts):
    parts = ts.split(":")
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

def make_segment(img, duration, idx):
    out = f"_seg_{idx:03d}.mp4"
    total_frames = int(duration * FPS)

    inner_w = int(W * (1 - 2 * MARGIN))
    inner_h = int(H * (1 - 2 * MARGIN))

    # Ảnh gốc 1376x768
    # Zoom in: crop vùng nhỏ dần từ giữa ảnh, rồi scale lên inner size
    # crop bắt đầu = full ảnh, crop kết thúc = nhỏ hơn ZOOM_PCT%
    cw_start = 1376
    cw_end = int(1376 / (1 + ZOOM_PCT / 100))
    ch_start = 768
    ch_end = int(768 / (1 + ZOOM_PCT / 100))

    # Dùng n (frame number) thay vì t
    # progress = n / total_frames (từ 0 → 1)
    cw = f"{cw_start}-({cw_start}-{cw_end})*n/{total_frames}"
    ch = f"{ch_start}-({ch_start}-{ch_end})*n/{total_frames}"

    fc = (
        f"[0]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},boxblur={BLUR}:{BLUR},fps={FPS},setsar=1[bg];"

        f"[0]fps={FPS},"
        f"crop=w='{cw}':h='{ch}':x='(iw-ow)/2':y='(ih-oh)/2',"
        f"scale={inner_w}:{inner_h},setsar=1[fg];"

        f"[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1[v]"
    )

    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-framerate", str(FPS), "-t", str(duration),
        "-i", img,
        "-filter_complex", fc,
        "-map", "[v]",
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        out
    ]

    print(f"  [{idx+1}/8] {img} ({duration:.1f}s)...", end=" ", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("LỖI!")
        for line in r.stderr.split("\n"):
            ll = line.lower()
            if any(k in ll for k in ["error", "invalid", "failed", "cannot", "no such"]):
                print(f"    {line.strip()}")
        sys.exit(1)
    print("OK")
    return out

def main():
    print("=== Kiểm tra file ===")
    ok = True
    for f, _, _ in shots:
        if not os.path.exists(f):
            print(f"  THIẾU: {f}"); ok = False
        else:
            print(f"  OK: {f}")
    if not os.path.exists("audio.mp3"):
        print("  THIẾU: audio.mp3"); ok = False
    else:
        print("  OK: audio.mp3")
    if not ok:
        sys.exit(1)
    print()

    print("=== Tạo segments ===")
    segs = []
    for i, (f, s, e) in enumerate(shots):
        dur = ts_to_sec(e) - ts_to_sec(s)
        segs.append(make_segment(f, dur, i))
    print()

    print("=== Ghép video + audio ===")
    with open("_list.txt", "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")

    r = subprocess.run([
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", "_list.txt",
        "-i", "audio.mp3",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        "test_output.mp4"
    ], capture_output=True, text=True)

    if r.returncode != 0:
        print("LỖI ghép!")
        for line in r.stderr.split("\n"):
            if any(k in line.lower() for k in ["error", "invalid", "failed"]):
                print(f"  {line.strip()}")
        sys.exit(1)

    for s in segs:
        os.remove(s)
    os.remove("_list.txt")

    print()
    print("=== HOÀN THÀNH ===")
    mb = os.path.getsize("test_output.mp4") / 1048576
    print(f"File: test_output.mp4 ({mb:.1f} MB)")

if __name__ == "__main__":
    main()