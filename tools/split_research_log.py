#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/split_research_log.py -- cat docs/research-log.md thanh tung file phien.

  python tools/split_research_log.py            # chay thu, khong ghi gi
  python tools/split_research_log.py --apply    # ghi that

Cat nguyen van tung byte theo tieu de cap hai. Khong sua noi dung,
chi doi dong "## X" thanh "# <tieu de moi>" o dau moi file.
File goc KHONG bi xoa; xoa bang tay sau khi da kiem tra.
"""
import sys, argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC  = REPO / "docs" / "research-log.md"
OUT  = REPO / "docs" / "research-log"

# (chuoi nhan dang tieu de, ten file dich, tieu de moi cap mot)
MAP = [
    ("## PH\u1ee4 L\u1ee4C E1",
     "2026-07-28-1-mo-dau.md",
     "# Nh\u1eadt k\u00fd phi\u00ean 28/07/2026 \u2014 m\u1edf \u0111\u1ea7u, b\u1ed9 test v3 v\u00e0 v4"),
    ("## PH\u1ee4 L\u1ee4C E.2",
     "2026-07-29-1-v5.md",
     "# Nh\u1eadt k\u00fd phi\u00ean 29/07/2026 (v5) \u2014 l\u1edbp filter b\u1eb1ng Python, quy t\u1eafc cache-first"),
    ("## PH\u1ee4 L\u1ee4C E.3",
     "2026-07-29-2-v6.md",
     "# Nh\u1eadt k\u00fd phi\u00ean 29/07/2026 (v6) \u2014 export MP4 th\u1eadt, kho\u00e1 Pro, \u0111o t\u1eebng khung"),
    ("## PH\u1ee4 L\u1ee4C E.4",
     "2026-07-29-3-v7.md",
     "# Nh\u1eadt k\u00fd phi\u00ean 29/07/2026 (v7) \u2014 chu\u1ea9n ho\u00e1 CAPCUT_LAB, \u0111\u00f3ng vendor kit, ch\u1eb7n updater"),
    ("## 2026-07-30",
     "2026-07-30-1-refactor.md",
     "# Nh\u1eadt k\u00fd phi\u00ean 30/07/2026 \u2014 di tr\u00fa c\u00e2y ba nh\u00e1nh v\u00e0 t\u1ea1o b\u1ed9 t\u00e0i li\u1ec7u"),
    ("## 31/07/2026",
     "2026-07-31-1-parity-300shot.md",
     "# Nh\u1eadt k\u00fd phi\u00ean 31/07/2026 (s\u00e1ng) \u2014 parity hai m\u00e1y, b\u00e0i t\u1ea3i 300 shot, \u0111\u00f3ng Vi\u1ec7c A"),
    ("## PHI\u00caN 31/07/2026 (chi\u1ec1u)",
     "2026-07-31-2-benchmark-render.md",
     "# Nh\u1eadt k\u00fd phi\u00ean 31/07/2026 (chi\u1ec1u) \u2014 benchmark m\u00e1y render, d\u1ef1ng v\u00e0 export 60 ph\u00fat"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    if not SRC.exists():
        print("KHONG THAY: %s" % SRC)
        return 1

    raw = SRC.read_text(encoding="utf-8", newline="")
    lines = raw.splitlines(keepends=True)
    total_bytes = len(raw.encode("utf-8"))

    # xac dinh vi tri moi tieu de cap hai
    heads = [(i, ln) for i, ln in enumerate(lines) if ln.startswith("## ")]
    print("=== TIEU DE CAP HAI TIM THAY: %d ===" % len(heads))
    for i, ln in heads:
        print("  dong %5d  %s" % (i + 1, ln.rstrip()[:80]))

    if len(heads) != len(MAP):
        print("")
        print("DUNG: so tieu de (%d) khac so muc trong MAP (%d). Sua MAP roi chay lai."
              % (len(heads), len(MAP)))
        return 2

    # ghep tung tieu de voi muc MAP theo dung thu tu, va kiem tra khop chuoi
    plan, ok = [], True
    for (idx, ln), (pat, fname, title) in zip(heads, MAP):
        if not ln.startswith(pat):
            print("")
            print("LECH: dong %d la %r nhung MAP cho %r" % (idx + 1, ln.rstrip()[:60], pat))
            ok = False
        plan.append((idx, fname, title, ln.rstrip()))
    if not ok:
        return 3

    preamble = "".join(lines[:heads[0][0]])
    print("")
    print("=== PHAN DAU FILE KHONG THUOC PHIEN NAO (%d byte) ==="
          % len(preamble.encode("utf-8")))
    print(preamble.strip()[:400])

    print("")
    print("=== KE HOACH CAT ===")
    print("%-34s %8s  %s" % ("file dich", "byte", "trang thai"))
    written = 0
    for k, (idx, fname, title, headline) in enumerate(plan):
        end = plan[k + 1][0] if k + 1 < len(plan) else len(lines)
        body = "".join(lines[idx + 1:end])
        # bo cac dong trang va dau --- o cuoi doan
        body = body.rstrip()
        while body.endswith("---"):
            body = body[:-3].rstrip()
        text = title + "\n\n" + body.lstrip("\n") + "\n"
        dst = OUT / fname
        nb = len(text.encode("utf-8"))
        written += nb
        state = "GHI DE (da co)" if dst.exists() else "tao moi"
        print("%-34s %8d  %s" % (fname, nb, state))
        if a.apply:
            OUT.mkdir(parents=True, exist_ok=True)
            with open(dst, "w", encoding="utf-8", newline="") as f:
                f.write(text)

    print("")
    print("file goc      : %d byte" % total_bytes)
    print("tong file moi : %d byte (chenh lech do bo tieu de cu, phan dau va dau ---)" % written)
    print("")
    if a.apply:
        print("DA GHI. Kiem tra roi xoa docs/research-log.md bang tay.")
    else:
        print("CHAY THU, chua ghi gi. Them --apply de ghi that.")
    return 0


if __name__ == "__main__":
    sys.exit(main())