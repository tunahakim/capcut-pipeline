#!/usr/bin/env python3
# D:\Test_tool\snap.py  (v2)
"""
Chup ca BON file draft cua project CapCut 9.1.0.
Dung: python snap.py <project-dir> <ten-snapshot>
Ghi ra: D:\\Test_tool\\snapshots\\<ten>__<slot>.json  (ban day du, de diff sau)
"""
import json, sys, pathlib

OUT = pathlib.Path(__file__).resolve().parent / "snapshots"

def us(v):
    try:    return int(v) / 1_000_000
    except: return 0.0

def slots(proj):
    out = [("ROOT_dc", proj / "draft_content.json"),
           ("ROOT_t2", proj / "template-2.tmp")]
    pj = proj / "Timelines" / "project.json"
    if pj.exists():
        tid = json.loads(pj.read_text(encoding="utf-8")).get("main_timeline_id")
        if tid:
            n = proj / "Timelines" / str(tid)
            out += [("NEST_dc", n / "draft_content.json"),
                    ("NEST_t2", n / "template-2.tmp")]
            print(f"main_timeline_id = {tid}")
    else:
        print("CANH BAO: khong thay Timelines/project.json")
    return out

def report(tag, path, name):
    if not path.exists():
        print(f"\n########## {tag}: KHONG TON TAI ##########")
        return
    d = json.loads(path.read_text(encoding="utf-8"))
    print(f"\n########## {tag}  ({path.stat().st_size} bytes) ##########")
    print(f"id={d.get('id')}  duration={us(d.get('duration')):.3f}s  fps={d.get('fps')}")
    print(f"canvas={json.dumps(d.get('canvas_config'), ensure_ascii=False)}")

    mats = {}
    for b, arr in (d.get("materials") or {}).items():
        if isinstance(arr, list):
            for m in arr:
                if isinstance(m, dict) and m.get("id"):
                    mats[m["id"]] = (b, m)
    counts = {b: len(a) for b, a in (d.get("materials") or {}).items()
              if isinstance(a, list) and a}
    print("materials:", json.dumps(counts, ensure_ascii=False))

    for tr in d.get("tracks", []):
        segs = tr.get("segments", [])
        print(f"\n  TRACK {tr.get('type')} id={str(tr.get('id'))[:8]} "
              f"flag={tr.get('flag')} attr={tr.get('attribute')} segs={len(segs)}")
        for i, s in enumerate(segs, 1):
            tt = s.get("target_timerange") or {}
            st = s.get("source_timerange") or {}
            c  = s.get("clip") or {}
            mb, mo = mats.get(s.get("material_id"), ("?", {}))
            lbl = (mo.get("material_name") or mo.get("name")
                   or str(mo.get("content") or "")[:30] or mb)
            refs = sorted({mats.get(r, ("MISSING", {}))[0]
                           for r in s.get("extra_material_refs", [])})
            sc = (c.get("scale") or {}).get("x")
            kf = [(k.get("property_type"), len(k.get("keyframe_list") or []))
                  for k in (s.get("common_keyframes") or [])]
            print(f"   {i:>2} {str(s.get('id'))[:8]} "
                  f"{us(tt.get('start')):>8.3f}s +{us(tt.get('duration')):<8.3f}s "
                  f"src={us(st.get('start')):.3f}/{us(st.get('duration')):.3f} "
                  f"scale={sc} flag={mo.get('check_flag')} "
                  f"ri={s.get('render_index')} vis={s.get('visible')}")
            print(f"      us={json.dumps(s.get('uniform_scale'))} kf={kf} refs={refs} | {lbl}")

    for b in ("transitions", "material_animations", "canvases",
              "video_effects", "texts", "audio_fades", "hsl"):
        arr = (d.get("materials") or {}).get(b) or []
        if arr:
            print(f"\n  -- materials.{b} ({len(arr)}) --")
            print("  " + json.dumps(arr, ensure_ascii=False, indent=1)[:2500])

    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"{name}__{tag}.json"
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  >> luu: {f.name}")

def main():
    print('ARGV =', sys.argv)
    if len(sys.argv) < 3:
        sys.exit("Dung: python snap.py <project-dir> <ten-snapshot>")
    proj = pathlib.Path(sys.argv[1]); name = sys.argv[2]
    for tag, path in slots(proj):
        report(tag, path, name)
    print("\nXONG.")

if __name__ == "__main__":
    main()