#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/docs_patch.py -- va tai lieu va ma nguon theo dac ta JSON, sau chot an toan.

  python tools/docs_patch.py --spec <file.json> --probe    # chi dem neo, khong ghi
  python tools/docs_patch.py --spec <file.json>            # chay thu, KHONG ghi
  python tools/docs_patch.py --spec <file.json> --apply     # ghi that
  python tools/docs_patch.py --selftest                     # tu kiem moi ca

Quy trinh chuan cho luot va dai: luot mot chi phat spec ke hoach gom neo ngan cong
khoa content_file tro toi mot file trong thu muc tam CHUA ton tai, roi chay --probe
cho re; luot hai moi viet noi dung moi ra dung file do roi --apply. Noi dung moi nam
tren dia chu khong nam trong lich su hoi thoai, nen neo hong thi chi phat lai neo.
Co --fill-bytes thi --probe tu ghi expect_bytes do duoc nguoc vao spec. Doan dai tu
khoang muoi dong tro len bat buoc dung replace_between voi hai neo ngan va duy nhat,
khong dung replace voi nguyen van doan cu, vi khi do chinh doan dai la cai neo.

Tam thao tac: replace, replace_between, delete, delete_block, insert_after,
insert_before, append, create. Op delete_block nhan anchor la dong dau khoi roi xoa
tu dau dong do den dong trong ke tiep; khong tim thay dong trong phia sau thi DUNG
chu KHONG xoa toi het file. Op replace_between nhan hai sentinel start va end, moi cai phai khop dung 1
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

Trần kích thước không đọc thẳng từ PER_FILE_BUDGET nữa mà hỏi cap_for() của tools/docs_audit.py, nên một file đang có miễn trừ còn hạn trong docs/budget-waivers.json thì vẫn ghi được và chỉ nhận một dòng CANH BAO, còn miễn trừ đã hết hạn thì chặn ghi như mọi lần vượt trần khác.

Ma thoat: 0 xong; 1 sai tham so hay spec khong doc duoc; 2 kiem TRUOC that bai nen
CHUA GHI FILE NAO; 3 da ghi nhung kiem SAU that bai -- tool KHONG tu hoi phuc, no chi
in ten file de nguoi dung tu chay git restore.
[KIEM: bo test]
"""
import argparse
import datetime
import json
import os
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
            "BUDGET", "PER_FILE_BUDGET", "NO_SCAN", "cap_for", "WAIVER_FILE")
OPS = ("replace", "replace_between", "delete", "delete_block", "insert_after",
       "insert_before", "append", "create")
NEED = {"replace": ("old", "new"), "delete": ("old",), "delete_block": ("anchor",),
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


def show_hits(body, s, lab, limit=3):
    """In cac cho khop kem mot dong tren mot dong duoi, de chon neo dai hon."""
    lines = body.split("\n")
    pos, start = [], 0
    while True:
        k = body.find(s, start)
        if k < 0:
            break
        pos.append(k)
        start = k + max(1, len(s))
    for k in pos[:limit]:
        ln = body.count("\n", 0, k) + 1
        lo, hi = max(1, ln - 1), min(len(lines), ln + 1)
        print("    --- %s khop tai dong %d ---" % (lab, ln))
        for m in range(lo, hi + 1):
            print("    %5d | %s" % (m, lines[m - 1][:100]))
    if len(pos) > limit:
        print("    ... con %d cho khop nua, khong in" % (len(pos) - limit))


def doc_than(rel):
    """Doc file dich va kiem BOM cung newline lan. Tra ve (body_LF, nl, loi).

    Duong doc duy nhat cho ca apply_edits() lan run_probe(): hai ben tung doc
    bang hai doan ma rieng nen probe co the bao sach roi apply moi tu choi.
    loi la None khi doc duoc.
    """
    p = REPO / rel
    if not p.is_file():
        return None, None, "khong tim thay file"
    raw = p.read_bytes()
    if raw[:3] == b"\xef\xbb\xbf":
        return None, None, "file co BOM, luat repo la UTF-8 khong BOM"
    try:
        body = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, None, "khong decode duoc UTF-8: %s" % exc
    crlf = body.count("\r\n")
    lone = body.replace("\r\n", "").count("\n")
    if crlf and lone:
        return None, None, "LAN newline: CRLF %d va LF %d" % (crlf, lone)
    return body.replace("\r\n", "\n"), ("\r\n" if crlf else "\n"), None


def do_vung(body, start, end):
    """Dem hai neo va do vung giua chung. Tra ve (n_start, n_end, xuoi, size).

    size la so byte UTF-8 cua vung GOM CA hai neo, bang 0 khi chua do duoc.
    Duong do duy nhat cho ca apply_edits() lan run_probe(), de hai ben khong
    the lech nhau sau moi lan sua.
    """
    n1, n2 = body.count(start), body.count(end)
    if n1 != 1 or n2 != 1:
        return n1, n2, False, 0
    i = body.index(start)
    j = body.index(end)
    if j < i + len(start):
        return n1, n2, False, 0
    return n1, n2, True, len(body[i:j + len(end)].encode("utf-8"))


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
        body, nl, loi = doc_than(rel)
        if loi is not None:
            errs.append("[%s] %s" % (rel, loi))
            return None

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
            ns_, ne, xuoi, got = do_vung(body, s_str, e_str)
            print("  ANCHOR %-22s start khop=%d end khop=%d" % (name, ns_, ne))
            if ns_ != 1 or ne != 1:
                errs.append("[%s] KHONG KHOP replace_between '%s': start khop %d, "
                            "end khop %d, ca hai phai dung 1" % (rel, name, ns_, ne))
                continue
            if not xuoi:
                errs.append("[%s] replace_between '%s': sentinel cuoi nam TRUOC hoac "
                            "chong len sentinel dau" % (rel, name))
                continue
            i = body.index(s_str)
            j = body.index(e_str)
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
        if op == "delete_block":
            anc = e["anchor"]
            n = body.count(anc)
            print("  ANCHOR %-22s khop=%d" % (name, n))
            if n != 1:
                errs.append("[%s] KHONG KHOP anchor '%s' khop %d lan, phai dung 1"
                            % (rel, name, n))
                continue
            i0 = body.index(anc)
            ls = body.rfind("\n", 0, i0) + 1
            j0 = body.find("\n\n", i0)
            if j0 < 0:
                errs.append("[%s] delete_block '%s': khong tim thay dong trong sau "
                            "khoi nen khong biet khoi ket thuc o dau, tu choi xoa toi "
                            "het file. Dung op delete voi nguyen van, hoac them mot "
                            "dong trong" % (rel, name))
                continue
            end = j0 + 2
            print("  XOA KHOI %-20s %d byte, tu dau dong den dong trong ke tiep"
                  % (name, len(body[ls:end].encode("utf-8"))))
            body = body[:ls] + body[end:]
            checks.append(("gone", name, anc))
            continue
        key = "old" if op in ("replace", "delete") else "anchor"
        src_s = e[key]
        n = body.count(src_s)
        print("  ANCHOR %-22s khop=%d" % (name, n))
        if n != 1:
            if n > 1:
                show_hits(body, src_s, name)
            else:
                diag(body, src_s, name)
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
        if op == "delete" or dst == "":
            checks.append(("gone", name, src_s))
        else:
            checks.append(("one", name, dst))
    return body, nl, checks


def diag(body, s, lab):
    """In chan doan khi mot neo khong khop dung mot lan."""
    lines = body.split("\n")
    first = (s.split("\n")[0] or "").strip()
    if first:
        hits = [k + 1 for k, ln in enumerate(lines) if first in ln]
        print("    chan doan %s: dong dau khop %d dong, vi tri %s"
              % (lab, len(hits), hits[:6]))
    fs = " ".join(s.split())
    flat = " ".join(body.split())
    print("    chan doan %s: go khoang trang thi khop %d lan"
          % (lab, flat.count(fs) if fs else -1))


def run_probe(spec_path, fill):
    """Dem neo va do vung giua hai neo, KHONG ghi file dich nao."""
    try:
        spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    except Exception as exc:
        print("LOI doc spec: %s" % exc)
        return 1
    edits = spec.get("edits")
    if not isinstance(edits, list) or not edits:
        print("LOI: spec thieu khoa 'edits' hoac rong")
        return 1
    print("=== PROBE: chi dem neo, KHONG ghi gi ===")
    cache, bad, changed = {}, 0, False
    for i, e in enumerate(edits):
        name = str(e.get("name", "edit%d" % (i + 1)))
        op = e.get("op", "")
        rel = Path(e.get("file", "")).as_posix()
        if op not in OPS:
            print("%-24s %-16s OP KHONG HOP LE, phai la mot trong: %s"
                  % (name, op, ", ".join(OPS)))
            bad += 1
            continue
        if op in ("append", "create"):
            print("%-24s %-16s khong co neo, bo qua" % (name, op))
            continue
        if rel not in cache:
            cache[rel] = doc_than(rel)
        body, _nl, loi = cache[rel]
        if loi is not None:
            print("%-24s %-16s %s: %s" % (name, op, rel, loi))
            bad += 1
            continue
        if op == "replace_between":
            s, t = e.get("start", ""), e.get("end", "")
            n1, n2, xuoi, size = do_vung(body, s, t)
            ok = (n1 == 1 and n2 == 1 and xuoi)
            chieu = "xuoi" if xuoi else ("NGUOC" if (n1 == 1 and n2 == 1) else "-")
            print("%-24s %-16s start=%d end=%d %s vung=%d byte"
                  % (name, op, n1, n2, chieu, size))
            if not ok:
                bad += 1
                if n1 != 1:
                    diag(body, s, "start")
                if n2 != 1:
                    diag(body, t, "end")
            elif fill and e.get("expect_bytes") != size:
                e["expect_bytes"] = size
                changed = True
        else:
            key = "old" if op in ("replace", "delete") else "anchor"
            s = e.get(key, "")
            n1 = body.count(s)
            print("%-24s %-16s %s khop=%d" % (name, op, key, n1))
            if n1 != 1:
                bad += 1
                diag(body, s, key)
    if fill and changed:
        Path(spec_path).write_text(
            json.dumps(spec, ensure_ascii=False, indent=1),
            encoding="utf-8", newline="\n")
        print("da ghi expect_bytes do duoc nguoc vao spec")
    print("")
    print("=== PROBE: %d muc, %d muc hong ===" % (len(edits), bad))
    return 0 if bad == 0 else 2


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
        cf = e.get("content_file")
        if cf:
            if "new" in e:
                print("LOI: edit thu %d khai ca 'new' lan 'content_file'" % (i + 1))
                return 1
            cp = Path(cf)
            if not cp.is_absolute():
                cp = REPO / cf
            if not cp.is_file():
                print("LOI: edit thu %d content_file khong ton tai: %s" % (i + 1, cp))
                return 1
            e["new"] = cp.read_text(encoding="utf-8").replace("\r\n", "\n")
            print("NOI DUNG %s <- %s (%d byte)"
                  % (e.get("name", i + 1), cp, len(e["new"].encode("utf-8"))))
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
            nb = len(e["new"].encode("utf-8"))
            if (rel.lower().endswith(".md") and nb >= 400
                    and not any(ord(c) > 127 for c in e["new"])):
                warns.append("[%s/%s] %d byte ghi vao file .md ma khong co ky tu co "
                             "dau nao -- tieng Viet phai co dau"
                             % (rel, e["name"], nb))
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
            cap, tt_mt, w_mt = ns["cap_for"](rel, nbyte)
            if nbyte <= cap:
                pass
            elif tt_mt == "CON HAN":
                warns.append("[%s] VUOT TRAN %d byte > tran %d byte, nhung %s cho mien "
                             "tru toi %s: %s"
                             % (rel, nbyte, cap, ns["WAIVER_FILE"], w_mt["het_han"],
                                w_mt["ly_do"]))
            elif tt_mt == "QUA HAN":
                errs.append("[%s] VUOT TRAN %d byte > tran %d byte, MIEN TRU HET HAN "
                            "ngay %s -- rut gon tai lieu, hoac gia han co y trong %s"
                            % (rel, nbyte, cap, w_mt["het_han"], ns["WAIVER_FILE"]))
            else:
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
        print("")
        print("Hướng xử lý theo từng loại. Neo khớp 0 lần: so lại nguyên văn, chú ý khoảng trắng cuối dòng và kiểu xuống dòng, phần chẩn đoán ở trên đã in số lần khớp của riêng dòng đầu. Neo khớp nhiều lần: đọc các đoạn vừa in kèm số dòng rồi kéo dài neo cho duy nhất, hoặc đổi sang op replace_between với hai neo ngắn. SAI CHO hoặc MISSING: viết lại đường dẫn tương đối đầy đủ tính từ gốc repo. VUOT TRAN: rút gọn tài liệu trước khi vá, và nếu đang ở cuối phiên không còn chỗ để rút gọn thì xem mục miễn trừ trần có hạn trong docs/TODO.md, đừng nâng trần lặng lẽ.")
        return 2
    print("=== KIEM TRUOC: SACH (%d file, %d edit) ===" % (len(plan), len(edits)))
    print("Mọi neo khớp đúng một lần, mọi phép kiểm trước đều sạch: vá được rồi.")
    if not apply:
        print("Đang chạy thử nên chưa ghi gì. Thêm --apply vào đúng lệnh vừa chạy để ghi thật.")
        return 0

    if not allow_dirty:
        r = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO),
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
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


def lay_so(text, khoa):
    """Lay so nguyen dung ngay sau mot khoa dang 'vung=' trong output cua tool."""
    k = text.find(khoa)
    if k < 0:
        return -1
    so = ""
    for ch in text[k + len(khoa):]:
        if ch.isdigit():
            so += ch
        else:
            break
    return int(so) if so else -1


def so_hai_duong(tmp, day, h1, h2):
    """Bat --probe va apply_edits do CUNG mot vung roi so hai con so do duoc.

    Hai duong tung dem neo bang hai doan ma rieng va chi tinh co dong y voi nhau.
    Ca nay khong nhin ma thoat, no doc thang so byte hai ben in ra: probe in
    'vung=' con apply_edits in 'thuc='. Lech nhau nghia la do_vung() da bi mot
    ben bo qua trong mot lan sua nao do.
    """
    spec = {"edits": [{"name": "haiduong", "file": "docs/TODO.md",
                       "op": "replace_between", "start": h1, "end": h2,
                       "new": "x\n", "expect_bytes": 1, "tol_bytes": 0}]}
    sp = tmp / ("tmp_" + day + "_selftest_haiduong.json")
    sp.write_text(json.dumps(spec, ensure_ascii=False, indent=1),
                  encoding="utf-8", newline="\n")
    me = str(Path(__file__).resolve())
    out = []
    for args in (["--probe"], []):
        r = subprocess.run([sys.executable, me, "--spec", str(sp)] + args,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        out.append(r.stdout or "")
    a = lay_so(out[0], "vung=")
    b = lay_so(out[1], "thuc=")
    return (a == b and a > 0), a, b


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

    cf = tmp / ("tmp_%s_selftest_contentfile.txt" % day)
    cf.write_text("noi dung thu tu content_file, khong nhac file nao.\n",
                  encoding="utf-8", newline="\n")
    cases.append(("content-file", 0, "KIEM TRUOC: SACH", {"edits": [
        {"name": "ngoaitep", "file": "docs/TODO.md", "op": "replace",
         "old": h1, "content_file": str(cf)}]}))
    cases.append(("probe-duong", 0, "0 muc hong", {"edits": [
        {"name": "probe1", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": h2}]}))
    cases.append(("probe-am", 2, "chan doan", {"edits": [
        {"name": "probe2", "file": "docs/TODO.md", "op": "replace",
         "old": "ANCHOR KHONG TON TAI 20260805 xyz"}]}))
    blk = REPO / ("_selftest_block_%s.txt" % day)
    blk.write_text("# thu nghiem\n\n## muc mot\n\ndong dau khoi 20260805\n"
                   "dong hai cua khoi\n\n## muc hai\n\nnoi dung cuoi\n",
                   encoding="utf-8", newline="\n")
    sc3 = REPO / ("_selftest_ma3_%s.txt" % day)
    sc3.write_text("ALPHA20260805\nBETA20260805\n", encoding="utf-8", newline="\n")
    cases.append(("delete-block", 0, "DA GHI 1 FILE, KIEM SAU SACH", {"edits": [
        {"name": "xoakhoi", "file": blk.name, "op": "delete_block",
         "anchor": "dong dau khoi 20260805"}]}))
    mdt = REPO / ("_selftest_md_" + day + ".md")
    mdt.write_text("# thu nghiem selftest\n\nmot dong noi dung.\n",
                   encoding="utf-8", newline="\n")
    cases.append(("md-khong-dau", 0, "khong co ky tu co dau", {"edits": [
        {"name": "khongdau", "file": mdt.name, "op": "append",
         "new": "\n" + ("z " * 300)}]}))
    cases.append(("ma-thoat-3", 3, "KIEM SAU THAT BAI", {"edits": [
        {"name": "trung", "file": sc3.name, "op": "replace",
         "old": "ALPHA20260805", "new": "BETA20260805"}]}))
    dup = REPO / ("_selftest_dup_%s.txt" % day)
    dup.write_text("DUP20260805\nkhac\nDUP20260805\n", encoding="utf-8", newline="\n")
    rong = REPO / ("_selftest_rong_%s.txt" % day)
    rong.write_text("GIU20260805\nXOA20260805\n", encoding="utf-8", newline="\n")
    cases.append(("am-anchor-2", 2, "khop 2 lan", {"edits": [
        {"name": "trunganchor", "file": dup.name, "op": "replace",
         "old": "DUP20260805", "new": "MOI20260805"}]}))
    cases.append(("replace-rong", 0, "DA GHI 1 FILE, KIEM SAU SACH", {"edits": [
        {"name": "xoachuoi", "file": rong.name, "op": "replace",
         "old": "XOA20260805\n", "new": ""}]}))
    dbe = REPO / ("_selftest_dbcuoi_" + day + ".txt")
    dbe.write_text("# thu nghiem\n\n## muc mot\n\ndong dau khoi cuoi 20260805\n"
                   "dong hai cua khoi cuoi\n", encoding="utf-8", newline="\n")
    cases.append(("delete-block-cuoi-file", 2, "tu choi xoa toi het file", {"edits": [
        {"name": "khoicuoi", "file": dbe.name, "op": "delete_block",
         "anchor": "dong dau khoi cuoi 20260805"}]}))
    bom = REPO / ("_selftest_bom_" + day + ".txt")
    bom.write_bytes(b"\xef\xbb\xbfGIU20260805\ndong hai\n")
    cases.append(("probe-bom", 2, "file co BOM", {"edits": [
        {"name": "cobom", "file": bom.name, "op": "replace",
         "old": "GIU20260805", "new": "MOI20260805"}]}))
    cases.append(("probe-op-la", 2, "OP KHONG HOP LE", {"edits": [
        {"name": "opla", "file": "docs/TODO.md", "op": "replace_bewteen",
         "start": h1, "end": h2}]}))
    cases.append(("probe-di-voi-apply", 1, "khong di cung --apply", {"edits": [
        {"name": "probeapply", "file": "docs/TODO.md", "op": "replace",
         "old": h1, "new": h1}]}))
    def bang_mt(ten, muc):
        p = tmp / ("tmp_" + day + "_selftest_wv_" + ten + ".json")
        p.write_text(json.dumps({"schema": 1, "waivers": muc},
                                ensure_ascii=False, indent=1),
                     encoding="utf-8", newline="\n")
        return str(p)

    wv_rong = bang_mt("rong", [])
    wv_con = bang_mt("con", [{"file": state_rel, "ngay_cap": "2026-01-01",
                              "het_han": "2099-12-31",
                              "ly_do": "ca tu kiem, mien tru con han"}])
    wv_het = bang_mt("het", [{"file": state_rel, "ngay_cap": "2019-01-01",
                              "het_han": "2020-01-01",
                              "ly_do": "ca tu kiem, mien tru da het han"}])
    cases.append(("mien-tru-con-han", 0, "cho mien tru toi", {"edits": [
        {"name": "mientrucon", "file": state_rel, "op": "append",
         "new": "\n" + ("x" * pad)}]}))
    cases.append(("mien-tru-het-han", 2, "MIEN TRU HET HAN", {"edits": [
        {"name": "mientruhet", "file": state_rel, "op": "append",
         "new": "\n" + ("x" * pad)}]}))
    envs = {"vuot-tran": {"DOCS_WAIVERS": wv_rong},
            "mien-tru-con-han": {"DOCS_WAIVERS": wv_con},
            "mien-tru-het-han": {"DOCS_WAIVERS": wv_het}}
    extra = {"probe-duong": ["--probe"], "probe-am": ["--probe"],
             "probe-bom": ["--probe"], "probe-op-la": ["--probe"],
             "probe-di-voi-apply": ["--probe", "--apply"],
             "delete-block": ["--apply", "--allow-dirty"],
             "ma-thoat-3": ["--apply", "--allow-dirty"],
             "replace-rong": ["--apply", "--allow-dirty"]}

    rac = [blk, sc3, dup, rong, mdt, dbe, bom]
    rows = []
    try:
        for name, want, marker, spec in cases:
            sp = tmp / ("tmp_" + day + "_selftest_" + name + ".json")
            sp.write_text(json.dumps(spec, ensure_ascii=False, indent=1),
                          encoding="utf-8", newline="\n")
            moi = dict(os.environ)
            moi.pop("DOCS_WAIVERS", None)
            moi.update(envs.get(name, {}))
            r = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                "--spec", str(sp)] + extra.get(name, []),
                               capture_output=True, text=True,
                               encoding="utf-8", errors="replace", env=moi)
            hit = marker in (r.stdout or "")
            rows.append((name, want, r.returncode, marker, hit))
        ok_vung, a_probe, a_apply = so_hai_duong(tmp, day, h1, h2)
        rows.append(("do-vung-mot-duong", 0, 0 if ok_vung else 1,
                     "probe=%d apply=%d" % (a_probe, a_apply), ok_vung))
    finally:
        for _p in rac:
            try:
                _p.unlink()
            except OSError:
                pass

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
    print("KET QUA: %d/%d ca dat" % (len(rows) - bad, len(rows)))
    return 0 if bad == 0 else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--fill-bytes", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.spec:
        print("LOI: can --spec <file.json> hoac --selftest")
        return 1
    if a.probe and a.apply:
        print("LOI: --probe khong di cung --apply, chon mot trong hai")
        return 1
    if a.fill_bytes and not a.probe:
        print("LOI: --fill-bytes chi co nghia khi di kem --probe")
        return 1
    if a.probe:
        return run_probe(a.spec, a.fill_bytes)
    return run_spec(a.spec, a.apply, a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())