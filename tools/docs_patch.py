#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/docs_patch.py -- vá tài liệu và mã nguồn theo đặc tả JSON, có bảy chốt an toàn trước khi ghi.

  python tools/docs_patch.py --spec <file.json> --probe    # chi dem neo, khong ghi
  python tools/docs_patch.py --spec <file.json>            # chay thu, KHONG ghi
  python tools/docs_patch.py --spec <file.json> --apply    # ghi that
  python tools/docs_patch.py --selftest                    # tu kiem moi ca
  python tools/docs_patch.py --example                     # in spec mau cho ca tam op

Quy trình chuẩn cho lượt vá dài: lượt một chỉ phát spec kế hoạch gồm neo ngắn cộng khoá content_file trỏ tới một file trong thư mục tạm CHƯA tồn tại, rồi chạy --probe cho rẻ; lượt hai mới viết nội dung mới ra đúng file đó rồi --apply. Nội dung mới nằm trên đĩa chứ không nằm trong lịch sử hội thoại, nên neo hỏng thì chỉ phát lại neo. Có --fill-bytes thì --probe tự ghi expect_bytes đo được ngược vào spec. Đoạn dài từ khoảng mười dòng trở lên bắt buộc dùng replace_between với hai neo ngắn và duy nhất, không dùng replace với nguyên văn đoạn cũ, vì khi đó chính đoạn dài là cái neo.

Tám thao tác: replace, replace_between, delete, delete_block, insert_after, insert_before, append, create.

Op delete_block nhận anchor là dòng đầu khối rồi xoá từ đầu dòng đó đến dòng trống kế tiếp; không tìm thấy dòng trống phía sau thì DỪNG chứ KHÔNG xoá tới hết file.

Op replace_between nhận hai sentinel start và end, mỗi cái phải khớp đúng 1 lần, end phải nằm sau start và không chồng lên start. MẶC ĐỊNH vùng bị thay gồm neo đầu và dừng NGAY TRƯỚC neo cuối, tức neo cuối vẫn còn nguyên trong file sau khi vá; khoá end_mode bằng "gom" khôi phục hành vi cũ là nuốt luôn cả neo cuối. Mặc định này đảo chiều ngày 06/08/2026 vì một spec quên chép neo cuối vào "new" đã xoá mất ba đoạn của docs/STATE.md mà không ai thấy: thừa một dòng thì dễ sửa, mất một dòng thì khoai. Khoá expect_bytes là số byte dự kiến của vùng THỰC SỰ bị thay theo đúng chế độ đang chọn, lệch quá tol_bytes thì dừng, vì đó là dấu hiệu sentinel cuối bắt vào chỗ xa hơn dự tính; tol_bytes mặc định là max(200, expect_bytes // 5).

Chế độ --probe dựng bản mới TUẦN TỰ trong bộ nhớ đúng như --apply và dùng chung hàm apply_edits, nên spec nhiều edit trên cùng một file không còn cảnh probe sạch rồi apply mới trượt vì edit trước đã xoá mất neo của edit sau. Edit nào chưa có "new", chẳng hạn content_file còn chưa viết, thì probe giữ nguyên vùng đó và in GHI CHU chứ không giả định là xoá. Với replace_between, --probe in thêm dòng đầu và dòng cuối của vùng sắp mất, kèm một dòng CANH BAO khi neo cuối bị nuốt mà không xuất hiện lại trong "new", hoặc khi neo cuối được giữ mà "new" cũng chứa nó nên sẽ lặp hai lần.

Sáu chốt an toàn: BOM báo lỗi và CRLF lẫn LF thì dừng; mọi anchor phải khớp đúng 1 lần và kiểm hết mọi file rồi mới ghi; số byte sắp ghi so với trần hỏi từ cap_for() của tools/docs_audit.py; file .py thì compile() trước khi ghi; kiểm lại sau khi ghi; từ chối cây git bẩn trừ khi có --allow-dirty. Chốt thứ bảy: mọi token dạng đường dẫn trong nội dung SẮP GHI được phân loại bằng resolve() của tools/docs_audit.py, gặp SAI CHO, MISSING hay TRUNG TEN thì dừng, còn tên trần không có thư mục thì CANH BAO kèm đường dẫn đầy đủ.

Khi spec có sửa chính tools/docs_audit.py thì BUDGET, PER_FILE_BUDGET và cả resolve() đều nhập từ bản ĐÃ VÁ TRONG BỘ NHỚ, nên một lượt vừa thêm entry PLANNED vừa nhắc file mới không còn bị chặn oan. Trần kích thước hỏi cap_for() chứ không đọc thẳng PER_FILE_BUDGET, nên một file đang có miễn trừ còn hạn trong docs/budget-waivers.json thì vẫn ghi được và chỉ nhận một dòng CANH BAO, còn miễn trừ đã hết hạn thì chặn ghi như mọi lần vượt trần khác.

Mã thoát: 0 xong; 1 sai tham số hay spec không đọc được; 2 kiểm TRƯỚC thất bại nên CHƯA GHI FILE NÀO; 3 đã ghi nhưng kiểm SAU thất bại, tool KHÔNG tự hồi phục mà chỉ in tên file để người dùng tự chạy git restore.
[KIEM: bo test]
"""
import argparse
import copy
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
END_MODES = ("giu", "gom")
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


def do_vung(body, start, end, end_mode="giu"):
    """Dem hai neo va do vung giua chung. Tra ve (n_start, n_end, xuoi, size, i, k).

    Vung bi thay la body[i:k]. Che do "giu" la mac dinh, k dung ngay TRUOC neo
    cuoi nen neo cuoi con nguyen trong file; che do "gom" la hanh vi cu, k nam
    sau neo cuoi nen neo cuoi bi nuot. size la so byte UTF-8 cua vung do, bang 0
    khi chua do duoc. Duong do duy nhat cho ca apply_edits() lan run_probe().
    """
    n1, n2 = body.count(start), body.count(end)
    if n1 != 1 or n2 != 1:
        return n1, n2, False, 0, -1, -1
    i = body.index(start)
    j = body.index(end)
    if j < i + len(start):
        return n1, n2, False, 0, -1, -1
    k = j + len(end) if end_mode == "gom" else j
    return n1, n2, True, len(body[i:k].encode("utf-8")), i, k


def in_vung(body, i, k, nhan):
    """In dong dau va dong cuoi cua vung sap bi thay, de nhin ra ngay neo cuoi bat sai cho."""
    doan = body[i:k]
    lines = doan.split("\n")
    ln_dau = body.count("\n", 0, i) + 1
    ln_cuoi = ln_dau + len(lines) - 1
    print("    VUNG SAP MAT %s: dong %d -> %d, %d dong, %d byte"
          % (nhan, ln_dau, ln_cuoi, len(lines), len(doan.encode("utf-8"))))
    print("    dong dau  | %s" % lines[0][:100])
    if len(lines) == 1:
        print("    dong cuoi | (vung chi co mot dong, trung dong dau)")
    else:
        print("    dong cuoi | %s" % lines[-1][:100])


def apply_edits(rel, edits, errs, probe=False, do_duoc=None):
    """Tra ve (text_moi, nl, kiem_sau) hoac None neu loi. Khong ghi gi.

    Cac edit duoc ap TUAN TU len cung mot ban trong bo nho, dung thu tu trong
    spec. Voi probe=True thi khong phan xu expect_bytes va khong doi phai co
    "new"; edit nao chua co "new" thi giu nguyen vung do roi in GHI CHU.
    """
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
            if "new" not in e:
                print("  ANCHOR %-22s create: chua co 'new', probe bo qua" % name)
                continue
            body = e["new"]
            checks.append(("in", name, e["new"]))
            print("  ANCHOR %-22s create %d byte" % (name, len(e["new"].encode("utf-8"))))
            continue
        if op == "append":
            if "new" not in e:
                print("  ANCHOR %-22s append: chua co 'new', probe bo qua" % name)
                continue
            body = body + e["new"]
            checks.append(("in", name, e["new"]))
            print("  ANCHOR %-22s append %d byte" % (name, len(e["new"].encode("utf-8"))))
            continue
        if op == "replace_between":
            s_str, e_str = e["start"], e["end"]
            mode = e.get("end_mode", "giu")
            ns_, ne, xuoi, got, i, k = do_vung(body, s_str, e_str, mode)
            print("  ANCHOR %-22s start khop=%d end khop=%d neo cuoi=%s"
                  % (name, ns_, ne, mode))
            if ns_ != 1 or ne != 1:
                if ns_ != 1:
                    diag(body, s_str, "start")
                if ne != 1:
                    diag(body, e_str, "end")
                errs.append("[%s] KHONG KHOP replace_between '%s': start khop %d, "
                            "end khop %d, ca hai phai dung 1" % (rel, name, ns_, ne))
                continue
            if not xuoi:
                errs.append("[%s] replace_between '%s': sentinel cuoi nam TRUOC hoac "
                            "chong len sentinel dau" % (rel, name))
                continue
            want = int(e["expect_bytes"]) if "expect_bytes" in e else -1
            tol = int(e.get("tol_bytes", max(200, (want if want > 0 else 0) // 5)))
            print("  VUNG THAY %-20s du kien=%s thuc=%d bien do=%d"
                  % (name, want if want >= 0 else "chua khai", got, tol))
            if do_duoc is not None:
                do_duoc[(rel, name)] = got
            if probe:
                in_vung(body, i, k, name)
            co_new = "new" in e
            new = e.get("new", "")
            if co_new:
                if mode == "gom" and e_str not in new:
                    print("  CANH BAO %s: end_mode=gom nen neo cuoi BI NUOT, ma 'new' "
                          "khong chep lai no -- doan do se mat han khoi file" % name)
                elif mode == "giu" and e_str in new:
                    print("  CANH BAO %s: end_mode=giu nen neo cuoi VAN CON trong file, "
                          "ma 'new' cung chua no -- neo cuoi se bi lap hai lan" % name)
            elif probe:
                print("  GHI CHU %s: chua co 'new' nen chua kiem duoc neo cuoi co "
                      "xuat hien lai hay khong, va vung nay duoc giu nguyen" % name)
            if not probe:
                if want >= 0 and abs(got - want) > tol:
                    errs.append("[%s] replace_between '%s': vung bi thay %d byte, du "
                                "kien %d, lech %d vuot bien do %d"
                                % (rel, name, got, want, abs(got - want), tol))
                    continue
                if not new:
                    errs.append("[%s] replace_between '%s': khoa 'new' rong, op nay "
                                "khong dung de xoa" % (rel, name))
                    continue
            if not co_new:
                continue
            body = body[:i] + new + body[k:]
            checks.append(("one", name, new))
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
        if op == "delete":
            dst = ""
        elif "new" not in e:
            print("  GHI CHU %s: chua co 'new', probe giu nguyen doan nay" % name)
            continue
        elif op == "replace":
            dst = e["new"]
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


def nhom_theo_file(edits):
    """Gom edit theo file, giu nguyen thu tu xuat hien trong spec."""
    order, groups = [], {}
    for e in edits:
        rel = Path(e.get("file", "")).as_posix()
        if rel not in groups:
            groups[rel] = []
            order.append(rel)
        groups[rel].append(e)
    return order, groups


def run_probe(spec_path, fill):
    """Dem neo va do vung, KHONG ghi file dich nao, dung chung duong ap voi --apply."""
    try:
        spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    except Exception as exc:
        print("LOI doc spec: %s" % exc)
        return 1
    edits = spec.get("edits")
    if not isinstance(edits, list) or not edits:
        print("LOI: spec thieu khoa 'edits' hoac rong")
        return 1
    print("=== PROBE: chi dem neo va do vung, KHONG ghi gi ===")
    print("Cac edit tren cung mot file duoc ap TUAN TU trong bo nho, dung thu tu spec.")
    bad = 0
    for i, e in enumerate(edits):
        if not isinstance(e, dict):
            print("LOI: edit thu %d khong phai doi tuong JSON" % (i + 1))
            return 1
        e.setdefault("name", "edit%d" % (i + 1))
        op = e.get("op", "")
        if op not in OPS:
            print("%-24s %-16s OP KHONG HOP LE, phai la mot trong: %s"
                  % (e["name"], op, ", ".join(OPS)))
            bad += 1
        if op == "replace_between" and e.get("end_mode", "giu") not in END_MODES:
            print("%-24s end_mode '%s' KHONG HOP LE, chi nhan: %s"
                  % (e["name"], e.get("end_mode"), ", ".join(END_MODES)))
            bad += 1
    if bad:
        print("")
        print("=== PROBE: %d muc, %d muc hong ===" % (len(edits), bad))
        return 2

    work = copy.deepcopy(edits)
    for e in work:
        cf = e.get("content_file")
        if not cf or "new" in e:
            continue
        cp = Path(cf)
        if not cp.is_absolute():
            cp = REPO / cf
        if cp.is_file():
            e["new"] = cp.read_text(encoding="utf-8").replace("\r\n", "\n")
            print("NOI DUNG %s <- %s (%d byte)"
                  % (e["name"], cp, len(e["new"].encode("utf-8"))))
        else:
            print("GHI CHU %s: content_file chua ton tai (%s), probe chi dem neo"
                  % (e["name"], cp))

    errs, do_duoc = [], {}
    order, groups = nhom_theo_file(work)
    for rel in order:
        print("")
        print("FILE %s" % rel)
        apply_edits(rel, groups[rel], errs, probe=True, do_duoc=do_duoc)

    if fill:
        changed = False
        for e in edits:
            if e.get("op") != "replace_between":
                continue
            k = (Path(e.get("file", "")).as_posix(), e["name"])
            if k in do_duoc and e.get("expect_bytes") != do_duoc[k]:
                e["expect_bytes"] = do_duoc[k]
                changed = True
        if changed:
            Path(spec_path).write_text(
                json.dumps(spec, ensure_ascii=False, indent=1),
                encoding="utf-8", newline="\n")
            print("")
            print("da ghi expect_bytes do duoc nguoc vao spec")

    print("")
    if errs:
        print("=== PROBE: %d muc, %d muc hong ===" % (len(edits), len(errs)))
        for x in errs:
            print("  " + x)
        return 2
    print("=== PROBE: %d muc, 0 muc hong ===" % len(edits))
    return 0


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
            if e.get("end_mode", "giu") not in END_MODES:
                print("LOI: edit '%s' khoa 'end_mode' phai la 'giu' hoac 'gom'"
                      % e["name"])
                return 1
            for k in ("expect_bytes", "tol_bytes"):
                if k in e and (isinstance(e[k], bool) or not isinstance(e[k], int)
                               or e[k] < 0):
                    print("LOI: edit '%s' khoa '%s' phai la so nguyen khong am"
                          % (e["name"], k))
                    return 1

    order, groups = nhom_theo_file(edits)
    allow = set(spec.get("allow_paths") or [])
    index, byname = da.build_index()
    for rel in order:
        index.add(rel)
        byname.setdefault(Path(rel).name, [])
        if rel not in byname[Path(rel).name]:
            byname[Path(rel).name].append(rel)

    errs, warns, plan = [], [], []
    for rel in order:
        print("")
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
                    if rel.lower().endswith(".py"):
                        continue
                    w = ("[%s] CANH BAO ten tran '%s' -- nen viet '%s'"
                         % (rel, tok, tgt))
                    if w not in warns:
                        warns.append(w)
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
    """Lay so nguyen dung ngay sau mot khoa dang 'thuc=' trong output cua tool."""
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


def so_hai_duong(tmp, day, h1, h2, vung_giu):
    """Bat --probe va --apply do CUNG mot vung sau khi mot edit truoc do da lam vung ay to ra.

    Spec co hai edit tren cung mot file: edit dau chen them chu ngay sau neo dau,
    edit sau do vung giua hai neo. Probe cu do tung edit doc lap tren ban goc nen
    se bao dung bang vung_giu, tuc BO SOT phan vua chen; probe tuan tu phai bao
    dung bang vung_giu cong so byte da chen. Ca nay khong nhin ma thoat, no doc
    thang con so hai ben in ra sau chu 'thuc='.
    """
    chen = "\ndong chen selftest " + day + "\n"
    spec = {"edits": [
        {"name": "chentruoc", "file": "docs/TODO.md", "op": "insert_after",
         "anchor": h1, "new": chen},
        {"name": "dovung", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": h2, "new": "x\n", "expect_bytes": 1, "tol_bytes": 0}]}
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
    a = lay_so(out[0], "thuc=")
    b = lay_so(out[1], "thuc=")
    mong = vung_giu + len(chen.encode("utf-8"))
    return (a == b == mong), a, b, mong


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
    vung_giu = len(todo[i:j].encode("utf-8"))
    vung_gom = len(todo[i:j + len(h2)].encode("utf-8"))
    than = "\n\nnoi dung thu cua selftest, khong nhac file nao.\n\n"
    moi_giu = h1 + than
    moi_gom = h1 + than + h2

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
         "start": h1, "end": h2, "new": moi_giu, "expect_bytes": vung_giu}]}))
    cases.append(("between-gom-tuong-thich", 0, "KIEM TRUOC: SACH", {"edits": [
        {"name": "betweengom", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": h2, "new": moi_gom, "expect_bytes": vung_gom,
         "end_mode": "gom"}]}))
    cases.append(("between-nuot-neo-cuoi", 0, "se mat han khoi file", {"edits": [
        {"name": "nuotneo", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": h2, "new": moi_giu, "expect_bytes": vung_gom,
         "end_mode": "gom"}]}))
    cases.append(("between-lap-neo-cuoi", 0, "se bi lap hai lan", {"edits": [
        {"name": "lapneo", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": h2, "new": moi_gom, "expect_bytes": vung_giu}]}))
    cases.append(("between-end-khop-nhieu", 2, "ca hai phai dung 1", {"edits": [
        {"name": "endnhieu", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": "\n\n", "new": moi_giu, "expect_bytes": vung_giu}]}))
    cases.append(("between-lech-byte", 2, "vuot bien do", {"edits": [
        {"name": "lechbyte", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": h2, "new": moi_giu, "expect_bytes": 50}]}))
    cases.append(("between-end-mode-la", 1, "phai la 'giu' hoac 'gom'", {"edits": [
        {"name": "modela", "file": "docs/TODO.md", "op": "replace_between",
         "start": h1, "end": h2, "new": moi_giu, "expect_bytes": vung_giu,
         "end_mode": "nuot"}]}))

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
    seq = REPO / ("_selftest_tuantu_%s.txt" % day)
    seq.write_text("GIU%s\nNEOA%s\nNEOB%s\ncuoi\n" % (day, day, day),
                   encoding="utf-8", newline="\n")
    cases.append(("probe-tuan-tu-am", 2, "KHONG KHOP", {"edits": [
        {"name": "xoaneo", "file": seq.name, "op": "delete",
         "old": "NEOA%s\n" % day},
        {"name": "dungneodaxoa", "file": seq.name, "op": "replace",
         "old": "NEOA%s" % day, "new": "MOI%s" % day}]}))
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
             "probe-tuan-tu-am": ["--probe"],
             "probe-di-voi-apply": ["--probe", "--apply"],
             "delete-block": ["--apply", "--allow-dirty"],
             "ma-thoat-3": ["--apply", "--allow-dirty"],
             "replace-rong": ["--apply", "--allow-dirty"]}

    rac = [blk, sc3, dup, rong, mdt, dbe, bom, seq]
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
        ok_vung, a_probe, a_apply, mong = so_hai_duong(tmp, day, h1, h2, vung_giu)
        rows.append(("do-vung-mot-duong", 0, 0 if ok_vung else 1,
                     "probe=%d apply=%d mong=%d" % (a_probe, a_apply, mong), ok_vung))
    finally:
        for _p in rac:
            try:
                _p.unlink()
            except OSError:
                pass

    print("")
    print("=== SELFTEST docs_patch ===")
    print("Moi ca duoi day goi lai chinh tool bang mot spec dung mot lan, roi cham hai")
    print("thu: ma thoat co dung du doan khong, va output co chua dung chuoi nhan khong.")
    print("Cot MONG la ma thoat mong doi, cot THAT la ma thoat that.")
    print("vung giua hai heading dau cua docs/TODO.md: %d byte khi GIU neo cuoi, "
          "%d byte khi GOM neo cuoi" % (vung_giu, vung_gom))
    print("ca vuot-tran: docs/STATE.md %d byte, tran %d byte, chen them %d byte"
          % (state_now, state_cap, pad))
    print("%-26s %5s %5s %-28s %s" % ("CA", "MONG", "THAT", "NHAN MONG DOI", "CO NHAN"))
    print("%-26s %5s %5s %-28s %s"
          % ("-" * 26, "-----", "-----", "-" * 28, "-------"))
    bad = 0
    for name, want, got, marker, hit in rows:
        okc = (want == got) and hit
        if not okc:
            bad += 1
        print("%-26s %5d %5d %-28s %s  %s"
              % (name, want, got, marker[:28], "co" if hit else "KHONG",
                 "OK" if okc else "THAT BAI"))
    print("")
    print("KET QUA: %d/%d ca dat" % (len(rows) - bad, len(rows)))
    if bad:
        print("Mong doi moi ca deu dat; thuc te con %d ca hong, doc dong THAT BAI o tren."
              % bad)
    else:
        print("Mong doi moi ca deu dat, thuc te dung nhu vay: tool dung duoc.")
    return 0 if bad == 0 else 2


SPEC_MAU = {
    "allow_paths": ["ten-file-vi-du-khong-co-that.md"],
    "edits": [
        {"name": "vi-du-replace", "file": "docs/TODO.md", "op": "replace",
         "old": "nguyen van doan cu, phai khop dung 1 lan",
         "new": "noi dung moi thay vao cho do"},
        {"name": "vi-du-replace-between", "file": "docs/TODO.md",
         "op": "replace_between", "start": "## Tieu de muc can thay",
         "end": "## Tieu de muc ke tiep",
         "new": "ca muc moi, GOM neo dau, KHONG chep lai neo cuoi",
         "end_mode": "giu", "expect_bytes": 1234, "tol_bytes": 400},
        {"name": "vi-du-delete", "file": "docs/TODO.md", "op": "delete",
         "old": "nguyen van doan can xoa"},
        {"name": "vi-du-delete-block", "file": "docs/TODO.md",
         "op": "delete_block", "anchor": "dong dau cua khoi can xoa"},
        {"name": "vi-du-insert-after", "file": "docs/TODO.md",
         "op": "insert_after", "anchor": "dong dung ngay truoc cho chen",
         "new": "\ndong moi chen vao sau neo\n"},
        {"name": "vi-du-insert-before", "file": "docs/TODO.md",
         "op": "insert_before", "anchor": "dong dung ngay sau cho chen",
         "new": "dong moi chen vao truoc neo\n"},
        {"name": "vi-du-append", "file": "docs/TODO.md", "op": "append",
         "new": "\ndoan noi them o cuoi file\n"},
        {"name": "vi-du-create", "file": "docs/file-hoan-toan-moi.md",
         "op": "create",
         "content_file": "D:\\IT\\capcut-lab\\data\\tmp\\tmp_20260805_noi_dung.txt"},
    ]}


def in_mau(ngan=False):
    """In mot spec mau hop le cho ca tam op, de nguoi dung va tro ly khong phai di tim tai lieu moi biet khuon."""
    if ngan:
        print("")
        print("Xem spec mau day du: python tools/docs_patch.py --example")
        return 1
    print("=== SPEC MAU, hop le cho ca tam op ===")
    print(json.dumps(SPEC_MAU, ensure_ascii=False, indent=1))
    print("")
    print("Moi edit bat buoc co ba khoa name, file, op. Khoa noi dung moi la 'new',")
    print("hoac 'content_file' tro toi mot file UTF-8 tren dia -- khai ca hai la loi.")
    print("Doan tu khoang muoi dong tro len thi dung replace_between voi hai neo ngan")
    print("va duy nhat, dung dan ca doan cu lam neo.")
    print("")
    print("replace_between: MAC DINH end_mode='giu', vung bi thay gom neo dau va dung")
    print("ngay TRUOC neo cuoi, nen 'new' KHONG duoc chep lai neo cuoi, neu chep thi")
    print("neo cuoi lap hai lan. Dat end_mode='gom' de nuot luon neo cuoi nhu ban cu,")
    print("khi do 'new' PHAI chep lai neo cuoi neu con muon giu no.")
    print("Quy trinh: --probe --fill-bytes de dem neo va tu do expect_bytes, roi")
    print("--apply de ghi. Bo --apply thi khong ghi gi. Khong can chay thu o giua:")
    print("--apply da chay lai toan bo phep kiem truoc va tu choi ghi khi co loi.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--fill-bytes", action="store_true")
    ap.add_argument("--example", action="store_true")
    a = ap.parse_args()
    if a.example:
        return in_mau()
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
    ma = (run_probe(a.spec, a.fill_bytes) if a.probe
          else run_spec(a.spec, a.apply, a.allow_dirty))
    if ma == 1:
        in_mau(ngan=True)
    return ma


if __name__ == "__main__":
    sys.exit(main())