#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/scripts_index.py -- kiem ke script va sinh bang mo ta cho docs/scripts.md.

  python tools/scripts_index.py           # bao cao, khong ghi gi
  python tools/scripts_index.py --write   # ghi lai hai vung giua moc trong docs/scripts.md

Mo ta lay tu docstring dau file, do la nguon su that duy nhat; bang chi la ban sinh ra.
Console in ASCII khong dau, file ghi UTF-8 khong BOM.
[KIEM: du lieu that]
"""
import ast, re, sys, unicodedata
from pathlib import Path

ROOT  = Path(__file__).resolve().parents[1]
LIVE  = ("scripts_v1", "tools")
ARCH  = ("_deprecated",)
EXTS  = (".py", ".ps1", ".bat")
DOC   = ROOT / "docs" / "scripts.md"
MARK  = {"live": ("<!-- scripts_index:begin:live -->", "<!-- scripts_index:end:live -->"),
         "arch": ("<!-- scripts_index:begin:arch -->", "<!-- scripts_index:end:arch -->")}
WRITE = "--write" in sys.argv

def scan(dirs):
    out = []
    for d in dirs:
        b = ROOT / d
        if not b.is_dir():
            continue
        for p in sorted(b.iterdir()):
            if p.is_file() and p.suffix.lower() in EXTS:
                out.append(p)
    return out

def doc_of(p):
    txt = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix.lower() == ".py":
        try:
            return ast.get_docstring(ast.parse(txt))
        except SyntaxError:
            return None
    out = []
    for ln in txt.splitlines()[:8]:
        t = ln.strip()
        if t.startswith("#"):
            t = t.lstrip("#").strip()
            if t:
                out.append(t)
        elif out:
            break
    return "\n".join(out) or None

KIEM_OK = ("du lieu that", "bo test", "mot lan", "chua")
KIEM_RE = re.compile(r"\[KIEM:\s*([^\]]*)\]")
QUY_UOC = ("Cot KIEM la muc kiem chung, khai bang hau to `[KIEM: ...]` dat o cuoi docstring dau file; script nao khong khai thi bang hien `chua`. Bon gia tri hop le: `du lieu that` da chay tren du lieu san xuat that, `bo test` da chay tren bo 8 shot hoac fixture, `mot lan` moi chay dung mot lan chua lap lai, `chua` chua ai chay hoac khong co bang chung. Gia tri la hien kem dau hoi. Bang nay sinh tu dong bang `python tools/scripts_index.py --write`, dung sua tay."
           + "\n\n")

def cell(doc):
    if not doc:
        return ("chua", "**THIEU DOCSTRING**")
    lab = "chua"
    m = KIEM_RE.search(doc)
    if m:
        lab = m.group(1).strip() or "chua"
        doc = KIEM_RE.sub("", doc)
    if lab not in KIEM_OK:
        lab = lab + " (?)"
    ls = [x.strip() for x in doc.strip().splitlines() if x.strip()]
    if not ls:
        return (lab, "**THIEU MO TA**")
    s = "`" + ls[0] + "`"
    if len(ls) > 1:
        s += " " + " ".join(ls[1:])
    return (lab, s.replace("|", "\\|"))

def table(paths, with_desc):
    rows = ["| File | KB | KIEM | Mô tả |", "|---|---|---|---|"] if with_desc else ["| File | KB |", "|---|---|"]
    for p in paths:
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        kb = "%.1f" % (p.stat().st_size / 1024.0)
        if with_desc:
            lab, desc = cell(doc_of(p))
            rows.append("| `%s` | %s | %s | %s |" % (rel, kb, lab, desc))
        else:
            rows.append("| `%s` | %s |" % (rel, kb))
    return "\n".join(rows)

def splice(text, key, block):
    a, b = MARK[key]
    i, j = text.find(a), text.find(b)
    if i < 0 or j < 0 or j < i:
        sys.exit("Khong thay moc %s trong %s" % (key, DOC))
    return text[:i + len(a)] + "\n" + block + "\n" + text[j:]

live = scan(LIVE)
arch = scan(ARCH)
nodoc = [p for p in live if not doc_of(p)]

print("=== TONG QUAN ===")
print("script dang dung : %d" % len(live))
print("script luu tru   : %d" % len(arch))
print("")
print("=== THIEU DOCSTRING (%d) ===" % len(nodoc))
for p in nodoc:
    print("  " + str(p.relative_to(ROOT)).replace("\\", "/"))

if not DOC.exists():
    sys.exit("Khong thay %s" % DOC)
cur = DOC.read_text(encoding="utf-8")
new = splice(splice(cur, "live", QUY_UOC + table(live, True)), "arch", table(arch, False))
tally = {}
for _p in live:
    _lab = cell(doc_of(_p))[0]
    tally[_lab] = tally.get(_lab, 0) + 1
print("")
print("=== NHAN KIEM ===")
for _k in sorted(tally):
    print("  %-18s %d" % (_k, tally[_k]))
print("")
print("=== BANG ===")
print("khop voi ma nguon" if new == cur else "da cu so voi ma nguon")
if WRITE:
    if new == cur:
        print("khong co gi de ghi")
    else:
        DOC.write_text(new, encoding="utf-8", newline="\n")
        print("da ghi: %s (%d byte)" % (DOC, len(new.encode("utf-8"))))
else:
    print("(chay lai voi --write de ghi)")