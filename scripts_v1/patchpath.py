"""patchpath.py <project-dir> <chuỗi-cũ> <chuỗi-mới> [--apply]
Thay chuỗi đường dẫn trong mọi file .json .tmp .bak .txt của một project; mặc định chỉ báo cáo, phải có --apply mới ghi.
Vào: thư mục project và cặp chuỗi cũ, mới. Ra: các file đã sửa kèm bản sao .pathbak cho từng file, và bảng kiểm media OK hoặc THIẾU đọc từ cả bản gốc lẫn bản LONG.
Bỏ qua file nào mà sau khi thay không còn là JSON hợp lệ.
"""

import json, pathlib, shutil, sys

proj = pathlib.Path(sys.argv[1]); old = sys.argv[2]; new = sys.argv[3]
apply = "--apply" in sys.argv
EXT = {".json", ".tmp", ".bak", ".txt", ""}

hits = []
for f in sorted(proj.rglob("*")):
    if not f.is_file() or f.suffix.lower() not in EXT:
        continue
    try:
        txt = f.read_text(encoding="utf-8")
    except Exception:
        continue
    n = txt.count(old)
    if n:
        hits.append((f, n, txt))

if not hits:
    print("Khong tim thay chuoi nao. Co the da sua roi.")
    sys.exit()

print(f"Tim thay {len(hits)} file chua '{old}':")
for f, n, _ in hits:
    print(f"  {n:>3} lan  {f.relative_to(proj)}")

if not apply:
    print("\n(CHE DO BAO CAO - chua sua gi. Them --apply de ghi)")
    sys.exit()

print()
for f, n, txt in hits:
    out = txt.replace(old, new)
    if f.suffix.lower() == ".json" or f.name.endswith(".tmp"):
        try:
            json.loads(out)
        except Exception as e:
            print(f"  BO QUA (khong phai JSON hop le): {f.name} -> {e}")
            continue
    shutil.copy2(f, str(f) + ".pathbak")
    f.write_text(out, encoding="utf-8")
    print(f"  da sua {n} lan: {f.relative_to(proj)}")

print("\n-- KIEM TRA LAI --")
tid = json.loads((proj / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
for tag, fp in (("GOC ", proj / "draft_content.json"),
                ("LONG", proj / "Timelines" / tid / "draft_content.json")):
    d = json.loads(fp.read_text(encoding="utf-8"))
    ok = bad = 0
    for b in ("videos", "audios"):
        for m in d.get("materials", {}).get(b, []):
            if pathlib.Path(m.get("path", "")).exists(): ok += 1
            else:
                bad += 1
                print(f"     THIEU: {m.get('path')}")
    print(f"{tag} media OK={ok} THIEU={bad}")