#!/usr/bin/env python3
"""
kb_apply.py - sinh keyframe Ken Burns tong quat cho project CapCut 9.1.0
Xem tai lieu muc X.8. He toa do: muc VIII.6.
  transform la NDC, +-1 = mep canvas
  transform.x = so_tren_UI / 1920      transform.y = so_tren_UI / 1080
  +X = phai, +Y = LEN TREN
  Rang buoc khong ho mep:  |x| <= 1-KX*s    |y| <= 1-KY*s
  KX va KY tinh theo TUNG anh, cong thuc o docs/reference.md muc 3.1
Cach dung:  python kb_apply.py <project-dir>
"""
import json, pathlib, shutil, sys, uuid

CW, CH = 1920.0, 1080.0
IMG_W, IMG_H = 1376.0, 768.0
CANVAS_BIT = 4096
KF_S, KF_X, KF_Y = "KFTypeScaleX", "KFTypePositionX", "KFTypePositionY"
LEGACY = {"UNIFORM_SCALE", "KFTYPEUNIFORMSCALE"}

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

def kxky(w, h):
    """KX, KY theo reference.md muc 3.1: anh duoc chua tron trong canvas."""
    ar_i, ar_c = float(w) / float(h), CW / CH
    return (1.0, ar_c / ar_i) if ar_i >= ar_c else (ar_i / ar_c, 1.0)


KX, KY = kxky(IMG_W, IMG_H)
# idx shot -> (kx, ky). Lop goi ngoai (bench_kb.py) nap tu shots.csv.
# Shot vang mat trong GEO thi dung KX, KY mac dinh cua bo anh test v3.
GEO = {}


def geo(n):
    return GEO.get(n, (KX, KY))


def lim_x(s, kx=KX):
    return 1.0 - kx * s


def lim_y(s, ky=KY):
    return 1.0 - ky * s


def uid():
    return str(uuid.uuid4()).upper()


def pt(t, v):
    return {"id": uid(), "curveType": "Line", "time_offset": int(t),
            "left_control": {"x": 0.0, "y": 0.0},
            "right_control": {"x": 0.0, "y": 0.0},
            "values": [float(v)], "string_value": "", "graphID": ""}


def kfl(prop, dur, a, b):
    return {"id": uid(), "material_id": "", "property_type": prop,
            "keyframe_list": [pt(0, a), pt(dur, b)]}


def main():
    if len(sys.argv) < 2:
        sys.exit("Dung: python kb_apply.py <project-dir>")
    proj = pathlib.Path(sys.argv[1])
    if not proj.is_dir():
        sys.exit("Khong phai thu muc: %s" % proj)

    print("KX mac dinh = %.5f   KY mac dinh = %.5f" % (KX, KY))
    print("hinh hoc rieng tung shot: %d shot co trong GEO" % len(GEO))

    print("\n=== KIEM TRA BIEN ===")
    bad = 0
    for n, (sa, sb, xa, xb, ya, yb, note) in sorted(PLAN.items()):
        kx, ky = geo(n)
        err = []
        for tag, s, x, y in (("dau", sa, xa, ya), ("cuoi", sb, xb, yb)):
            if abs(x) > lim_x(s, kx) + 1e-9:
                err.append("%s:x %.4f>%.4f" % (tag, abs(x), lim_x(s, kx)))
            if abs(y) > lim_y(s, ky) + 1e-9:
                err.append("%s:y %.4f>%.4f" % (tag, abs(y), lim_y(s, ky)))
        if err:
            bad += 1
        print("  shot %d  s %.2f->%.2f  UIpx x %+5.0f->%+5.0f  y %+5.0f->%+5.0f | %-24s %s"
              % (n, sa, sb, xa * CW, xb * CW, ya * CH, yb * CH, note,
                 "OK" if not err else "<<< " + "; ".join(err)))
    if bad:
        sys.exit("DUNG LAI: %d shot vuot le, khong ghi gi ca" % bad)

    pj = proj / "Timelines" / "project.json"
    if not pj.exists():
        sys.exit("Khong thay Timelines/project.json - project khong hop le")
    tid = json.loads(pj.read_text(encoding="utf-8"))["main_timeline_id"]
    tg = [proj / "draft_content.json", proj / "template-2.tmp",
          proj / "Timelines" / tid / "draft_content.json",
          proj / "Timelines" / tid / "template-2.tmp"]
    tg = [t for t in tg if t.exists()]
    if len(tg) != 4:
        sys.exit("Chi thay %d/4 file dich" % len(tg))

    d = json.loads(tg[0].read_text(encoding="utf-8"))
    blur_ids = {c["id"] for c in d["materials"].get("canvases", [])
                if c.get("type") == "canvas_blur"}
    vids = {m["id"]: m for m in d["materials"].get("videos", [])}
    anim_ids = {m["id"] for m in d["materials"].get("material_animations", [])}

    vtracks = [t for t in d["tracks"] if t.get("type") == "video"]
    if len(vtracks) != 1:
        sys.exit("Co %d track video, mong doi dung 1" % len(vtracks))
    segs = vtracks[0]["segments"]
    print("\n  main_timeline_id = %s" % tid)
    print("  track video: %d segment | canvas_blur: %d" % (len(segs), len(blur_ids)))

    print("\n=== AP DUNG ===")
    nflag = 0
    for i, seg in enumerate(segs, start=1):
        if i not in PLAN:
            continue
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
        ncv = sum(1 for r in refs if r in blur_ids)
        if ncv > 1:
            print("     CANH BAO: shot %d tham chieu %d canvas_blur" % (i, ncv))
        mat = vids.get(seg.get("material_id"))
        if ncv and mat is not None:
            o = int(mat.get("check_flag", 0))
            if o | CANVAS_BIT != o:
                mat["check_flag"] = o | CANVAS_BIT
                nflag += 1
        combo = "COMBO" if any(r in anim_ids for r in refs) else ""
        print("  shot %d %s %8.3fs  %-24s blurref=%d %s"
              % (i, str(seg["id"])[:8], dur / 1e6, note, ncv, combo))

    print("\n  check_flag bat bit 4096 cho %d material" % nflag)

    payload = json.dumps(d, ensure_ascii=False)
    json.loads(payload)
    print()
    for t in tg:
        shutil.copy2(t, str(t) + ".prepost")
        t.write_text(payload, encoding="utf-8")
        print("  ghi:", t.relative_to(proj))

    print("\n=== DOC LAI TU BAN LONG ===")
    d2 = json.loads((proj / "Timelines" / tid / "draft_content.json")
                    .read_text(encoding="utf-8"))
    v2 = {m["id"]: m for m in d2["materials"].get("videos", [])}
    for n2, s in enumerate(next(t for t in d2["tracks"]
                                if t.get("type") == "video")["segments"], 1):
        c = s.get("clip") or {}
        kf = [k.get("property_type") for k in (s.get("common_keyframes") or [])]
        print("  %d %s scale=%.2f xform=(%+.4f,%+.4f) flag=%s kf=%d"
              % (n2, str(s["id"])[:8], c.get("scale", {}).get("x", 0),
                 c.get("transform", {}).get("x", 0),
                 c.get("transform", {}).get("y", 0),
                 v2.get(s.get("material_id"), {}).get("check_flag"), len(kf)))
    print("\nXONG. Chay check_sync.py roi mo CapCut kiem tra.")


if __name__ == "__main__":
    main()