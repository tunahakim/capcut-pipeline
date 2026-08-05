#!/usr/bin/env python3
"""
cache_probe.py - chot 2 cau hoi ve Cache/effect:
  1. ten md5 la FILE hay THU MUC  -> quyet dinh cach viet lai fx_audit.py
  2. md5 trong enums.json co khop md5 CapCut thuc dung khong
     -> neu KHONG thi ket luan "CapCut resolve theo md5" o VIII.5 phai sua
Chi doc, khong sua gi.
[KIEM: bo test]
"""
import json, os, pathlib, re, subprocess, sys, time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
DR = pathlib.Path(os.environ["LOCALAPPDATA"]) / "CapCut/User Data/Projects/com.lveditor.draft"
CACHE = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"
OUT = LAB / "perf"
OUT.mkdir(parents=True, exist_ok=True)
HEX32 = re.compile(r"^[0-9a-f]{32}$")
L = []


def say(s=""):
    print(s)
    L.append(s)


say("=" * 78)
say("1. CAU TRUC THU MUC CACHE  (10 muc moi nhat)")
say("=" * 78)
tops = sorted((x for x in CACHE.iterdir() if x.is_dir()),
              key=lambda p: -p.stat().st_mtime)
say("tong thu muc goc: %d" % len(tops))
for t in tops[:10]:
    kind = "rid-dai" if len(t.name) > 15 and t.name.isdigit() else "short-id"
    say("\n  %s   [%s]   mtime %s"
        % (t.name, kind, time.strftime("%m-%d %H:%M", time.localtime(t.stat().st_mtime))))
    for c in sorted(t.iterdir())[:6]:
        say("      %-40s %-4s %s"
            % (c.name[:40], "DIR" if c.is_dir() else "FILE",
               ("%d file ben trong" % len(list(c.iterdir()))) if c.is_dir()
               else ("%d bytes" % c.stat().st_size)))

nd = nf = 0
for t in tops:
    for c in t.iterdir():
        if HEX32.match(c.name):
            if c.is_dir():
                nd += 1
            else:
                nf += 1
say("")
say("=== DEM TREN TOAN CACHE ===")
say("  ten md5 la THU MUC : %d" % nd)
say("  ten md5 la FILE    : %d" % nf)
say("  -> fx_audit.py phai kiem %s"
    % ("THU MUC ten md5" if nd > nf else "FILE ten md5"))
nrid = sum(1 for t in tops if len(t.name) > 15 and t.name.isdigit())
say("  thu muc goc kieu rid-dai: %d | kieu short-id: %d" % (nrid, len(tops) - nrid))

say("")
say("=" * 78)
say("2. md5 TRONG ENUMS  vs  md5 CAPCUT THUC DUNG")
say("=" * 78)
p = subprocess.run("capcut enums --transitions", shell=True, capture_output=True)
enum = {}
try:
    for x in json.loads(p.stdout.decode("utf-8", "replace")):
        if x.get("resource_id"):
            enum[str(x["resource_id"])] = x
except Exception as e:
    say("  khong doc duoc enums: %s" % e)
p = subprocess.run("capcut enums --scene-effects", shell=True, capture_output=True)
try:
    for x in json.loads(p.stdout.decode("utf-8", "replace")):
        if x.get("resource_id"):
            enum.setdefault(str(x["resource_id"]), x)
except Exception:
    pass
say("  doc duoc %d entry co resource_id tu enums" % len(enum))

say("")
say("%-13s %-9s %-22s %-34s %-34s %s"
    % ("project", "bucket", "name", "md5 trong PATH", "md5 trong ENUMS", "kq"))
khop = lech = khongro = 0
for d in sorted(DR.iterdir(), key=lambda q: -q.stat().st_mtime):
    pj = d / "Timelines" / "project.json"
    if not pj.exists():
        continue
    try:
        tid = json.loads(pj.read_text(encoding="utf-8"))["main_timeline_id"]
        f = d / "Timelines" / tid / "draft_content.json"
        if not f.exists():
            f = d / "draft_content.json"
        j = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    for bk in ("transitions", "video_effects", "effects", "material_animations"):
        arr = (j.get("materials") or {}).get(bk) or []
        for m in arr:
            items = m.get("animations") if bk == "material_animations" else [m]
            for it in (items or []):
                path = str(it.get("path") or "")
                if not path or "placeholder" in path:
                    continue
                seg = [s for s in path.replace("\\", "/").split("/") if HEX32.match(s)]
                if not seg:
                    continue
                pm = seg[-1]
                rid = str(it.get("resource_id") or m.get("resource_id") or "")
                em = (enum.get(rid) or {}).get("md5")
                if em is None:
                    kq = "khong co trong enums"
                    khongro += 1
                elif em == pm:
                    kq = "KHOP"
                    khop += 1
                else:
                    kq = "*** LECH ***"
                    lech += 1
                say("%-13s %-9s %-22s %-34s %-34s %s"
                    % (d.name[:13], bk[:9], str(it.get("name"))[:22], pm,
                       em or "-", kq))

say("")
say("  KHOP %d | LECH %d | khong co trong enums %d" % (khop, lech, khongro))
if lech:
    say("  => md5 trong enums.json KHONG phai khoa dang tin.")
    say("     Ket luan VIII.5 'CapCut resolve theo md5' phai sua thanh 'theo resource_id'.")
    say("     Anh huong: filter_apply.py hardcode md5 de dung path -> diem de vo.")
else:
    say("  => md5 khop toan bo, giu nguyen ket luan VIII.5.")

say("")
say("=" * 78)
say("3. BLACK FADE DA CO CACHE TRUOC PHEP THU CHUA")
say("=" * 78)
TARGET = "3bca53e9f3dfa2c184fbee96438ea097"
found = False
for t in tops:
    for c in t.iterdir():
        if c.name.startswith(TARGET):
            found = True
            say("  %s\\%s   mtime %s   %s"
                % (t.name, c.name,
                   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(c.stat().st_mtime)),
                   "DIR" if c.is_dir() else "FILE"))
if not found:
    say("  khong tim thay md5 %s trong cache" % TARGET)
say("")
say("  Doc mtime: neu la HOM NAY quanh gio chay phep thu -> CapCut moi tai ve,")
say("  tuc Python ghi duoc ca tai nguyen CHUA cache. Neu la ngay cu -> phep thu")
say("  chua chung minh dieu do, can lam lai voi mot slug chua tung dung.")

(OUT / "cache_probe.txt").write_text("\n".join(L), encoding="utf-8")
print("\nDa ghi: %s" % (OUT / "cache_probe.txt"))