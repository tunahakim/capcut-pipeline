"""shots_crosscheck.py
Đối chiếu shots.csv với draft_content.json trên năm trường: start, duration, mức blur quy đổi từ level 0 tới 4, tên ảnh, và cặp keyframe scale đầu cuối; đầu báo cáo in draft_fold_path, tên ảnh của shot 1 ở cả hai phía và kết quả so kích thước bản draft_content.json lồng trong Timelines với bản gốc; cuối báo cáo in số shot có blur, số transition ở hai bên và bản đồ xen kẽ theo khối 50 shot.
Vào: bắt buộc --project là tên project trong thư mục draft của CapCut hoặc đường dẫn đầy đủ tới thư mục project, và --csv là đường dẫn đầy đủ tới bảng shot; không còn cơ chế tự dò. Ra: chỉ in console.
Mã thoát 0 khi cả năm trường sạch; 2 khi chạy xong nhưng có lệch, hoặc số dòng không khớp số segment, hoặc thiếu cặp cột kb_s0 và kb_s1 nên trường thứ năm không được kiểm; 1 khi sai tham số hoặc thiếu file.
Ví dụ: python tools/shots_crosscheck.py --project prod60 --csv D:/IT/capcut-lab/data/prod60/shots.csv
[KIEM: chua]
"""

import argparse, csv, json, os, sys
from pathlib import Path

DRAFTS = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
LEVELS = {0: None, 1: 0.0625, 2: 0.375, 3: 0.75, 4: 1.0}
NEED = ["image", "start_s", "dur_s", "transition", "blur"]
KBCOLS = ["kb_s0", "kb_s1"]

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

def resolve_project(val):
    p = Path(val)
    if p.is_dir():
        return p
    p2 = DRAFTS / val
    if p2.is_dir():
        return p2
    print("KHONG THAY PROJECT: %s" % val)
    print("  da thu: %s" % p)
    print("  da thu: %s" % p2)
    if DRAFTS.is_dir():
        names = sorted(d.name for d in DRAFTS.iterdir() if d.is_dir())
        print("  project dang co: %s" % ", ".join(names))
    return None


def fold_path(pdir):
    mp = pdir / "draft_meta_info.json"
    if not mp.is_file():
        return "KHONG CO draft_meta_info.json"
    try:
        m = load(mp)
    except Exception as e:
        return "DOC LOI draft_meta_info.json: %s" % e
    v = m.get("draft_fold_path")
    if not v:
        return "draft_meta_info.json KHONG CO khoa draft_fold_path"
    return str(v)


def nested_report(pdir, root_size):
    tl = pdir / "Timelines"
    if not tl.is_dir():
        return "khong co thu muc Timelines"
    ns = sorted(tl.rglob("draft_content.json"))
    if not ns:
        return "Timelines khong chua draft_content.json"
    out = []
    for n in ns:
        sz = n.stat().st_size
        tag = "trung kich thuoc ban goc" if sz == root_size else "CANH BAO LECH KICH THUOC"
        out.append("%s %d byte %s" % (n.parent.name, sz, tag))
    return " | ".join(out)


class ArgParser(argparse.ArgumentParser):
    """Thoat bang 1 khi sai tham so, de danh ma 2 cho ca chay xong nhung du lieu co van de."""

    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write("%s: loi tham so: %s\n" % (self.prog, message))
        raise SystemExit(1)


def main():
    ap = ArgParser(description="Doi chieu shots.csv voi draft_content.json. Khong tu do, phai chi ro project va csv.")
    ap.add_argument("--project", required=True, help="ten project trong thu muc draft cua CapCut, hoac duong dan day du toi thu muc project")
    ap.add_argument("--csv", required=True, help="duong dan day du toi bang shot")
    args = ap.parse_args()

    pdir = resolve_project(args.project)
    if pdir is None:
        return 1
    dcp = pdir / "draft_content.json"
    if not dcp.is_file():
        print("KHONG THAY %s" % dcp)
        return 1
    csvp = Path(args.csv)
    if not csvp.is_file():
        print("KHONG THAY CSV: %s" % csvp)
        return 1

    rsz = dcp.stat().st_size
    print("=== DAU BAO CAO ===")
    print("project dir     : %s" % pdir)
    print("draft_fold_path : %s" % fold_path(pdir))
    print("draft_content   : %d byte" % rsz)
    print("ban long        : %s" % nested_report(pdir, rsz))
    print("csv             : %s" % csvp)

    dc = load(dcp)
    mi = mat_index(dc)
    tr0 = main_track(dc)
    if tr0 is None:
        print("KHONG CO TRACK VIDEO nao trong %s" % dcp)
        return 1
    segs = tr0.get("segments") or []

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

    print("shot 1 anh JSON : %s" % (js[0]["img"] if js else "(khong co segment)"))

    with open(csvp, "r", encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        cols = [c.strip() for c in (rd.fieldnames or [])]
        rows = list(rd)
    if rows:
        print("shot 1 anh CSV  : %s" % rows[0].get("image", "(khong co cot image)"))
    else:
        print("shot 1 anh CSV  : (csv rong)")
    print("cot CSV         : %s" % ", ".join(cols))
    print("")

    miss = [c for c in NEED if c not in cols]
    if miss:
        print("THIEU COT BAT BUOC: %s" % ", ".join(miss))
        print("Dung lai, khong doi chieu.")
        return 1
    has_kb = all(c in cols for c in KBCOLS)
    mismatch = len(rows) != len(segs)
    if mismatch:
        print("SO DONG KHONG KHOP: CSV %d dong, JSON %d segment, chi doi chieu %d muc dau"
              % (len(rows), len(segs), min(len(rows), len(segs))))

    bad = {"start": [], "dur": [], "blur": [], "img": [], "kb": []}
    for i, (r, j) in enumerate(zip(rows, js)):
        n = i + 1
        cs, cd = float(r["start_s"]), float(r["dur_s"])
        if abs(cs - j["start"]) > 0.0005:
            bad["start"].append((n, cs, j["start"]))
        if abs(cd - j["dur"]) > 0.0005:
            bad["dur"].append((n, cd, j["dur"]))
        lv = int(float(r["blur"] or 0))
        got = j["blur"]
        if lv not in LEVELS:
            bad["blur"].append((n, lv, "MUC BLUR NGOAI THANG 0..4", got, j["ctype"]))
        else:
            exp = LEVELS[lv]
            if (exp is None) != (got is None) or (exp is not None and got is not None and abs(exp - got) > 1e-6):
                bad["blur"].append((n, lv, exp, got, j["ctype"]))
        if r["image"].strip() and Path(r["image"].strip()).name != j["img"]:
            bad["img"].append((n, r["image"], j["img"]))
        if has_kb:
            try:
                k0, k1 = float(r["kb_s0"]), float(r["kb_s1"])
            except (TypeError, ValueError):
                bad["kb"].append((n, r.get("kb_s0"), r.get("kb_s1"), "GIA TRI KHONG DOC DUOC", ""))
            else:
                if j["s0"] is None or abs(k0 - j["s0"]) > 1e-4 or abs(k1 - j["s1"]) > 1e-4:
                    bad["kb"].append((n, k0, k1, j["s0"], j["s1"]))

    print("")
    print("rows CSV = %d, segments JSON = %d" % (len(rows), len(segs)))
    for k in ["start", "dur", "blur", "img", "kb"]:
        if k == "kb" and not has_kb:
            print("  lech kb     : KHONG CO COT kb_s0 va kb_s1, truong thu nam KHONG duoc kiem")
            continue
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

    nlech = sum(len(v) for v in bad.values())
    print("")
    if nlech == 0 and has_kb and not mismatch:
        print("KET LUAN: SACH, 0 lech tren ca nam truong")
        return 0
    if nlech:
        print("KET LUAN: CO LECH, tong %d" % nlech)
    if not has_kb:
        print("KET LUAN: thieu cot kb, chua du can cu tuyen bo sach")
    if mismatch:
        print("KET LUAN: so dong CSV khac so segment JSON")
    return 2

if __name__ == "__main__":
    sys.exit(main())