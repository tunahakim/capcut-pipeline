#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data_manifest.py
Kiểm kê hai nhánh ngoài repo là data/ và vendor/ ra bản kê JSON có kích thước và hash SHA256 từng file để hai máy so được với nhau; vendor/ chia hai khối, canonical là sáu thứ mà mục 3 của START-HERE.md kể ra và chỉ khối này tham gia phán xử mã thoát, extra là mọi thứ còn lại, vẫn ghi đủ kích thước và hash để không mất bằng chứng nhưng chỉ in ra dạng thông tin; vendor/Cache_effect gộp thành một mục tổng có số file, tổng byte và một hash tổng hợp, không liệt kê từng file.
Vào: chế độ quét bắt buộc --scan --machine --data --vendor --out; chế độ so bắt buộc --compare --mine --theirs; không có cơ chế tự dò đường dẫn. Ra: chế độ quét ghi JSON ở --out và in báo cáo, chế độ so chỉ in console.
Mã thoát 0 khi sạch; 2 khi quét gặp file đọc không được nên bản kê bị thủng, hoặc khi so thấy lệch ở phần được phán xử, hoặc khi một trong hai bản kê có lỗ; 1 khi sai tham số, thiếu thư mục, hoặc bản kê hỏng.
Loại trừ cố định: data/tmp, data/archive, mọi thư mục tên __pycache__ và .git.
Ví dụ: python tools/data_manifest.py --scan --machine lab --data D:/IT/capcut-lab/data --vendor D:/IT/capcut-lab/vendor --out manifests/lab.json
[KIEM: mot lan]
"""
import argparse, fnmatch, hashlib, json, os, sys, time, datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SCHEMA = 1
BS = 1024 * 1024
SEP = chr(92)
LP = SEP + SEP + "?" + SEP
NL = chr(10)

EXCLUDE_DIR_NAMES = {"__pycache__", ".git"}
EXCLUDE_DATA_ROOT = {"tmp", "archive"}
ROLLUP_DIRS = {"Cache_effect"}
CANON_VENDOR_NAMES = {
    "Cache_effect",
    "capcut-cli-0.15.0.tgz",
    "MANIFEST.txt",
    "README_PARITY.txt",
    "CapCut_9.1.0.3879_User_X64_exe_en-US.exe",
    "CapCut_9.1.0.3879_User_X64_exe_en-US.yaml",
    "CapCut_9.1.0.3879.sha256.txt",
    "setup_1_runtimes.ps1",
    "setup_2_capcut.ps1",
}
CANON_VENDOR_GLOBS = ()
JUDGED = ("data", "vendor_canonical")

def lp(p):
    s = str(p)
    if os.name == "nt" and len(s) > 240 and not s.startswith(LP):
        return LP + s
    return s

def relp(root, p):
    r = os.path.relpath(str(p), str(root))
    return "" if r == "." else r.replace(SEP, "/")

def human(n):
    return "%.1f MB" % (n / 1048576.0)

def sha256_file(p):
    h = hashlib.sha256()
    with open(lp(p), "rb") as f:
        while True:
            b = f.read(BS)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def iter_files(root, skip_root):
    for dirpath, dirnames, filenames in os.walk(str(root)):
        r = relp(root, dirpath)
        keep = []
        for name in sorted(dirnames):
            if name in EXCLUDE_DIR_NAMES:
                continue
            if r == "" and name in skip_root:
                continue
            keep.append(name)
        dirnames[:] = keep
        for fn in sorted(filenames):
            if r == "" and fn in skip_root:
                continue
            yield os.path.join(dirpath, fn)

def file_entry(root, p, errors):
    try:
        sz = os.path.getsize(lp(p))
        h = sha256_file(p)
    except OSError as e:
        errors.append({"path": relp(root, p), "error": str(e)})
        return None
    return {"kind": "file", "size": sz, "sha256": h}

def rollup_dir(root, d, mode, errors):
    files = []
    for dirpath, dirnames, filenames in os.walk(str(d)):
        dirnames[:] = sorted([x for x in dirnames if x not in EXCLUDE_DIR_NAMES])
        for fn in sorted(filenames):
            files.append(os.path.join(dirpath, fn))
    files.sort(key=lambda x: relp(root, x).lower())
    h = hashlib.sha256()
    n = 0
    total = 0
    for p in files:
        try:
            sz = os.path.getsize(lp(p))
            fh = sha256_file(p) if mode == "content" else ""
        except OSError as e:
            errors.append({"path": relp(root, p), "error": str(e)})
            continue
        n += 1
        total += sz
        h.update((relp(root, p) + "|" + str(sz) + "|" + fh + NL).encode("utf-8"))
    return {"kind": "rollup", "mode": mode, "files": n, "bytes": total, "sha256": h.hexdigest()}

def classify(top):
    if top in CANON_VENDOR_NAMES:
        return "canonical", "ten khai bao"
    for g in CANON_VENDOR_GLOBS:
        if fnmatch.fnmatch(top, g):
            return "canonical", "mau " + g
    return "extra", "khong khai bao"

def total_bytes(m):
    t = 0
    for v in m.values():
        t += v.get("bytes", 0) if v.get("kind") == "rollup" else v.get("size", 0)
    return t

def cmd_scan(a):
    missing = [n for n in ("machine", "data", "vendor", "out") if not getattr(a, n)]
    if missing:
        print("LOI: che do --scan thieu tham so bat buoc: " + ", ".join("--" + m for m in missing))
        return 1
    data_root = os.path.abspath(a.data)
    vendor_root = os.path.abspath(a.vendor)
    for lbl, d in (("--data", data_root), ("--vendor", vendor_root)):
        if not os.path.isdir(d):
            print("LOI: %s khong phai thu muc: %s" % (lbl, d))
            return 1
    errors = []
    t0 = time.time()

    print("=== QUET ===")
    print("may        : " + a.machine)
    print("data        : " + data_root)
    print("vendor      : " + vendor_root)
    print("loai tru    : data/tmp, data/archive, __pycache__, .git")
    print("rollup      : " + ", ".join(sorted(ROLLUP_DIRS)) + "  (che do " + a.rollup_mode + ")")
    print("")

    data_map = {}
    for p in iter_files(data_root, EXCLUDE_DATA_ROOT):
        e = file_entry(data_root, p, errors)
        if e:
            data_map[relp(data_root, p)] = e
    print("data   : %d file, %s  (%.1f s)" % (len(data_map), human(total_bytes(data_map)), time.time() - t0))

    canon = {}
    extra = {}
    present_rollups = sorted([n for n in ROLLUP_DIRS if os.path.isdir(os.path.join(vendor_root, n))])
    for n in present_rollups:
        ent = rollup_dir(vendor_root, os.path.join(vendor_root, n), a.rollup_mode, errors)
        (canon if classify(n)[0] == "canonical" else extra)[n] = ent
        print("rollup %-14s: %d file, %s  (%.1f s)" % (n, ent["files"], human(ent["bytes"]), time.time() - t0))
    for p in iter_files(vendor_root, set(present_rollups)):
        r = relp(vendor_root, p)
        e = file_entry(vendor_root, p, errors)
        if not e:
            continue
        (canon if classify(r.split("/")[0])[0] == "canonical" else extra)[r] = e
    print("vendor canonical: %d muc, %s" % (len(canon), human(total_bytes(canon))))
    print("vendor extra    : %d muc, %s" % (len(extra), human(total_bytes(extra))))

    print("")
    print("=== PHAN LOAI GOC VENDOR ===")
    print("%-52s %-5s %-10s %s" % ("ten", "loai", "khoi", "vi sao"))
    for name in sorted(os.listdir(vendor_root), key=str.lower):
        kind = "thumuc" if os.path.isdir(os.path.join(vendor_root, name)) else "file"
        k, why = classify(name)
        print("%-52s %-5s %-10s %s" % (name[:52], kind[:5], k, why))
    absent = sorted([n for n in CANON_VENDOR_NAMES if not os.path.exists(os.path.join(vendor_root, n))])
    print("")
    print("=== CANONICAL KHAI BAO MA KHONG THAY (%d) ===" % len(absent))
    for n in absent:
        print("  " + n)

    doc = {
        "_meta": {
            "schema": SCHEMA,
            "tool": "tools/data_manifest.py",
            "machine": a.machine,
            "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data_root": data_root,
            "vendor_root": vendor_root,
            "hash": "sha256",
            "rollup_mode": a.rollup_mode,
            "exclude_dir_names": sorted(EXCLUDE_DIR_NAMES),
            "exclude_data_root": sorted(EXCLUDE_DATA_ROOT),
            "canon_vendor_names": sorted(CANON_VENDOR_NAMES),
            "canon_vendor_globs": list(CANON_VENDOR_GLOBS),
            "canon_declared_absent": absent,
            "counts": {"data": len(data_map), "vendor_canonical": len(canon), "vendor_extra": len(extra)},
            "bytes": {"data": total_bytes(data_map), "vendor_canonical": total_bytes(canon), "vendor_extra": total_bytes(extra)},
            "errors": errors,
            "elapsed_s": round(time.time() - t0, 1),
        },
        "data": data_map,
        "vendor_canonical": canon,
        "vendor_extra": extra,
    }
    out = os.path.abspath(a.out)
    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(lp(out), "w", encoding="utf-8", newline=NL) as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + NL)

    dt = time.time() - t0
    tot = total_bytes(data_map) + total_bytes(canon) + total_bytes(extra)
    print("")
    print("ghi: %s  (%d byte)" % (out, os.path.getsize(lp(out))))
    print("tong %s trong %.1f s = %.1f MB/s" % (human(tot), dt, (tot / 1048576.0) / dt if dt > 0 else 0))
    print("")
    if errors:
        print("=== LOI DOC (%d) ===" % len(errors))
        for e in errors[: a.max_list]:
            print("  %s  %s" % (e["path"], e["error"]))
        print("KET LUAN: ban ke bi thung, chua du can cu tuyen bo sach")
        return 2
    print("KET LUAN: QUET SACH, 0 loi doc")
    return 0

def load_manifest(path, label):
    if not os.path.isfile(path):
        print("LOI: %s khong ton tai: %s" % (label, path))
        return None
    try:
        with open(lp(path), "r", encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        print("LOI: %s doc khong duoc: %s" % (label, e))
        return None
    for k in ("_meta",) + JUDGED:
        if k not in d:
            print("LOI: %s thieu khoi %s" % (label, k))
            return None
    return d

def diff_section(a_map, b_map):
    only_a = sorted(set(a_map) - set(b_map), key=str.lower)
    only_b = sorted(set(b_map) - set(a_map), key=str.lower)
    changed = []
    for k in sorted(set(a_map) & set(b_map), key=str.lower):
        x, y = a_map[k], b_map[k]
        if x.get("kind") != y.get("kind"):
            changed.append((k, "kieu muc khac nhau"))
        elif x.get("kind") == "rollup":
            if x.get("mode") != y.get("mode"):
                changed.append((k, "che do rollup khac nhau, khong so duoc"))
            elif x.get("sha256") != y.get("sha256"):
                changed.append((k, "rollup lech: %d file %d byte / %d file %d byte" % (x.get("files", 0), x.get("bytes", 0), y.get("files", 0), y.get("bytes", 0))))
        elif x.get("size") != y.get("size"):
            changed.append((k, "kich thuoc %d / %d" % (x.get("size", 0), y.get("size", 0))))
        elif x.get("sha256") != y.get("sha256"):
            changed.append((k, "hash khac, cung kich thuoc %d" % x.get("size", 0)))
    return only_a, only_b, changed

def show(title, items, limit):
    print("-- %s (%d) --" % (title, len(items)))
    for it in items[:limit]:
        print("  " + (it if isinstance(it, str) else "%s  %s" % it))
    if len(items) > limit:
        print("  ... con %d muc nua" % (len(items) - limit))

def cmd_compare(a):
    missing = [n for n in ("mine", "theirs") if not getattr(a, n)]
    if missing:
        print("LOI: che do --compare thieu tham so bat buoc: " + ", ".join("--" + m for m in missing))
        return 1
    m = load_manifest(os.path.abspath(a.mine), "--mine")
    t = load_manifest(os.path.abspath(a.theirs), "--theirs")
    if m is None or t is None:
        return 1
    mm, tm = m["_meta"], t["_meta"]
    nm, nt = mm.get("machine", "?"), tm.get("machine", "?")
    print("=== SO BAN KE ===")
    print("mine   : %-8s sinh %s  %s" % (nm, mm.get("generated_utc", "?"), os.path.abspath(a.mine)))
    print("theirs : %-8s sinh %s  %s" % (nt, tm.get("generated_utc", "?"), os.path.abspath(a.theirs)))
    print("rollup : %s / %s" % (mm.get("rollup_mode", "?"), tm.get("rollup_mode", "?")))
    if nm == nt:
        print("CANH BAO: hai ban ke cung ten may, co the dang so mot ban voi chinh no")
        nm, nt = nm + "/mine", nt + "/theirs"
    if mm.get("schema") != tm.get("schema"):
        print("LOI: schema khac nhau, %s / %s" % (mm.get("schema"), tm.get("schema")))
        return 1
    holes = len(mm.get("errors") or []) + len(tm.get("errors") or [])
    if holes:
        print("CANH BAO: tong %d loi doc trong hai ban ke, co lo bang chung" % holes)
    total = 0
    for sec in JUDGED:
        oa, ob, ch = diff_section(m[sec], t[sec])
        total += len(oa) + len(ob) + len(ch)
        print("")
        print("=== %s ===" % sec.upper())
        show("CHI CO BEN " + nm, oa, a.max_list)
        show("CHI CO BEN " + nt, ob, a.max_list)
        show("KHAC NHAU", ch, a.max_list)
    oa, ob, ch = diff_section(m.get("vendor_extra", {}), t.get("vendor_extra", {}))
    print("")
    print("=== VENDOR_EXTRA (thong tin, khong tinh vao ma thoat) ===")
    print("chi ben %s: %d | chi ben %s: %d | khac: %d" % (nm, len(oa), nt, len(ob), len(ch)))
    print("")
    if total == 0 and not holes:
        print("KET LUAN: SACH, 0 lech tren phan duoc phan xu")
        return 0
    if total:
        print("KET LUAN: CO LECH, tong %d muc tren phan duoc phan xu" % total)
    if holes:
        print("KET LUAN: ban ke co lo, chua du can cu tuyen bo sach")
    return 2

def main():
    ap = argparse.ArgumentParser(add_help=True, description="Kiem ke data/ va vendor/ ra ban ke co kich thuoc va hash.")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--machine")
    ap.add_argument("--data")
    ap.add_argument("--vendor")
    ap.add_argument("--out")
    ap.add_argument("--rollup-mode", dest="rollup_mode", choices=("content", "meta"), default="content")
    ap.add_argument("--mine")
    ap.add_argument("--theirs")
    ap.add_argument("--max-list", dest="max_list", type=int, default=40)
    a = ap.parse_args()
    if a.scan == a.compare:
        print("LOI: chon dung mot che do, --scan hoac --compare")
        print("  python tools/data_manifest.py --scan --machine lab --data <duong dan> --vendor <duong dan> --out manifests/lab.json")
        print("  python tools/data_manifest.py --compare --mine manifests/lab.json --theirs manifests/render.json")
        return 1
    return cmd_scan(a) if a.scan else cmd_compare(a)

if __name__ == "__main__":
    sys.exit(main())