"""shots_dump.py - đọc ngược draft_content.json ra shots.csv với cột giống bảng shot đầu vào, gồm idx, image, start_s, dur_s, transition, blur, thêm kb_s0 và kb_s1 khi mọi segment đều có keyframe KFTypeScaleX.
Dùng chung hàm với tools/shots_crosscheck.py là mat_index, main_track, kf_scales và LEVELS, nên bản dump đưa ngược vào crosscheck phải sạch.
Cảnh báo hai mức khi có thứ không thuộc bảng shot: CANH BAO cho thứ mất hẳn và cho bucket materials lạ, GHI CHU cho thứ đã biết là không thuộc bảng; script này KHÔNG giữ được hiệu ứng thả tay từ GUI.
Vào: bắt buộc --project là tên project trong thư mục draft của CapCut hoặc đường dẫn đầy đủ, và --out là đường dẫn file CSV ra, không tự đoán.
Mã thoát 0 khi đã ghi hoặc file ra đã có và giống hệt; 2 khi file ra đã có và khác, khi đó KHÔNG ghi đè trừ phi thêm --force; 1 khi sai tham số hoặc thiếu file.
[KIEM: bo test]
"""

import csv, io, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shots_crosscheck as sc

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = ["idx", "image", "start_s", "dur_s", "transition", "blur"]
KB = ["kb_s0", "kb_s1"]

# CSV nay chi giu: track video dau tien, canvas va muc blur, so transition, keyframe scale.
# Moi thu khac trong draft deu khong di vao CSV. Hai danh sach duoi khai tuong minh cai gi
# duoc coi la mat da biet (GHI CHU) va cai gi phai bao dong (CANH BAO); bucket khong nam
# trong hai danh sach thi mac dinh la CANH BAO, de tinh nang moi cua CapCut khong lot im lang.
MAT_STRUCT = ("canvases", "loudnesses", "material_colors", "placeholder_infos",
              "sound_channel_mappings", "speeds", "videos", "vocal_separations",
              "transitions")
MAT_NOTE = ("audios", "material_animations")


def losses(dc):
    """Tra ve (canh_bao, ghi_chu): thu bi mat khi dump draft ra CSV."""
    warn, note = [], []
    tracks = dc.get("tracks") or []
    for i, t in enumerate(tracks):
        if i == 0:
            continue
        ty = str(t.get("type"))
        n = len(t.get("segments") or [])
        if ty == "audio":
            note.append("track %d type=audio, %d segment: khong thuoc bang shot" % (i, n))
        elif ty == "video":
            warn.append("track %d type=video, %d segment: track video phu, CSV chi doc track dau tien" % (i, n))
        else:
            warn.append("track %d type=%s, %d segment: MAT HAN khoi CSV" % (i, ty, n))
    mats = dc.get("materials") or {}
    for k in sorted(mats.keys()):
        v = mats.get(k)
        if not isinstance(v, list) or not v:
            continue
        if k in MAT_STRUCT:
            continue
        ten = []
        for e in v[:4]:
            if isinstance(e, dict):
                ten.append(str(e.get("name") or e.get("type") or "?"))
        mo = (" -- " + ", ".join(ten)) if ten else ""
        if k in MAT_NOTE:
            note.append("materials.%s co %d muc: khong thuoc bang shot%s" % (k, len(v), mo))
        else:
            warn.append("materials.%s co %d muc: MAT HAN khoi CSV%s" % (k, len(v), mo))
    return warn, note


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
    lost_w, lost_n = losses(dc)
    for m in lost_n:
        print("GHI CHU : %s" % m)
    for m in lost_w:
        print("CANH BAO: %s" % m)
    if lost_w:
        print("=> %d muc tren KHONG co trong CSV. Dung ban dump nay de dung lai project la mat chung." % len(lost_w))
    else:
        print("mat mat         : khong co muc nao phai canh bao")
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
