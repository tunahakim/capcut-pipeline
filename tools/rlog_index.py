#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/rlog_index.py -- sinh bang muc luc docs/research-log/INDEX.md tu dong Tom tat
cua tung file nhat ky, cong mot luot chen nguoc tom tat tu bang hien co vao cac file cu.

  python tools/rlog_index.py                       # chay thu che do sinh bang
  python tools/rlog_index.py --apply               # ghi lai bang cua INDEX.md
  python tools/rlog_index.py --backfill            # chay thu che do chen nguoc
  python tools/rlog_index.py --backfill --apply    # ghi that vao cac file nhat ky

Nguon su that la dong "**Tom tat:**" ngay duoi tieu de H1 cua tung file nhat ky. Ngay
va so phien suy TU TEN FILE chu khong go tay, cot Phien in dang 04/08-3. File chua co
dong tom tat thi giu nguyen o cu doc tu bang hien co va in GIU O CU. Chi phan bang bi
ghi lai; doan mo dau phia tren va moi thu phia duoi giu nguyen. Dong nao da nam trong
INDEX-archive.md thi bo qua, khong hoi sinh. Che do chen nguoc chi THEM mot dong duoi
H1, khong sua than bai, va tu doi chieu so byte voi tran nhap tu tools/docs_audit.py.

Luu y thu tu: tieu chi "xoa tay mot dong roi chay tool thi dong do hien lai" chi dat
duoc SAU khi chay --backfill, vi truoc do nguon duy nhat cua o tom tat chinh la bang.
[KIEM: chua]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_audit as da

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = da.REPO
RLOG = REPO / "docs" / "research-log"
IDX = RLOG / "INDEX.md"
ARC = RLOG / "INDEX-archive.md"
SUMMARY_KEY = "**Tóm tắt:**"
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


def summary_in_file(text):
    for ln in text.split("\n"):
        if ln.startswith(SUMMARY_KEY):
            return ln[len(SUMMARY_KEY):].strip()
    return None


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

    rows, giu, thieu = [], 0, []
    for fname in sorted(files, key=sort_key, reverse=True):
        if fname in arch:
            print("TRONG LUU TRU %s" % fname)
            continue
        _, _, ft = read_doc(RLOG / fname)
        s = summary_in_file(ft)
        if s:
            src = "file  "
        else:
            got = cells.get(fname)
            if not got:
                thieu.append(fname)
                continue
            s = got[1]
            src = "GIU O CU"
            giu += 1
        rows.append((phien_of(fname), fname, s))
        print("%-8s %-9s %s" % (phien_of(fname), src, fname))

    print("")
    if thieu:
        print("=== THIEU TOM TAT (%d) -- KHONG GHI ===" % len(thieu))
        for f in thieu:
            print("  %s: khong co dong tom tat va khong co o cu trong bang" % f)
        return 2

    doi = [(p, f) for p, f, _ in rows if cells.get(f) and cells[f][0] != p]
    print("dong lay tu file        : %d" % (len(rows) - giu))
    print("dong GIU O CU           : %d" % giu)
    print("dong doi cot Phien      : %d" % len(doi))
    for p, f in doi[:4]:
        print("  %-24s %-12s -> %s" % (f, cells[f][0], p))
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
    print("=== CHEN NGUOC TOM TAT VAO FILE NHAT KY ===")
    print("file nhat ky: %d | dong INDEX-archive: %d" % (len(files), n_arc))
    print("")
    plan, san, thieu, lech, over = [], [], [], [], []
    for fname in sorted(files, key=sort_key):
        p = RLOG / fname
        raw, nl, text = read_doc(p)
        cur = summary_in_file(text)
        got = cells.get(fname)
        if cur is not None:
            san.append(fname)
            if got and got[1] != cur:
                lech.append(fname)
            print("CO SAN   %-42s %s" % (fname, "khop bang" if got and got[1] == cur
                                          else "LECH BANG" if got else "khong co o cu"))
            continue
        if not got:
            thieu.append(fname)
            print("THIEU    %-42s khong co o cu trong bang" % fname)
            continue
        lines = text.split("\n")
        h1 = next((i for i, ln in enumerate(lines) if ln.startswith("# ")), None)
        if h1 is None:
            thieu.append(fname)
            print("THIEU    %-42s khong tim thay tieu de H1" % fname)
            continue
        ins = ["", "%s %s" % (SUMMARY_KEY, got[1])]
        if h1 + 1 < len(lines) and lines[h1 + 1].strip() != "":
            ins.append("")
        new_text = "\n".join(lines[:h1 + 1] + ins + lines[h1 + 1:])
        nbyte = len(new_text.replace("\n", nl).encode("utf-8"))
        cap = budget_of("docs/research-log/%s" % fname)
        flag = ""
        if nbyte > cap:
            over.append(fname)
            flag = " VUOT TRAN %d" % cap
        print("CHEN     %-42s %d -> %d byte%s" % (fname, len(raw), nbyte, flag))
        plan.append((p, new_text, nl, got[1]))

    print("")
    print("can chen: %d | co san: %d | thieu o cu: %d | lech bang: %d | vuot tran: %d"
          % (len(plan), len(san), len(thieu), len(lech), len(over)))
    if thieu or over:
        print("=== CO VAN DE -- KHONG GHI FILE NAO ===")
        return 2
    if not apply_it:
        print("=== CHAY THU, KHONG GHI GI (them --apply de ghi) ===")
        return 0
    bad = []
    for p, new_text, nl, s in plan:
        p.write_bytes(new_text.replace("\n", nl).encode("utf-8"))
        _, _, back = read_doc(p)
        if summary_in_file(back) != s:
            bad.append(p.name)
    print("KIEM SAU: %d/%d file co dong tom tat dung nguyen van"
          % (len(plan) - len(bad), len(plan)))
    for f in bad:
        print("  THAT BAI %s" % f)
    return 3 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backfill", action="store_true")
    a = ap.parse_args()
    return backfill(a.apply) if a.backfill else gen_index(a.apply)


if __name__ == "__main__":
    sys.exit(main())