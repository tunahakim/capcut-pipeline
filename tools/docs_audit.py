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
Nam loai do khong tinh la loi. Loi gom FILE THIEU, TRUNG TEN, MUC THIEU, SAI CHO,
VUOT TRAN va PLANNED DA CHET; SAI CHO nghia la file co that nhung nam khac duong dan
ma tai lieu ghi, con PLANNED DA CHET nghia la entry trong PLANNED tro toi file nay da
ton tai nen phai xoa khoi PLANNED.

Miễn trừ trần có thời hạn. Trần khai trong PER_FILE_BUDGET là con số cứng, còn docs/budget-waivers.json chỉ hoãn một lần vượt trần cụ thể tới một ngày hết hạn chứ không nới trần: còn hạn thì file hiện ở khối MIEN TRU TRAN kèm đủ số byte thừa và mã thoát vẫn 0, quá hạn thì thành VAN DE thật, và khi file đã tụt xuống dưới trần mà mục miễn trừ vẫn còn thì tool báo MIEN TRU THUA để người dùng xoá mục đi.
Hàm cap_for(rel, size) là nguồn sự thật duy nhất về trần, dùng chung cho tool này và tools/docs_patch.py, nên hai tool không thể phán xử lệch nhau; biến môi trường DOCS_WAIVERS trỏ tool sang một bảng miễn trừ khác và chỉ dùng cho phép tự kiểm.

Van newline. Repo co ca file CRLF va file LF, nen mot script va ghi ky tu xuong dong
kieu LF vao file dang CRLF se lam file do LAN hai kieu, va luc do tools/docs_patch.py
cung tools/rlog_index.py dung lai. Quet va chuan hoa bang tools/nl_audit.py. Tool nay
KHONG kiem newline va KHONG kiem ma hoa, nen mot file UTF-16LE nhu reference/describe.json
van lot qua sach.
[KIEM: du lieu that]
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
# Tran rieng, khai bao tuong minh kem ly do. Hai nhom, hai ly do khac nhau.
# Nhom chat hon BUDGET -- chong phinh, khong lien quan gi toi fetch: hai file nay
# la anh chup va danh sach, phien nao tro ly cung doc nguoi chung tu dau phien.
# Nhom rong hon BUDGET -- thuoc tang DAN o docs/ai-reading-channel.md muc 5, nguoi
# dung dan thang vao hoi thoai nen khong dinh nguong cat 10000 token cua crawler.
# Nhom nhat ky trong thu muc research-log KHONG co tran rieng, va tran 26 KB voi nhom
# do la nguong FETCH mot luot cua crawler chu KHONG phai nguong chong phinh: nhat ky la
# thi qua khu chi ghi them nen dai ngan tuy khoi luong viec cua phien. File lon nhat
# hien 8455 byte, tuc 32 phan tram tran. Vuot tran thi TACH THEO CHU DE thanh hai file
# cung ngay, dung cat chu -- cat chu trong nhat ky la pha bang chung. Xem
# docs/ai-reading-channel.md.
PER_FILE_BUDGET = {
    "docs/STATE.md":    25 * 1024,  # noi 04/08/2026 tu 15 KB: van la chong phinh, nhung 15 KB
                                    # cham tran dung luc ket phien khi khong con ngu canh de rut gon,
                                    # tuc luat tu no gay ra kieu hong no dinh chan. Rut gon la viec rieng.
    "docs/TODO.md":     25 * 1024,  # noi 04/08/2026: chua dac ta docs_patch.py; cham 25 KB thi tach file
    "docs/scripts.md":  40 * 1024,  # tang DAN: sinh tu dong, dai theo so script
    "docs/reference.md": 40 * 1024, # tang DAN: so tra, day len theo kien thuc da do
    "docs/failures.md": 40 * 1024,  # tang DAN: so tra loi, chi ghi them
}

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
PLANNED = {"docs/scripts-archive.md", "tools/docs_size.py", "tools/probe_drafts.py",
           "pipeline/__main__.py", "tools/scaffold_make.py"}
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


def build_index():
    """Dung index duong dan repo va bang tra ten tran. Dung chung voi tools/docs_patch.py."""
    index = set(walk_repo())
    byname = {}
    for p in index:
        byname.setdefault(Path(p).name, []).append(p)
    return index, byname


WAIVER_FILE = "docs/budget-waivers.json"
_WAIVER_CACHE = None


def load_waivers():
    """Đọc bảng miễn trừ trần từ docs/budget-waivers.json, hoặc từ đường dẫn khai trong biến môi trường DOCS_WAIVERS khi cần thử nghiệm, rồi trả về cặp (bảng, lỗi) với bảng là dict đường dẫn tương đối trỏ tới mục miễn trừ."""
    global _WAIVER_CACHE
    if _WAIVER_CACHE is not None:
        return _WAIVER_CACHE
    p = Path(os.environ.get("DOCS_WAIVERS") or (REPO / WAIVER_FILE))
    bang, loi = {}, []
    if not p.is_file():
        _WAIVER_CACHE = (bang, loi)
        return _WAIVER_CACHE
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        loi.append("khong doc duoc bang mien tru: %s" % exc)
        _WAIVER_CACHE = (bang, loi)
        return _WAIVER_CACHE
    if d.get("schema") != 1:
        loi.append("bang mien tru khai schema %r, tool nay chi hieu schema 1"
                   % d.get("schema"))
    for i, w in enumerate(d.get("waivers") or []):
        thieu = [k for k in ("file", "ly_do", "ngay_cap", "het_han") if not w.get(k)]
        if thieu:
            loi.append("muc mien tru thu %d thieu khoa: %s" % (i + 1, ", ".join(thieu)))
            continue
        rel = Path(w["file"]).as_posix()
        if rel in bang:
            loi.append("muc mien tru thu %d trung file %s" % (i + 1, rel))
            continue
        try:
            datetime.date.fromisoformat(w["het_han"])
        except ValueError:
            loi.append("muc mien tru cho %s co het_han %r khong dung dang YYYY-MM-DD"
                       % (rel, w["het_han"]))
            continue
        bang[rel] = w
    _WAIVER_CACHE = (bang, loi)
    return _WAIVER_CACHE


def cap_for(rel, size=None, hom_nay=None):
    """Nguồn sự thật duy nhất về trần kích thước của một file tài liệu, trả về bộ ba (trần, trạng thái miễn trừ, mục miễn trừ) để tool này và tools/docs_patch.py không bao giờ phán xử lệch nhau."""
    rel = Path(rel).as_posix()
    cap = PER_FILE_BUDGET.get(rel, BUDGET)
    bang, _loi = load_waivers()
    w = bang.get(rel)
    if w is None:
        return cap, "KHONG CO", None
    hom_nay = hom_nay or datetime.date.today()
    if datetime.date.fromisoformat(w["het_han"]) < hom_nay:
        return cap, "QUA HAN", w
    if size is not None and size <= cap:
        return cap, "THUA", w
    return cap, "CON HAN", w


def scan():
    index, byname = build_index()

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

    waived = []
    bang_mt, loi_mt = load_waivers()
    for msg in loi_mt:
        problems.append(("MIEN TRU HONG", WAIVER_FILE, 0, WAIVER_FILE, msg))
    for p, s in sorted(sizes.items()):
        if p.startswith(NO_SCAN):
            continue
        cap, tt, w = cap_for(p, s)
        if tt == "THUA":
            problems.append(("MIEN TRU THUA", p, 0, p,
                             "%d byte da xuong duoi tran %d byte, MIEN TRU THUA, "
                             "xoa muc nay di khoi %s" % (s, cap, WAIVER_FILE)))
            continue
        if s <= cap:
            continue
        if tt == "CON HAN":
            waived.append((p, s, cap, w["het_han"], w["ly_do"]))
        elif tt == "QUA HAN":
            problems.append(("VUOT TRAN", p, 0, p,
                             "%d byte > tran %d byte, MIEN TRU HET HAN ngay %s"
                             % (s, cap, w["het_han"])))
        else:
            problems.append(("VUOT TRAN", p, 0, p,
                             "%d byte > tran %d byte" % (s, cap)))
    for rel_mt in sorted(bang_mt):
        if rel_mt not in sizes:
            problems.append(("MIEN TRU HONG", WAIVER_FILE, 0, rel_mt,
                             "khong co file .md nao ten nay trong repo"))

    for pl in sorted(PLANNED):
        if pl in index:
            problems.append(("PLANNED DA CHET", pl, 0, pl,
                             "file da ton tai, xoa khoi PLANNED"))

    referenced = {r["target"] for r in refs if r["target"]}
    orphans = [p for p in md_files
               if p not in referenced and not p.startswith(NO_SCAN)]

    return {"sizes": sizes, "refs": refs, "problems": problems, "planned": planned,
            "ngoai": ngoai, "romans": romans, "orphans": orphans, "waived": waived,
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
        cap, tt_mt, w_mt = cap_for(p, s)
        if p.startswith(NO_SCAN):
            tag = "mien tru (legacy)"
        else:
            tag = ("VUOT %d%%" if s > cap else "ok %d%%") % round(s * 100.0 / cap)
            if p in PER_FILE_BUDGET:
                tag += " (tran rieng %d KB)" % (cap // 1024)
            if tt_mt == "CON HAN":
                tag += " -- MIEN TRU toi %s" % w_mt["het_han"]
            elif tt_mt == "QUA HAN":
                tag += " -- mien tru HET HAN %s" % w_mt["het_han"]
            elif tt_mt == "THUA":
                tag += " -- MIEN TRU THUA, xoa muc di"
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

    wv = d.get("waived") or []
    if wv:
        print("")
        print("=== MIEN TRU TRAN (%d) ===" % len(wv))
        for p, s, cap, han, ly_do in wv:
            print("  %s  %d byte > tran %d byte, mien tru toi %s" % (p, s, cap, han))
            print("      ly do: %s" % ly_do)
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