#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""nl_audit.py - quét ký tự xuống dòng của mọi file văn bản trong repo, bắt file LẪN CRLF với LF cùng file có BOM, và chuẩn hoá được bằng --fix.
Bốn cách chạy: không tham số thì chỉ quét và không ghi gì, --all in cả file sạch, --fix chạy thử chế độ chuẩn hoá, --fix --apply ghi thật về kiểu xuống dòng chiếm đa số trong từng file.
Lý do tồn tại: mọi tool và tài liệu trong repo đều theo khuôn đo file đang dùng CRLF hay LF rồi đổi khuôn so khớp cho khớp, nên một file lẫn hai kiểu sẽ làm tools/docs_patch.py cùng tools/rlog_index.py dừng lại; chết ở file đầu tiên thì không ai biết còn bao nhiêu file nữa, vì vậy phải quét cả lượt.
--fix chỉ chạm file lẫn, và chuẩn hoá về kiểu chiếm đa số trong chính file đó chứ không áp một kiểu chung cho cả repo.
Mã thoát: 0 sạch, 2 còn file lẫn hoặc file có BOM, 3 đã ghi nhưng kiểm lại thất bại.
[KIEM: du lieu that]
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXTS = {".md", ".py", ".json", ".txt", ".toml", ".bat", ".ps1", ".cfg",
        ".ini", ".csv", ".tsv", ".yml", ".yaml", ".gitignore"}
SKIP = {".git", "__pycache__", ".venv", ".idea", ".vscode"}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def files():
    out = []
    for p in sorted(REPO.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP for part in p.parts):
            continue
        if p.suffix.lower() in EXTS or p.name in EXTS:
            out.append(p)
    return out


def look(raw):
    """Tra ve (kieu, so_crlf, so_lf_don, so_cr_don, bom, dong_lf_don)."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    cr = raw.count(b"\r") - crlf
    bom = raw[:3] == b"\xef\xbb\xbf"
    kinds = [k for k, n in (("CRLF", crlf), ("LF", lf), ("CR", cr)) if n]
    kind = "TRONG" if not kinds else (kinds[0] if len(kinds) == 1 else "LAN")
    lines, ln, i = [], 1, 0
    while i < len(raw) and lf:
        c = raw[i:i + 1]
        if c == b"\r" and raw[i + 1:i + 2] == b"\n":
            ln += 1
            i += 2
            continue
        if c == b"\n":
            lines.append(ln)
            ln += 1
        i += 1
    return kind, crlf, lf, cr, bom, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    rows, bad, boms, skipped = [], [], [], []
    for p in files():
        raw = p.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            skipped.append((p, exc))
            continue
        kind, crlf, lf, cr, bom, lfl = look(raw)
        rows.append((p, kind, crlf, lf, cr, bom, lfl, len(raw)))
        if kind == "LAN":
            bad.append(rows[-1])
        if bom:
            boms.append(p)

    tong = {}
    for r in rows:
        tong[r[1]] = tong.get(r[1], 0) + 1
    print("=== TONG QUAN ===")
    print("file van ban quet : %d" % len(rows))
    for k in sorted(tong):
        print("  %-6s %d" % (k, tong[k]))
    if skipped:
        print("bo qua khong decode duoc UTF-8: %d" % len(skipped))
        for p, exc in skipped:
            print("  KHONG UTF-8 %s (%s)" % (p.relative_to(REPO).as_posix(), exc))
    print("file co BOM       : %d" % len(boms))
    print("")

    if a.all:
        print("=== TUNG FILE ===")
        for p, kind, crlf, lf, cr, bom, lfl, n in rows:
            print("%-6s CRLF=%-5d LF=%-4d CR=%-3d %7d  %s"
                  % (kind, crlf, lf, cr, n, p.relative_to(REPO).as_posix()))
        print("")

    print("=== FILE LAN XUONG DONG (%d) ===" % len(bad))
    for p, kind, crlf, lf, cr, bom, lfl, n in bad:
        rel = p.relative_to(REPO).as_posix()
        print("%s" % rel)
        print("  CRLF=%d LF don=%d CR don=%d byte=%d" % (crlf, lf, cr, n))
        print("  dong co LF don: %s" % (", ".join(str(x) for x in lfl[:20])
                                        or "(khong xac dinh)"))
        if len(lfl) > 20:
            print("  ... va %d dong nua" % (len(lfl) - 20))
    for p in boms:
        print("BOM %s" % p.relative_to(REPO).as_posix())
    if not bad and not boms:
        print("khong co -- sach")
        return 0
    if not a.fix:
        print("")
        print("=> them --fix de xem ke hoach chuan hoa, --fix --apply de ghi")
        return 2

    print("")
    print("=== KE HOACH CHUAN HOA ===")
    plan = []
    for p, kind, crlf, lf, cr, bom, lfl, n in bad:
        dom = "\r\n" if crlf >= lf else "\n"
        text = p.read_bytes().decode("utf-8").replace("\r\n", "\n")
        new = text.replace("\n", dom).encode("utf-8")
        print("%-58s %s  %d -> %d byte"
              % (p.relative_to(REPO).as_posix(),
                 "CRLF" if dom == "\r\n" else "LF  ", n, len(new)))
        plan.append((p, new, dom))
    if boms:
        print("CANH BAO: file co BOM khong duoc tool nay sua, phai xu ly rieng")
    if not a.apply:
        print("=== CHAY THU, KHONG GHI GI (them --apply de ghi) ===")
        return 2
    fail = []
    for p, new, dom in plan:
        p.write_bytes(new)
        raw = p.read_bytes()
        kind = look(raw)[0]
        ok = kind in ("CRLF", "LF")
        print("KIEM SAU %-52s %s (%s)"
              % (p.relative_to(REPO).as_posix(), "OK" if ok else "THAT BAI", kind))
        if not ok:
            fail.append(p)
    return 3 if fail else 0


if __name__ == "__main__":
    sys.exit(main())