#!/usr/bin/env python3
"""
patch_v8.py [--apply]
Va hai file tren dia theo ket qua do cua cache_probe.py (phien v8):
  fx_audit.py     -> kiem cache bang THU MUC ten md5, khong phai file
  filter_apply.py -> dung path bang cach QUET cache theo resource_id,
                     khong hardcode md5 tu enums.json

Khong co --apply thi chi bao cao. Backup duoi .v8bak. Xac thuc ast.parse
truoc khi ghi de. Idempotent: chay lai bao nhieu lan cung duoc.
"""
import ast, os, pathlib, shutil, sys

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
APPLY = "--apply" in sys.argv

HELPER_AUDIT = '''
import re
HEX32 = re.compile(r"^[0-9a-f]{32}$")


def cache_of(rid):
    """Tra ve danh sach THU MUC md5 nam trong Cache/effect/<rid>/.
    Ten md5 la THU MUC chu khong phai file - do 279 dir / 0 file (xem IX.12).
    Tra ve [] KHONG co nghia la tai nguyen thieu: tai nguyen namespace CapCut
    dung thu muc short-id nen khong tra duoc theo rid. Doc kem cot trang thai path."""
    d = CACHE / str(rid)
    if not d.is_dir():
        return []
    return [x.name for x in d.iterdir() if x.is_dir() and HEX32.match(x.name)]
'''

HELPER_FILT = '''
import re
HEX32 = re.compile(r"^[0-9a-f]{32}$")


def resolve_path(rid, md5_hint=""):
    """Dung path tai nguyen bang cach QUET cache theo resource_id.
    KHONG tin md5 trong enums.json: do tren 25 material co doi chieu thi 6 cai
    LECH (xem VIII.5). CapCut resolve theo resource_id, CDN tra md5 hien hanh.
    md5_hint chi la phuong an du phong khi khong co thu muc <rid>."""
    d = CACHE / str(rid)
    if d.is_dir():
        subs = [x for x in d.iterdir() if x.is_dir() and HEX32.match(x.name)]
        if subs:
            return str(subs[0]).replace("\\\\", "/"), "quet theo rid"
    if md5_hint:
        for t in CACHE.iterdir():
            if t.is_dir() and (t / md5_hint).is_dir():
                return str(t / md5_hint).replace("\\\\", "/"), "quet theo md5 goi y"
    return "", "KHONG TIM THAY TRONG CACHE"
'''

JOBS = [
    ("fx_audit.py", "cache_of", [
        ('PH = "##_material_placeholder"',
         'PH = "##_material_placeholder"' + HELPER_AUDIT,
         "chen helper cache_of"),
        ('    rid = str(m.get("resource_id"))\n'
         '    dd = CACHE / rid\n'
         '    if dd.is_dir():\n'
         '        print("       cache/%s -> %s" % (rid, [x.name for x in dd.iterdir()][:3]))',
         '    rid = str(m.get("resource_id"))\n'
         '    cs = cache_of(rid)\n'
         '    print("       cache/%s -> %s" % (rid, cs if cs else "(khong tra duoc theo rid)"))',
         "khoi transitions"),
        ('        rid = str(m.get("resource_id"))\n'
         '        dd = CACHE / rid\n'
         '        print("       cache/%s ton_tai=%s %s" % (rid, dd.is_dir(),\n'
         '              [x.name for x in dd.iterdir()][:3] if dd.is_dir() else ""))',
         '        rid = str(m.get("resource_id"))\n'
         '        cs = cache_of(rid)\n'
         '        print("       cache/%s -> %s" % (rid, cs if cs else "(khong tra duoc theo rid)"))',
         "khoi video_effects/effects"),
    ]),
    ("filter_apply.py", "resolve_path", [
        ('CACHE = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"',
         'CACHE = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"'
         + HELPER_FILT,
         "chen helper resolve_path"),
        ('        if p.get("path_mode") == "empty":\n'
         '            path, note = "", "PATH RONG (thu nghiem tu tai)"\n'
         '        else:\n'
         '            path = str(CACHE / p["rid"] / p["md5"]).replace("\\\\", "/")\n'
         '            note = "cache_san_co=%s" % pathlib.Path(path).exists()',
         '        if p.get("path_mode") == "empty":\n'
         '            path, note = "", "PATH RONG (thu nghiem tu tai)"\n'
         '        else:\n'
         '            path, note = resolve_path(p["rid"], p.get("md5", ""))\n'
         '            if not path:\n'
         '                print("  *** %s: khong co trong cache. Mo CapCut, tab Filters,"\n'
         '                      " bam mui ten tai xuong, roi chay lai. ***" % p["name"])',
         "khoi dung path trong main()"),
    ]),
]

print("LAB   = %s" % LAB)
print("che do: %s\n" % ("GHI THAT" if APPLY else "BAO CAO (them --apply de ghi)"))

for fname, marker, edits in JOBS:
    f = LAB / fname
    print("=" * 74)
    print(fname)
    print("=" * 74)
    if not f.exists():
        print("  *** KHONG CO TREN DIA - bo qua ***\n")
        continue
    txt = f.read_text(encoding="utf-8")
    print("  %d bytes | %d dong" % (f.stat().st_size, txt.count("\n") + 1))
    if ("def %s(" % marker) in txt:
        print("  DA VA TU TRUOC (thay 'def %s'). Bo qua.\n" % marker)
        continue

    new = txt
    ok = True
    for old, rep, label in edits:
        n = new.count(old)
        line = new[:new.find(old)].count("\n") + 1 if n else 0
        print("  %-34s %d cho%s" % (label, n, (" (dong %d)" % line) if n == 1 else ""))
        if n != 1:
            ok = False
            print("       *** MONG DOI DUNG 1 CHO - KHONG VA FILE NAY ***")
            print("       Doan can tim:")
            for l in old.split("\n"):
                print("         | %s" % l)
            continue
        new = new.replace(old, rep, 1)

    if not ok:
        print("  -> BO QUA file nay, gui lai noi dung file de doi chieu\n")
        continue
    try:
        ast.parse(new)
    except SyntaxError as e:
        print("  *** CU PHAP HONG SAU KHI VA: %s - KHONG GHI ***\n" % e)
        continue
    print("  cu phap OK sau khi va | %d -> %d dong"
          % (txt.count("\n") + 1, new.count("\n") + 1))
    if not APPLY:
        print("  (chua ghi)\n")
        continue
    shutil.copy2(f, str(f) + ".v8bak")
    f.write_text(new, encoding="utf-8")
    print("  DA GHI (backup %s.v8bak)\n" % fname)

print("Xong. Neu da --apply, chay kiem chung:")
print("  python %s <project-dir>   (fx_audit)" % (LAB / "fx_audit.py"))