import json, pathlib, shutil, sys, uuid

PROJ = pathlib.Path(sys.argv[1])
CW, CH = 1920.0, 1080.0
IMG_W, IMG_H = 1376.0, 768.0
CANVAS_BIT = 4096
KF_S, KF_X, KF_Y = "KFTypeScaleX", "KFTypePositionX", "KFTypePositionY"
LEGACY = {"UNIFORM_SCALE", "KFTYPEUNIFORMSCALE"}

# anh fit theo chieu rong -> nua chieu cao anh trong NDC = KY * s
DISP_H = CW * IMG_H / IMG_W
KY = DISP_H / CH

def lim_x(s): return 1.0 - s
def lim_y(s): return 1.0 - KY * s

# shot: (scale_a, scale_b, f, dao_chieu)   f = ti le bien do so voi muc toi da
PLAN = {
 1: (0.78, 0.86, 0.55, False),
 2: (0.80, 0.88, 0.45, False),
 3: (0.78, 0.86, 0.55, False),
 4: (0.75, 0.85, 0.65, False),
 5: (0.88, 0.78, 0.45, True ),
 6: (0.80, 0.88, 0.45, False),
 7: (0.78, 0.88, 0.60, False),
 8: (0.75, 0.85, 1.00, False),   # PROBE BIEN: phai cham sat mep o cuoi shot
}

print("KY = %.5f   (nua cao anh NDC = KY * scale)" % KY)
print("\n=== KE HOACH & KIEM TRA BIEN ===")
computed = {}
bad = 0
for n, (sa, sb, f, rev) in sorted(PLAN.items()):
    ax = f * min(lim_x(sa), lim_x(sb))
    ay = f * min(lim_y(sa), lim_y(sb))
    xa, xb = (ax, -ax) if rev else (-ax, ax)
    ya, yb = (ay, -ay) if rev else (-ay, ay)
    okA = abs(xa) <= lim_x(sa) + 1e-9 and abs(ya) <= lim_y(sa) + 1e-9
    okB = abs(xb) <= lim_x(sb) + 1e-9 and abs(yb) <= lim_y(sb) + 1e-9
    if not (okA and okB):
        bad += 1
    computed[n] = (sa, sb, xa, xb, ya, yb)
    print("  shot %d  s %.2f->%.2f  f=%.2f  x %+.4f->%+.4f  y %+.4f->%+.4f"
          % (n, sa, sb, f, xa, xb, ya, yb))
    print("           UI px: x %+6.0f->%+6.0f  y %+6.0f->%+6.0f | gioi han cuoi x=%.4f y=%.4f  %s"
          % (xa * CW, xb * CW, ya * CH, yb * CH, lim_x(sb), lim_y(sb),
             "OK" if okA and okB else "<<< VUOT LE"))
if bad:
    sys.exit("DUNG LAI: %d shot vuot le" % bad)

def uid(): return str(uuid.uuid4()).upper()

def pt(t, v):
    return {"id": uid(), "curveType": "Line", "time_offset": int(t),
            "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
            "values": [float(v)], "string_value": "", "graphID": ""}

def kfl(prop, dur, a, b):
    return {"id": uid(), "material_id": "", "property_type": prop,
            "keyframe_list": [pt(0, a), pt(dur, b)]}

pj = json.loads((PROJ / "Timelines" / "project.json").read_text(encoding="utf-8"))
TID = pj["main_timeline_id"]
tg = [PROJ / "draft_content.json", PROJ / "template-2.tmp",
      PROJ / "Timelines" / TID / "draft_content.json",
      PROJ / "Timelines" / TID / "template-2.tmp"]
tg = [t for t in tg if t.exists()]
if len(tg) != 4:
    sys.exit("Chi thay %d/4 file dich" % len(tg))

d = json.loads(tg[0].read_text(encoding="utf-8"))
blur_ids = {c["id"] for c in d["materials"].get("canvases", []) if c.get("type") == "canvas_blur"}
vids = {m["id"]: m for m in d["materials"].get("videos", [])}
segs = next(t for t in d["tracks"] if t.get("type") == "video")["segments"]

print("\n=== AP DUNG (%d segment) ===" % len(segs))
for i, seg in enumerate(segs, start=1):
    if i not in computed:
        continue
    sa, sb, xa, xb, ya, yb = computed[i]
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
    mat = vids.get(seg.get("material_id"))
    if any(r in blur_ids for r in seg.get("extra_material_refs", [])) and mat:
        mat["check_flag"] = int(mat.get("check_flag", 0)) | CANVAS_BIT
    print("  shot %d %s dur=%9.4fs  giu %d kf cu" % (i, str(seg["id"])[:8], dur / 1e6, len(keep)))

payload = json.dumps(d, ensure_ascii=False)
json.loads(payload)
print()
for t in tg:
    shutil.copy2(t, str(t) + ".prepost2")
    t.write_text(payload, encoding="utf-8")
    print("  ghi:", t.relative_to(PROJ))
print("\nXONG.")