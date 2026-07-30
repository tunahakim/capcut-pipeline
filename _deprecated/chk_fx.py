import json, pathlib, sys
proj = pathlib.Path(sys.argv[1])
d = json.loads((proj / "draft_content.json").read_text(encoding="utf-8"))
cache = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"

print("\n=== MATERIALS.TRANSITIONS ===")
for t in d["materials"].get("transitions", []):
    print(json.dumps(t, ensure_ascii=False, indent=1))
    p = t.get("path", "")
    print(f"  >> path ton_tai = {pathlib.Path(p).exists() if p else 'PATH RONG'}")
    rid = str(t.get("resource_id", ""))
    print(f"  >> thu muc cache {rid} = {(cache / rid).exists()}\n")

print("=== MATERIALS.MATERIAL_ANIMATIONS ===")
for m in d["materials"].get("material_animations", []):
    for a in m.get("animations", []):
        print(f"  {a.get('type'):4} {a.get('name')} id={a.get('resource_id')} "
              f"start={a.get('start')} dur={a.get('duration')}")
        p = a.get("path", "")
        print(f"       path ton_tai = {pathlib.Path(p).exists() if p else 'PATH RONG'}  [{p}]")

print("\n=== TIMING SAU KHI THEM (kiem tra khong dich) ===")
for i, s in enumerate(next(t for t in d["tracks"] if t["type"] == "video")["segments"], 1):
    tt = s["target_timerange"]
    refs = []
    for bucket in ("transitions", "material_animations"):
        ids = {x["id"] for x in d["materials"].get(bucket, [])}
        if any(r in ids for r in s.get("extra_material_refs", [])):
            refs.append(bucket[:5])
    print(f"  {i} {str(s['id'])[:8]} start={int(tt['start'])/1e6:9.4f} "
          f"dur={int(tt['duration'])/1e6:8.4f}  {' '.join(refs)}")