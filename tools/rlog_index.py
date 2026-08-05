#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/rlog_index.py -- sinh bảng mục lục docs/research-log/INDEX.md từ hai dòng khai của từng file nhật ký, cộng một lượt chèn ngược hai dòng đó vào các file cũ.

  python tools/rlog_index.py                       # chạy thử chế độ sinh bảng
  python tools/rlog_index.py --apply               # ghi lại bảng của INDEX.md
  python tools/rlog_index.py --backfill            # chạy thử chế độ chèn ngược
  python tools/rlog_index.py --backfill --apply    # ghi thật vào các file nhật ký
  python tools/rlog_index.py --selftest            # tự kiểm trên thư mục nhật ký giả

Nguồn sự thật là hai dòng nằm ngay dưới tiêu đề H1 của từng file nhật ký: dòng khai SUMMARY_KEY mang một câu tóm tắt, và dòng khai PHIEN_KEY mang giờ cùng buổi của phiên, ví dụ 23:13 khuya.
Hai hằng số đó CÓ DẤU và so khớp NGUYÊN VĂN bằng startswith, nên viết không dấu là tool không thấy dòng dù dòng có mặt; đó là lỗi đã mất bốn lượt để tìm ra ngày 05/08/2026, nên nhánh không tìm thấy nay tự quét lại bằng hai bậc so khớp bỏ dấu rồi in số dòng cùng ascii của dòng gần giống.
Ngày và số thứ tự phiên suy TỪ TÊN FILE chứ không gõ tay, còn buổi đọc từ dòng khai, rồi ghép thành cột Phiên dạng 04/08-4 khuya; buổi là trường tự do nên chấp nhận cả dòng không có buổi, nhãn phiên bản kiểu (v5), lẫn buổi viết dài kiểu tối muộn. Giờ cố ý KHÔNG lên bảng, nó chỉ nằm trong file, vì bảng là thứ đã chật.
File chưa có dòng khai thì giữ nguyên ô cũ đọc từ bảng hiện có và in GIU O CU, nên bảng vẫn là nguồn dự phòng cho tới khi lượt chèn ngược chạy xong. Chỉ phần bảng bị ghi lại, đoạn mở đầu phía trên và mọi thứ phía dưới giữ nguyên, và dòng nào đã nằm trong INDEX-archive.md thì bỏ qua chứ không hồi sinh.
Chế độ chèn ngược chỉ THÊM tối đa hai dòng dưới H1, không sửa thân bài, và tự đối chiếu số byte với trần nhập từ tools/docs_audit.py; giờ chỉ được điền khi ngày tạo file trùng ngày trong tên file, vì file chép hoặc clone mang ngày của lần chép chứ không phải ngày viết, và lệch thì để trống chứ không bịa.
Biến môi trường RLOG_DIR trỏ tool sang một thư mục nhật ký khác, chỉ dùng cho phép tự kiểm.
[KIEM: du lieu that]
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_audit as da

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = da.REPO
RLOG = Path(os.environ.get("RLOG_DIR") or (REPO / "docs" / "research-log"))
IDX = RLOG / "INDEX.md"
ARC = RLOG / "INDEX-archive.md"
SUMMARY_KEY = "**Tóm tắt:**"
PHIEN_KEY = "**Phiên:**"
FN_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(\d+)-")


def read_doc(path):
    raw = path.read_bytes()
    if raw[:3] == b"\xef\xbb\xbf":
        sys.exit("BOM: %s" % path)
    text = raw.decode("utf-8")
    crlf = text.count("\r\n")
    lone = text.replace("\r\n", "").count("\n")
    if crlf and lone:
        sys.exit("LAN XUONG DONG: %s (CRLF %d, LF %d)" % (path, crlf, lone))
    return raw, ("\r\n" if crlf else "\n"), text.replace("\r\n", "\n")


def parse_table(text, label):
    """Tra ve (prefix, head, rows, suffix). rows la list (phien, fname, tom_tat)."""
    lines = text.split("\n")
    starts = [i for i, ln in enumerate(lines) if ln.startswith("|")]
    if not starts:
        return lines, [], [], []
    ts = starts[0]
    te = ts
    while te + 1 < len(lines) and lines[te + 1].startswith("|"):
        te += 1
    extra = [i for i in starts if i > te]
    if extra:
        sys.exit("%s: co bang thu hai o dong %d, tool chi xu ly mot bang"
                 % (label, extra[0] + 1))
    head, rows = [], []
    for ln in lines[ts:te + 1]:
        parts = ln.split("|")
        if len(parts) < 5 or ln.startswith("|---") or parts[2].strip() == "File":
            head.append(ln)
            continue
        fname = parts[2].strip().strip("`")
        rows.append((parts[1].strip(), fname, "|".join(parts[3:-1]).strip()))
    return lines[:ts], head, rows, lines[te + 1:]


def journal_files():
    out = []
    for p in sorted(RLOG.glob("*.md")):
        if p.name.startswith("INDEX"):
            continue
        if not FN_RE.match(p.name):
            print("BO QUA %s (ten khong theo khuon <ngay>-<so>-<nhan>.md)" % p.name)
            continue
        out.append(p.name)
    return out


def sort_key(fname):
    m = FN_RE.match(fname)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))


def phien_of(fname):
    m = FN_RE.match(fname)
    return "%s/%s-%s" % (m.group(3), m.group(2), int(m.group(4)))


GIO_RE = re.compile(r"^(\d{1,2}:\d{2})\s*(.*)$")
O_PHIEN_RE = re.compile(r"^\s*(\d{1,2}/\d{1,2})(?:-(\d+))?\s*(.*)$")


def khong_dau(s):
    """Bỏ dấu tiếng Việt và hạ chữ thường, dùng cho phép so khớp lỏng ở bước chẩn đoán chứ không dùng để nhận dòng khai."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


def rut_gon(s):
    """Chỉ giữ chữ và số của một chuỗi đã bỏ dấu, là bậc so khớp lỏng nhất khi cả phép bỏ dấu cũng trượt."""
    return re.sub(r"[^a-z0-9]", "", khong_dau(s))


def gia_tri_dong_khai(text, key):
    """Trả về phần nguyên văn nằm sau một khoá khai, hoặc None khi không dòng nào bắt đầu đúng bằng khoá đó."""
    for ln in text.split("\n"):
        if ln.startswith(key):
            return ln[len(key):].strip()
    return None


def chan_doan_khoa(text, key, nhan):
    """In chẩn đoán khi không tìm thấy dòng khai, vì nguyên nhân thường gặp nhất là khoá bị viết không dấu chứ không phải thiếu dòng."""
    kd, rg = khong_dau(key), rut_gon(key)
    for i, ln in enumerate(text.split("\n"), 1):
        s = ln.strip()
        if not s:
            continue
        if khong_dau(s).startswith(kd) or rut_gon(s).startswith(rg):
            print("    chan doan %s: dong %d la %s" % (nhan, i, ascii(s[:90])))
            print("    co dong gan giong nhung khong dung nguyen van, nhieu kha nang "
                  "thieu dau -- khoa dung la %s" % ascii(key))
            return True
    print("    chan doan %s: khong co dong nao gan giong khoa %s" % (nhan, ascii(key)))
    return False


def summary_in_file(text):
    return gia_tri_dong_khai(text, SUMMARY_KEY)


def tach_gio_buoi(gia_tri):
    """Tách giá trị của dòng khai Phiên thành cặp giờ và buổi; giờ để trống khi dòng chỉ khai buổi."""
    m = GIO_RE.match((gia_tri or "").strip())
    if m:
        return m.group(1), m.group(2).strip()
    return "", (gia_tri or "").strip()


def buoi_tu_o(o):
    """Lấy phần buổi từ một ô Phiên của bảng cũ, chấp nhận cả 28/07, 29/07 (v5), 31/07 tối muộn lẫn khuôn mới 04/08-4 khuya."""
    m = O_PHIEN_RE.match(o or "")
    return m.group(3).strip() if m else ""


def gio_tu_ctime(p, fname):
    """Trả về giờ tạo file dạng HH:MM, nhưng chỉ khi ngày tạo trùng ngày trong tên file, vì mọi trường hợp lệch đều là dấu vết của lần chép chứ không phải lần viết."""
    m = FN_RE.match(fname)
    d = datetime.datetime.fromtimestamp(p.stat().st_ctime)
    if (d.year, d.month, d.day) != (int(m.group(1)), int(m.group(2)),
                                    int(m.group(3))):
        return ""
    return d.strftime("%H:%M")


def old_cells():
    """Ban do fname -> (phien_cu, tom_tat_cu) tu INDEX.md va INDEX-archive.md."""
    cells, arch = {}, set()
    _, _, t = read_doc(IDX)
    for phien, fname, summ in parse_table(t, "INDEX.md")[2]:
        cells[fname] = (phien, summ)
    n_arc = 0
    if ARC.is_file():
        _, _, ta = read_doc(ARC)
        rows = parse_table(ta, "INDEX-archive.md")[2]
        n_arc = len(rows)
        for phien, fname, summ in rows:
            cells.setdefault(fname, (phien, summ))
            arch.add(fname)
    return cells, arch, n_arc


def budget_of(rel):
    return da.PER_FILE_BUDGET.get(rel, da.BUDGET)


def gen_index(apply_it):
    cells, arch, n_arc = old_cells()
    raw, nl, text = read_doc(IDX)
    prefix, head, old_rows, suffix = parse_table(text, "INDEX.md")
    files = journal_files()
    print("=== NGUON ===")
    print("file nhat ky            : %d" % len(files))
    print("dong trong INDEX.md     : %d" % len(old_rows))
    print("dong trong INDEX-archive: %d" % n_arc)
    print("")

    rows, giu, giu_buoi, thieu = [], 0, 0, []
    for fname in sorted(files, key=sort_key, reverse=True):
        if fname in arch:
            print("TRONG LUU TRU %s" % fname)
            continue
        _, _, ft = read_doc(RLOG / fname)
        got = cells.get(fname)
        s = summary_in_file(ft)
        if s:
            src = "file  "
        else:
            if not got:
                print("THIEU TOM TAT %s" % fname)
                chan_doan_khoa(ft, SUMMARY_KEY, "tom tat")
                thieu.append(fname)
                continue
            s = got[1]
            src = "GIU O CU"
            giu += 1
        pv = gia_tri_dong_khai(ft, PHIEN_KEY)
        if pv is None:
            buoi = buoi_tu_o(got[0]) if got else ""
            if buoi:
                giu_buoi += 1
        else:
            buoi = tach_gio_buoi(pv)[1]
        phien = phien_of(fname) + ((" " + buoi) if buoi else "")
        rows.append((phien, fname, s))
        print("%-18s %-9s %s" % (phien, src, fname))

    print("")
    if thieu:
        print("=== THIEU TOM TAT (%d) -- KHONG GHI ===" % len(thieu))
        for f in thieu:
            print("  %s: khong co dong tom tat va khong co o cu trong bang" % f)
        return 2

    doi = [(p, f) for p, f, _ in rows if cells.get(f) and cells[f][0] != p]
    print("dong lay tu file        : %d" % (len(rows) - giu))
    print("dong GIU O CU tom tat   : %d" % giu)
    print("dong GIU O CU buoi      : %d" % giu_buoi)
    print("dong doi cot Phien      : %d" % len(doi))
    for p, f in doi[:4]:
        print("  %-24s %-14s -> %s" % (f, cells[f][0], p))
    if len(doi) > 4:
        print("  ... va %d dong nua" % (len(doi) - 4))

    body = ["| %s | `%s` | %s |" % (p, f, s) for p, f, s in rows]
    new_text = "\n".join(prefix + head + body + suffix)
    nbyte = len(new_text.replace("\n", nl).encode("utf-8"))
    cap = budget_of("docs/research-log/INDEX.md")
    print("")
    print("byte: %d -> %d (tran %d)" % (len(raw), nbyte, cap))
    if nbyte > cap:
        print("=== VUOT TRAN -- KHONG GHI ===")
        return 2
    if not apply_it:
        print("=== CHAY THU, KHONG GHI GI (them --apply de ghi) ===")
        return 0
    IDX.write_bytes(new_text.replace("\n", nl).encode("utf-8"))
    _, _, back = read_doc(IDX)
    got = parse_table(back, "INDEX.md")[2]
    ok = len(got) == len(rows) and all(g[1] == r[1] and g[2] == r[2]
                                       for g, r in zip(got, rows))
    print("KIEM SAU: %s (%d dong doc lai)" % ("OK" if ok else "THAT BAI", len(got)))
    return 0 if ok else 3


def backfill(apply_it):
    cells, arch, n_arc = old_cells()
    files = journal_files()
    print("=== CHEN NGUOC DONG TOM TAT VA DONG PHIEN VAO FILE NHAT KY ===")
    print("file nhat ky: %d | dong INDEX-archive: %d" % (len(files), n_arc))
    print("")
    plan, thieu, lech, over = [], [], [], []
    n_tt, n_ph, n_khong_gio = 0, 0, 0
    for fname in sorted(files, key=sort_key):
        p = RLOG / fname
        raw, nl, text = read_doc(p)
        cur_tt = summary_in_file(text)
        cur_ph = gia_tri_dong_khai(text, PHIEN_KEY)
        got = cells.get(fname)
        if cur_tt is None and not got:
            thieu.append(fname)
            print("THIEU    %-42s khong co dong tom tat va khong co o cu" % fname)
            chan_doan_khoa(text, SUMMARY_KEY, "tom tat")
            continue
        if cur_tt is not None and got and got[1] != cur_tt:
            lech.append(fname)
        if cur_tt is not None and cur_ph is not None:
            print("CO SAN   %-42s %s"
                  % (fname, "khop bang" if got and got[1] == cur_tt
                     else ("LECH BANG" if got else "khong co o cu")))
            continue
        lines = text.split("\n")
        h1 = next((i for i, ln in enumerate(lines) if ln.startswith("# ")), None)
        if h1 is None:
            thieu.append(fname)
            print("THIEU    %-42s khong tim thay tieu de H1" % fname)
            continue
        them = []
        if cur_tt is None:
            them.append("%s %s" % (SUMMARY_KEY, got[1]))
            n_tt += 1
        gio = ""
        if cur_ph is None:
            gio = gio_tu_ctime(p, fname)
            buoi = buoi_tu_o(got[0]) if got else ""
            them.append(("%s %s %s" % (PHIEN_KEY, gio, buoi)).replace("  ", " ").strip())
            n_ph += 1
            if not gio:
                n_khong_gio += 1
        if cur_tt is None:
            neo, ins = h1, [""] + them
        else:
            neo = next(i for i, ln in enumerate(lines)
                       if ln.startswith(SUMMARY_KEY))
            ins = list(them)
        if neo + 1 < len(lines) and lines[neo + 1].strip() != "":
            ins = ins + [""]
        new_text = "\n".join(lines[:neo + 1] + ins + lines[neo + 1:])
        nbyte = len(new_text.replace("\n", nl).encode("utf-8"))
        cap = budget_of("docs/research-log/%s" % fname)
        flag = ""
        if nbyte > cap:
            over.append(fname)
            flag = " VUOT TRAN %d" % cap
        print("CHEN     %-42s %d -> %d byte, them %d dong, gio %s%s"
              % (fname, len(raw), nbyte, len(them), gio or "TRONG", flag))
        plan.append((p, new_text, nl, them))

    print("")
    print("can chen: %d | dong tom tat: %d | dong phien: %d | khong doan duoc gio: %d"
          % (len(plan), n_tt, n_ph, n_khong_gio))
    print("thieu o cu: %d | lech bang: %d | vuot tran: %d"
          % (len(thieu), len(lech), len(over)))
    if thieu or over:
        print("=== CO VAN DE -- KHONG GHI FILE NAO ===")
        return 2
    if not apply_it:
        print("=== CHAY THU, KHONG GHI GI (them --apply de ghi) ===")
        return 0
    bad = []
    for p, new_text, nl, them in plan:
        p.write_bytes(new_text.replace("\n", nl).encode("utf-8"))
        _, _, back = read_doc(p)
        for dong in them:
            if dong not in back.split("\n"):
                bad.append("%s / %s" % (p.name, ascii(dong[:40])))
    print("KIEM SAU: %d/%d file co du dong khai dung nguyen van"
          % (len(plan) - len({x.split(" / ")[0] for x in bad}), len(plan)))
    for f in bad:
        print("  THAT BAI %s" % f)
    return 3 if bad else 0


def _viet(p, text):
    p.write_text(text, encoding="utf-8", newline="\n")


def _dung_thu_muc(goc, ten, dong_bang, ho_so):
    """Dựng một thư mục nhật ký giả gồm INDEX.md và vài file nhật ký, để phép tự kiểm không đụng tới thư mục thật."""
    d = goc / ten
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.md"):
        f.unlink()
    bang = ["# INDEX thu nghiem", "", "| Phiên | File | Tóm tắt |", "|---|---|---|"]
    _viet(d / "INDEX.md", "\n".join(bang + dong_bang) + "\n")
    for ten_f, than in ho_so:
        _viet(d / ten_f, than)
    return d


def selftest():
    """Chạy chính tool này trên thư mục nhật ký giả qua biến môi trường RLOG_DIR, với một ca dương và ba ca âm, trong đó ca cuối là tiêu chí xong đã tự động hoá: xoá một dòng khỏi bảng rồi chạy tool thì dòng đó phải hiện lại đúng nguyên văn."""
    day = datetime.datetime.now().strftime("%Y%m%d")
    goc = da.LAB / "tmp" / ("tmp_%s_rlog_selftest" % day)
    me = str(Path(__file__).resolve())
    A = "2026-07-28-1-alpha.md"
    B = "2026-08-04-4-beta.md"
    du = ("# Phien %s\n\n**Tóm tắt:** tom tat trong file cua %s.\n"
          "**Phiên:** 23:13 khuya\n\nThan bai.\n")
    cases = []
    d1 = _dung_thu_muc(goc, "duong",
                       ["| 28/07-1 khuya | `%s` | tom tat cu A |" % A,
                        "| 04/08-4 khuya | `%s` | tom tat cu B |" % B],
                       [(A, du % ("A", "A")), (B, du % ("B", "B"))])
    cases.append(("sinh-duong", d1, [], 0, "CHAY THU"))
    d2 = _dung_thu_muc(goc, "ttkhongdau", [],
                       [(A, "# Phien A\n\n**Tom tat:** thieu dau nen tool khong "
                            "thay.\n\nThan bai.\n")])
    cases.append(("tom-tat-thieu-dau", d2, [], 2, "nhieu kha nang thieu dau"))
    d3 = _dung_thu_muc(goc, "phienkhongdau",
                       ["| 28/07 tối muộn | `%s` | tom tat cu A |" % A],
                       [(A, "# Phien A\n\n**Tóm tắt:** co dau nen tool thay.\n"
                            "**Phien:** 23:13 khuya\n\nThan bai.\n")])
    cases.append(("phien-thieu-dau-lay-o-cu", d3, [], 0, "28/07-1 tối muộn"))
    d4 = _dung_thu_muc(goc, "khoiphuc",
                       ["| 04/08-4 khuya | `%s` | tom tat cu B |" % B],
                       [(A, du % ("A", "A")), (B, du % ("B", "B"))])
    cases.append(("khoi-phuc-dong-da-xoa", d4, ["--apply"], 0, "KIEM SAU: OK"))

    rows = []
    for ten, d, args, want, nhan in cases:
        moi = dict(os.environ)
        moi["RLOG_DIR"] = str(d)
        r = subprocess.run([sys.executable, me] + args, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", env=moi)
        rows.append((ten, want, r.returncode, nhan, nhan in (r.stdout or "")))
    mong = "| 28/07-1 khuya | `%s` | tom tat trong file cua A. |" % A
    sau = (d4 / "INDEX.md").read_text(encoding="utf-8")
    rows.append(("dong-hien-lai-nguyen-van", 0, 0 if mong in sau else 1,
                 "dong 28/07-1 nguyen van", mong in sau))

    print("")
    print("=== SELFTEST rlog_index ===")
    print("thu muc nhat ky gia: %s" % goc)
    print("%-26s %5s %5s %-26s %s"
          % ("CA", "MONG", "THAT", "NHAN MONG DOI", "CO NHAN"))
    print("%-26s %5s %5s %-26s %s"
          % ("-" * 26, "-----", "-----", "-" * 26, "-------"))
    bad = 0
    for ten, want, got, nhan, hit in rows:
        okc = (want == got) and hit
        if not okc:
            bad += 1
        print("%-26s %5d %5d %-26s %s  %s"
              % (ten, want, got, nhan[:26], "co" if hit else "KHONG",
                 "OK" if okc else "THAT BAI"))
    print("")
    print("KET QUA: %d/%d ca dat" % (len(rows) - bad, len(rows)))
    return 0 if bad == 0 else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return backfill(a.apply) if a.backfill else gen_index(a.apply)


if __name__ == "__main__":
    sys.exit(main())