#!/usr/bin/env python3
r"""
audit_kit.py - kiem ke thuc trang dia, doi chieu voi Phu luc B cua tai lieu.
Chi DOC, khong sua gi. Ghi bao cao ra <LAB>\perf\audit_kit.txt
Tra loi:
  1. script nao co that tren dia, script nao thieu, script nao thua
  2. script nao con ghi cung duong dan (doi chieu tuyen bo o muc II.1)
  3. vendor kit: dung luong that, so file, so muc cache
  4. bytes tren moi segment cua draft_content.json  <-- so quyet dinh kien truc
[KIEM: chua]
"""
import hashlib, json, os, pathlib, re, sys

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
DR = pathlib.Path(os.environ["LOCALAPPDATA"]) / "CapCut/User Data/Projects/com.lveditor.draft"
CACHE = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"
OUT = LAB / "perf"
OUT.mkdir(parents=True, exist_ok=True)
L = []


def say(s=""):
    print(s)
    L.append(s)


# ---- danh sach mong doi, chep tu Phu luc B ----
EXPECT_LAB = [
    "kb_apply.py", "filter_apply.py", "strip_filters.py", "clone_project.py",
    "patchpath.py", "capcut_post.py",
    "fx_audit.py", "check_sync.py", "diff_timing.py", "find_ph.py",
    "oracle_read.py", "snap.py", "chk_fx.py",
    "grab_frames.py", "tr_profile3.py",
    "syntax.py", "enum_list.py", "fx_list.py", "filt_enum.py", "v4_mold.py",
    "lab_patch.py", "parity_build.py",
    "session.ps1", "pack_vendor.ps1",
]
EXPECT_VENDOR = [
    "setup_1_runtimes.ps1", "setup_2_capcut.ps1",
    "README_PARITY.txt", "MANIFEST.txt", "enums_backup.json",
]
NO_SRC_IN_DOC = [
    "grab_frames.py", "tr_profile3.py", "strip_filters.py",
    "pack_vendor.ps1", "parity_build.py",
    "_vendor/setup_1_runtimes.ps1", "_vendor/setup_2_capcut.ps1",
    "_vendor/README_PARITY.txt",
]


def sha10(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()[:10]


def hardcoded(p):
    """so dong con ghi cung D:\\Test_tool, bo qua dong fallback co CAPCUT_LAB"""
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return -1, False, 0
    bad = [l for l in t.split("\n")
           if "D:\\Test_tool" in l and "CAPCUT_LAB" not in l]
    return len(bad), ("CAPCUT_LAB" in t), t.count("\n") + 1


say("=" * 78)
say("1. KIEM KE SCRIPT TRONG %s" % LAB)
say("=" * 78)
say("%-24s %8s %6s %-10s %-5s %s" % ("file", "bytes", "dong", "sha256", "LAB", "ghi cung"))
missing = []
for n in EXPECT_LAB:
    p = LAB / n
    if not p.exists():
        missing.append(n)
        say("%-24s %8s" % (n, "*** THIEU ***"))
        continue
    nb, haslab, nl = hardcoded(p)
    say("%-24s %8d %6d %-10s %-5s %s"
        % (n, p.stat().st_size, nl, sha10(p),
           "co" if haslab else "-", nb if nb else "-"))
say("")
say("THIEU tren dia: %s" % (missing or "khong"))

say("")
say("-- file .py/.ps1 CO tren dia nhung KHONG co trong Phu luc B --")
known = set(EXPECT_LAB)
extra = []
for p in sorted(LAB.glob("*.py")) + sorted(LAB.glob("*.ps1")):
    if p.name not in known:
        extra.append(p.name)
        say("   %-26s %8d bytes" % (p.name, p.stat().st_size))
if not extra:
    say("   khong co")

say("")
say("-- verify.py (Phu luc B ghi DA XOA) --")
say("   ton tai tren dia: %s" % (LAB / "verify.py").exists())

say("")
say("-- _deprecated\\ --")
dep = LAB / "_deprecated"
if dep.is_dir():
    for p in sorted(dep.iterdir()):
        say("   %-26s %8d bytes" % (p.name, p.stat().st_size))
else:
    say("   thu muc khong ton tai")

say("")
say("-- 8 muc KHONG CO MA trong tai lieu: co tren dia khong --")
for n in NO_SRC_IN_DOC:
    p = LAB / n
    say("   %-34s %s  %s" % (n, "CO " if p.exists() else "THIEU",
                             ("%d bytes" % p.stat().st_size) if p.exists() else ""))

say("")
say("=" * 78)
say("2. VENDOR KIT")
say("=" * 78)
V = LAB / "_vendor"
if not V.is_dir():
    say("   khong ton tai")
else:
    tot = 0
    nf = 0
    for p in V.rglob("*"):
        if p.is_file():
            tot += p.stat().st_size
            nf += 1
    say("   TONG: %.3f GB | %d file" % (tot / 1073741824, nf))
    for d in sorted(x for x in V.iterdir() if x.is_dir()):
        s = 0
        c = 0
        for p in d.rglob("*"):
            if p.is_file():
                s += p.stat().st_size
                c += 1
        sub = len([x for x in d.iterdir() if x.is_dir()])
        say("   %-16s %10.1f MB  %6d file  %5d thu muc con"
            % (d.name, s / 1048576, c, sub))
    for f in sorted(x for x in V.iterdir() if x.is_file()):
        say("   %-40s %10.2f MB" % (f.name, f.stat().st_size / 1048576))
    for n in EXPECT_VENDOR:
        say("   mong doi %-24s -> %s" % (n, (V / n).exists()))

say("")
say("=== CACHE HIEU UNG DANG SONG ===")
if CACHE.is_dir():
    top = [x for x in CACHE.iterdir() if x.is_dir()]
    allf = [x for x in CACHE.rglob("*") if x.is_file()]
    md5f = set(x.name for x in allf if re.fullmatch(r"[0-9a-f]{32}", x.name))
    say("   %s" % CACHE)
    say("   thu muc goc: %d | tong file: %d | file ten md5 duy nhat: %d"
        % (len(top), len(allf), len(md5f)))
else:
    say("   KHONG THAY")

say("")
say("=" * 78)
say("3. BYTES TREN MOI SEGMENT  (so quyet dinh kien truc)")
say("=" * 78)
say("%-14s %6s %6s %10s %10s %9s %s"
    % ("project", "vseg", "aseg", "root_KB", "nested_KB", "B/seg", "ghi chu"))
for d in sorted(DR.iterdir(), key=lambda p: -p.stat().st_mtime):
    if not d.is_dir():
        continue
    root = d / "draft_content.json"
    if not root.exists():
        continue
    pj = d / "Timelines" / "project.json"
    nested = None
    if pj.exists():
        try:
            tid = json.loads(pj.read_text(encoding="utf-8"))["main_timeline_id"]
            c = d / "Timelines" / tid / "draft_content.json"
            if c.exists():
                nested = c
        except Exception:
            pass
    src = nested if nested else root
    try:
        j = json.loads(src.read_text(encoding="utf-8"))
    except Exception as e:
        say("%-14s  LOI DOC: %s" % (d.name, e))
        continue
    vs = asg = 0
    for t in j.get("tracks", []):
        n = len(t.get("segments") or [])
        if t.get("type") == "video":
            vs += n
        elif t.get("type") == "audio":
            asg += n
    if vs == 0:
        src = root
        j = json.loads(root.read_text(encoding="utf-8"))
        for t in j.get("tracks", []):
            n = len(t.get("segments") or [])
            if t.get("type") == "video":
                vs += n
            elif t.get("type") == "audio":
                asg += n
    kbr = root.stat().st_size / 1024
    kbn = nested.stat().st_size / 1024 if nested else 0
    per = (src.stat().st_size / vs) if vs else 0
    feats = []
    m = j.get("materials", {})
    for b in ("transitions", "material_animations", "video_effects", "effects"):
        if m.get(b):
            feats.append("%s=%d" % (b[:5], len(m[b])))
    nkf = sum(len(s.get("common_keyframes") or [])
              for t in j.get("tracks", []) if t.get("type") == "video"
              for s in (t.get("segments") or []))
    if nkf:
        feats.append("kf=%d" % nkf)
    say("%-14s %6d %6d %10.1f %10.1f %9.0f %s"
        % (d.name[:14], vs, asg, kbr, kbn, per, " ".join(feats)))

say("")
say("=== NGOAI SUY 300 SHOT ===")
say("   Lay B/seg lon nhat o bang tren (project day du tinh nang) nhan 300.")
say("   Neu ket qua ~3 MB thi bai toan bac hai KHONG dang lo.")
say("   Neu ~30 MB thi phai doi kien truc ngay.")

(OUT / "audit_kit.txt").write_text("\n".join(L), encoding="utf-8")
print("\nDa ghi: %s" % (OUT / "audit_kit.txt"))