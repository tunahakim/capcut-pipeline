import json, pathlib, sys

p = pathlib.Path(sys.argv[1])
tid = json.loads((p/"Timelines"/"project.json").read_text(encoding="utf-8"))["main_timeline_id"]

files = [p/"draft_content.json", p/"template-2.tmp",
         p/"Timelines"/tid/"draft_content.json", p/"Timelines"/tid/"template-2.tmp"]

for f in files:
    if not f.exists():
        continue
    d = json.loads(f.read_text(encoding="utf-8"))
    n = 0
    for m in d["materials"].get("videos", []):
        if m.get("type") == "photo":
            m["check_flag"] = 4103
            n += 1
    f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print(f.name, "->", n, "material")
