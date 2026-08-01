"""bgblur_diag.py
Chẩn đoán lớp canvas của hai project cứng tên bench300 và parity01, đọc cả draft_content.json gốc lẫn mọi bản trong Timelines.
Vào: không tham số, đọc thẳng thư mục draft của CapCut. Ra: in console và ghi <CAPCUT_LAB>/perf/bgblur_diag.txt.
Thống kê số canvas theo type, vị trí ref canvas_blur trong extra_material_refs, phân bố check_flag, các mức blur, dải scale, và tám shot blur mạnh nhất kèm mốc thời gian. Chỉ đọc, không sửa gì.
"""

import json, os, sys
from pathlib import Path
from collections import Counter

DRAFTS = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
LAB = Path(os.environ.get("CAPCUT_LAB") or (Path(__file__).resolve().parents[2] / "data"))
NAMES = ["bench300", "parity01"]
LINES = []

def say(s=""):
    s = str(s)
    print(s)
    LINES.append(s)

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def files_of(proj):
    out = []
    r = proj / "draft_content.json"
    if r.exists():
        out.append(("root", r))
    tl = proj / "Timelines"
    if tl.is_dir():
        for c in sorted(tl.glob("*/draft_content.json")):
            out.append(("nested." + c.parent.name[:8], c))
    return out

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

def tstr(us):
    s = float(us) / 1000000.0
    return "%d:%05.2f" % (int(s // 60), s % 60)

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

def analyse(name, tag, path):
    dc = load(path)
    mi = mat_index(dc)
    tr = main_track(dc)
    segs = (tr.get("segments") or []) if tr else []
    cv_all = ((dc.get("materials") or {}).get("canvases") or [])
    say("")
    say("== %s / %s" % (name, tag))
    say("   file bytes                : %d" % path.stat().st_size)
    say("   video segments            : %d" % len(segs))
    say("   materials.canvases        : %d  types=%s" % (len(cv_all), dict(Counter([c.get("type") for c in cv_all]))))
    shape = Counter(); posn = Counter(); flags = Counter(); blurv = Counter()
    blurred = []
    gmin = None; gmax = None
    for i, s in enumerate(segs):
        refs = s.get("extra_material_refs") or []
        cvs = [(k, mi[r][1]) for k, r in enumerate(refs) if r in mi and mi[r][0] == "canvases"]
        shape[tuple(m.get("type") for _, m in cvs)] += 1
        mat = (mi.get(s.get("material_id")) or (None, {}))[1]
        flags[mat.get("check_flag")] += 1
        sc = scales_of(s)
        smin = min(sc) if sc else None
        if sc:
            gmin = min(sc) if gmin is None else min(gmin, min(sc))
            gmax = max(sc) if gmax is None else max(gmax, max(sc))
        for k, m in cvs:
            if m.get("type") == "canvas_blur":
                posn["ref idx %d of %d" % (k, len(refs))] += 1
                blurv[round(float(m.get("blur") or 0.0), 4)] += 1
                blurred.append((round(float(m.get("blur") or 0.0), 4),
                                smin if smin is not None else 1.0, i,
                                (s.get("target_timerange") or {}).get("start", 0),
                                mat.get("check_flag")))
    say("   canvas refs per segment   : %s" % dict(shape))
    say("   canvas_blur ref position  : %s" % dict(posn))
    say("   check_flag distribution   : %s" % dict(flags))
    say("   blur values               : %s" % dict(blurv))
    if gmin is not None:
        say("   scale range kf+clip       : %.4f .. %.4f" % (gmin, gmax))
    say("   segments with canvas_blur : %d" % len(blurred))
    if blurred:
        blurred.sort(key=lambda r: (-r[0], r[1]))
        say("   manh nhat truoc, scale nho nhat truoc:")
        say("     %-8s %-9s %-6s %-9s %s" % ("blur", "minscale", "shot", "start", "check_flag"))
        for b, sm, i, st, cf in blurred[:8]:
            say("     %-8.4f %-9.4f %-6d %-9s %s" % (b, sm, i + 1, tstr(st), cf))

def main():
    if not DRAFTS.is_dir():
        say("KHONG THAY thu muc draft: %s" % DRAFTS)
        return 1
    say("draft dir : %s" % DRAFTS)
    say("projects  : %s" % ", ".join(sorted([p.name for p in DRAFTS.iterdir() if p.is_dir()])))
    for n in NAMES:
        proj = DRAFTS / n
        if not proj.is_dir():
            say("")
            say("== %s : KHONG TON TAI, bo qua" % n)
            continue
        fs = files_of(proj)
        if not fs:
            say("")
            say("== %s : khong co draft_content.json" % n)
            continue
        for tag, p in fs:
            analyse(n, tag, p)
    outdir = LAB / "perf"
    try:
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "bgblur_diag.txt").write_text("\n".join(LINES), encoding="utf-8")
        print("")
        print("report: %s" % (outdir / "bgblur_diag.txt"))
    except Exception as e:
        print("khong ghi duoc report: %s" % e)
    return 0

if __name__ == "__main__":
    sys.exit(main())