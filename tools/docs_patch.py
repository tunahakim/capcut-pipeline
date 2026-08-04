#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/docs_patch.py -- va tai lieu va ma nguon theo dac ta JSON, sau chot an toan.

  python tools/docs_patch.py --spec <file.json>           # chay thu, KHONG ghi
  python tools/docs_patch.py --spec <file.json> --apply    # ghi that
  python tools/docs_patch.py --selftest                    # tu kiem bay ca

Bay thao tac: replace, replace_between, delete, insert_after, insert_before, append,
create. Op replace_between nhan hai sentinel start va end, moi cai phai khop dung 1
lan, end phai nam sau start va khong chong len start, vung bi thay GOM CA hai
sentinel, va dac ta phai khai truoc expect_bytes la so byte du kien bi thay -- lech
qua tol_bytes thi dung, vi do la dau hieu sentinel cuoi bat vao cho xa hon du tinh.
tol_bytes mac dinh la max(200, expect_bytes // 5).

Sau chot: BOM bao loi va CRLF lan LF thi dung; moi anchor phai khop dung 1 lan va
kiem het moi file roi moi ghi; so byte sap ghi voi tran nhap tu tools/docs_audit.py;
file .py thi compile() truoc khi ghi; kiem lai sau khi ghi; tu choi cay git ban tru
khi co --allow-dirty. Chot thu bay: moi token dang duong dan trong noi dung SAP GHI
duoc phan loai bang resolve() cua tools/docs_audit.py -- SAI CHO, MISSING va TRUNG
TEN thi dung, ten tran khong co thu muc thi CANH BAO kem duong dan day du.

Khi spec co sua chinh tools/docs_audit.py thi BUDGET, PER_FILE_BUDGET va ca resolve()
deu nhap tu ban DA VA TRONG BO NHO, nen mot luot vua them entry PLANNED vua nhac file
moi khong con bi chan oan.

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
AUDIT_REL = "tools/docs_audit.py"
NS_NAMES = ("resolve", "strip_fences", "norm", "TOKEN_RE",
            "BUDGET", "PER_FILE_BUDGET", "NO_SCAN")
OPS = ("replace", "replace_between", "delete", "insert_after", "insert_before",
       "append", "create")
NEED = {"replace": ("old", "new"), "delete": ("old",),
        "replace_between": ("start", "end", "new", "expect_bytes"),
        "insert_after": ("anchor", "new"), "insert_before": ("anchor", "new"),
        "append": ("new",), "create": ("new",)}


def audit_ns_default():
    """Bang luat lay tu ban tools/docs_audit.py dang nam tren dia."""
    return dict((k, getattr(da, k)) for k in NS_NAMES)


def audit_from_text(text):
    """Bang luat lay tu ban tools/docs_audit.py DA VA, con trong bo nho."""
    ns = {"__name__": "docs_audit_patched",
          "__file__": str(REPO / AUDIT_REL)}
    exec(compile(text, "docs_audit(patched)", "exec"), ns)
    missing = [k for k in NS_NAMES if k not in ns]
    if missing:
        raise KeyError("thieu ten: %s" % ", ".join(missing))
    return dict((k, ns[k]) for k in NS_NAMES)


def scan_new_text(text, src, index, byname, ns):
    """Phan loai token duong dan trong noi dung sap ghi. Phan phan xu dung resolve()."""
    out = []
    for lineno, line in ns["strip_fences"](text):
        for m in ns["TOKEN_RE"].finditer(line):
            a, b = m.start(), m.end()
            if (line[a - 1] if a > 0 else " ") in ":\\/":
                continue
            if "http" in line[max(0, a - 12):a]:
                continue
            st, tgt = ns["resolve"](m.group(0), src, index, byname)
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
        if op == "replace_between":
            s_str, e_str = e["start"], e["end"]
            ns_, ne = body.count(s_str), body.count(e_str)
            print("  ANCHOR %-22s start khop=%d end khop=%d" % (name, ns_, ne))
            if ns_ != 1 or ne != 1:
                errs.append("[%s] KHONG KHOP replace_between '%s': start khop %d, "
                            "end khop %d, ca hai phai dung 1" % (rel, name, ns_, ne))
                continue
            i = body.index(s_str)
            j = body.index(e_str)
            if j < i + len(s_str):
                errs.append("[%s] replace_between '%s': sentinel cuoi nam TRUOC hoac "
                            "chong len sentinel dau" % (rel, name))
                continue
            region = body[i:j + len(e_str)]
            got = len(region.encode("utf-8"))
            want = int(e["expect_bytes"])
            tol = int(e.get("tol_bytes", max(200, want // 5)))
            print("  VUNG THAY %-20s du kien=%d thuc=%d bien do=%d"
                  % (name, want, got, tol))
            if abs(got - want) > tol:
                errs.append("[%s] replace_between '%s': vung bi thay %d byte, du kien "
                            "%d, lech %d vuot bien do %d"
                            % (rel, name, got, want, abs(got - want), tol))
                continue
            if not e["new"]:
                errs.append("[%s] replace_between '%s': khoa 'new' rong, op nay khong "
                            "dung de xoa" % (rel, name))
                continue
            body = body[:i] + e["new"] + body[j + len(e_str):]
            checks.append(("one", name, e["new"]))
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
        if e["op"] == "replace_between":
            for k in ("expect_bytes", "tol_bytes"):
                if k in e and (isinstance(e[k], bool) or not isinstance(e[k], int)
                               or e[k] < 0):
                    print("LOI: edit '%s' khoa '%s' phai la so nguyen khong am"
                          % (e["name"], k))
                    return 1
        rel = Path(e["file"]).as_posix()
        if rel not in groups:
            groups[rel] = []
            order.append(rel)
        groups[rel].append(e)

    allow = set(spec.get("allow_paths") or [])
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
        plan.append((rel, body, nl, checks))

    ns, src_label = audit_ns_default(), "ban tren dia"
    for rel, body, nl, checks in plan:
        if rel == AUDIT_REL:
            try:
                ns = audit_from_text(body)
                src_label = "ban DA VA trong bo nho"
            except Exception as exc:
                errs.append("[%s] khong nap duoc ban da va: %s: %s"
                            % (rel, type(exc).__name__, exc))
    print("")
    print("nguon luat (BUDGET, PLANNED, resolve): %s" % src_label)
    print("")

    for rel, body, nl, checks in plan:
        for e in groups[rel]:
            if "new" not in e:
                continue
            for lineno, tok, st, tgt in scan_new_text(e["new"], rel, index, byname, ns):
                if ns["norm"](tok) in allow:
                    print("  MIEN TRU %s (khai trong allow_paths)" % tok)
                    continue
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
        if rel.lower().endswith(".md") and not rel.startswith(ns["NO_SCAN"]):
            cap = ns["PER_FILE_BUDGET"].get(rel, ns["BUDGET"])
            if nbyte > cap:
                errs.append("[%s] VUOT TRAN %d byte > tran %d byte" % (rel, nbyte, cap))
        if rel.lower().endswith(".py"):
            try:
                compile(body, rel, "exec")
            except SyntaxError as e:
                errs.append("[%s] LOI compile dong %s: %s" % (rel, e.lineno, e.msg))
        old = (REPO / rel).stat().st_size if (REPO / rel).is_file() else 0
        print("FILE %s byte: %d -> %d" % (rel, old, nbyte))

    print("")
    for w in warns:
        print("CANH BAO %s" % w)
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
    heads = [ln for ln in todo.split("\n")
             if ln.startswith("## ") and todo.count(ln) == 1]
    if len(heads) < 2:
        print("LOI selftest: docs/TODO.md khong co du hai heading '## ' duy nhat")
        return 1
    h1, h2 = heads[0], heads[1]
    i, j = todo.index(h1), todo.index(h2)
    region = len(todo[i:j + len(h2)].encode("utf-8"))
    mid = h1 + "\n\nnoi dung thu cua selftest, khong nhac file nao.\n\n" + h2

    cases = []
    cases.append(("duong-dry-run", 0, "KIEM TRUOC: SACH", {"edits": [
        {"name": "duong", "file": "docs/TODO.md", "op": "replace",
         "old": h1, "new": h1}]}))
    cases.append(("am-anchor-0", 2, "KHONG KHOP", {"edits": [
        {"name": "khongco", "file": "docs/TODO.md", "op": "replace",
         "old": "ANCHOR KHONG TON TAI 20260804 xyz", "new": "abc"}]}))
    state_rel = "docs/STATE.md"
    state_now = (REPO / state_rel).stat().st_size
    state_cap = da.PER_FILE_BUDGET.get(state_rel, da.BUDGET)
    pad = max(1000, state_cap - state_now + 1000)
    cases.append(("vuot-tran", 2, "VUOT TRAN", {"edits": [
        {"name": "phinh", "file": state_rel, "op": "append",
         "new": "\n" + ("x" * pad)}]}))
    cases.append(("duong-dan-thieu-tien-to", 2, "SAI CHO", {"edits": [
        {"name": "saicho", "file": "docs/STATE.md", "op": "append",
         "new": "\nDoc core/shotlist.py de biet them.\n"}]}))
    cases.append(("between-duong", 0, "KIEM TRUOC: SACH", {"edits": [
        {"name": "between", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": h2, "new": mid, "expect_bytes": region}]}))
    cases.append(("between-end-khop-nhieu", 2, "ca hai phai dung 1", {"edits": [
        {"name": "endnhieu", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": "\n\n", "new": mid, "expect_bytes": region}]}))
    cases.append(("between-lech-byte", 2, "vuot bien do", {"edits": [
        {"name": "lechbyte", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": h2, "new": mid, "expect_bytes": 50}]}))

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
    print("vung giua hai heading dau cua docs/TODO.md: %d byte" % region)
    print("ca vuot-tran: docs/STATE.md %d byte, tran %d byte, chen them %d byte"
          % (state_now, state_cap, pad))
    print("%-26s %5s %5s %-20s %s" % ("CA", "MONG", "THAT", "NHAN MONG DOI", "CO NHAN"))
    print("%-26s %5s %5s %-20s %s" % ("-" * 26, "-----", "-----", "-" * 20, "-------"))
    bad = 0
    for name, want, got, marker, hit in rows:
        okc = (want == got) and hit
        if not okc:
            bad += 1
        print("%-26s %5d %5d %-20s %s  %s"
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