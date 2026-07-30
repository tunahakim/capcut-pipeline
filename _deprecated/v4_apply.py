import json, pathlib, shutil, sys, uuid

PROJ = pathlib.Path(sys.argv[1])
CW, CH = 1920.0, 1080.0
KY = (CW * 768.0 / 1376.0) / CH          # = 0.99225
CANVAS_BIT = 4096
KF_S, KF_X, KF_Y = "KFTypeScaleX", "KFTypePositionX", "KFTypePositionY"
LEGACY = {"UNIFORM_SCALE", "KFTYPEUNIFORMSCALE"}

def lim_x(s): return 1.0 - s
def lim_y(s): return 1.0 - KY * s

# shot: (sa, sb, xa, xb, ya, yb, mo_ta)
PLAN = {
 1: (0.72, 0.86,  0.000,  0.000,  0.000,  0.000, "zoom in, dung yen"),
 2: (0.82, 0.82, -0.150,  0.150,  0.000,  0.000, "pan ngang trai->phai"),
 3: (0.78, 0.86, -0.084,  0.084, -0.088,  0.088, "cheo len phai"),
 4: (0.92, 0.76,  0.050, -0.050, -0.030,  0.030, "ZOOM OUT tu can canh"),
 5: (0.80, 0.88,  0.050, -0.050,  0.055, -0.055, "cheo xuong trai"),
 6: (0.84, 0.84,  0.000,  0.000, -0.120,  0.120, "pan doc duoi->tren"),
 7: (0.78, 0.88,  0.060, -0.060, -0.060,  0.060, "cheo len trai"),
 8: (0.80, 0.90, -0.040,  0.020, -0.030,  0.040, "zoom in cham + drift"),
}

print("KY = %.5f" % KY)
print("\n=== KIEM TRA BIEN (ca 2 diem dau-cuoi) ===")
bad = 0
for n, (sa, sb, xa, xb, ya, yb, note) in sorted(PLAN.items()):
    e = []
    for tag, s, x, y in (("dau", sa, xa, ya), ("cuoi", sb, xb, yb)):
        if abs(x) > lim_x(s) + 1e-9: e.append("%s:x %.3f>%.3f" % (tag, abs(x), lim_x(s)))
        if abs(y) > lim_y(s) + 1e-9: e.append("%s:y %.3f>%.3f" % (tag, abs(y), lim_y(s)))
    if e: bad += 1
    print("  shot %d  s %.2f->%.2f  UIpx x %+5.0f->%+5.0f  y %+5.0f->%+5.0f  | %-24s %s"
          % (n, sa, sb, xa*CW, xb*CW, ya*CH, yb*CH, note, "OK" if not e else "<<< " + "; ".join(e)))
if bad: sys.exit("DUNG LAI: %d shot vuot le" % bad)

def uid(): return str(uuid.uuid4()).upper()
def pt(t, v):
    return {"id": uid(), "curveType": "Line", "time_offset": int(t),
            "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
            "values": [float(v)], "string_value": "", "graphID": ""}
def kfl(p, dur, a, b):
    return {"id": uid(), "material_id": "", "property_type": p,
            "keyframe_list": [pt(0, a), pt(dur, b)]}

TID = json.loads((PROJ / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
tg = [PROJ / "draft_content.json", PROJ / "template-2.tmp",
      PROJ / "Timelines" / TID / "draft_content.json",
      PROJ / "Timelines" / TID / "template-2.tmp"]
tg = [t for t in tg if t.exists()]
if len(tg) != 4: sys.exit("Chi thay %d/4 file" % len(tg))

d = json.loads(tg[0].read_text(encoding="utf-8"))
blur_ids = {c["id"] for c in d["materials"].get("canvases", []) if c.get("type") == "canvas_blur"}
vids = {m["id"]: m for m in d["materials"].get("videos", [])}
anim_ids = {m["id"] for m in d["materials"].get("material_animations", [])}
vtracks = [t for t in d["tracks"] if t.get("type") == "video"]
if len(vtracks) != 1: sys.exit("Co %d track video, mong doi 1" % len(vtracks))
segs = vtracks[0]["segments"]
print("\n  track video: %d segment | canvas_blur: %d" % (len(segs), len(blur_ids)))

print("\n=== AP DUNG ===")
for i, seg in enumerate(segs, start=1):
    if i not in PLAN: continue
    sa, sb, xa, xb, ya, yb, note = PLAN[i]
    dur = int(seg["target_timerange"]["duration"])
    keep = [k for k in (seg.get("common_keyframes") or [])
            if str(k.get("property_type", "")).upper() not in LEGACY
            and k.get("property_type") not in (KF_S, KF_X, KF_Y)]
    seg["common_keyframes"] = keep + [kfl(KF_S, dur, sa, sb),
                                      kfl(KF_X, dur, xa, xb),
                                      kfl(KF_Y, dur, ya, yb)]
    seg["uniform_scale"] = {"on": True, "value": 1.0}
    clip = seg.setdefault("clip", {})
    clip["scale"] = {"x": float(sb), "y": float(sb)}
    clip["transform"] = {"x": float(xb), "y": float(yb)}
    refs = seg.get("extra_material_refs", [])
    mat = vids.get(seg.get("material_id"))
    if any(r in blur_ids for r in refs) and mat:
        mat["check_flag"] = int(mat.get("check_flag", 0)) | CANVAS_BIT
    combo = "COMBO" if any(r in anim_ids for r in refs) else ""
    print("  shot %d %s %8.3fs  %-24s %s" % (i, str(seg["id"])[:8], dur/1e6, note, combo))

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
    c = s.get("clip") or {}
    kf = [k.get("property_type") for k in (s.get("common_keyframes") or [])]
    print("  %d %s scale=%.2f xform=(%+.4f,%+.4f) flag=%s kf=%d"
          % (n2, str(s["id"])[:8], c.get("scale", {}).get("x", 0),
             c.get("transform", {}).get("x", 0), c.get("transform", {}).get("y", 0),
             v2.get(s.get("material_id"), {}).get("check_flag"), len(kf)))
print("\nXONG.")