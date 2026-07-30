import json, pathlib, shutil, sys, uuid

KF_SCALE, KF_PX, KF_PY = "KFTypeScaleX", "KFTypePositionX", "KFTypePositionY"
LEGACY = {"UNIFORM_SCALE", "KFTYPEUNIFORMSCALE"}

def uid(): return str(uuid.uuid4()).upper()

def pt(t, v):
    return {"id": uid(), "curveType": "Line", "time_offset": int(t),
            "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
            "values": [float(v)], "string_value": "", "graphID": ""}

def kflist(prop, dur, a, b):
    return {"id": uid(), "material_id": "", "property_type": prop,
            "keyframe_list": [pt(0, a), pt(dur, b)]}

def targets(proj):
    out = [proj / "draft_content.json", proj / "template-2.tmp"]
    pj = proj / "Timelines" / "project.json"
    if pj.exists():
        tid = json.loads(pj.read_text(encoding="utf-8")).get("main_timeline_id")
        if tid:
            n = proj / "Timelines" / tid
            out += [n / "draft_content.json", n / "template-2.tmp"]
            print(f"  main_timeline_id = {tid}")
    return [t for t in out if t.exists()]

proj = pathlib.Path(sys.argv[1])
plan = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
tg = targets(proj)
if len(tg) != 4:
    print(f"  CANH BAO: chi thay {len(tg)} file dich")

src = tg[0]
d = json.loads(src.read_text(encoding="utf-8"))
vtrack = next(t for t in d["tracks"] if t.get("type") == "video")
segs = vtrack["segments"]
print(f"  doc tu {src.name}, {len(segs)} segment video\n")

for key, spec in plan.items():
    i = int(key) - 1
    if not (0 <= i < len(segs)):
        print(f"  BO QUA shot {key}: ngoai pham vi"); continue
    seg = segs[i]
    dur = int(seg["target_timerange"]["duration"])

    keep = [k for k in (seg.get("common_keyframes") or [])
            if str(k.get("property_type", "")).upper() not in LEGACY
            and k.get("property_type") not in (KF_SCALE, KF_PX, KF_PY)]

    clip = seg.setdefault("clip", {})
    new = []
    if "scale" in spec:
        a, b = spec["scale"]
        new.append(kflist(KF_SCALE, dur, a, b))
        clip["scale"] = {"x": float(b), "y": float(b)}
    if "posx" in spec:
        ax, bx = spec["posx"]
        ay, by = spec.get("posy", [0.0, 0.0])
        new.append(kflist(KF_PX, dur, ax, bx))
        new.append(kflist(KF_PY, dur, ay, by))
        clip["transform"] = {"x": float(bx), "y": float(by)}

    seg["common_keyframes"] = keep + new
    seg["uniform_scale"] = {"on": True, "value": 1.0}
    props = [k["property_type"] for k in new]
    print(f"  shot {key} id={str(seg['id'])[:8]} dur={dur/1e6:.4f}s -> {props}")

payload = json.dumps(d, ensure_ascii=False)
json.loads(payload)
print()
for t in tg:
    shutil.copy2(t, str(t) + ".kfbak")
    t.write_text(payload, encoding="utf-8")
    print(f"  ghi: {t.relative_to(proj)}")

print("\n-- DOC LAI TU BAN LONG --")
tid = json.loads((proj / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
d2 = json.loads((proj / "Timelines" / tid / "draft_content.json").read_text(encoding="utf-8"))
for n, s in enumerate(next(t for t in d2["tracks"] if t.get("type") == "video")["segments"], 1):
    kf = [k.get("property_type") for k in (s.get("common_keyframes") or [])]
    sc = (s.get("clip") or {}).get("scale", {}).get("x")
    print(f"  {n} {str(s['id'])[:8]} scale={sc} kf={kf}")