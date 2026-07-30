import json, sys, pathlib

proj = pathlib.Path(sys.argv[1])
scale = float(sys.argv[2])

def patch(path):
    if not path.exists():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for tr in d.get("tracks", []):
        if tr.get("type") != "video":
            continue
        for seg in tr.get("segments", []):
            clip = seg.get("clip")
            if not clip:
                continue
            clip["scale"] = {"x": scale, "y": scale}
            seg["common_keyframes"] = [
                k for k in seg.get("common_keyframes", [])
                if "SCALE" not in str(k.get("property_type", "")).upper()
            ]
            n += 1
    path.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return n

for name in ("draft_content.json", "template-2.tmp"):
    r = patch(proj / name)
    print(f"{name}: {r} segment" if r is not None else f"{name}: khong co")
