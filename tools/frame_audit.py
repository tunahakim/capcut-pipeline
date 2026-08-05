"""frame_audit.py --project <tên-project> --mp4 <đường-dẫn-mp4>
Đối chiếu JSON với pixel thật của bản export, tức bằng chứng mức 5: với mỗi shot, nội suy scale tại giữa shot từ keyframe KFTypeScaleX, dự đoán tỉ lệ diện tích viền, trích một khung xám bằng ffmpeg rồi đếm tỉ lệ pixel tối ở hai ngưỡng 6 và 20 để kết luận BLUR, BLACK hay AMBIG.
Vào: draft của project và file MP4. Ra: bảng tổng hợp theo mức blur, danh sách shot mâu thuẫn giữa JSON và pixel, và CSV <CAPCUT_LAB>/perf/frame_audit_<project>.csv.
Chỉ kết luận khi viền dự đoán chiếm trên 2 phần trăm khung hình, dưới ngưỡng đó ghi AMBIG.
[KIEM: bo test]
"""

import argparse, csv, json, os, subprocess, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DRAFTS = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
LAB = Path(os.environ.get("CAPCUT_LAB") or r"D:\IT\capcut-lab\data")
_AP = argparse.ArgumentParser(description="Doi chieu JSON voi pixel that cua ban export, bang chung muc 5.")
_AP.add_argument("--project", required=True, help="ten project trong thu muc draft cua CapCut")
_AP.add_argument("--mp4", required=True, help="duong dan MP4 da export cua chinh project do")
_ARGS = _AP.parse_args()
PROJ = _ARGS.project
MP4 = _ARGS.mp4
CW, CH = 1920, 1080
NPIX = CW * CH
T_DARK, T_GRAIN = 6, 20
TBL_D = bytes(1 if i <= T_DARK else 0 for i in range(256))
TBL_G = bytes(1 if i <= T_GRAIN else 0 for i in range(256))


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


def scale_at(seg, rel_us):
    pts = []
    for kf in (seg.get("common_keyframes") or []):
        if kf.get("property_type") == "KFTypeScaleX":
            for k in (kf.get("keyframe_list") or []):
                v = (k.get("values") or [None])[0]
                if v is not None:
                    pts.append((float(k.get("time_offset") or 0.0), float(v)))
    if not pts:
        cs = ((seg.get("clip") or {}).get("scale") or {}).get("x")
        return float(cs) if cs is not None else 1.0
    pts.sort()
    if rel_us <= pts[0][0]:
        return pts[0][1]
    if rel_us >= pts[-1][0]:
        return pts[-1][1]
    for j in range(1, len(pts)):
        if rel_us <= pts[j][0]:
            t0, v0 = pts[j - 1]
            t1, v1 = pts[j]
            f = 0.0 if t1 == t0 else (rel_us - t0) / (t1 - t0)
            return v0 + f * (v1 - v0)
    return pts[-1][1]


def bar_frac(w, h, s):
    if not w or not h:
        return None
    fit = min(CW / float(w), CH / float(h))
    dw = min(CW, float(w) * fit * s)
    dh = min(CH, float(h) * fit * s)
    return max(0.0, 1.0 - (dw * dh) / NPIX)


def grab(t):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "%.3f" % t,
           "-i", MP4, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    # enc: nhi phan
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    d = p.stdout
    if len(d) < NPIX:
        return None
    d = d[:NPIX]
    return (d.translate(TBL_D).count(1) / NPIX,
            d.translate(TBL_G).count(1) / NPIX,
            sum(d) / NPIX)


def main():
    if not Path(MP4).exists():
        print("KHONG THAY MP4: %s" % MP4)
        return 1
    dcp = DRAFTS / PROJ / "draft_content.json"
    if not dcp.exists():
        print("KHONG THAY %s" % dcp)
        return 1
    dc = load(dcp)
    mi = mat_index(dc)
    segs = (main_track(dc).get("segments") or [])
    print("project %s : %d segment | mp4 %.2f GB" % (PROJ, len(segs), Path(MP4).stat().st_size / 2**30))

    recs = []
    for i, s in enumerate(segs):
        blur = 0.0
        for r in (s.get("extra_material_refs") or []):
            e = mi.get(r)
            if e and e[0] == "canvases" and (e[1].get("type") == "canvas_blur"):
                blur = float(e[1].get("blur") or 0.0)
        mat = (mi.get(s.get("material_id")) or (None, {}))[1]
        tr = s.get("target_timerange") or {}
        st, du = float(tr.get("start", 0)), float(tr.get("duration", 0))
        mid = (st + du / 2.0) / 1e6
        sc = scale_at(s, du / 2.0)
        bf = bar_frac(mat.get("width"), mat.get("height"), sc)
        g = grab(mid)
        if g is None:
            print("  shot %d: khong doc duoc khung tai %.3fs" % (i + 1, mid))
            continue
        dk, gr, mn = g
        verdict = "AMBIG"
        if bf and bf > 0.02:
            if gr < bf * 0.35:
                verdict = "BLUR"
            elif gr > bf * 0.65:
                verdict = "BLACK"
        recs.append({"shot": i + 1, "blur": round(blur, 4), "scale": round(sc, 4),
                     "mid_s": round(mid, 3), "bar_pred": round(bf or 0.0, 4),
                     "dark6": round(dk, 4), "dark20": round(gr, 4),
                     "ymean": round(mn, 2), "verdict": verdict})
        if (i + 1) % 25 == 0:
            print("  %3d/%d" % (i + 1, len(segs)))

    groups = {}
    for r in recs:
        groups.setdefault(r["blur"], []).append(r)
    print("")
    print("%-9s %-6s %-9s %-9s %-9s %-8s %-6s %-6s %s" % (
        "blur", "n", "bar_pred", "dark20", "dark6", "ymean", "BLUR", "BLACK", "AMBIG"))
    for b in sorted(groups):
        g = groups[b]
        av = lambda k: sum(x[k] for x in g) / len(g)
        print("%-9.4f %-6d %-9.4f %-9.4f %-9.4f %-8.2f %-6d %-6d %d" % (
            b, len(g), av("bar_pred"), av("dark20"), av("dark6"), av("ymean"),
            sum(1 for x in g if x["verdict"] == "BLUR"),
            sum(1 for x in g if x["verdict"] == "BLACK"),
            sum(1 for x in g if x["verdict"] == "AMBIG")))

    bad = [r for r in recs if (r["blur"] > 0 and r["verdict"] == "BLACK") or (r["blur"] == 0 and r["verdict"] == "BLUR")]
    print("")
    print("mau thuan JSON vs pixel: %d / %d" % (len(bad), len(recs)))
    for r in bad[:20]:
        print("  shot %3d blur %.4f scale %.3f bar %.3f dark20 %.3f -> %s"
              % (r["shot"], r["blur"], r["scale"], r["bar_pred"], r["dark20"], r["verdict"]))

    out = LAB / "perf" / ("frame_audit_%s.csv" % PROJ)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
    print("")
    print("chi tiet: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())