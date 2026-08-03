#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/docs_audit.py -- kiem ke tai lieu: kich thuoc va tham chieu cheo.

  python tools/docs_audit.py                 # quet, in bao cao, ghi snapshot
  python tools/docs_audit.py --baseline      # quet va ghi de moc chuan
  python tools/docs_audit.py --compare       # so voi moc chuan
  python tools/docs_audit.py --brief         # bo ma tran, chi in file gan tran

Snapshot ghi vao <CAPCUT_LAB>/perf/. Console chi in ASCII.

Phan loai tham chieu. OK la file co that, dung duong dan. PLANNED la file da len ke
hoach nhung chua viet. NGOAI la duong dan co y tro ra ngoai repo, vi du script dung
mot lan trong CAPCUT_LAB. LICHSU la file da xoa ma tai lieu nhac lai nhu qua khu.
LUUTRU la file da chuyen vao
_deprecated/ sau khi cau van duoc viet, ma nhat ky chi ghi them nen khong sua lai.
Nam loai do khong tinh la loi. Loi gom FILE THIEU, TRUNG TEN, MUC THIEU va SAI CHO;
SAI CHO nghia la file co that nhung nam khac duong dan ma tai lieu ghi.
"""
import os, re, sys, json, argparse, datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parents[1]
LAB  = Path(os.environ.get("CAPCUT_LAB") or (Path(__file__).resolve().parents[2] / "data"))
PERF = LAB / "perf"
BUDGET = 26 * 1024
PER_FILE_BUDGET = {"docs/STATE.md": 10 * 1024, "docs/TODO.md": 12 * 1024}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".idea", ".vscode", ".pytest_cache"}
NO_SCAN   = ("docs/legacy/",)
REPO_DIR_PREFIX = ("docs/", "tools/", "scripts_v1/", "pipeline/", "tests/",
                   "molds/", "reference/", "fixtures/", "_deprecated/", "artifacts/")
EXTRA_VALIDATE = {"run.bat", "config.example.json"}
VALIDATE_EXT   = {".md", ".py"}

# token la vi du, placeholder, hoac co y noi toi file KHONG ton tai
IGNORE = {"file.py", "__init__.py", "capcut_post.py", "scan_paths.py",
          "scripts/pack_vendor.py", "x.mp4", "operations.jsonl"}
# file da len ke hoach nhung chua viet -- bao rieng, khong tinh la loi
PLANNED = {"docs/scripts-archive.md", "tools/shots_dump.py", "tools/data_manifest.py",
           "tools/docs_size.py", "tools/probe_drafts.py"}
# duong dan co y nam NGOAI repo: thu muc lab CAPCUT_LAB, noi de script dung mot lan
EXTERNAL_PREFIX = ("data/",)
# file da tung ton tai roi bi xoa; tai lieu nhac lai lich su, khong phai lien ket hong
HISTORICAL = {"docs/research-log.md"}

TOKEN_RE   = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_\-./\\]*\.[A-Za-z][A-Za-z0-9]{0,4}")
FENCE_RE   = re.compile(r"^\s*```")
HEAD_RE    = re.compile(r"^(#{1,6})\s+(.*)$")
SECNUM_RE  = re.compile(r"^\**\s*(\d+(?:\.\d+)*)\s*\.?\s")
MUC_AFTER  = re.compile(r"^\W{0,4}(?:m\u1ee5c|muc)\s*(\d+(?:\.\d+)*)", re.IGNORECASE)
MUC_BEFORE = re.compile(r"(?:m\u1ee5c|muc)\s*(\d+(?:\.\d+)*)\s+(?:c\u1ee7a|cua|trong|\u1edf)\s*\W{0,3}$", re.IGNORECASE)
ROMAN_RE   = re.compile(r"(?:m\u1ee5c|muc|ph\u1ea7n|phan|ph\u1ee5 l\u1ee5c|phu luc)\s+([IVXL]+(?:\.\d+)*)", re.IGNORECASE)


def walk_repo():
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            out.append((Path(root) / f).relative_to(REPO).as_posix())
    return sorted(out)


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8", errors="replace")


def headings(text):
    secs = set()
    for ln in text.splitlines():
        m = HEAD_RE.match(ln)
        if not m:
            continue
        s = SECNUM_RE.match(m.group(2).strip())
        if s:
            num = s.group(1)
            secs.add(num)
            parts = num.split(".")
            for i in range(1, len(parts)):
                secs.add(".".join(parts[:i]))
    return secs


def strip_fences(text):
    out, inside = [], False
    for i, ln in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(ln):
            inside = not inside
            continue
        if not inside:
            out.append((i, ln))
    return out


def norm(tok):
    return tok.replace("\\", "/").strip("./").rstrip(".,;:)")


def resolve(tok, src, index, byname):
    t = norm(tok)
    if not t or t in IGNORE or Path(t).name in IGNORE:
        return "INFO", ""
    ext = Path(t).suffix.lower()
    base = Path(t).name
    if not ((ext in VALIDATE_EXT) or base in EXTRA_VALIDATE or t.startswith(REPO_DIR_PREFIX)):
        return "INFO", ""
    for c in (t, (Path(src).parent / t).as_posix(), "docs/" + t):
        c = Path(c).as_posix().replace("//", "/")
        if c in index:
            return "OK", c
    if t.startswith(EXTERNAL_PREFIX):
        return "NGOAI", ""
    if t in HISTORICAL:
        return "LICHSU", ""
    if t in PLANNED:
        return "PLANNED", ""
    hits = byname.get(base, [])
    if len(hits) == 1:
        if "/" in t and hits[0] != t:
            if hits[0].startswith("_deprecated/"):
                return "LUUTRU", ""
            return "SAI CHO", hits[0]
        return "OK-BASENAME", hits[0]
    if len(hits) > 1:
        return "MULTI", " | ".join(hits)
    return "MISSING", ""


def scan():
    index = set(walk_repo())
    byname = {}
    for p in index:
        byname.setdefault(Path(p).name, []).append(p)

    md_files = [p for p in index if p.lower().endswith(".md")]
    sizes = {p: (REPO / p).stat().st_size for p in md_files}
    heads = {p: headings(read(p)) for p in md_files}

    refs, romans = [], []
    for src in md_files:
        if src.startswith(NO_SCAN):
            continue
        for lineno, line in strip_fences(read(src)):
            for rm in ROMAN_RE.finditer(line):
                romans.append({"src": src, "line": lineno, "roman": rm.group(1)})
            for m in TOKEN_RE.finditer(line):
                a, b = m.start(), m.end()
                if (line[a - 1] if a > 0 else " ") in ":\\/" or "http" in line[max(0, a - 12):a]:
                    continue
                before = line[:a].rstrip("`*_ ")
                after = line[b:].lstrip("`*_ ")
                ma, mb = MUC_AFTER.match(after), MUC_BEFORE.search(before)
                muc = ma.group(1) if ma else (mb.group(1) if mb else None)
                st, tgt = resolve(m.group(0), src, index, byname)
                if st == "INFO":
                    continue
                refs.append({"src": src, "line": lineno, "token": m.group(0),
                             "status": st, "target": tgt, "muc": muc})

    problems, planned, ngoai = [], [], []
    for r in refs:
        if r["status"] == "PLANNED":
            planned.append((r["src"], r["line"], r["token"]))
        elif r["status"] in ("NGOAI", "LICHSU", "LUUTRU"):
            ngoai.append((r["src"], r["line"], r["token"], r["status"]))
        elif r["status"] == "SAI CHO":
            problems.append(("SAI CHO", r["src"], r["line"], r["token"],
                             "thuc te nam o " + r["target"]))
        elif r["status"] == "MISSING":
            problems.append(("FILE THIEU", r["src"], r["line"], r["token"], ""))
        elif r["status"] == "MULTI":
            problems.append(("TRUNG TEN", r["src"], r["line"], r["token"], r["target"]))
        elif r["muc"] and r["target"].lower().endswith(".md"):
            if r["muc"] not in heads.get(r["target"], set()):
                problems.append(("MUC THIEU", r["src"], r["line"],
                                 r["token"] + " muc " + r["muc"], r["target"]))

    for p, s in sorted(sizes.items()):
        if p.startswith(NO_SCAN):
            continue
        cap = PER_FILE_BUDGET.get(p, BUDGET)
        if s > cap:
            problems.append(("VUOT TRAN", p, 0, p,
                             "%d byte > tran %d byte" % (s, cap)))

    referenced = {r["target"] for r in refs if r["target"]}
    orphans = [p for p in md_files
               if p not in referenced and not p.startswith(NO_SCAN)]

    return {"sizes": sizes, "refs": refs, "problems": problems, "planned": planned,
            "ngoai": ngoai, "romans": romans, "orphans": orphans,
            "when": datetime.datetime.now().isoformat(timespec="seconds")}


def report(d, brief=False):
    print("")
    print("=== KICH THUOC ===")
    print("%-48s %8s %7s  %s" % ("file", "byte", "KB", "trang thai"))
    an = 0
    for p, s in sorted(d["sizes"].items(), key=lambda kv: -kv[1]):
        cap0 = PER_FILE_BUDGET.get(p, BUDGET)
        if brief and p not in PER_FILE_BUDGET and (
                p.startswith(NO_SCAN) or s <= cap0 * 0.70):
            an += 1
            continue
        cap = PER_FILE_BUDGET.get(p, BUDGET)
        if p.startswith(NO_SCAN):
            tag = "mien tru (legacy)"
        else:
            tag = ("VUOT %d%%" if s > cap else "ok %d%%") % round(s * 100.0 / cap)
            if p in PER_FILE_BUDGET:
                tag += " (tran rieng %d KB)" % (cap // 1024)
        print("%-48s %8d %7.1f  %s" % (p, s, s / 1024.0, tag))

    print("")
    if an:
        print("... %d file khac duoi 70%% tran, khong in (--brief)" % an)
        print("")
    print("=== TONG QUAN ===")
    print("file .md quet ref  : %d" % len([p for p in d["sizes"] if not p.startswith(NO_SCAN)]))
    print("tham chieu bat duoc: %d" % len(d["refs"]))
    print("tham chieu La Ma   : %d" % len(d["romans"]))
    print("tro toi file KE HOACH chua viet: %d" % len(d["planned"]))
    print("NGOAI repo, LICH SU, LUU TRU   : %d" % len(d.get("ngoai", [])))

    print("")
    print("=== VAN DE (%d) ===" % len(d["problems"]))
    if not d["problems"]:
        print("khong co -- sach")
    for kind, src, line, tok, extra in d["problems"]:
        print("[%-10s] %s:%d  -> %s %s" % (kind, src, line, tok, extra))

    print("")
    if brief:
        nsrc = len({r["src"] for r in d["refs"]
                    if r["target"].lower().endswith(".md")})
        print("ma tran: %d file nguon | mo coi: %d -- bo qua (--brief)"
              % (nsrc, len(d["orphans"])))
        return
    print("=== MA TRAN NGUON -> DICH (.md) ===")
    mat = {}
    for r in d["refs"]:
        if r["target"].lower().endswith(".md"):
            mat.setdefault(r["src"], {})
            mat[r["src"]][r["target"]] = mat[r["src"]].get(r["target"], 0) + 1
    for src in sorted(mat):
        items = sorted(mat[src].items(), key=lambda kv: -kv[1])
        print("%-46s -> %s" % (src, ", ".join("%s x%d" % (k, v) for k, v in items)))

    print("")
    print("=== FILE .md KHONG AI TRO TOI (%d) ===" % len(d["orphans"]))
    for p in d["orphans"]:
        print("  " + p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--brief", action="store_true")
    a = ap.parse_args()

    PERF.mkdir(parents=True, exist_ok=True)
    d = scan()
    report(d, brief=a.brief)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    snap = PERF / ("docs_xref_%s.json" % ts)
    snap.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    base = PERF / "docs_xref_baseline.json"
    if a.baseline:
        if d["problems"]:
            print("")
            print("KHONG ghi moc chuan: con %d van de, xem khoi VAN DE"
                  % len(d["problems"]))
        else:
            base.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                            encoding="utf-8")
            print("")
            print("moc chuan da ghi de: %s" % base)
    print("")
    print("snapshot: %s" % snap)

    if a.compare:
        print("")
        print("=== SO VOI MOC CHUAN ===")
        if not base.exists():
            print("chua co moc chuan, chay --baseline truoc")
        else:
            old = json.loads(base.read_text(encoding="utf-8"))
            ok = {(p[0], p[1], p[3]) for p in old["problems"]}
            nw = {(p[0], p[1], p[3]) for p in d["problems"]}
            print("moc chuan: %d van de | hien tai: %d" % (len(ok), len(nw)))
            print("-- MOI CHET (%d) --" % len(nw - ok))
            for x in sorted(nw - ok):
                print("  %s  %s  %s" % x)
            print("-- DA CHUA (%d) --" % len(ok - nw))
            for x in sorted(ok - nw):
                print("  %s  %s  %s" % x)
    return 2 if d["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())