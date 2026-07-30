import json, pathlib, shutil, sys, uuid

PROJ = pathlib.Path(sys.argv[1])
CW, CH = 1920.0, 1080.0
IMG_W, IMG_H = 1376.0, 768.0
CANVAS_BIT = 4096
KF_S, KF_X, KF_Y = "KFTypeScaleX", "KFTypePositionX", "KFTypePositionY"
LEGACY = {"UNIFORM_SCALE", "KFTYPEUNIFORMSCALE"}

# shot: (scale_a, scale_b, x_a_px, x_b_px, y_a_px, y_b_px)
PLAN = {
 1: (0.78, 0.86, -110,  110,  -70,   70),
 2: (0.80, 0.88,  -90,   90,  -55,   55),
 3: (0.78, 0.86, -110,  110,  -70,   70),
 4: (0.75, 0.85, -130,  130,  -75,   75),
 5: (0.88, 0.78,   90,  -90,   55,  -55),
 6: (0.80, 0.88,  -90,   90,  -55,   55),
 7: (0.78, 0.88, -100,  100,  -60,   60),
 8: (0.75, 0.85, -144,  144,  -84,   84),
}

# anh fit theo chieu rong canvas
DISP_W = CW
DISP_H = CW * IMG_H / IMG_W

def limits(s):
    return (CW - DISP_W * s) / 2.0, (CH - DISP_H * s) / 2.0

print("=== KIEM TRA BIEN (truoc khi ghi) ===")
bad = 0
for n, (sa, sb, xa, xb, ya, yb) in sorted(PLAN.items()):
    smax = max(sa, sb)
    lx, ly = limits(smax)
    mx, my = max(abs(xa), abs(xb)), max(abs(ya), abs(yb))
    ok = mx <= lx + 1e-9 and my <= ly + 1e-9
    if not ok:
        bad += 1
    print("  shot %d  smax=%.2f  gioi han x=%6.1f y=%5.1f | dung x=%6.1f y=%5.1f  %s"
          % (n, smax, lx, ly, mx, my, "OK" if ok else "<<< VUOT LE"))
if bad:
    sys.exit("DUNG LAI: co %d shot vuot le" % bad)

def uid():
    return str(uuid.uuid4()).upper()

def pt(t, v):
    return {"id": uid(), "curveType": "Line", "time_offset": int(t),
            "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
            "values": [float(v)], "string_value": "", "graphID": ""}

def kfl(prop, dur, a, b):
    return {"id": uid(), "material_id": "", "property_type": prop,
            "keyframe_list": [pt(0, a), pt(dur, b)]}

def targets(p):
    out = [p / "draft_content.json", p / "template-2.tmp"]
    pj = p / "Timelines" / "project.json"
    tid = json.loads(pj.read_text(encoding="utf-8"))["main_timeline_id"]
    n = p / "Timelines" / tid
    out += [n / "draft_content.json", n / "template-2.tmp"]
    print("\n  main_timeline_id =", tid)
    return [t for t in out if t.exists()], tid

tg, TID = targets(PROJ)
if len(tg) != 4:
    sys.exit("Chi thay %d/4 file dich" % len(tg))

d = json.loads(tg[0].read_text(encoding="utf-8"))
blur_ids = {c["id"] for c in d["materials"].get("canvases", []) if c.get("type") == "canvas_blur"}
vids = {m["id"]: m for m in d["materials"].get("videos", [])}
vtrack = next(t for t in d["tracks"] if t.get("type") == "video")
segs = vtrack["segments"]
print("  %d segment video, %d canvas_blur\n" % (len(segs), len(blur_ids)))

print("=== AP DUNG ===")
nflag = 0
for i, seg in enumerate(segs, start=1):
    spec = PLAN.get(i)
    if not spec:
        continue
    sa, sb, xa, xb, ya, yb = spec
    dur = int(seg["target_timerange"]["duration"])
    rxa, rxb = xa / CW, xb / CW
    rya, ryb = ya / CH, yb / CH

    keep = [k for k in (seg.get("common_keyframes") or [])
            if str(k.get("property_type", "")).upper() not in LEGACY
            and k.get("property_type") not in (KF_S, KF_X, KF_Y)]
    new = [kfl(KF_S, dur, sa, sb), kfl(KF_X, dur, rxa, rxb), kfl(KF_Y, dur, rya, ryb)]
    seg["common_keyframes"] = keep + new
    seg["uniform_scale"] = {"on": True, "value": 1.0}
    clip = seg.setdefault("clip", {})
    clip["scale"] = {"x": float(sb), "y": float(sb)}
    clip["transform"] = {"x": float(rxb), "y": float(ryb)}

    refs = seg.get("extra_material_refs", [])
    ncv = sum(1 for r in refs if r in blur_ids)
    mat = vids.get(seg.get("material_id"))
    if ncv and mat is not None:
        o = int(mat.get("check_flag", 0))
        if o | CANVAS_BIT != o:
            mat["check_flag"] = o | CANVAS_BIT
            nflag += 1
    print("  shot %d %s dur=%8.4fs  s %.2f->%.2f  x %+.4f->%+.4f  y %+.4f->%+.4f  blurref=%d"
          % (i, str(seg["id"])[:8], dur / 1e6, sa, sb, rxa, rxb, rya, ryb, ncv))

print("\n  check_flag da bat bit 4096 cho %d material" % nflag)

payload = json.dumps(d, ensure_ascii=False)
json.loads(payload)
print()
for t in tg:
    shutil.copy2(t, str(t) + ".prepost")
    t.write_text(payload, encoding="utf-8")
    print("  ghi:", t.relative_to(PROJ))

print("\n=== DOC LAI TU BAN LONG ===")
d2 = json.loads((PROJ / "Timelines" / TID / "draft_content.json").read_text(encoding="utf-8"))
v2 = {m["id"]: m for m in d2["materials"].get("videos", [])}
for n2, s in enumerate(next(t for t in d2["tracks"] if t.get("type") == "video")["segments"], 1):
    kf = [k.get("property_type") for k in (s.get("common_keyframes") or [])]
    c = s.get("clip") or {}
    print("  %d %s scale=%.2f xform=(%+.4f,%+.4f) flag=%s kf=%s"
          % (n2, str(s["id"])[:8], c.get("scale", {}).get("x", 0),
             c.get("transform", {}).get("x", 0), c.get("transform", {}).get("y", 0),
             v2.get(s.get("material_id"), {}).get("check_flag"), kf))
print("\nXONG.")