import csv, subprocess, sys
from collections import Counter
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
CW, CH = 1920.0, 1080.0
EXTS = {".jpg", ".jpeg", ".png"}

def dims(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height",
                        "-of", "csv=p=0:s=x", str(p)], capture_output=True, text=True)
    t = r.stdout.strip().split("\n")[0].strip()
    if "x" not in t:
        return None, None
    a, b = t.split("x")[:2]
    try:
        return int(a), int(b)
    except ValueError:
        return None, None

def main():
    if not SRC.is_dir():
        print(f"KHONG THAY thu muc: {SRC}")
        return 1
    files = sorted([p for p in SRC.rglob("*") if p.is_file() and p.suffix.lower() in EXTS])
    print(f"thu muc : {SRC}")
    print(f"file ung vien : {len(files)}")
    rows, bad = [], []
    for i, p in enumerate(files, 1):
        w, h = dims(p)
        if not w or not h:
            bad.append(p)
            continue
        fit = min(CW / w, CH / h)
        kx = w * fit / CW
        ky = h * fit / CH
        rows.append({"path": str(p), "w": w, "h": h, "bytes": p.stat().st_size,
                     "ar": round(w / float(h), 6), "kx": round(kx, 6), "ky": round(ky, 6)})
        if i % 50 == 0:
            print(f"  ... {i}/{len(files)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        wtr = csv.DictWriter(f, fieldnames=["path", "w", "h", "bytes", "ar", "kx", "ky"])
        wtr.writeheader()
        wtr.writerows(rows)

    ext = Counter(Path(r["path"]).suffix.lower() for r in rows)
    size = Counter((r["w"], r["h"]) for r in rows)
    land = sum(1 for r in rows if r["w"] > r["h"])
    port = sum(1 for r in rows if r["w"] < r["h"])
    sq = sum(1 for r in rows if r["w"] == r["h"])
    exact169 = sum(1 for r in rows if r["kx"] == 1.0 and r["ky"] == 1.0)
    tot_mb = sum(r["bytes"] for r in rows) / 1048576.0
    print("")
    print(f"doc duoc      : {len(rows)} anh, {tot_mb:.1f} MB")
    print(f"khong doc duoc: {len(bad)}")
    for p in bad[:10]:
        print(f"    {p}")
    print(f"duoi file     : {dict(ext)}")
    print(f"huong         : ngang {land}, doc {port}, vuong {sq}")
    print(f"dung 16:9     : {exact169}  (so con lai LUON lo nen ke ca o scale 1.0)")
    print(f"w min/max     : {min(r['w'] for r in rows)} / {max(r['w'] for r in rows)}")
    print(f"h min/max     : {min(r['h'] for r in rows)} / {max(r['h'] for r in rows)}")
    print("")
    print("10 kich thuoc pho bien nhat:")
    for (w, h), n in size.most_common(10):
        print(f"    {w}x{h}  x{n}")
    print("")
    print(f"CSV: {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())