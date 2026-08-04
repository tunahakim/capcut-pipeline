#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rlog_index_trim.py -- giu bang trong docs/research-log/INDEX.md o toi da N phien gan nhat, phan cu hon day sang INDEX-archive.md.
Mac dinh CHAY THU khong ghi gi; them --apply de ghi. --limit doi nguong, mac dinh 30.
Vi du: python tools/rlog_index_trim.py --limit 30 --apply
[KIEM: bo test]
"""
import argparse, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, "docs", "research-log", "INDEX.md")
ARC = os.path.join(ROOT, "docs", "research-log", "INDEX-archive.md")
ARC_HEAD = """# Nhat ky nghien cuu — muc luc luu tru

Cac phien cu hon ba muoi phien gan nhat, day sang day bang `python tools/rlog_index_trim.py --apply`. Muc luc dang dung o `INDEX.md`. Khong sua tay file nay.

| Phien | File | Noi dung chinh |
|---|---|---|
"""
TRO = "Cac phien cu hon nam o [`INDEX-archive.md`](INDEX-archive.md)."


def doc(p):
    with open(p, "rb") as f:
        raw = f.read()
    t = raw.decode("utf-8")
    nc = t.count("\r\n")
    if nc and (t.count("\n") - nc):
        sys.exit("LAN XUONG DONG: " + p)
    return raw, ("\r\n" if nc else "\n"), t.replace("\r\n", "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile(IDX):
        print("KHONG THAY " + IDX)
        return 1
    raw, nl, txt = doc(IDX)
    lines = txt.split("\n")
    rows = [i for i, ln in enumerate(lines)
            if ln.startswith("|") and not ln.startswith("|---") and not ln.startswith("| Phien")
            and not ln.startswith("| Phi\u00ean")]
    print("FILE   : " + IDX)
    print("BYTE   : " + str(len(raw)))
    print("DONG BANG: " + str(len(rows)) + " | nguong: " + str(a.limit))
    if len(rows) <= a.limit:
        print("=> CHUA CAN CAT (" + str(len(rows)) + " <= " + str(a.limit) + ")")
        return 0
    cut = rows[a.limit:]
    print("=> SE DAY " + str(len(cut)) + " dong sang INDEX-archive.md")
    for i in cut[:3]:
        print("   " + lines[i][:80])
    if len(cut) > 3:
        print("   ... va " + str(len(cut) - 3) + " dong nua")
    moved = [lines[i] for i in cut]
    keep = [ln for i, ln in enumerate(lines) if i not in set(cut)]
    if TRO not in txt:
        keep.append("")
        keep.append(TRO)
    new_idx = "\n".join(keep)
    if os.path.isfile(ARC):
        _, _, at = doc(ARC)
        new_arc = at.rstrip("\n") + "\n" + "\n".join(moved) + "\n"
    else:
        new_arc = ARC_HEAD + "\n".join(moved) + "\n"
    print("BYTE MOI : INDEX " + str(len(new_idx.encode("utf-8")))
          + " | archive " + str(len(new_arc.encode("utf-8"))))
    if not a.apply:
        print("=== CHAY THU, KHONG GHI GI (them --apply de ghi) ===")
        return 0
    with open(ARC, "wb") as f:
        f.write(new_arc.replace("\n", nl).encode("utf-8"))
    with open(IDX, "wb") as f:
        f.write(new_idx.replace("\n", nl).encode("utf-8"))
    print("=== DA GHI CA HAI FILE ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())