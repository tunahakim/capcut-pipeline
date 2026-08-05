"""clone_project.py <scaffold-sạch> <thư-mục-drafts> <tên-project-mới>
Tạo project CapCut mới bằng cách nhân bản scaffold: sinh GUID mới cho mọi GUID tìm thấy và giữ nguyên kiểu hoa thường, đổi tên thư mục Timelines theo GUID mới, thay tên project cũ bằng tên mới trong mọi file .json .tmp .bak .txt, xoá .capcut-cli-history cùng các file .prepost .prepost2 .kfbak, đặt lại dấu thời gian và draft_name.
Vào: thư mục scaffold sạch. Ra: thư mục project mới trong drafts, kèm báo cáo main_timeline_id, đối chiếu draft_name với tên thư mục, số file còn sót tên cũ.
Từ chối chạy nếu thư mục đích đã tồn tại; mọi nội dung JSON đều được kiểm hợp lệ trước khi ghi đè.
Đặt luôn draft_fold_path bằng đường dẫn tuyệt đối của thư mục project mới, gộp từ tools/fix_fold_path.py ngày 01/08/2026, nên sau khi clone không còn bước tay nào; báo cáo cuối in giá trị đã ghi kèm cờ KHOP.
[KIEM: du lieu that]
"""

import json, pathlib, re, shutil, sys, time, uuid

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SRC = pathlib.Path(sys.argv[1])          # scaffold sach
DR  = pathlib.Path(sys.argv[2])          # thu muc drafts
NEW = sys.argv[3]                        # ten project moi
DST = DR / NEW

if not SRC.is_dir(): sys.exit("Khong thay scaffold: %s" % SRC)
if DST.exists():     sys.exit("Da ton tai: %s" % DST)

OLD = SRC.name
GUID = re.compile(r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}")
EXT = {".json", ".tmp", ".bak", ".txt", ""}

# --- 1. gom GUID tu toan bo scaffold ---
found = []
for f in sorted(SRC.rglob("*")):
    if f.is_file() and f.suffix.lower() in EXT:
        try: found += GUID.findall(f.read_text(encoding="utf-8"))
        except Exception: pass
for d in SRC.rglob("*"):
    if d.is_dir(): found += GUID.findall(d.name)

def like(sample, g):
    return g.upper() if sample == sample.upper() else g.lower()

mapping = {}
for g in found:
    if g not in mapping:
        mapping[g] = like(g, str(uuid.uuid4()))
print("Tim thay %d GUID duy nhat:" % len(mapping))
for a, b in mapping.items():
    print("   %s -> %s" % (a, b))

# --- 2. copy ---
shutil.copytree(SRC, DST)
for junk in (".capcut-cli-history",):
    p = DST / junk
    if p.exists(): shutil.rmtree(p, ignore_errors=True)
for b in list(DST.rglob("*.prepost")) + list(DST.rglob("*.prepost2")) + list(DST.rglob("*.kfbak")):
    b.unlink()
print("\nDa copy -> %s" % DST)

# --- 3. thay noi dung ---
def swap(s):
    for a, b in mapping.items():
        s = s.replace(a, b)
    return s.replace(OLD, NEW)

nfile = 0
for f in sorted(DST.rglob("*")):
    if not f.is_file() or f.suffix.lower() not in EXT: continue
    try: txt = f.read_text(encoding="utf-8")
    except Exception: continue
    out = swap(txt)
    if out != txt:
        if f.suffix.lower() == ".json" or f.name.endswith(".tmp"):
            try: json.loads(out)
            except Exception as e:
                print("   BO QUA (JSON hong): %s -> %s" % (f.name, e)); continue
        f.write_text(out, encoding="utf-8"); nfile += 1
print("Da sua noi dung %d file" % nfile)

# --- 4. doi ten thu muc timeline ---
for d in sorted(DST.rglob("*"), key=lambda p: -len(str(p))):
    if d.is_dir() and GUID.fullmatch(d.name) and d.name in mapping:
        d.rename(d.with_name(mapping[d.name]))
        print("Doi ten thu muc: %s -> %s" % (d.name, mapping[d.name]))

# --- 5. dau thoi gian + draft_name ---
now = int(time.time() * 1_000_000)
def touch(fp, keys, extra=None):
    if not fp.exists(): return
    d = json.loads(fp.read_text(encoding="utf-8"))
    for k in keys:
        if k in d: d[k] = now
    if extra: d.update(extra)
    fp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

touch(DST / "Timelines" / "project.json", ("create_time", "update_time"))
FOLD = str(DST.resolve())
touch(DST / "draft_meta_info.json",
      ("tm_draft_create", "tm_draft_modified", "tm_duration"),
      {"draft_name": NEW, "draft_fold_path": FOLD})

# --- 6. bao cao ---
print("\n=== KET QUA ===")
pj = json.loads((DST / "Timelines" / "project.json").read_text(encoding="utf-8"))
print("  main_timeline_id =", pj["main_timeline_id"])
print("  thu muc timeline ton tai =", (DST / "Timelines" / pj["main_timeline_id"]).is_dir())
mi = json.loads((DST / "draft_meta_info.json").read_text(encoding="utf-8"))
print("  draft_name =", mi.get("draft_name"), " | folder =", NEW,
      "->", "KHOP" if mi.get("draft_name") == NEW else "*** LECH ***")
got_fold = mi.get("draft_fold_path")
print("  draft_fold_path =", got_fold,
      "->", "KHOP" if got_fold == FOLD else "*** LECH ***")
leftover = 0
for f in DST.rglob("*"):
    if f.is_file() and f.suffix.lower() in EXT:
        try:
            if OLD in f.read_text(encoding="utf-8"): leftover += 1
        except Exception: pass
print("  file con sot ten cu '%s': %d" % (OLD, leftover))
print("\nXONG.")