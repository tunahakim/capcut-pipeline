"""enc_probe.py - đo đường đi của chữ có dấu qua console và qua pipe rồi đối chiếu bằng codepoint, để biết khâu nào làm hỏng mã hoá.
Kết luận đã đo được ngày 04/08/2026 và ghi ở mục 8 của docs/START-HERE.md: in thẳng ra console thì sạch dù code page là 437 vì Python ghi bằng WriteConsoleW, còn khi stdout bị pipe thì Python tụt về mã hoá theo locale và chết bằng UnicodeEncodeError ở chữ có dấu đầu tiên.
[KIEM: bo test]
"""
import argparse
import locale
import os
import sys

CP = (0x110, 0x1B0, 0x1EDD, 0x6E, 0x67, 0x20, 0x30, 0x2C, 0x31, 0x20,
      0x67, 0x69, 0xE2, 0x79, 0x20, 0x2014, 0x20, 0x1EC7, 0x20, 0x1EEF)
S_REF = "".join(chr(c) for c in CP)
S_LIT = "Đường 0,1 giây — ệ ữ"


def cp_list(s):
    return " ".join("%04X" % ord(ch) for ch in s)


def console_cp():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        return "out=%d in=%d" % (k.GetConsoleOutputCP(), k.GetConsoleCP())
    except Exception as e:
        return "khong doc duoc (%s)" % type(e).__name__


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reconfigure", action="store_true",
                    help="goi sys.stdout.reconfigure UTF-8 truoc khi in, dung khuon repo")
    a = ap.parse_args()
    if a.reconfigure:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print("=== GROUND TRUTH (ASCII, khong the hong) ===")
    print("reconfigure        : %s" % ("CO" if a.reconfigure else "khong"))
    print("so ky tu ky vong   : %d" % len(CP))
    print("codepoint ky vong  : %s" % " ".join("%04X" % c for c in CP))
    ok = (S_LIT == S_REF)
    print("nguon script       : %s" % ("NGUON OK" if ok else "NGUON HONG"))
    if not ok:
        print("  literal len=%d" % len(S_LIT))
        print("  literal cp     =%s" % cp_list(S_LIT))
    print("")

    print("=== MOI TRUONG ===")
    print("python             : %s" % sys.version.split()[0])
    print("stdout.encoding    : %s" % sys.stdout.encoding)
    print("stdout.isatty      : %s" % sys.stdout.isatty())
    print("locale preferred   : %s" % locale.getpreferredencoding(False))
    print("console code page  : %s" % console_cp())
    print("PYTHONUTF8         : %s" % os.environ.get("PYTHONUTF8", "(khong dat)"))
    print("")

    print("=== DONG THU (phai trung ground truth o tren) ===")
    try:
        sys.stdout.write(S_REF + "\n")
        sys.stdout.flush()
        print("ket qua ghi        : KHONG LOI")
    except UnicodeEncodeError as e:
        print("ket qua ghi        : LOI UnicodeEncodeError encoding=%s" % e.encoding)
    except Exception as e:
        print("ket qua ghi        : LOI %s" % type(e).__name__)
    print("=== HET ===")


if __name__ == "__main__":
    main()