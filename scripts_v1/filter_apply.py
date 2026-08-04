#!/usr/bin/env python3
"""
filter_apply.py v2 <project-dir>

Thay hoan toan `capcut add-filter` (hong tu goc: catalogue --filters cua namespace
CapCut la 10 entry bia, rid chay lien tiep, khong co md5).

Python la NGUON SU THAT DUY NHAT cho lop filter: script xoa sach moi filter dang co
(ca rac cua CLI lan filter tha tay trong GUI) roi dung lai tu PLAN. Chay lai nhieu
lan cho cung mot ket qua.

path_mode:
  "cache" -> path = Cache/effect/<rid>/<md5>
  "empty" -> path = ""   (thu xem CapCut co tu tai ve khong, giong ca transition)
[KIEM: chua]
"""
import json, pathlib, shutil, sys, uuid

CACHE = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"
import re
HEX32 = re.compile(r"^[0-9a-f]{32}$")


def resolve_path(rid, md5_hint=""):
    """Dung path tai nguyen bang cach QUET cache theo resource_id.
    KHONG tin md5 trong enums.json: do tren 25 material co doi chieu thi 6 cai
    LECH (xem VIII.5). CapCut resolve theo resource_id, CDN tra md5 hien hanh.
    md5_hint chi la phuong an du phong khi khong co thu muc <rid>."""
    d = CACHE / str(rid)
    if d.is_dir():
        subs = [x for x in d.iterdir() if x.is_dir() and HEX32.match(x.name)]
        if subs:
            return str(subs[0]).replace("\\", "/"), "quet theo rid"
    if md5_hint:
        for t in CACHE.iterdir():
            if t.is_dir() and (t / md5_hint).is_dir():
                return str(t / md5_hint).replace("\\", "/"), "quet theo md5 goi y"
    return "", "KHONG TIM THAY TRONG CACHE"


# ---------------- CAU HINH ----------------
PLAN = [
    {"name": "Film", "rid": "6706773528319906308",
     "md5": "f6d0e038c2f82b7e262f7a7698e7f642", "path_mode": "cache",
     "category_id": "18582", "category_name": "Retro",
     "value": 0.70, "half": "first"},
    {"name": "1980", "rid": "7127828208690433311",
     "md5": "d3595847ee8348c69c6037b8003a76e9", "path_mode": "empty",
     "category_id": "", "category_name": "Retro",
     "value": 0.60, "half": "second"},
]
# ------------------------------------------


def uid():
    return str(uuid.uuid4()).upper()


def mk_material(p, path):
    return {
        "id": uid(),
        "effect_id": p["rid"], "resource_id": p["rid"], "third_resource_id": p["rid"],
        "name": p["name"], "report_name": "", "type": "filter", "sub_type": "none",
        "path": path, "value": float(p["value"]), "visible": True,
        "item_effect_type": 0,
        "category_id": p.get("category_id", ""), "category_name": p.get("category_name", ""),
        "category_key": "", "sub_category_id": "", "sub_category_name": "",
        "platform": "all", "apply_target_type": 0, "source_platform": 1, "version": "",
        "adjust_params": [], "time_range": None, "formula_id": "",
        "enable_skin_tone_correction": False, "algorithm_artifact_path": "",
        "intensity_key": "", "face_adjust_params": [], "exclusion_group": [],
        "panel_id": "", "bloom_params": None, "request_id": "",
        "color_match_info": {"target_feature_path": "", "source_feature_path": "",
                             "target_image_path": ""},
        "multi_language_current": "", "lumi_hub_path": "",
        "covering_relation_change": 0,
        "beauty_face_auto_preset_id": "", "beauty_body_auto_preset_id": "",
        "beauty_face_auto_retouch_info": {"face_id": [], "beauty_face_auto_retouch_id": ""},
        "smart_color_mode": 0, "is_from_intelligent_quality": False,
    }


def mk_segment(mid, start, dur, tri):
    return {
        "id": uid(), "source_timerange": None,
        "target_timerange": {"start": int(start), "duration": int(dur)},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "", "state": 0, "speed": 1.0, "is_loop": False,
        "is_tone_modify": False, "reverse": False, "intensifies_audio": False,
        "cartoon": False, "volume": 1.0, "last_nonzero_volume": 1.0,
        "clip": None, "uniform_scale": None,
        "material_id": mid, "extra_material_refs": [],
        "render_index": 10000, "keyframe_refs": [],
        "enable_lut": False, "enable_adjust": False, "enable_hsl": False,
        "visible": True, "group_id": "",
        "enable_color_curves": True, "enable_hsl_curves": True,
        "track_render_index": int(tri), "hdr_settings": None,
        "enable_color_wheels": True, "track_attribute": 0,
        "is_placeholder": False, "template_id": "",
        "enable_smart_color_adjust": False, "template_scene": "default",
        "common_keyframes": [], "caption_info": None,
        "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0,
                              "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
        "enable_color_match_adjust": False, "enable_color_correct_adjust": False,
        "enable_adjust_mask": False, "raw_segment_id": "", "lyric_keyframes": None,
        "enable_video_mask": True, "digital_human_template_group_id": "",
        "color_correct_alg_result": "", "source": "segmentsourcenormal",
        "enable_mask_stroke": False, "enable_mask_shadow": False,
        "enable_color_adjust_pro": False, "segment_color_tag": "",
    }


def main():
    if len(sys.argv) < 2:
        sys.exit("Dung: python filter_apply.py <project-dir>")
    proj = pathlib.Path(sys.argv[1])
    pj = proj / "Timelines" / "project.json"
    if not pj.exists():
        sys.exit("Khong thay Timelines/project.json")
    tid = json.loads(pj.read_text(encoding="utf-8"))["main_timeline_id"]
    tg = [proj / "draft_content.json", proj / "template-2.tmp",
          proj / "Timelines" / tid / "draft_content.json",
          proj / "Timelines" / tid / "template-2.tmp"]
    tg = [t for t in tg if t.exists()]
    if len(tg) != 4:
        sys.exit("Chi thay %d/4 file dich" % len(tg))

    d = json.loads(tg[0].read_text(encoding="utf-8"))
    mats = d.setdefault("materials", {})
    total = int(d.get("duration") or 0)
    print("duration draft = %.4fs" % (total / 1e6))

    # ---- 1. xoa SACH moi filter dang co, ca 2 bucket ----
    print("\n=== DON LOP FILTER CU ===")
    bad = set()
    for bk in ("effects", "video_effects"):
        for m in (mats.get(bk) or []):
            if m.get("type") == "filter" or str(m.get("path", "")).startswith("##_material_placeholder"):
                bad.add(m["id"])
                print("  xoa material %s  bucket=%-14s name=%r" % (m["id"][:8], bk, m.get("name")))
        mats[bk] = [m for m in (mats.get(bk) or []) if m["id"] not in bad]
    if not bad:
        print("  khong co gi de don")

    keep = []
    for t in d.get("tracks", []):
        n0 = len(t.get("segments") or [])
        t["segments"] = [s for s in (t.get("segments") or []) if s.get("material_id") not in bad]
        if len(t["segments"]) != n0:
            print("  xoa %d segment khoi track type=%s" % (n0 - len(t["segments"]), t.get("type")))
        if not t["segments"] and t.get("type") in ("effect", "filter"):
            print("  xoa track rong type=%s id=%s" % (t.get("type"), str(t.get("id"))[:8]))
            continue
        keep.append(t)
    d["tracks"] = keep

    tri = max([int(s.get("track_render_index") or 0)
               for t in d["tracks"] for s in (t.get("segments") or [])] or [0]) + 1
    print("\n  track_render_index moi = %d" % tri)

    # ---- 2. dap filter tu khuon ----
    print("\n=== DAP FILTER ===")
    mats.setdefault("effects", [])
    segs = []
    for p in PLAN:
        if p.get("half") == "first":
            st, en = 0, total // 2
        elif p.get("half") == "second":
            st, en = total // 2, total
        else:
            st = int(p.get("start", 0) * 1e6)
            en = total if p.get("end") is None else int(p["end"] * 1e6)
        if p.get("path_mode") == "empty":
            path, note = "", "PATH RONG (thu nghiem tu tai)"
        else:
            path, note = resolve_path(p["rid"], p.get("md5", ""))
            if not path:
                print("  *** %s: khong co trong cache. Mo CapCut, tab Filters,"
                      " bam mui ten tai xuong, roi chay lai. ***" % p["name"])
        m = mk_material(p, path)
        mats["effects"].append(m)
        segs.append(mk_segment(m["id"], st, en - st, tri))
        print("  %-8s rid=%-20s value=%.2f  %8.3f -> %8.3f s   %s"
              % (p["name"], p["rid"], p["value"], st / 1e6, en / 1e6, note))

    d["tracks"].append({"id": uid(), "type": "filter", "flag": 0, "attribute": 0,
                        "name": "", "is_default_name": True, "segments": segs})

    payload = json.dumps(d, ensure_ascii=False)
    json.loads(payload)
    print()
    for t in tg:
        shutil.copy2(t, str(t) + ".prefilt")
        t.write_text(payload, encoding="utf-8")
        print("  ghi:", t.relative_to(proj))
    print("\n  chuoi '##_material_placeholder' con sot:",
          sum(t.read_text(encoding="utf-8").count("##_material_placeholder") for t in tg))

    print("\n=== DOC LAI TU BAN LONG ===")
    d2 = json.loads((proj / "Timelines" / tid / "draft_content.json").read_text(encoding="utf-8"))
    for t in d2["tracks"]:
        print("  track type=%-7s %d segment" % (t.get("type"), len(t.get("segments") or [])))
    for m in (d2.get("materials", {}).get("effects") or []):
        p = m.get("path", "")
        print("  effects: %-8s value=%.2f path=%s" % (m.get("name"), m.get("value"),
              "(RONG)" if not p else ("TON TAI" if pathlib.Path(p).exists() else "THIEU FILE")))
    print("\nXONG.")


if __name__ == "__main__":
    main()