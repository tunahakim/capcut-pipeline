#!/usr/bin/env python3
"""preflight.py - kiểm tra môi trường trước khi refactor, chỉ đọc và không sửa gì.
Hai cách chạy: không tham số thì kiểm đầy đủ và có tính dung lượng thư mục, còn --fast thì bỏ qua phần tính dung lượng nên nhanh hơn.
Ghi chú: lệnh doctor trong docs/TODO.md sẽ thay hẳn script này, vì doctor đọc file khai phiên bản ghim rồi đối chiếu thứ đang cài và từ chối chạy khi lệch.
[KIEM: chua]
"""
import os, sys, shutil, subprocess, pathlib, platform

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LAB    = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
TARGET = pathlib.Path(r"D:\IT\CapCut")
FAST   = "--fast" in sys.argv
BLOCK, WARN = [], []


def run(cmd, timeout=30):
    try:
        # enc: tu decode
        p = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
        out = (p.stdout + b"\n" + p.stderr).decode("utf-8", errors="replace").strip()
        return p.returncode, out
    except Exception as e:
        return -1, "LOI: %s" % e


def first(s):
    return (s or "").splitlines()[0].strip() if s else "(rong)"


def head(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


def line(label, value, status=""):
    print("  %-26s %-38s %s" % (label, str(value)[:38], status))


def dsize(p):
    n = tot = 0
    for root, dirs, files in os.walk(p):
        for f in files:
            try:
                tot += os.path.getsize(os.path.join(root, f))
                n += 1
            except Exception:
                pass
    return n, tot


print("preflight.py  |  %s  |  %s" % (platform.platform(), platform.machine()))

# ---------------------------------------------------------------- PYTHON
head("1. PYTHON")
line("version", sys.version.split()[0])
line("executable", sys.executable)
if "WindowsApps" in sys.executable:
    WARN.append("Python la ban Microsoft Store (WindowsApps). Tai lieu XI.5 khuyen "
                "dung ban python.org. Hien tai van chay duoc, nhung neu gap loi quyen "
                "ghi file thi day la nghi can dau tien.")
    line("nguon", "Microsoft Store", "<-- CANH BAO")
else:
    line("nguon", "khong phai Store", "OK")
rc, out = run("pip --version")
line("pip", first(out) if rc == 0 else "khong co", "OK" if rc == 0 else "(khong bat buoc)")

# ---------------------------------------------------------------- NODE
head("2. NODE / CAPCUT-CLI")
for cmd, label in (("node --version", "node"), ("npm --version", "npm"),
                   ("capcut version", "capcut-cli")):
    rc, out = run(cmd)
    line(label, first(out) if rc == 0 else "KHONG TIM THAY",
         "OK" if rc == 0 else "<-- THIEU")
    if rc != 0 and label != "capcut-cli":
        WARN.append("%s khong goi duoc. Can cho giai doan do hieu nang." % label)
rc, out = run("capcut doctor -H")
if rc == 0:
    for k in ("Version:", "Support:", "Write guard:", "Schema int:"):
        for l in out.splitlines():
            if l.strip().startswith(k):
                line("doctor " + k.strip(":"), l.split(":", 1)[1].strip())
else:
    WARN.append("capcut doctor khong chay duoc.")

# ---------------------------------------------------------------- FFMPEG
head("3. FFMPEG")
for cmd, label in (("ffmpeg -version", "ffmpeg"), ("ffprobe -version", "ffprobe")):
    rc, out = run(cmd)
    line(label, first(out)[:38] if rc == 0 else "KHONG TIM THAY",
         "OK" if rc == 0 else "<-- THIEU")
    if rc != 0:
        WARN.append("%s khong co tren PATH." % label)

# ---------------------------------------------------------------- GIT
head("4. GIT")
rc, out = run("git --version")
has_git = rc == 0
line("git", first(out) if has_git else "KHONG TIM THAY", "OK" if has_git else "<-- CHAN")
if not has_git:
    BLOCK.append("Chua co Git tren PATH. Cai Git for Windows: "
                 "winget install --id Git.Git -e")
else:
    for key, want, note in (
            ("user.name",          None,    "phai co, dung cho commit"),
            ("user.email",         None,    "phai co, dung cho commit"),
            ("core.autocrlf",      "false", "de false + .gitattributes ep LF"),
            ("core.longpaths",     "true",  "bat de tranh loi duong dan >260 ky tu"),
            ("init.defaultBranch", "main",  "dat main cho khop GitHub")):
        rc2, val = run("git config --global --get %s" % key)
        val = first(val) if rc2 == 0 and val else ""
        ok = bool(val) if want is None else (val == want)
        line(key, val or "(chua dat)", "OK" if ok else "<-- can chinh (%s)" % note)
        if not ok:
            WARN.append("git config --global %s %s" % (key, want or "<gia tri cua ban>"))

gd = pathlib.Path(os.environ["LOCALAPPDATA"]) / "GitHubDesktop"
line("GitHub Desktop", "da cai" if gd.is_dir() else "chua cai",
     "OK" if gd.is_dir() else "(tuy chon)")

# ---------------------------------------------------------------- WINDOWS
head("5. WINDOWS")
try:
    import winreg
    k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                       r"SYSTEM\CurrentControlSet\Control\FileSystem")
    v, _ = winreg.QueryValueEx(k, "LongPathsEnabled")
    line("LongPathsEnabled", v, "OK" if v == 1 else "<-- nen bat")
    if v != 1:
        WARN.append("LongPathsEnabled = 0. Cache effect long sau co the vuot 260 ky tu. "
                    "Bat bang PowerShell quyen Admin: Set-ItemProperty -Path "
                    "'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem' "
                    "-Name LongPathsEnabled -Value 1")
except Exception as e:
    line("LongPathsEnabled", "khong doc duoc", str(e)[:30])

rc, out = run('tasklist /FO CSV /NH')
running = [l.split(",")[0].strip('"') for l in out.splitlines()
           if "capcut" in l.lower()]
line("CapCut dang chay", running if running else "khong",
     "<-- PHAI TAT" if running else "OK")
if running:
    BLOCK.append("CapCut dang chay (%s). Tat han truoc khi lam bat cu viec gi."
                 % ", ".join(sorted(set(running))))

# ---------------------------------------------------------------- CAPCUT
head("6. CAPCUT")
la = pathlib.Path(os.environ["LOCALAPPDATA"]) / "CapCut"
apps = sorted((la / "Apps").glob("*")) if (la / "Apps").is_dir() else []
line("thu muc Apps", [p.name for p in apps] or "khong thay")
for app in apps:
    for n in ("CapCut-DiffUpgrade.exe", "hpatchz.exe"):
        f = app / n
        if f.exists():
            sz = f.stat().st_size
            line("  " + n, "%d byte" % sz,
                 "DA CHAN" if sz == 0 else "<-- CHUA CHAN")
        elif (app / (n + ".disabled")).exists():
            line("  " + n, "chi con .disabled", "DA CHAN")

cache = la / "User Data" / "Cache" / "effect"
if cache.is_dir():
    line("Cache/effect", "%d muc goc" % len(list(cache.iterdir())), "OK")
else:
    WARN.append("Khong thay Cache/effect.")

draft = la / "User Data" / "Projects" / "com.lveditor.draft"
if draft.is_dir():
    ps = [p for p in draft.iterdir() if p.is_dir()]
    line("so project draft", len(ps))
    for p in sorted(ps, key=lambda x: x.stat().st_mtime, reverse=True)[:6]:
        line("  " + p.name, "Timelines=%s" % (p / "Timelines").is_dir())

# ---------------------------------------------------------------- DISK
head("7. DUNG LUONG")
for d in ("C:\\", "D:\\"):
    try:
        t, u, f = shutil.disk_usage(d)
        gb = f / 1024 ** 3
        line(d, "trong %.2f GB / tong %.0f GB" % (gb, t / 1024 ** 3),
             "OK" if gb > 8 else "<-- SAT")
        if gb < 8:
            WARN.append("O %s chi con %.2f GB." % (d, gb))
    except Exception as e:
        line(d, "loi", str(e)[:30])

# ---------------------------------------------------------------- LAB
head("8. THU MUC LAM VIEC HIEN TAI")
line("LAB", LAB, "OK" if LAB.is_dir() else "<-- KHONG THAY")
if LAB.is_dir():
    py = sorted(p.name for p in LAB.glob("*.py"))
    ps = sorted(p.name for p in LAB.glob("*.ps1"))
    line("so file .py", len(py))
    line("so file .ps1", len(ps))
    for d in sorted(p for p in LAB.iterdir() if p.is_dir()):
        if FAST:
            line("  " + d.name + "\\", "(bo qua tinh dung luong)")
        else:
            n, t = dsize(d)
            line("  " + d.name + "\\", "%6d file  %8.1f MB" % (n, t / 1024 ** 2))
    big = [p for p in LAB.glob("*") if p.is_file() and p.stat().st_size > 50 * 1024 ** 2]
    for b in big:
        line("  file lon", "%s  %.1f MB" % (b.name, b.stat().st_size / 1024 ** 2),
             "<-- gitignore")

# ---------------------------------------------------------------- TARGET
head("9. DICH DEN")
line("D:\\IT", "co" if pathlib.Path(r"D:\IT").is_dir() else "chua co",
     "(script refactor se tao)")
line(str(TARGET), "co" if TARGET.exists() else "chua co",
     "<-- DA TON TAI, kiem tra truoc" if TARGET.exists() else "OK, san sang")
if TARGET.exists() and any(TARGET.iterdir()):
    BLOCK.append("%s da ton tai va KHONG rong. Doi ten hoac xoa truoc khi chay refactor."
                 % TARGET)

# ---------------------------------------------------------------- TONG KET
head("TONG KET")
if BLOCK:
    print("\nCHAN (%d) - phai xu ly truoc khi refactor:" % len(BLOCK))
    for i, b in enumerate(BLOCK, 1):
        print("  %d. %s" % (i, b))
else:
    print("\nKhong co gi CHAN.")
if WARN:
    print("\nCAN CHINH (%d):" % len(WARN))
    for i, w in enumerate(WARN, 1):
        print("  %d. %s" % (i, w))
else:
    print("Khong co canh bao.")
print("\nXong. Script nay khong sua gi ca.")