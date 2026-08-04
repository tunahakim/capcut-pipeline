"""shots_dump.py
Doc nguoc draft_content.json ra shots.csv voi cot giong bang shot dau vao: idx, image, start_s, dur_s, transition, blur, them kb_s0 va kb_s1 khi moi segment deu co keyframe KFTypeScaleX. Dung chung ham voi shots_crosscheck.py (mat_index, main_track, kf_scales, LEVELS) nen ban dump dua nguoc vao crosscheck phai sach.
Vao: bat buoc --project la ten project trong thu muc draft cua CapCut hoac duong dan day du, va --out la duong dan file CSV ra; khong tu do.
Ma thoat 0 khi da ghi hoac file ra da co va giong het; 2 khi file ra da co va khac, khi do KHONG ghi de tru phi them --force; 1 khi sai tham so hoac thieu file.
Vi du: python tools/shots_dump.py --project testV3 --out D:/IT/capcut-lab/data/tmp/shots_testV3.csv
[KIEM: bo test]
"""

import csv, io, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shots_crosscheck as sc

BASE = ["idx", "image", "start_s", "dur_s", "transition", "blur"]
KB = ["kb_s0", "kb_s1"]


def lvl(blur):
    for k, v in sc.LEVELS.items():
        if v is None and blur is None:
            return k
        if v is not None and blur is not None and abs(v - blur) < 1e-6:
            return k
    return None


def build_rows(dc):
    mi = sc.mat_index(dc)
    tr0 = sc.main_track(dc)
    if tr0 is None:
        return None, 0, ["KHONG CO TRACK VIDEO"]
    rows, nokb, warn = [], 0, []
    for i, s in enumerate(tr0.get("segments") or []):
        ctype, blur, ntrans = "none", None, 0
        for r in (s.get("extra_material_refs") or []):
            e = mi.get(r)
            if not e:
                continue
            if e[0] == "canvases":
                ctype = e[1].get("type") or "?"
                if ctype == "canvas_blur":
                    blur = e[1].get("blur")
            if e[0] == "transitions":
                ntrans += 1
        mat = (mi.get(s.get("material_id")) or (None, {}))[1]
        tr = s.get("target_timerange") or {}
        s0, s1 = sc.kf_scales(s)
        if s0 is None:
            nokb += 1
        lv = lvl(blur)
        if lv is None:
            warn.append("shot %d: blur %s khong khop thang LEVELS, ghi 0" % (i + 1, blur))
            lv = 0
        row = {"idx": i + 1,
               "image": Path(str(mat.get("path") or "")).name,
               "start_s": "%.6f" % ((tr.get("start") or 0) / 1e6),
               "dur_s": "%.6f" % ((tr.get("duration") or 0) / 1e6),
               "transition": ntrans,
               "blur": lv}
        if s0 is not None and s1 is not None:
            row["kb_s0"] = "%.6f" % s0
            row["kb_s1"] = "%.6f" % s1
        rows.append(row)
    return rows, nokb, warn


def to_csv(rows, cols):
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore", lineterminator=chr(10))
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def main():
    ap = sc.ArgParser(description="Doc nguoc draft_content.json ra shots.csv. Khong tu do.")
    ap.add_argument("--project", required=True, help="ten project trong thu muc draft, hoac duong dan day du")
    ap.add_argument("--out", required=True, help="duong dan day du file CSV ra")
    ap.add_argument("--force", action="store_true", help="ghi de khi file ra da co va khac")
    args = ap.parse_args()

    pdir = sc.resolve_project(args.project)
    if pdir is None or not Path(pdir).is_dir():
        print("KHONG THAY PROJECT: %s" % args.project)
        return 1
    pdir = Path(pdir)
    dcp = pdir / "draft_content.json"
    if not dcp.is_file():
        print("KHONG THAY %s" % dcp)
        return 1

    dc = sc.load(dcp)
    rows, nokb, warn = build_rows(dc)
    if rows is None:
        print("KHONG DUNG DUOC: %s" % "; ".join(warn))
        return 1
    if not rows:
        print("TRACK VIDEO KHONG CO SEGMENT")
        return 1

    has_kb = all(("kb_s0" in r) for r in rows)
    cols = BASE + (KB if has_kb else [])
    text = to_csv(rows, cols)

    print("project         : %s" % pdir)
    print("draft_content   : %d byte" % dcp.stat().st_size)
    print("ban long        : %s" % sc.nested_report(pdir, dcp.stat().st_size))
    print("segments        : %d" % len(rows))
    print("thieu keyframe  : %d segment" % nokb)
    print("cot ghi         : %s" % ", ".join(cols))
    if not has_kb:
        print("=> KHONG ghi cot kb; crosscheck se ra ma thoat 2 kem dong thieu cot, dung nhu thiet ke")
    for m in warn:
        print("CANH BAO: %s" % m)

    out = Path(args.out)
    if out.is_file():
        old = out.read_text(encoding="utf-8-sig")
        if old == text:
            print("FILE RA DA CO VA GIONG HET: %s" % out)
            return 0
        a, b = old.split(chr(10)), text.split(chr(10))
        nd = sum(1 for i in range(max(len(a), len(b)))
                 if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None))
        print("FILE RA DA CO VA KHAC: %s" % out)
        print("  cu %d dong, moi %d dong, %d dong lech" % (len(a), len(b), nd))
        for i in range(max(len(a), len(b))):
            x = a[i] if i < len(a) else "<<het file>>"
            y = b[i] if i < len(b) else "<<het file>>"
            if x != y:
                print("  dong %d cu : %s" % (i + 1, x[:90]))
                print("  dong %d moi: %s" % (i + 1, y[:90]))
                break
        if not args.force:
            print("KHONG ghi de. Them --force neu muon ghi de.")
            return 2
        print("--force: van ghi de.")

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(str(out), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("DA GHI: %s (%d byte, %d dong du lieu)" % (out, out.stat().st_size, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
