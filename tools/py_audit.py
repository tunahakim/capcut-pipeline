#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/py_audit.py -- rà mọi file Python trong repo cho khớp luật mã hoá ba chiều và luật docstring, bằng cách phân tích cây cú pháp chứ không grep chuỗi.

  python tools/py_audit.py            # quét toàn repo, in báo cáo
  python tools/py_audit.py --brief    # chỉ in file có vấn đề
  python tools/py_audit.py <file>     # quét đúng một file

Ba chiều của luật mã hoá, đo được ngày 04 và 05 tháng 8 năm 2026 và ghi ở mục 8 của docs/START-HERE.md: chiều ghi ra là mọi script có thể in tiếng Việt phải gọi sys.stdout.reconfigure sang UTF-8 ngay sau phần import, chiều đọc file là mọi open cùng read_text và write_text phải khai encoding tường minh, và chiều thứ ba là mọi lệnh subprocess có bắt output của tiến trình con phải khai encoding utf-8 vì nếu không Python decode theo locale rồi ném UnicodeDecodeError trong thread đọc, khiến kết quả về rỗng mà tiến trình con vẫn chạy đúng.
Hai phép kiểm docstring: docstring đầu file phải có ít nhất một ký tự có dấu, vì bảng tra viết không dấu thì người đọc không hiểu nổi và chế độ --find của tools/scripts_index.py mất một nửa giá trị; và docstring không được hard wrap, tức mỗi ý là một dòng dài chứ không ngắt dòng theo độ rộng cột.
Mã thoát 0 khi sạch và 2 khi còn LOI; nhóm CANH BAO không làm đổi mã thoát vì phép đoán hard wrap có thể nhầm với danh sách gạch đầu dòng.
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

REPO = da.REPO
DOC_OPEN = ("read_text", "write_text")
SP_CALL = ("run", "Popen", "check_output", "call", "check_call")


def co_dau(s):
    """Trả về True khi chuỗi có ít nhất một ký tự mang dấu tiếng Việt."""
    return any(unicodedata.combining(c) for c in unicodedata.normalize("NFD", s))


def ten_ham(node):
    """Trả về tên hàm được gọi dưới dạng chuỗi phẳng, ví dụ open hoặc subprocess.run hoặc p.read_text."""
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        goc = f.value.id if isinstance(f.value, ast.Name) else "?"
        return "%s.%s" % (goc, f.attr)
    return "?"


def kw(node, ten):
    """Trả về nút giá trị của một tham số từ khoá, hoặc None khi lệnh gọi không khai tham số đó."""
    for k in node.keywords:
        if k.arg == ten:
            return k.value
    return None


def la_true(node):
    return isinstance(node, ast.Constant) and node.value is True


def quet_file(rel):
    """Quét một file Python và trả về cặp danh sách lỗi và danh sách cảnh báo, mỗi mục là chuỗi mô tả kèm số dòng."""
    p = REPO / rel
    try:
        src = p.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return ["file khong doc duoc bang UTF-8: %s" % exc], []
    try:
        cay = ast.parse(src)
    except SyntaxError as exc:
        return ["loi cu phap dong %s: %s" % (exc.lineno, exc.msg)], []

    loi, canh = [], []
    co_reconfigure = "stdout.reconfigure" in src
    co_in = False

    for n in ast.walk(cay):
        if not isinstance(n, ast.Call):
            continue
        ten = ten_ham(n)
        if ten == "print":
            co_in = True
        goc, _, duoi = ten.rpartition(".")
        if duoi == "open" or duoi in DOC_OPEN:
            mode = n.args[1] if (duoi == "open" and len(n.args) > 1) else kw(n, "mode")
            if isinstance(mode, ast.Constant) and "b" in str(mode.value):
                continue
            if kw(n, "encoding") is None:
                loi.append("dong %d: %s thieu encoding" % (n.lineno, ten))
        elif duoi in SP_CALL and goc in ("subprocess", ""):
            bat = (la_true(kw(n, "capture_output")) or kw(n, "stdout") is not None
                   or duoi == "check_output")
            if bat and kw(n, "encoding") is None:
                loi.append("dong %d: %s bat output nhung thieu encoding"
                           % (n.lineno, ten))

    if co_in and not co_reconfigure:
        loi.append("co lenh print nhung khong goi sys.stdout.reconfigure")

    doc = ast.get_docstring(cay)
    if not doc:
        canh.append("khong co docstring dau file")
    else:
        if not co_dau(doc):
            loi.append("docstring dau file khong co ky tu co dau nao")
        dong = [d for d in doc.split("\n")]
        for i in range(len(dong) - 1):
            a, b = dong[i].rstrip(), dong[i + 1].strip()
            if (60 <= len(a) <= 100 and b and not a.endswith((".", ":", "?"))
                    and not b.startswith(("-", "*", "|", "#", "python "))
                    and not dong[i].startswith("  ")):
                canh.append("docstring nghi hard wrap sau dong %d" % (i + 1))
    return loi, canh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--brief", action="store_true")
    ap.add_argument("--exclude", action="append", metavar="TIEN-TO",
                    help="bỏ qua mọi file có đường dẫn bắt đầu bằng tiền tố này, lặp lại được; mặc định là _deprecated/")
    ap.add_argument("--tat-ca", action="store_true", dest="tat_ca",
                    help="quét cả thư mục vốn bị loại trừ mặc định")
    a = ap.parse_args()
    bo = [] if a.tat_ca else (a.exclude or ["_deprecated/"])

    if a.file:
        ds = [Path(a.file).as_posix()]
    else:
        ds = [f for f in da.walk_repo()
              if f.endswith(".py") and not any(f.startswith(x) for x in bo)]

    n_loi, n_canh, n_ban = 0, 0, 0
    for rel in ds:
        loi, canh = quet_file(rel)
        n_loi += len(loi)
        n_canh += len(canh)
        if loi or canh:
            n_ban += 1
        if not loi and not canh:
            if not a.brief and not a.file:
                continue
        if loi or canh or a.file:
            print("%s" % rel)
            for x in loi:
                print("  LOI     %s" % x)
            for x in canh:
                print("  CANH BAO %s" % x)

    print("")
    print("=== TONG QUAN ===")
    print("file .py quet : %d" % len(ds))
    print("loai tru      : %s" % (", ".join(bo) if bo else "khong"))
    print("file co van de: %d" % n_ban)
    print("LOI           : %d" % n_loi)
    print("CANH BAO      : %d" % n_canh)
    return 2 if n_loi else 0


if __name__ == "__main__":
    sys.exit(main())
