"""syntax.py
Đọc capcut describe và in cú pháp đầy đủ của chín lệnh hay dùng: add-effect, add-filter, add-sticker, add-sfx, export, render, tracks, batch, import-srt.
Vào: không tham số, cần capcut-cli trong PATH. Ra: in console usage, tham số vị trí và tuỳ chọn kèm mô tả của từng lệnh.
[KIEM: chua]
"""

import subprocess, json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

p = subprocess.run("capcut describe", shell=True, capture_output=True)
d = json.loads(p.stdout.decode("utf-8", errors="replace"))
cs = d["commands"] if isinstance(d, dict) and "commands" in d else d

WANT = ("add-effect", "add-filter", "add-sticker", "add-sfx",
        "export", "render", "tracks", "batch", "import-srt")

for c in cs:
    if c.get("name") not in WANT:
        continue
    print("=" * 74)
    print(c.get("name"), "|", c.get("usage"))
    if c.get("description"):
        print("  ", c["description"])
    for x in c.get("positionals", []):
        print("   pos: %-16s %-10s %s" % (x.get("name"), x.get("type"),
              "REQUIRED" if x.get("required") else "optional"))
    for o in c.get("options", []):
        print("   opt: %-26s %-8s :: %s" % ("/".join(o.get("flags", [])),
              o.get("type"), o.get("description")))
    print()