#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/docstring_dump.py -- in nguyên văn docstring đầu file của các script Python, để viết lại bằng tiếng Việt có dấu mà không phải dán tay từng file vào hội thoại.

  python tools/docstring_dump.py                  # mọi file còn thiếu dấu, bỏ qua _deprecated/
  python tools/docstring_dump.py --scope tools/   # chỉ một thư mục
  python tools/docstring_dump.py --all            # in cả file docstring đã có dấu

Sinh ra để trả món nợ docstring không dấu mà tools/py_audit.py đo được: mỗi lần chạy in đủ nguyên liệu cho một lô viết lại, kèm số dòng và số byte của file để ước lượng công việc.
Mỗi docstring nằm giữa hai dòng đánh dấu có tên file, nên chép ra và đối chiếu ngược đều chính xác.
[KIEM: chua]
"""
import argparse
import ast
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_audit as da

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def co_dau(s):
    """Trả về True khi chuỗi có ít nhất một ký tự mang dấu tiếng Việt."""
    return any(unicodedata.combining(c) for c in unicodedata.normalize("NFD", s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", default="", help="chỉ quét file có đường dẫn bắt đầu bằng tiền tố này")
    ap.add_argument("--all", action="store_true", help="in cả file đã có docstring tiếng Việt có dấu")
    a = ap.parse_args()
    n = 0
    for rel in da.walk_repo():
        if not rel.endswith(".py") or rel.startswith("_deprecated/"):
            continue
        if a.scope and not rel.startswith(a.scope):
            continue
        src = (da.REPO / rel).read_text(encoding="utf-8")
        try:
            doc = ast.get_docstring(ast.parse(src), clean=False)
        except SyntaxError as exc:
            print("### %s LOI CU PHAP: %s" % (rel, exc))
            continue
        if doc and co_dau(doc) and not a.all:
            continue
        n += 1
        print("########## %s | %d dong | %d byte ##########"
              % (rel, len(src.split("\n")), len(src.encode("utf-8"))))
        print(doc if doc else "(KHONG CO DOCSTRING)")
        print("########## HET %s ##########" % rel)
        print("")
    print("=== so file can viet lai: %d ===" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())