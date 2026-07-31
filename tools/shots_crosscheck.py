import csv, json, os, sys
from pathlib import Path

DRAFTS = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
LAB = Path(os.environ.get("CAPCUT_LAB") or r"D:\IT\capcut-lab\data")
PROJ = "bench300"
LEVELS = {0: None, 1: 0.0625, 2: 0.375, 3: 0.75, 4: 1.0}
NEED = ["idx", "image", "start_s", "dur_s", "transition", "blur"]

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

def kf_scales(seg):
    for kf in (seg.get("common_keyframes") or []):
        if kf.get("property_type") == "KFTypeScaleX":
            kl = sorted((kf.get("keyframe_list") or []), key=lambda k: k.get("time_offset", 0))
            vs = [(k.get("values") or [None])[0] for k in kl]
            vs = [float(v) for v in vs if v is not None]
            if vs:
                return vs[0], vs[-1]
    return None, None

def find_csvs():
    out = []
    for root in [LAB, Path(r"D:\IT\capcut-lab")]:
        if not root.exists():
            continue
        for p in root.rglob("*.csv"):
            try:
                with open(p, "r", encoding="utf-8-sig", newline="") as f:
                    head = f.readline().strip().lower()
            except Exception:
                continue
            if all(n in head for n in NEED):
                out.append(p)
    return sorted(set(out), key=lambda p: (-p.stat().st_mtime))

def main():
    dcp = DRAFTS / PROJ / "draft_content.json"
    if not dcp.exists():
        print("KHONG THAY %s" % dcp)
        return 1
    dc = load(dcp)
    mi = mat_index(dc)
    segs = main_track(dc).get("segments") or []

    js = []
    for i, s in enumerate(segs):
        ctype, blur, ntrans = "none", None, 0
        for r in (s.get("extra_material_refs") or []):
            e = mi.get(r)
            if not e:
                continue
            if e[0] == "canvases":
                ctype = e[1].get("type") or "?"
                if ctype == "canvas_blur":
                    blur = round(float(e[1].get("blur") or 0.0), 4)
            if e[0] == "transitions":
                ntrans += 1
        mat = (mi.get(s.get("material_id")) or (None, {}))[1]
        tr = s.get("target_timerange") or {}
        s0, s1 = kf_scales(s)
        js.append({"start": float(tr.get("start", 0)) / 1e6, "dur": float(tr.get("duration", 0)) / 1e6,
                   "ctype": ctype, "blur": blur, "ntrans": ntrans,
                   "img": Path(str(mat.get("path") or "")).name, "s0": s0, "s1": s1})

    cands = find_csvs()
    print("CSV ung vien:")
    for p in cands:
        print("   %s" % p)
    csvp = None
    for p in cands:
        with open(p, "r", encoding="utf-8-sig", newline="") as f:
            if sum(1 for _ in csv.DictReader(f)) == len(segs):
                csvp = p
                break
    if csvp is None:
        print("")
        print("KHONG THAY CSV nao co dung %d dong. Dung lai." % len(segs))
        return 1
    print("")
    print("dung CSV: %s" % csvp)
    with open(csvp, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    bad = {"start": [], "dur": [], "blur": [], "img": [], "kb": []}
    for i, (r, j) in enumerate(zip(rows, js)):
        n = i + 1
        cs, cd = float(r["start_s"]), float(r["dur_s"])
        if abs(cs - j["start"]) > 0.0005:
            bad["start"].append((n, cs, j["start"]))
        if abs(cd - j["dur"]) > 0.0005:
            bad["dur"].append((n, cd, j["dur"]))
        lv = int(float(r["blur"] or 0))
        exp = LEVELS.get(lv, "??")
        got = j["blur"]
        if (exp is None) != (got is None) or (exp is not None and got is not None and abs(exp - got) > 1e-6):
            bad["blur"].append((n, lv, exp, got, j["ctype"]))
        if r["image"].strip() and Path(r["image"].strip()).name != j["img"]:
            bad["img"].append((n, r["image"], j["img"]))
        try:
            k0, k1 = float(r["kb_s0"]), float(r["kb_s1"])
            if j["s0"] is None or abs(k0 - j["s0"]) > 1e-4 or abs(k1 - j["s1"]) > 1e-4:
                bad["kb"].append((n, k0, k1, j["s0"], j["s1"]))
        except (KeyError, TypeError, ValueError):
            pass

    print("")
    print("rows CSV = %d, segments JSON = %d" % (len(rows), len(segs)))
    for k in ["start", "dur", "blur", "img", "kb"]:
        print("  lech %-6s : %d" % (k, len(bad[k])))
        for t in bad[k][:5]:
            print("      %s" % (t,))

    nb_csv = sum(1 for r in rows if int(float(r["blur"] or 0)) > 0)
    nb_json = sum(1 for j in js if j["ctype"] == "canvas_blur")
    ntr_csv = sum(1 for r in rows if str(r["transition"]).strip() not in ("", "0", "none", "None"))
    ntr_json = sum(j["ntrans"] for j in js)
    print("")
    print("shot co blur : CSV %d / JSON %d" % (nb_csv, nb_json))
    print("transition   : CSV %d / JSON %d" % (ntr_csv, ntr_json))
    print("")
    print("mau xen ke, B = co blur, dau cham = canvas_color")
    for off in range(0, len(js), 50):
        a = "".join("B" if j["ctype"] == "canvas_blur" else "." for j in js[off:off + 50])
        b = "".join("B" if int(float(rows[k]["blur"] or 0)) > 0 else "." for k in range(off, min(off + 50, len(rows))))
        print("  shot %3d  JSON %s" % (off + 1, a))
        print("            CSV  %s" % b)
    return 0

if __name__ == "__main__":
    sys.exit(main())