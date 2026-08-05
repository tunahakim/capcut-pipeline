#!/usr/bin/env python3
"""filt_enum.py - xem catalogue filter ca hai namespace + tra ID da biet + kiem cache. [KIEM: chua]"""
import subprocess, json, pathlib
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CACHE = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"


def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True)
    t = p.stdout.decode("utf-8", errors="replace").strip()
    if not t:
        print("  (RONG)", p.stderr.decode("utf-8", errors="replace")[:200])
        return []
    try:
        return json.loads(t)
    except Exception as e:
        print("  (LOI)", e, t[:200])
        return []


for flag in ("--filters", "--filters --jianying"):
    a = run("capcut enums " + flag)
    print("\n" + "=" * 74)
    print("capcut enums %s  ->  %d muc" % (flag, len(a)))
    print("=" * 74)
    if a:
        print("  khoa cua 1 muc:", sorted(a[0].keys()))
    for x in a[:60]:
        print("  slug=%-22s rid=%-21s md5=%-34s %s"
              % (str(x.get("slug") or "")[:22], x.get("resource_id"),
                 x.get("md5"), x.get("name")))
    if len(a) > 60:
        print("  ... con %d muc nua" % (len(a) - 60))

print("\n" + "=" * 74)
print("TRA CUU ID DA BIET")
print("=" * 74)
WANT = {"7028463716732079117": "Vintage  (CLI dung, slug 'vintage')",
        "6706773528319906308": "Film     (GUI ghi, source_platform=1)"}
for flag in ("--filters", "--filters --jianying", "--scene-effects",
             "--scene-effects --jianying"):
    for x in run("capcut enums " + flag):
        if str(x.get("resource_id")) in WANT or str(x.get("effect_id")) in WANT:
            print("\n [%s] %s" % (flag, WANT.get(str(x.get("resource_id")),
                                                 WANT.get(str(x.get("effect_id"))))))
            print("   ", json.dumps(x, ensure_ascii=False))

print("\n=== THU MUC CACHE ===")
for rid, note in WANT.items():
    print("  %s (%s) -> %s" % (rid, note.split("(")[0].strip(), (CACHE / rid).is_dir()))