#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/docs_patch.py -- va tai lieu va ma nguon theo dac ta JSON, sau chot an toan.

  python tools/docs_patch.py --spec <file.json>           # chay thu, KHONG ghi
  python tools/docs_patch.py --spec <file.json> --apply    # ghi that
  python tools/docs_patch.py --selftest                    # tu kiem bon ca

Sau thao tac: replace, delete, insert_after, insert_before, append, create.
Sau chot: BOM bao loi va CRLF lan LF thi dung; moi anchor phai khop dung 1 lan va
kiem het moi file roi moi ghi; so byte sap ghi voi tran nhap tu tools/docs_audit.py;
file .py thi compile() truoc khi ghi; kiem lai sau khi ghi; tu choi cay git ban tru
khi co --allow-dirty. Chot thu bay: moi token dang duong dan trong noi dung SAP GHI
duoc phan loai bang resolve() cua tools/docs_audit.py -- SAI CHO, MISSING va TRUNG
TEN thi dung, ten tran khong co thu muc thi CANH BAO kem duong dan day du.

Ma thoat: 0 xong; 1 sai tham so hay spec khong doc duoc; 2 kiem TRUOC that bai nen
CHUA GHI FILE NAO; 3 da ghi nhung kiem SAU that bai, chay git restore ngay.
[KIEM: bo test]
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_audit as da

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = da.REPO
OPS = ("replace", "delete", insert_after_marker := "insert_after",
       "insert_before", "append", "create")
NEED = {"replace": ("old", "new"), "delete": ("old",),
        "insert_after": ("anchor", "new"), "insert_before": ("anchor", "new"),
        "append": ("new",), "create": ("new",)}


def budgets_from_text(text):
    """Doc BUDGET va PER_FILE_BUDGET tu ban docs_audit.py da va TRONG BO NHO."""
    ns = {"__name__": "docs_audit_patched"}
    exec(compile(text, "docs_audit(patched)", "exec"), ns)
    return ns["BUDGET"], ns["PER_FILE_BUDGET"]


def scan_new_text(text, src, index, byname):
    """Phan loai token duong dan trong noi dung sap ghi. Phan phan xu dung resolve()."""
    out = []
    for lineno, line in da.strip_fences(text):
        for m in da.TOKEN_RE.finditer(line):
            a, b = m.start(), m.end()
            if (line[a - 1] if a > 0 else " ") in ":\\/":
                continue
            if "http" in line[max(0, a - 12):a]:
                continue
            st, tgt = da.resolve(m.group(0), src, index, byname)
            if st in ("SAI CHO", "MISSING", "MULTI", "OK-BASENAME"):
                out.append((lineno, m.group(0), st, tgt))
    return out


def apply_edits(rel, edits, errs):
    """Tra ve (text_moi, nl, kiem_sau) hoac None neu loi. Khong ghi gi."""
    path = REPO / rel
    creating = any(e["op"] == "create" for e in edits)
    if creating:
        if len(edits) != 1:
            errs.append("[%s] op create phai dung mot minh cho moi file" % rel)
            return None
        if path.exists():
            errs.append("[%s] op create nhung file DA TON TAI" % rel)
            return None
        body, nl = "", "\n"
    else:
        if not path.is_file():
            errs.append("[%s] khong tim thay file" % rel)
            return None
        raw = path.read_bytes()
        if raw[:3] == b"\xef\xbb\xbf":
            errs.append("[%s] file co BOM, luat repo la UTF-8 khong BOM" % rel)
            return None
        try:
            body = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            errs.append("[%s] khong decode duoc UTF-8: %s" % (rel, e))
            return None
        crlf = body.count("\r\n")
        lone = body.replace("\r\n", "").count("\n")
        if crlf and lone:
            errs.append("[%s] LAN newline: CRLF %d va LF %d" % (rel, crlf, lone))
            return None
        nl = "\r\n" if crlf else "\n"
        body = body.replace("\r\n", "\n")

    checks = []
    for e in edits:
        op, name = e["op"], e["name"]
        if op == "create":
            body = e["new"]
            checks.append(("in", name, e["new"]))
            print("  ANCHOR %-22s create %d byte" % (name, len(e["new"].encode("utf-8"))))
            continue
        if op == "append":
            body = body + e["new"]
            checks.append(("in", name, e["new"]))
            print("  ANCHOR %-22s append %d byte" % (name, len(e["new"].encode("utf-8"))))
            continue
        key = "old" if op in ("replace", "delete") else "anchor"
        src_s = e[key]
        n = body.count(src_s)
        print("  ANCHOR %-22s khop=%d" % (name, n))
        if n != 1:
            errs.append("[%s] KHONG KHOP anchor '%s' khop %d lan, phai dung 1"
                        % (rel, name, n))
            continue
        if op == "replace":
            dst = e["new"]
        elif op == "delete":
            dst = ""
        elif op == "insert_after":
            dst = src_s + e["new"]
        else:
            dst = e["new"] + src_s
        body = body.replace(src_s, dst)
        if op == "delete":
            checks.append(("gone", name, src_s))
        else:
            checks.append(("one", name, dst))
    return body, nl, checks


def run_spec(spec_path, apply, allow_dirty):
    try:
        spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    except Exception as e:
        print("LOI doc spec: %s" % e)
        return 1
    edits = spec.get("edits")
    if not isinstance(edits, list) or not edits:
        print("LOI: spec thieu khoa 'edits' hoac rong")
        return 1

    order, groups = [], {}
    for i, e in enumerate(edits):
        for k in ("name", "file", "op"):
            if k not in e:
                print("LOI: edit thu %d thieu khoa '%s'" % (i + 1, k))
                return 1
        if e["op"] not in OPS:
            print("LOI: edit '%s' op '%s' khong hop le" % (e["name"], e["op"]))
            return 1
        for k in NEED[e["op"]]:
            if k not in e:
                print("LOI: edit '%s' op %s thieu khoa '%s'" % (e["name"], e["op"], k))
                return 1
        rel = Path(e["file"]).as_posix()
        if rel not in groups:
            groups[rel] = []
            order.append(rel)
        groups[rel].append(e)

    index, byname = da.build_index()
    for rel in order:
        index.add(rel)
        byname.setdefault(Path(rel).name, [])
        if rel not in byname[Path(rel).name]:
            byname[Path(rel).name].append(rel)

    errs, warns, plan = [], [], []
    for rel in order:
        print("FILE %s" % rel)
        r = apply_edits(rel, groups[rel], errs)
        if r is None:
            continue
        body, nl, checks = r
        for e in groups[rel]:
            if "new" not in e:
                continue
            for lineno, tok, st, tgt in scan_new_text(e["new"], rel, index, byname):
                if st == "OK-BASENAME":
                    warns.append("[%s/%s] CANH BAO ten tran '%s' -- nen viet '%s'"
                                 % (rel, e["name"], tok, tgt))
                elif st == "SAI CHO":
                    errs.append("[%s/%s] SAI CHO '%s' -- duong dan dung la '%s'"
                                % (rel, e["name"], tok, tgt))
                elif st == "MULTI":
                    errs.append("[%s/%s] TRUNG TEN '%s' -- ung vien: %s"
                                % (rel, e["name"], tok, tgt))
                else:
                    errs.append("[%s/%s] MISSING '%s' -- hoac sai chinh ta, hoac phai "
                                "khai vao PLANNED cua tools/docs_audit.py"
                                % (rel, e["name"], tok))
        nbyte = len(body.replace("\n", nl).encode("utf-8"))
        if rel.lower().endswith(".md") and not rel.startswith(da.NO_SCAN):
            bud, per = da.BUDGET, da.PER_FILE_BUDGET
            if rel == "tools/docs_audit.py":
                bud, per = budgets_from_text(body)
            cap = per.get(rel, bud)
            if nbyte > cap:
                errs.append("[%s] VUOT TRAN %d byte > tran %d byte" % (rel, nbyte, cap))
        if rel.lower().endswith(".py"):
            try:
                compile(body, rel, "exec")
            except SyntaxError as e:
                errs.append("[%s] LOI compile dong %s: %s" % (rel, e.lineno, e.msg))
        old = (REPO / rel).stat().st_size if (REPO / rel).is_file() else 0
        print("  byte: %d -> %d" % (old, nbyte))
        plan.append((rel, body, nl, checks))

    print("")
    for w in warns:
        print("CANH BAO %s" % w[w.index("]") + 2:] if w.startswith("[") else w)
    for w in warns:
        pass
    if errs:
        print("=== LOI (%d) -- KHONG SUA FILE NAO ===" % len(errs))
        for x in errs:
            print("  " + x)
        return 2
    print("=== KIEM TRUOC: SACH (%d file, %d edit) ===" % (len(plan), len(edits)))
    if not apply:
        print("che do chay thu, khong ghi. Them --apply de ghi that.")
        return 0

    if not allow_dirty:
        r = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO),
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("LOI: khong chay duoc git status")
            return 2
        if r.stdout.strip():
            print("=== CAY GIT BAN -- KHONG GHI ===")
            for ln in r.stdout.strip().split("\n")[:20]:
                print("  " + ln)
            print("commit hoac stash truoc, hoac them --allow-dirty neu co y")
            return 2

    bad = []
    for rel, body, nl, checks in plan:
        p = REPO / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body.replace("\n", nl).encode("utf-8"))
        got = p.read_bytes().decode("utf-8").replace("\r\n", "\n")
        for kind, name, s in checks:
            if kind == "one":
                ok = got.count(s) == 1
            elif kind == "gone":
                ok = got.count(s) == 0
            else:
                ok = s in got
            print("KIEM SAU %-22s %s" % (name, "OK" if ok else "THAT BAI"))
            if not ok:
                bad.append("%s / %s" % (rel, name))
    print("")
    if bad:
        print("=== KIEM SAU THAT BAI (%d) -- FILE DA BI GHI ===" % len(bad))
        for x in bad:
            print("  " + x)
        print("chay: git restore <file>  roi doc lai spec")
        return 3
    print("=== DA GHI %d FILE, KIEM SAU SACH ===" % len(plan))
    return 0


def selftest():
    tmp = da.LAB / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    day = datetime.datetime.now().strftime("%Y%m%d")

    todo = (REPO / "docs" / "TODO.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    anchor = None
    for ln in todo.split("\n"):
        if ln.startswith("## ") and todo.count(ln) == 1:
            anchor = ln
            break
    if anchor is None:
        print("LOI selftest: khong tim duoc heading duy nhat trong docs/TODO.md")
        return 1

    cases = []
    cases.append(("duong-dry-run", 0, "KIEM TRUOC: SACH", {"edits": [
        {"name": "duong", "file": "docs/TODO.md", "op": "replace",
         "old": anchor, "new": anchor}]}))
    cases.append(("am-anchor-0", 2, "KHONG KHOP", {"edits": [
        {"name": "khongco", "file": "docs/TODO.md", "op": "replace",
         "old": "ANCHOR KHONG TON TAI 20260804 xyz", "new": "abc"}]}))
    cases.append(("vuot-tran", 2, "VUOT TRAN", {"edits": [
        {"name": "phinh", "file": "docs/STATE.md", "op": "append",
         "new": "\n" + ("x" * 3000)}]}))
    cases.append(("duong-dan-thieu-tien-to", 2, "SAI CHO", {"edits": [
        {"name": "saicho", "file": "docs/STATE.md", "op": "append",
         "new": "\nDoc core/shotlist.py de biet them.\n"}]}))

    rows = []
    for name, want, marker, spec in cases:
        sp = tmp / ("tmp_%s_selftest_%s.json" % (day, name))
        sp.write_text(json.dumps(spec, ensure_ascii=False, indent=1),
                      encoding="utf-8", newline="\n")
        r = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                            "--spec", str(sp)], capture_output=True, text=True)
        hit = marker in (r.stdout or "")
        rows.append((name, want, r.returncode, marker, hit))

    print("")
    print("=== SELFTEST docs_patch ===")
    print("%-26s %5s %5s %-18s %s" % ("CA", "MONG", "THAT", "NHAN MONG DOI", "CO NHAN"))
    print("%-26s %5s %5s %-18s %s" % ("-" * 26, "-----", "-----", "-" * 18, "-------"))
    bad = 0
    for name, want, got, marker, hit in rows:
        okc = (want == got) and hit
        if not okc:
            bad += 1
        print("%-26s %5d %5d %-18s %s  %s"
              % (name, want, got, marker, "co" if hit else "KHONG",
                 "OK" if okc else "THAT BAI"))
    print("")
    print("ma thoat 3 (ghi xong nhung kiem sau that bai): KHONG dung duoc ca thu, CHUA KIEM CHUNG")
    print("KET QUA: %d/%d ca dat" % (len(rows) - bad, len(rows)))
    return 0 if bad == 0 else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.spec:
        print("LOI: can --spec <file.json> hoac --selftest")
        return 1
    return run_spec(a.spec, a.apply, a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())