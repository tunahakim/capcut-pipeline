"""Doc ma nguon theo nguong ba bac: tu chon in tron hay trich dong roi ghi UTF-8 va mo Notepad."""

import argparse
import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.environ.get("CAPCUT_LAB") or r"D:\IT\capcut-lab\data"
NL = chr(10)


def main():
    ap = argparse.ArgumentParser(description="Read a source file, full or excerpted.")
    ap.add_argument("path")
    ap.add_argument("--grep", action="append", default=[])
    ap.add_argument("--ctx", type=int, default=3)
    ap.add_argument("--head", type=int, default=25)
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()

    p = a.path if os.path.isabs(a.path) else os.path.join(ROOT, a.path.replace("/", os.sep))
    if not os.path.isfile(p):
        print("KHONG THAY FILE: " + p)
        return 1
    with open(p, "rb") as f:
        data = f.read()
    lines = data.decode("utf-8", "replace").split(NL)
    if lines and lines[-1] == "":
        lines.pop()
    total = len(lines)
    in_repo = os.path.abspath(p).lower().startswith(ROOT.lower() + os.sep)

    keep = set()
    if a.grep:
        low = [g.lower() for g in a.grep]
        for i, ln in enumerate(lines):
            s = ln.lower()
            if any(g in s for g in low):
                for j in range(max(0, i - a.ctx), min(total, i + a.ctx + 1)):
                    keep.add(j)
        for j in range(min(a.head, total)):
            keep.add(j)
    kept = len(keep)
    cut = (100.0 * (total - kept) / total) if total else 0.0

    if a.full:
        trich, ly_do = False, "co co --full"
    elif not a.grep:
        trich, ly_do = False, "khong co --grep nen khong loai duoc dong nao"
    elif not in_repo:
        trich, ly_do = True, "file ngoai repo -> luon trich"
    elif total < 250:
        trich, ly_do = False, "duoi 250 dong -> luon in tron"
    else:
        need = 50 if total <= 600 else 30
        trich = cut >= need
        ly_do = "loai " + ("%.1f" % cut) + "% " + (">=" if trich else "<") + " nguong " + str(need) + "%"
        if not trich:
            ly_do = ly_do + " -> in tron"

    out = []
    out.append("FILE   : " + p)
    out.append("DONG   : " + str(total) + " | BYTE: " + str(len(data))
               + " | trong repo: " + ("co" if in_repo else "khong"))
    out.append("GREP   : " + (", ".join(a.grep) if a.grep else "(khong)"))
    out.append("NHANH  : " + ("TRICH" if trich else "IN TRON") + " -- " + ly_do)
    out.append("=" * 60)
    if trich:
        i = 0
        while i < total:
            if i in keep:
                out.append(str(i + 1).rjust(5) + "  " + lines[i])
                i += 1
            else:
                j = i
                while j < total and j not in keep:
                    j += 1
                out.append("      ... bo qua " + str(j - i) + " dong ("
                           + str(i + 1) + "-" + str(j) + ") ...")
                i = j
    else:
        for i, ln in enumerate(lines):
            out.append(str(i + 1).rjust(5) + "  " + ln)

    stamp = datetime.datetime.now().strftime("%Y%m%d")
    name = "tmp_" + stamp + "_read_" + os.path.basename(p).replace(".", "_") + ".txt"
    dst = os.path.join(LAB, "tmp", name)
    with open(dst, "w", encoding="utf-8", newline=NL) as f:
        f.write(NL.join(out))
    print(out[1])
    print(out[3])
    print("DA GHI : " + dst)
    subprocess.Popen(["notepad.exe", dst])
    return 0


if __name__ == "__main__":
    sys.exit(main())