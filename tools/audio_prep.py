"""audio_prep.py <audio-nguồn> <audio-đích> [số-phút-mục-tiêu=59]
Nối lặp một file audio ngắn thành file dài dùng cho bài tải, bằng concat demuxer với -c copy nên không mã hoá lại.
Vào: file audio nguồn. Ra: file audio đích, file concat_list.txt cạnh nó, và bộ số làm việc cho bộ sinh shot.
Đo độ dài hai lần, container bằng ffprobe và giải mã thật bằng ffmpeg -f null, lấy giá trị lớn hơn làm audio_ms, cộng đuôi cố ý 2000 ms, rồi bắt tổng lên lưới 100 ms.
[KIEM: du lieu that]
"""

import math, re, subprocess, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SRC = Path(sys.argv[1])
DST = Path(sys.argv[2])
TARGET_MIN = float(sys.argv[3]) if len(sys.argv) > 3 else 59.0
TAIL_MS = 2000
GRID_MS = 100

def probe_container(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None

def probe_decoded(p):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        return None
    h, mn, s = m[-1]
    return int(h) * 3600 + int(mn) * 60 + float(s)

def main():
    if not SRC.exists():
        print(f"KHONG THAY nguon: {SRC}")
        return 1
    c0 = probe_container(SRC)
    d0 = probe_decoded(SRC)
    if c0 is None:
        print("ffprobe khong doc duoc nguon")
        return 1
    print(f"nguon      : {SRC}")
    print(f"  container : {c0:.6f} s")
    print(f"  decoded   : {d0:.6f} s" if d0 else "  decoded   : khong doc duoc")

    unit = max(c0, d0 or 0.0)
    repeat = int(math.ceil(TARGET_MIN * 60.0 / unit))
    print(f"  muc tieu  : {TARGET_MIN:.1f} phut -> lap {repeat} lan")

    DST.parent.mkdir(parents=True, exist_ok=True)
    lst = DST.parent / "concat_list.txt"
    esc = str(SRC.resolve()).replace("\\", "/")
    lst.write_text("".join(f"file '{esc}'\n" for _ in range(repeat)), encoding="utf-8")

    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "concat",
                        "-safe", "0", "-i", str(lst), "-c", "copy", "-y", str(DST)])
    if r.returncode != 0 or not DST.exists():
        print(f"FAIL ffmpeg rc={r.returncode}")
        return 1

    c1 = probe_container(DST)
    d1 = probe_decoded(DST)
    print("")
    print(f"ket qua    : {DST}")
    print(f"  size      : {DST.stat().st_size / 1048576.0:.2f} MB")
    print(f"  container : {c1:.6f} s = {c1/60.0:.3f} phut")
    print(f"  decoded   : {d1:.6f} s" if d1 else "  decoded   : khong doc duoc")
    if d1:
        print(f"  lech container vs decoded : {c1 - d1:.6f} s")

    base = max(c1, d1 or 0.0)
    base_ms = int(math.ceil(base * 1000.0))
    total_ms = int(math.ceil((base_ms + TAIL_MS) / float(GRID_MS))) * GRID_MS
    ok = "OK" if total_ms % GRID_MS == 0 else "SAI"
    print("")
    print("=== so lam viec cho bo sinh shot ===")
    print(f"  audio_ms        : {base_ms}")
    print(f"  duoi co y       : {TAIL_MS} ms")
    print(f"  tong tren luoi  : {total_ms} ms = {total_ms/1000.0:.1f} s = {total_ms/60000.0:.4f} phut")
    print(f"  thua sau audio  : {total_ms - base_ms} ms")
    print(f"  kiem tra luoi   : {ok}")
    return 0

if __name__ == "__main__":
    sys.exit(main())