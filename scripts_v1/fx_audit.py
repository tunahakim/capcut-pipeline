#!/usr/bin/env python3
"""fx_audit.py <project-dir> - kiem ke tai nguyen moi transition/effect/filter. [KIEM: du lieu that]"""
import json, pathlib, sys

CACHE = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"
PH = "##_material_placeholder"
import re

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
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

PROJ = pathlib.Path(sys.argv[1])
TID = json.loads((PROJ / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
d = json.loads((PROJ / "Timelines" / TID / "draft_content.json").read_text(encoding="utf-8"))

tr = {m["id"]: m for m in d["materials"].get("transitions", [])}
seg_of = {}
for i, s in enumerate(next(t for t in d["tracks"] if t["type"] == "video")["segments"], 1):
    for r in s.get("extra_material_refs", []):
        if r in tr:
            seg_of[r] = i

print("=== TRANSITIONS (%d) ===" % len(tr))
bad = []
for mid, m in tr.items():
    p = m.get("path", "")
    if not p:            st = "RONG"
    elif PH in p:        st = "*** PLACEHOLDER - CHUA RESOLVE ***"
    elif pathlib.Path(p).exists(): st = "OK"
    else:                st = "*** PATH SAI, FILE KHONG CO ***"
    if st != "OK":
        bad.append(m.get("name"))
    print("  sau shot %-2s %-16s rid=%-21s dur=%-8s overlap=%-5s %s"
          % (seg_of.get(mid, "?"), m.get("name"), m.get("resource_id"),
             m.get("duration"), m.get("is_overlap"), st))
    rid = str(m.get("resource_id"))
    cs = cache_of(rid)
    print("       cache/%s -> %s" % (rid, cs if cs else "(khong tra duoc theo rid)"))
print(">>> transition HONG:", bad or "khong co")

for bucket in ("video_effects", "effects"):
    arr = d["materials"].get(bucket) or []
    print("\n=== MATERIALS.%s (%d) ===" % (bucket.upper(), len(arr)))
    for m in arr:
        p = m.get("path", "")
        st = "RONG" if not p else ("PLACEHOLDER" if PH in p
             else ("OK" if pathlib.Path(p).exists() else "FILE KHONG CO"))
        print("  %-12s type=%-12s rid=%-21s value=%-6s %s"
              % (m.get("name"), m.get("type"), m.get("resource_id"), m.get("value"), st))
        rid = str(m.get("resource_id"))
        cs = cache_of(rid)
        print("       cache/%s -> %s" % (rid, cs if cs else "(khong tra duoc theo rid)"))

print("\n=== THU MUC CACHE: %d muc ===" % len(list(CACHE.iterdir())))