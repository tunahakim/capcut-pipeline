#!/usr/bin/env python3
"""
snap.py <project-dir> <ten-snapshot>
LUON doc tu file LONG (Timelines/<id>/) = nguon su that.
Ghi ra <LAB>/snapshots/<ten>.json (rut gon) + <ten>_full.json (nguyen ban)
[KIEM: chua]
"""
import json, os, pathlib, sys

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
OUT = LAB / "snapshots"


def truth_file(proj: pathlib.Path) -> pathlib.Path:
    pj = proj / "Timelines" / "project.json"
    if pj.exists():
        tid = json.loads(pj.read_text(encoding="utf-8")).get("main_timeline_id")
        cand = proj / "Timelines" / str(tid) / "draft_content.json"
        if cand.exists():
            return cand
        print("  CANH BAO: co project.json nhung khong thay draft long")
    else:
        print("  CANH BAO: khong thay Timelines/project.json")
    return proj / "draft_content.json"


def us(v):
    try:
        return round(int(v) / 1_000_000, 4)
    except Exception:
        return 0.0


def main():
    if len(sys.argv) < 3:
        sys.exit("Dung: python snap.py <project-dir> <ten-snapshot>")
    proj = pathlib.Path(sys.argv[1]); name = sys.argv[2]
    f = truth_file(proj)
    d = json.loads(f.read_text(encoding="utf-8"))

    print("Doc tu : %s" % f)
    print("Duration: %ss | fps=%s | canvas=%s" % (us(d.get('duration')), d.get('fps'),
                                                  d.get('canvas_config')))

    mats = {}
    for bucket, arr in (d.get("materials") or {}).items():
        if isinstance(arr, list):
            for m in arr:
                if isinstance(m, dict) and m.get("id"):
                    mats[m["id"]] = (bucket, m)

    print("\n-- MATERIALS COUNT --")
    for b, arr in sorted((d.get("materials") or {}).items()):
        if isinstance(arr, list) and arr:
            print("   %s: %d" % (b, len(arr)))

    snap = {"source": str(f), "duration": d.get("duration"), "tracks": []}

    for tr in d.get("tracks", []):
        ttype = tr.get("type")
        print("\n-- TRACK %s (id=%s flag=%s attr=%s) --"
              % (ttype, str(tr.get('id'))[:8], tr.get('flag'), tr.get('attribute')))
        tsnap = {"type": ttype, "id": tr.get("id"), "segments": []}
        for i, s in enumerate(tr.get("segments", []), 1):
            tt = s.get("target_timerange") or {}
            st = s.get("source_timerange") or {}
            clip = s.get("clip") or {}
            mb, mo = mats.get(s.get("material_id"), ("?", {}))
            label = (mo.get("material_name") or mo.get("name")
                     or str(mo.get("content") or "")[:40] or mb)
            refs = [mats.get(r, ("MISSING", {}))[0] for r in s.get("extra_material_refs", [])]
            kfs = [{
                "property_type": k.get("property_type"),
                "points": [{"t": us(p.get("time_offset")), "v": p.get("values"),
                            "curve": p.get("curveType"),
                            "lc": p.get("left_control"), "rc": p.get("right_control")}
                           for p in (k.get("keyframe_list") or [])]
            } for k in (s.get("common_keyframes") or [])]

            row = {
                "n": i, "id8": str(s.get("id"))[:8], "label": label,
                "start": tt.get("start"), "dur": tt.get("duration"),
                "src_start": st.get("start"), "src_dur": st.get("duration"),
                "scale": clip.get("scale"), "transform": clip.get("transform"),
                "rotation": clip.get("rotation"), "alpha": clip.get("alpha"),
                "uniform_scale": s.get("uniform_scale"),
                "check_flag": mo.get("check_flag"),
                "render_index": s.get("render_index"), "visible": s.get("visible"),
                "refs": refs, "keyframes": kfs,
            }
            tsnap["segments"].append(row)
            sc = (clip.get("scale") or {}).get("x")
            print("  %2d %s %9.3fs +%-8.3fs scale=%s flag=%s kf=%s refs=%s | %s"
                  % (i, row['id8'], us(tt.get('start')), us(tt.get('duration')), sc,
                     mo.get('check_flag'), [k['property_type'] for k in kfs],
                     sorted(set(refs)), label))
        snap["tracks"].append(tsnap)

    for bucket in ("transitions", "material_animations", "canvases",
                   "video_effects", "effects", "texts", "audio_fades"):
        arr = (d.get("materials") or {}).get(bucket) or []
        if arr:
            snap[bucket] = arr
            print("\n-- MATERIALS.%s (%d) --" % (bucket, len(arr)))
            print(json.dumps(arr, ensure_ascii=False, indent=1)[:3000])

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (name + ".json")).write_text(json.dumps(snap, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    (OUT / (name + "_full.json")).write_text(json.dumps(d, ensure_ascii=False, indent=1),
                                             encoding="utf-8")
    print("\nDa ghi: %s" % (OUT / (name + ".json")))
    print("Da ghi: %s" % (OUT / (name + "_full.json")))


if __name__ == "__main__":
    main()