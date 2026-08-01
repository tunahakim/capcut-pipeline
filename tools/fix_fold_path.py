"""fix_fold_path.py <project-dir>
Ghi lại draft_fold_path trong draft_meta_info.json cho khớp vị trí thật của thư mục project, việc bắt buộc sau khi clone hoặc di chuyển project.
Vào: thư mục project. Ra: file draft_meta_info.json đã sửa, in giá trị trước và sau cùng cờ đã sửa hay chưa.
Ghi thẳng, không sao lưu, không có chế độ chạy thử. Dự kiến gộp vào scripts_v1/clone_project.py để bớt một bước tay dễ quên.
"""

import json, pathlib, sys
proj = pathlib.Path(sys.argv[1])
mi = proj / "draft_meta_info.json"
d = json.loads(mi.read_text(encoding="utf-8"))
want = str(proj)
print("draft_fold_path truoc : %s" % d.get("draft_fold_path"))
print("thu muc that          : %s" % want)
changed = False
for k in ("draft_fold_path", "draft_root_path", "draft_removable_storage_device"):
    if k in d and isinstance(d[k], str) and d[k] and d[k] != want and "draft" in k:
        if k == "draft_fold_path" and d[k] != want:
            d[k] = want
            changed = True
if changed:
    mi.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print("da sua                : %s" % changed)
print("draft_fold_path sau   : %s" % json.loads(mi.read_text(encoding="utf-8")).get("draft_fold_path"))