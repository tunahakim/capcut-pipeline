#!/usr/bin/env python3
"""
migrate.py - dung cay thu muc moi cho du an CapCut pipeline.

CHEP, KHONG xoa gi o nguon. Mac dinh chi bao cao.
  python migrate.py                      bao cao
  python migrate.py --apply              chep that
  python migrate.py --apply --move-big   DI CHUYEN _vendor va *.mp4 thay vi chep
Idempotent: chay lai nhieu lan cho cung ket qua.
"""
import json, os, pathlib, re, shutil, sys

SRC  = pathlib.Path(r"D:\Test_tool")
ROOT = pathlib.Path(r"D:\IT\CapCut")
REPO = ROOT / "capcut-pipeline"
DATA = ROOT / "data"
VEND = ROOT / "vendor"

APPLY    = "--apply" in sys.argv
MOVE_BIG = "--move-big" in sys.argv

SCRIPTS_V1 = ["kb_apply.py", "filter_apply.py", "strip_filters.py", "clone_project.py",
              "patchpath.py", "fx_audit.py", "check_sync.py", "diff_timing.py",
              "find_ph.py", "snap.py", "grab_frames.py", "tr_profile3.py",
              "parity_build.py"]
TOOLS      = ["oracle_read.py", "v4_mold.py", "syntax.py", "enum_list.py",
              "fx_list.py", "filt_enum.py", "cache_probe.py", "preflight.py",
              "audit_kit.py"]
DEAD       = ["session.ps1", "pack_vendor.ps1", "patch_v8.py", "tr_uncached.py",
              "lab_patch.py", "chk_fx.py", "migrate.py"]

SKELETON = [
    REPO / "pipeline" / "core", REPO / "pipeline" / "capcut",
    REPO / "scripts_v1", REPO / "tools", REPO / "tests",
    REPO / "molds" / "capcut-9.1.0", REPO / "reference",
    REPO / "docs" / "legacy" / "older", REPO / "_deprecated" / "backups",
    DATA / "exports", DATA / "perf",
    DATA / "scaffold", DATA / "archive" / "draft-copies",
    DATA / "archive" / "duplicates", DATA / "archive" / "misc",
    VEND,
]

RULES = []
for n in SCRIPTS_V1: RULES.append((n, REPO / "scripts_v1", False, False))
for n in TOOLS:      RULES.append((n, REPO / "tools",      False, False))
for n in DEAD:       RULES.append((n, REPO / "_deprecated", False, False))
RULES += [
    ("_deprecated",       REPO / "_deprecated",                  True,  False),
    ("enums_backup.json", REPO / "reference",                    False, False),
    ("describe.json",     REPO / "reference",                    False, False),
    ("Test_tool_v3",      DATA / "Test_tool_v3",                 True,  False),
    ("snapshots",         DATA / "snapshots",                    True,  False),
    ("frames",            DATA / "frames",                       True,  False),
    ("perf",              DATA / "perf",                         True,  False),
    ("oracle_dump.json",  DATA,                                  False, False),
    ("testV3_CLEAN",      DATA / "scaffold" / "testV3_CLEAN",    True,  False),
    ("v2oracle_CLEAN",    DATA / "scaffold" / "v2oracle_CLEAN",  True,  False),
    ("v2oracle_KF",       DATA / "archive" / "draft-copies" / "v2oracle_KF",     True, False),
    ("v2oracle_ORACLE",   DATA / "archive" / "draft-copies" / "v2oracle_ORACLE", True, False),
    ("Test_A_Basic",      DATA / "archive" / "draft-copies" / "Test_A_Basic",    True, False),
    ("Test_tool_v2",      DATA / "archive" / "duplicates" / "Test_tool_v2",      True, False),
    ("spec_a.json",       DATA / "archive" / "misc",             False, False),
    ("kf_plan.json",      DATA / "archive" / "misc",             False, False),
    ("root_meta_info.json", DATA / "archive" / "misc",           False, False),
    ("FolderTree_Clean.txt", DATA / "archive" / "misc",          False, False),
    ("shots.csv",         DATA / "archive" / "duplicates",       False, False),
    ("audio.mp3",         DATA / "archive" / "duplicates",       False, False),
    ("video1.srt",        DATA / "archive" / "duplicates",       False, False),
    ("_vendor",           VEND,                                  True,  True),
    ("export_v4.mp4",     DATA / "exports",                      False, True),
    ("test_output.mp4",   DATA / "exports",                      False, True),
    ("b1.mp4",            DATA / "exports",                      False, True),
]
for p in sorted(SRC.glob("Shot_0*.png")):
    RULES.append((p.name, DATA / "archive" / "duplicates", False, False))
for p in sorted(SRC.glob("*.v8bak")):
    RULES.append((p.name, REPO / "_deprecated" / "backups", False, False))

SPECIAL = {"Docs", "mold_filter.json"}


def size_of(p):
    if p.is_file():
        return p.stat().st_size
    t = 0
    for r, _, fs in os.walk(p):
        for f in fs:
            try:
                t += os.path.getsize(os.path.join(r, f))
            except OSError:
                pass
    return t


def human(b):
    return "%8.1f MB" % (b / 1024 ** 2)


print("NGUON : %s" % SRC)
print("DICH  : %s" % ROOT)
print("che do: %s%s\n" % ("GHI THAT" if APPLY else "BAO CAO (them --apply de chep)",
                          "  [--move-big]" if MOVE_BIG else ""))
if not SRC.is_dir():
    sys.exit("Khong thay thu muc nguon.")

known, plan, total = set(), [], 0
for name, dest, isdir, big in RULES:
    s = SRC / name
    known.add(name)
    if not s.exists():
        continue
    sz = size_of(s)
    total += sz
    plan.append((s, dest, isdir, big, sz))

stray = [p for p in sorted(SRC.iterdir())
         if p.name not in known and p.name not in SPECIAL]

print("=" * 76)
print("KE HOACH CHEP (%d muc, %s)" % (len(plan), human(total)))
print("=" * 76)
for s, dest, isdir, big, sz in plan:
    tag = "  [LON]" if big else ""
    print("  %-26s -> %-46s %s%s"
          % (s.name[:26], str(dest.relative_to(ROOT))[:46], human(sz), tag))

print("\n  Docs\\  -> docs\\legacy\\  (09 thanh v0.8-full.md, con lai vao older\\)")
print("  mold_filter.json -> molds\\capcut-9.1.0\\filter.json")

if stray:
    print("\n" + "=" * 76)
    print("CHUA PHAN LOAI (%d) - se chep vao data\\archive\\_inbox\\" % len(stray))
    print("=" * 76)
    for p in stray:
        print("  %-40s %s" % (p.name[:40], human(size_of(p))))

free = shutil.disk_usage(ROOT.drive + "\\").free
print("\n  O %s con trong: %.2f GB | can them: %.2f GB"
      % (ROOT.drive, free / 1024 ** 3, total / 1024 ** 3))
if free < total * 1.2:
    sys.exit("  *** KHONG DU CHO. Dung lai. ***")

print("\n" + "=" * 76)
print("SCRIPT V1 DANG MONG DOI THU MUC CON NAO CUA CAPCUT_LAB")
print("=" * 76)
pat = re.compile(r'LAB\s*/\s*["\']([^"\']+)["\']')
want = {}
for n in SCRIPTS_V1 + TOOLS:
    f = SRC / n
    if not f.exists():
        continue
    for m in pat.findall(f.read_text(encoding="utf-8", errors="replace")):
        want.setdefault(m, []).append(n)
if want:
    for k in sorted(want):
        _fut = set()
        for _n, _d, _isd, _b in RULES:
            _fut.add(str(_d if _isd else _d / _n).lower())
        have = (DATA / k).exists() or str(DATA / k).lower() in _fut
        print("  LAB/%-18s %-40s %s" % (k, ",".join(sorted(set(want[k])))[:40],
                                        "se co" if have else "*** SE THIEU ***"))
else:
    print("  (khong script nao dung mau LAB / \"...\")")
print("\n  => CAPCUT_LAB moi = %s" % DATA)

if not APPLY:
    print("\n(chua chep gi. Them --apply de thuc thi)")
    sys.exit()

print("\n" + "=" * 76)
print("DANG CHEP")
print("=" * 76)
for d in SKELETON:
    d.mkdir(parents=True, exist_ok=True)

for s, dest, isdir, big, sz in plan:
    if isdir:
        dest.mkdir(parents=True, exist_ok=True)
        if big and MOVE_BIG:
            for item in list(s.iterdir()):
                tgt = dest / item.name
                if not tgt.exists():
                    shutil.move(str(item), str(tgt))
        else:
            shutil.copytree(s, dest, dirs_exist_ok=True)
    else:
        dest.mkdir(parents=True, exist_ok=True)
        tgt = dest / s.name
        if big and MOVE_BIG:
            if not tgt.exists():
                shutil.move(str(s), str(tgt))
        else:
            shutil.copy2(s, tgt)
    print("  ok  %s" % s.name)

docs_src = SRC / "Docs"
if docs_src.is_dir():
    for f in sorted(docs_src.iterdir()):
        if not f.is_file():
            continue
        if f.name.startswith("09."):
            shutil.copy2(f, REPO / "docs" / "legacy" / "v0.8-full.md")
            print("  ok  %s -> docs/legacy/v0.8-full.md" % f.name)
        else:
            shutil.copy2(f, REPO / "docs" / "legacy" / "older" / f.name)
    print("  ok  Docs/")

mf = SRC / "mold_filter.json"
if mf.exists():
    shutil.copy2(mf, REPO / "molds" / "capcut-9.1.0" / "filter.json")
    print("  ok  mold_filter.json -> molds/capcut-9.1.0/filter.json")

for n in ("snap.py", "run.py"):
    f = SRC / "Test_tool_v2" / n
    if f.exists():
        shutil.copy2(f, REPO / "_deprecated" / ("Test_tool_v2__" + n))
        print("  ok  Test_tool_v2/%s -> _deprecated/" % n)

if stray:
    inbox = DATA / "archive" / "_inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    for p in stray:
        tgt = inbox / p.name
        if p.is_dir():
            shutil.copytree(p, tgt, dirs_exist_ok=True)
        else:
            shutil.copy2(p, tgt)
        print("  ok  [inbox] %s" % p.name)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print("  giu nguyen (da co): %s" % path.relative_to(ROOT))
        return
    path.write_text(text, encoding="utf-8")
    print("  sinh: %s" % path.relative_to(ROOT))


print("\n" + "=" * 76)
print("SINH FILE KHUNG")
print("=" * 76)

write(REPO / ".gitignore", """\
config.json
__pycache__/
*.pyc
*.bak
*.prepost
*.pathbak
*.kfbak
*.labbak
*.v8bak
*.log
*.mp4
*.mov
*.tmp
.vscode/
.idea/
""")

write(REPO / ".gitattributes", """\
* text=auto eol=lf
*.png binary
*.jpg binary
*.mp4 binary
*.tgz binary
""")

for p in (REPO / "pipeline", REPO / "pipeline" / "core", REPO / "pipeline" / "capcut"):
    write(p / "__init__.py", '"""Xem docs/model.md."""\n')
for p in (REPO / "tests", REPO / "scripts_v1", REPO / "tools"):
    (p / ".gitkeep").touch(exist_ok=True)

write(REPO / "config.example.json", json.dumps({
    "_doc": "Chep file nay thanh config.json roi sua. config.json bi gitignore.",
    "paths": {
        "data_root":   str(DATA).replace("\\", "/"),
        "vendor_root": str(VEND).replace("\\", "/"),
        "drafts_dir":  "%LOCALAPPDATA%/CapCut/User Data/Projects/com.lveditor.draft",
        "cache_dir":   "%LOCALAPPDATA%/CapCut/User Data/Cache/effect",
        "scaffold":    str(DATA / "scaffold" / "testV3_CLEAN").replace("\\", "/"),
        "ffmpeg": "ffmpeg", "ffprobe": "ffprobe", "capcut_cli": "capcut"
    },
    "canvas": {"width": 1920, "height": 1080, "fps": 30},
    "source_image": {"width": 1376, "height": 768, "normalize_to_canvas": False},
    "kenburns": {"seed": 20260730, "scale_min": 0.72, "scale_max": 0.92,
                 "amplitude_factor": 0.55, "margin_safety": 0.98},
    "canvas_blur": {"enabled": True, "level": 3},
    "transitions": {
        "enabled": True, "default_duration_us": 466666,
        "require_is_overlap_false": True,
        "whitelist": ["dissolve", "black-fade", "blur", "gradient-wipe", "dissolve-ii",
                      "page-turning", "glitch", "whirlpool", "split", "flip-ii", "shutter"],
        "blacklist": ["cube"]},
    "scene_effect": {"enabled": True, "slug": "retro-film", "intensity": 0.6},
    "filters": {"enabled": False, "items": [
        {"name": "Film", "resource_id": "6706773528319906308", "value": 0.7}]},
    "runtime": {"strategy": "hybrid",
                "_note": "cli | hybrid | stamp - chot sau khi do hieu nang"}
}, ensure_ascii=False, indent=2))

write(REPO / "run.bat", """\
@echo off
set CAPCUT_LAB=%~dp0..\\data
python "%~dp0pipeline\\cli.py" %*
""")

write(REPO / "README.md", """\
# capcut-pipeline

Tu dong hoa dung video documentary dai 55-70 phut bang CapCut Desktop 9.1.0
va capcut-cli 0.15.0. Chay tren Windows, chi dung thu vien chuan cua Python.

## Doc gi truoc

| File | Tra loi cau hoi |
|---|---|
| `docs/model.md` | CapCut luu du lieu the nao, ai doc file nao |
| `docs/reference.md` | Hang so, cong thuc, catalogue, danh sach den |
| `docs/failures.md` | Cach nao KHONG chay va vi sao. Doc truoc khi thu gi moi |
| `docs/procedures.md` | Quy trinh dung mot video, probe parity, dung may moi |
| `docs/research-log.md` | Nhat ky theo ngay |
| `docs/legacy/v0.8-full.md` | Ban day du cu, nguon de di tru dan |

## Cay thu muc

    pipeline/     code moi (dang xay)
    scripts_v1/   script dang chay that, thay dan sang pipeline/
    tools/        script nghien cuu, KHONG thuoc runtime
    molds/        khuon JSON chup tu CapCut, phan theo phien ban
    reference/    enums_backup.json, describe.json
    tests/        kiem bat bien, chay duoi 1 phut, khong can mo CapCut
    _deprecated/  code da chet, giu lam tai lieu

Du lieu KHONG nam trong repo. Anh, audio, snapshot, ban export o `../data`;
bo cai CapCut va cache hieu ung o `../vendor`.

## Bat dau

    copy config.example.json config.json
    (sua duong dan trong config.json)
    set CAPCUT_LAB=D:\\IT\\CapCut\\data

## Ba luat khong duoc pha

1. Tat han CapCut truoc moi lenh ghi. `Get-Process *CapCut*` phai rong.
2. Chay het lenh CLI roi moi den lop Python. Khong xen ke.
3. Moi thay doi bang Python phai propagate ra CA BON file draft.
""")

write(REPO / "_deprecated" / "README.md", """\
# _deprecated

Code da chet, van commit vi ma sai kem ghi chu la tai lieu. Ba lan phai dieu tra
lai mot ket luan cu deu vi khong con dau vet cua duong da di.

| File | Chet vi | Thay bang |
|---|---|---|
| migrate.py | script MOT LAN, dung de dung cay thu muc nay | khong con can |
| patch_v8.py | script va MOT LAN, da chay xong 29/07 22:47 | khong con can |
| tr_uncached.py | vong luan quan: dung md5 tu enums.json de xac dinh "chua cache", ma md5 do chinh la thu bi bac bo | viet lai theo huong chup cache truoc/sau |
| lab_patch.py | khong con duong dan ghi cung de va | test kiem duong dan tuyet doi |
| chk_fx.py | fx_audit.py bao gom day du | fx_audit.py |
| session.ps1 | bo PowerShell | run.bat + config.json |
| pack_vendor.ps1 | bo PowerShell; con loi robocopy khong xoa file cu o dich | scripts/pack_vendor.py |
| v4_apply.py | rat co the chinh no da dung testV4 | kb_apply.py |
| kf_inject.py | khong co lop kiem bien | kb_apply.py |
| tr_profile.py, tr_profile2.py | do bang md5, khong phan biet duoc cat cung | tr_profile3.py |
| v3_apply.py, v3_apply2.py, set_scale.py, fix_canvas.py, propagate.py | gop lai | kb_apply.py |
| chkpath.py | ban cu | patchpath.py |
| v3_check.py, v3_fx.py | ban cu | check_sync.py, fx_audit.py |
| v4_fx.py | hardcode ten snapshot, in bang timing SAI o moi lan chay sau | check_sync.py |
| make_video.py | ban FFmpeg thuan | giu lam phuong an du phong |
""")

write(REPO / "molds" / "capcut-9.1.0" / "_README.md", """\
# Khuon material - CapCut 9.1.0

Moi file la mot material do CHINH CAPCUT ghi ra (phep thu oracle), dung lam khuon
de Python dap lai. Phan thu muc theo phien ban CapCut vi schema co the doi.

Cach chup khuon moi: tao doi tuong bang tay trong GUI, dong CapCut bang nut X,
chay `tools/v4_mold.py <project>`, roi luu ket qua vao day.

| File | Nguon | Trang thai |
|---|---|---|
| filter.json | GUI tha filter "Film", 28/07 | da dung trong filter_apply.py |

Con thieu: transition, canvas_blur, video_segment, audio_segment,
material_animation, scene_effect, track cua tung loai.
""")

for n, title in (("model", "CapCut hoat dong the nao"),
                 ("reference", "Hang so, cong thuc, catalogue"),
                 ("failures", "Cach nao KHONG chay va vi sao"),
                 ("procedures", "Quy trinh"),
                 ("research-log", "Nhat ky nghien cuu")):
    write(REPO / "docs" / (n + ".md"),
          "# %s\n\nCHUA DI TRU. Xem `legacy/v0.8-full.md`.\n" % title)

rows = []
for folder, label in ((REPO / "scripts_v1", "scripts_v1"),
                      (REPO / "tools", "tools"),
                      (REPO / "_deprecated", "_deprecated")):
    for f in sorted(folder.glob("*.py")) + sorted(folder.glob("*.ps1")):
        rows.append("| `%s/%s` | %.1f KB | |" % (label, f.name, f.stat().st_size / 1024))
write(REPO / "docs" / "scripts.md",
      "# Danh muc script\n\nSinh tu dong boi `migrate.py`. Cot cuoi dien tay: "
      "script lam gi, hop dong dau vao/ra, muc bang chung.\n\n"
      "| File | KB | Mo ta |\n|---|---|---|\n" + "\n".join(rows) + "\n")

print("\n" + "=" * 76)
print("XONG - viec con phai lam tay")
print("=" * 76)
print("""
1. Kiem tra cay moi:  explorer %s
2. Dat bien moi truong (mo lai PowerShell thi moi co hieu luc):
     setx CAPCUT_LAB "%s"
3. Chay thu mot script v1 de xac nhan khong gay
4. Khoi tao git trong %s
5. NGUON D:\\Test_tool VAN CON NGUYEN, chua xoa gi
""" % (ROOT, DATA, REPO))