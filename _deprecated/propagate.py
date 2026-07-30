import json, sys, pathlib, shutil

proj = pathlib.Path(sys.argv[1])
src = proj / "draft_content.json"

pj = json.loads((proj / "Timelines" / "project.json").read_text(encoding="utf-8"))
tid = pj["main_timeline_id"]
nested = proj / "Timelines" / tid

targets = [proj / "template-2.tmp",
           nested / "draft_content.json",
           nested / "template-2.tmp"]

data = src.read_text(encoding="utf-8")
json.loads(data)  # validate

for t in targets:
    if t.exists():
        shutil.copy2(t, str(t) + ".prepropagate")
    t.write_text(data, encoding="utf-8")
    print("ghi:", t.relative_to(proj))

print("main_timeline_id:", tid)
