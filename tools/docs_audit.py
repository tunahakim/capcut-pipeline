#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/docs_audit.py -- kiem ke tai lieu: kich thuoc va tham chieu cheo.

  python tools/docs_audit.py                 # quet, in bao cao, ghi snapshot
  python tools/docs_audit.py --baseline      # quet va ghi de moc chuan
  python tools/docs_audit.py --compare       # so voi moc chuan, liet ke lien ket moi chet

Snapshot va bao cao ghi vao <CAPCUT_LAB>\perf\.
Console chi in ASCII de tranh loi encoding cua PowerShell 5.1.
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

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".idea", ".vscode", ".pytest_cache"}
NO_SCAN   = ("docs/legacy/",)
REPO_DIR_PREFIX = ("docs/", "tools/", "scripts_v1/", "pipeline/", "tests/",
                   "molds/", "reference/", "fixtures/", "_deprecated/")
EXTRA_VALIDATE = {"run.bat", "config.example.json"}
VALIDATE_EXT   = {".md", ".py"}

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
            p = Path(root) / f
            out.append(p.relative_to(REPO).as_posix())
    return sorted(out)


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8", errors="replace")


def headings(text):
    secs, titles = set(), []
    for ln in text.splitlines():
        m = HEAD_RE.match(ln)
        if not m:
            continue
        title = m.group(2).strip()
        titles.append((len(m.group(1)), title))
        s = SECNUM_RE.match(title)
        if s:
            num = s.group(1)
            secs.add(num)
            parts = num.split(".")
            for i in range(1, len(parts)):
                secs.add(".".join(parts[:i]))
    return secs, titles


def strip_fences(text):
    """Tra ve danh sach (lineno, line) da bo cac dong nam trong khoi rao ma."""
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
    """Tra ve (status, path_thuc). status: OK | OK-BASENAME | MISSING | INFO | MULTI"""
    t = norm(tok)
    if not t:
        return "INFO", ""
    ext = Path(t).suffix.lower()
    base = Path(t).name
    interesting = (ext in VALIDATE_EXT) or base in EXTRA_VALIDATE or t.startswith(REPO_DIR_PREFIX)
    if not interesting:
        return "INFO", ""
    cands = [t, (Path(src).parent / t).as_posix(), "docs/" + t]
    for c in cands:
        c = Path(c).as_posix().replace("//", "/")
        if c in index:
            return "OK", c
    hits = byname.get(base, [])
    if len(hits) == 1:
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
    sizes, heads = {}, {}
    for p in md_files:
        sizes[p] = (REPO / p).stat().st_size
        heads[p] = headings(read(p))[0]

    refs, romans = [], []
    for src in md_files:
        if src.startswith(NO_SCAN):
            continue
        text = read(src)
        for lineno, line in strip_fences(text):
            for rm in ROMAN_RE.finditer(line):
                romans.append({"src": src, "line": lineno, "roman": rm.group(1)})
            for m in TOKEN_RE.finditer(line):
                a, b = m.start(), m.end()
                prev = line[a - 1] if a > 0 else " "
                if prev in ":\\/" or "http" in line[max(0, a - 12):a]:
                    continue
                tok = m.group(0)
                before = line[:a].rstrip("`*_ ")
                after = line[b:].lstrip("`*_ ")
                muc = None
                ma = MUC_AFTER.match(after)
                mb = MUC_BEFORE.search(before)
                if ma:
                    muc = ma.group(1)
                elif mb:
                    muc = mb.group(1)
                st, tgt = resolve(tok, src, index, byname)
                if st == "INFO":
                    continue
                refs.append({"src": src, "line": lineno, "token": tok,
                             "status": st, "target": tgt, "muc": muc})

    problems = []
    for r in refs:
        if r["status"] == "MISSING":
            problems.append(("FILE THIEU", r["src"], r["line"], r["token"], ""))
        elif r["status"] == "MULTI":
            problems.append(("TRUNG TEN", r["src"], r["line"], r["token"], r["target"]))
        elif r["muc"] and r["target"].lower().endswith(".md"):
            if r["muc"] not in heads.get(r["target"], set()):
                problems.append(("MUC THIEU", r["src"], r["line"],
                                 r["token"] + " muc " + r["muc"], r["target"]))

    referenced = {r["target"] for r in refs if r["target"]}
    orphans = [p for p in md_files
               if p not in referenced and not p.startswith(NO_SCAN) and p != "README.md"]

    return {"sizes": sizes, "refs": refs, "problems": problems,
            "romans": romans, "orphans": orphans,
            "when": datetime.datetime.now().isoformat(timespec="seconds")}


def report(d):
    print("")
    print("=== KICH THUOC (tran %d byte = 26 KB) ===" % BUDGET)
    print("%-42s %8s %7s  %s" % ("file", "byte", "KB", "trang thai"))
    for p, s in sorted(d["sizes"].items(), key=lambda kv: -kv[1]):
        if p.startswith(NO_SCAN):
            tag = "mien tru (legacy)"
        elif s > BUDGET:
            tag = "VUOT %d%%" % round(s * 100.0 / BUDGET)
        else:
            tag = "ok %d%%" % round(s * 100.0 / BUDGET)
        print("%-42s %8d %7.1f  %s" % (p, s, s / 1024.0, tag))

    md = sum(1 for r in d["refs"] if r["target"].lower().endswith(".md"))
    py = sum(1 for r in d["refs"] if r["token"].lower().endswith(".py"))
    print("")
    print("=== TONG QUAN ===")
    print("file .md quet ref : %d" % len([p for p in d["sizes"] if not p.startswith(NO_SCAN)]))
    print("tham chieu bat duoc: %d  (toi .md: %d, toi .py: %d)" % (len(d["refs"]), md, py))
    print("tham chieu kieu La Ma (tro v0.8-full): %d" % len(d["romans"]))

    print("")
    print("=== VAN DE (%d) ===" % len(d["problems"]))
    if not d["problems"]:
        print("khong co")
    for kind, src, line, tok, extra in d["problems"]:
        print("[%-10s] %s:%d  -> %s %s" % (kind, src, line, tok, extra))

    print("")
    print("=== MA TRAN NGUON -> DICH (.md) ===")
    mat = {}
    for r in d["refs"]:
        if r["target"].lower().endswith(".md"):
            mat.setdefault(r["src"], {})
            mat[r["src"]][r["target"]] = mat[r["src"]].get(r["target"], 0) + 1
    for src in sorted(mat):
        items = sorted(mat[src].items(), key=lambda kv: -kv[1])
        print("%-30s -> %s" % (Path(src).name,
              ", ".join("%s x%d" % (Path(k).name, v) for k, v in items)))

    print("")
    print("=== FILE .md KHONG AI TRO TOI (%d) ===" % len(d["orphans"]))
    for p in d["orphans"]:
        print("  " + p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--compare", action="store_true")
    a = ap.parse_args()

    PERF.mkdir(parents=True, exist_ok=True)
    d = scan()
    report(d)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    snap = PERF / ("docs_xref_%s.json" % ts)
    snap.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    base = PERF / "docs_xref_baseline.json"
    if a.baseline:
        base.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    print("")
    print("snapshot: %s" % snap)
    if a.baseline:
        print("moc chuan: %s" % base)

    if a.compare:
        print("")
        print("=== SO VOI MOC CHUAN ===")
        if not base.exists():
            print("chua co moc chuan, chay --baseline truoc")
        else:
            old = json.loads(base.read_text(encoding="utf-8"))
            ok = {(p[0], p[1], p[3]) for p in old["problems"]}
            nw = {(p[0], p[1], p[3]) for p in d["problems"]}
            gone = sorted(ok - nw)
            fresh = sorted(nw - ok)
            print("van de moc chuan: %d | hien tai: %d" % (len(ok), len(nw)))
            print("-- MOI CHET (%d) --" % len(fresh))
            for x in fresh:
                print("  %s  %s  %s" % x)
            print("-- DA CHUA (%d) --" % len(gone))
            for x in gone:
                print("  %s  %s  %s" % x)


if __name__ == "__main__":
    main()