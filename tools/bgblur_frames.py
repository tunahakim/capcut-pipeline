"""bgblur_frames.py --project <tên-project> [--mp4 <đường-dẫn-export.mp4>]
Chọn mẫu shot của một project chỉ định để kiểm thị giác canvas blur, theo quy tắc in ground truth ra trước rồi mới nhìn ở failures.md mục 1.
Vào: tên project trong thư mục draft, tuỳ chọn thêm file MP4 đã export. Ra: bảng shot kèm mức blur, scale nhỏ nhất và lớn nhất, mốc giữa shot, bề rộng viền dự đoán; nếu có MP4 thì trích khung PNG tại giữa mỗi shot ra <CAPCUT_LAB>/perf/bgblur_frames_<tên-project>.
Mẫu gồm một cặp đối chứng blur mạnh cạnh canvas_color, một shot blur mức 4, một shot blur mức 1, một shot canvas_color âm tính và một shot blur mức giữa. Thiếu vai nào thì in cảnh báo kèm danh sách chứ không im lặng.
[KIEM: bo test]
"""

import argparse, json, os, subprocess, sys
from pathlib import Path

DRAFTS = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
LAB = Path(os.environ.get("CAPCUT_LAB") or r"D:\IT\capcut-lab\data")
_AP = argparse.ArgumentParser(description="Chon mau shot de kiem thi giac canvas blur.")
_AP.add_argument("--project", required=True, help="ten project trong thu muc draft cua CapCut")
_AP.add_argument("--mp4", default="", help="tuy chon; duong dan MP4 da export de trich khung PNG")
_ARGS = _AP.parse_args()
PROJ = _ARGS.project
CW, CH = 1920.0, 1080.0
MP4 = _ARGS.mp4.strip()

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def mat_index(dc):
    out = {}
    for bucket, arr in (dc.get("materials") or {}).items():
        if isinstance(arr, list):
            for m in arr:
                if isinstance(m, dict) and m.get("id"):
                    out[m["id"]] = (bucket, m)
    return out

def main_track(dc):
    best = None
    for t in (dc.get("tracks") or []):
        if t.get("type") == "video":
            if best is None or len(t.get("segments") or []) > len(best.get("segments") or []):
                best = t
    return best

def scales_of(seg):
    vals = []
    for kf in (seg.get("common_keyframes") or []):
        if kf.get("property_type") == "KFTypeScaleX":
            for k in (kf.get("keyframe_list") or []):
                v = (k.get("values") or [None])[0]
                if v is not None:
                    vals.append(float(v))
    cs = ((seg.get("clip") or {}).get("scale") or {}).get("x")
    if cs is not None:
        vals.append(float(cs))
    return vals

def border(w, h, sc):
    if not w or not h:
        return None, None
    fit = min(CW / float(w), CH / float(h))
    dw = float(w) * fit * sc
    dh = float(h) * fit * sc
    return (CW - dw) / 2.0, (CH - dh) / 2.0

def main():
    dcp = DRAFTS / PROJ / "draft_content.json"
    if not dcp.exists():
        print("KHONG THAY %s" % dcp)
        return 1
    dc = load(dcp)
    mi = mat_index(dc)
    segs = (main_track(dc).get("segments") or [])
    rows = []
    for i, s in enumerate(segs):
        refs = s.get("extra_material_refs") or []
        ctype, blur = "none", 0.0
        for r in refs:
            e = mi.get(r)
            if e and e[0] == "canvases":
                ctype = e[1].get("type") or "?"
                blur = float(e[1].get("blur") or 0.0)
        mat = (mi.get(s.get("material_id")) or (None, {}))[1]
        tr = s.get("target_timerange") or {}
        sc = scales_of(s)
        rows.append({
            "shot": i + 1,
            "ctype": ctype,
            "blur": round(blur, 4),
            "smin": min(sc) if sc else 1.0,
            "smax": max(sc) if sc else 1.0,
            "start": float(tr.get("start", 0)) / 1e6,
            "dur": float(tr.get("duration", 0)) / 1e6,
            "w": mat.get("width"),
            "h": mat.get("height"),
            "img": Path(str(mat.get("path") or "")).name,
        })

    long_enough = [r for r in rows if r["dur"] >= 4.0]
    picks = []

    def take(pred, n, why):
        cs = sorted([r for r in long_enough if pred(r) and r["shot"] not in [p[0]["shot"] for p in picks]],
                    key=lambda r: r["smin"])
        for r in cs[:n]:
            picks.append((r, why))

    pair = None
    for r in long_enough:
        if r["ctype"] == "canvas_blur" and r["blur"] >= 0.75:
            for q in long_enough:
                if q["ctype"] == "canvas_color" and abs(q["shot"] - r["shot"]) <= 2:
                    pair = (r, q)
                    break
        if pair:
            break
    if pair:
        picks.append((pair[0], "AB-pos blur%.4f" % pair[0]["blur"]))
        picks.append((pair[1], "AB-neg color"))
    take(lambda r: r["ctype"] == "canvas_blur" and r["blur"] == 1.0, 1, "blur-max")
    take(lambda r: r["ctype"] == "canvas_blur" and r["blur"] <= 0.0625, 1, "blur-min")
    take(lambda r: r["ctype"] == "canvas_color", 1, "neg-color")
    take(lambda r: r["ctype"] == "canvas_blur" and 0.3 < r["blur"] < 0.8, 1, "blur-mid")

    WANT = [
        ("AB-pos", "doi chung duong: canvas_blur >= 0.75 co canvas_color ke ben"),
        ("AB-neg", "doi chung am nam ke cap AB"),
        ("blur-max", "blur muc 4 = 1.0"),
        ("blur-min", "blur muc 1 = 0.0625"),
        ("neg-color", "canvas_color am tinh"),
        ("blur-mid", "blur muc giua, 0.3 < blur < 0.8"),
    ]
    got = set(why.split(" ")[0] for r, why in picks)
    vblur = sorted(set(r["blur"] for r in rows))
    vctype = sorted(set(str(r["ctype"]) for r in rows))
    missing = [(k, d) for k, d in WANT if k not in got]
    print("")
    print("DO PHU MAU: %d/%d vai" % (len(WANT) - len(missing), len(WANT)))
    print("segment: %d | dat dieu kien dur >= 4.0s: %d" % (len(rows), len(long_enough)))
    print("so gia tri blur PHAN BIET: %d -> %s" % (len(vblur), vblur))
    print("so loai canvas PHAN BIET: %d -> %s" % (len(vctype), vctype))
    if len(rows) != len(long_enough):
        print("CANH BAO: %d shot bi loai vi ngan hon 4.0s" % (len(rows) - len(long_enough)))
    if missing:
        print("CANH BAO: THIEU %d VAI. Bang duoi KHONG phu du danh muc," % len(missing))
        print("  nen KHONG duoc ket luan gi ve cac muc blur vang mat.")
        for k, d in missing:
            print("  thieu %-10s : %s" % (k, d))
    else:
        print("DU CA %d VAI" % len(WANT))

    print("")
    print("%-4s %-14s %-8s %-6s %-6s %-9s %-7s %-9s %-11s %s" % (
        "shot", "role", "blur", "smin", "smax", "start", "dur", "mid", "borderX px", "image"))
    outdir = LAB / "perf" / ("bgblur_frames_%s" % PROJ)
    outdir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for r, why in picks:
        mid = r["start"] + r["dur"] / 2.0
        bx0, by0 = border(r["w"], r["h"], r["smin"])
        bx1, by1 = border(r["w"], r["h"], r["smax"])
        bs = "n/a" if bx0 is None else "%d..%d" % (round(min(bx0, bx1)), round(max(bx0, bx1)))
        print("%-4d %-14s %-8.4f %-6.2f %-6.2f %-9.3f %-7.3f %-9.3f %-11s %s" % (
            r["shot"], why, r["blur"], r["smin"], r["smax"], r["start"], r["dur"], mid, bs, r["img"]))
        name = "shot%03d_%s_blur%.4f_s%.2f_t%.3f.png" % (r["shot"], why.replace(" ", "-"), r["blur"], r["smin"], mid)
        jobs.append((mid, outdir / name))

    if not MP4:
        print("")
        print("CHUA CO MP4. Chay lai kem --mp4 \"D:\\duong\\dan\\export.mp4\"")
        return 0
    print("")
    print("mp4: %s" % MP4)
    for mid, dst in jobs:
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "%.3f" % mid,
               "-i", MP4, "-frames:v", "1", "-y", str(dst)]
        p = subprocess.run(cmd)
        ok = "OK" if (p.returncode == 0 and dst.exists()) else "FAIL rc=%s" % p.returncode
        print("  %-6s %s" % (ok, dst.name))
    print("")
    print("frames: %s" % outdir)
    return 0

if __name__ == "__main__":
    sys.exit(main())