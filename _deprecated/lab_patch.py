#!/usr/bin/env python3
"""
lab_patch.py [--apply]
Chuan hoa duong dan: thay moi pathlib.Path(r"D:\Test_tool\...") trong cac file .py
cua thu muc lam viec bang LAB / "..." , voi
    LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))

Khong co --apply thi chi bao cao, khong sua gi.
Backup duoi duoi .labbak. Xac thuc cu phap truoc khi ghi de.
"""
import ast, os, pathlib, re, shutil, sys

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
APPLY = "--apply" in sys.argv

HDR_LINE = 'LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\\Test_tool"))'
PAT = re.compile(r'pathlib\.Path\(r"D:\\Test_tool\\([^"]+)"\)')
BARE = re.compile(r'r"D:\\Test_tool')


def to_lab(m):
    parts = [p for p in m.group(1).split("\\") if p]
    return " / ".join(['LAB'] + ['"%s"' % p for p in parts])


def patch(txt):
    """Tra ve (text_moi, so_lan_thay) hoac (None, 0) neu khong can dong."""
    new, n = PAT.subn(to_lab, txt)
    if n == 0:
        return None, 0
    lines = new.split("\n")
    if "CAPCUT_LAB" not in new:
        idx = [i for i, l in enumerate(lines)
               if l.startswith("import ") or l.startswith("from ")]
        if not idx:
            return None, -1
        at = idx[-1] + 1
        ins = []
        if not re.search(r'^import .*\bos\b|^import os$', new, re.M):
            ins.append("import os")
        ins += ["", HDR_LINE]
        lines[at:at] = ins
    return "\n".join(lines), n


print("LAB = %s" % LAB)
print("che do: %s\n" % ("GHI THAT" if APPLY else "BAO CAO (them --apply de ghi)"))

files = sorted(p for p in LAB.glob("*.py") if p.name != "lab_patch.py")
done = skipped = 0
for f in files:
    txt = f.read_text(encoding="utf-8")
    new, n = patch(txt)
    if n == 0:
        if BARE.search(txt):
            print("  %-22s con chuoi D:\\Test_tool KHONG khop mau -> xem tay" % f.name)
        else:
            skipped += 1
        continue
    if n < 0:
        print("  %-22s *** khong tim thay dong import -> bo qua ***" % f.name)
        continue
    print("  %-22s %d cho" % (f.name, n))
    for a, b in zip(PAT.findall(txt), [to_lab(m) for m in PAT.finditer(txt)]):
        print("        r\"D:\\Test_tool\\%s\"  ->  %s" % (a, b))
    if not APPLY:
        continue
    try:
        ast.parse(new)
    except SyntaxError as e:
        print("        *** CU PHAP HONG, KHONG GHI: %s ***" % e)
        continue
    shutil.copy2(f, str(f) + ".labbak")
    f.write_text(new, encoding="utf-8")
    print("        da ghi (backup .labbak)")
    done += 1

print("\nsua %d file | khong lien quan %d file" % (done, skipped))

print("\n=== KIEM LAI: con chuoi 'D:\\Test_tool' o dau ===")
left = 0
for f in files:
    for i, l in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
        if "D:\\Test_tool" in l and "CAPCUT_LAB" not in l:
            print("  %-22s dong %-4d %s" % (f.name, i, l.strip()[:80]))
            left += 1
print("  (bo qua dong fallback co CAPCUT_LAB)")
print("  tong: %d cho con lai" % left)