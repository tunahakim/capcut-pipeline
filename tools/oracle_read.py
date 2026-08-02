"""oracle_read.py <project-dir> [--baseline v3|<file.json>]
Đọc bản LONG Timelines/<id>/draft_content.json và in toàn cảnh một project để làm phép thử oracle: bảng timing, check_flag, clip, uniform_scale, extra_material_refs phân loại theo bucket, common_keyframes, và ba bucket transitions, material_animations, canvases.
Vào: thư mục project. Ra: in console và bản dump đầy đủ ở <CAPCUT_LAB>/oracle_dump.json.
Cột delta chỉ hiện khi có --baseline: giá trị v3 lấy mốc cứng 8 shot của bộ test v3, hoặc trỏ tới file JSON chứa danh sách [[start, duration], ...] tính bằng giây. Không truyền --baseline thì bảng timing in trần, không có cột delta, vì mốc của project này không áp được cho project khác.
"""

import json, pathlib, sys
import os
import argparse

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\IT\capcut-lab\data"))

BASE_V3 = [(0,19.74),(19.74,14.94),(34.68,14.20),(48.88,23.84),
           (72.72,19.24),(91.96,14.74),(106.70,26.02),(132.72,36.005)]

ap = argparse.ArgumentParser(description="Doc nguoc draft_content.json va in toan canh mot project de lam phep thu oracle.")
ap.add_argument("project", help="thu muc project CapCut")
ap.add_argument("--baseline", default=None, metavar="v3|FILE.json",
                help="moc de tinh cot delta. 'v3' dung moc cung 8 shot cua bo test v3; hoac duong dan file JSON chua [[start, duration], ...] tinh bang giay. Bo qua thi khong in cot delta.")
args = ap.parse_args()

BASE = None
BASE_NAME = ""
if args.baseline == "v3":
    BASE = BASE_V3
    BASE_NAME = "bo test v3, 8 shot"
elif args.baseline:
    bp = pathlib.Path(args.baseline)
    if not bp.is_file():
        sys.exit("khong tim thay file moc: %s" % bp)
    BASE = [tuple(x) for x in json.loads(bp.read_text(encoding="utf-8"))]
    BASE_NAME = str(bp)

proj = pathlib.Path(args.project)
tid = json.loads((proj / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
f = proj / "Timelines" / tid / "draft_content.json"
d = json.loads(f.read_text(encoding="utf-8"))

def s(v):
    try: return int(v)/1e6
    except: return 0.0

mats = {}
for bucket, arr in (d.get("materials") or {}).items():
    if isinstance(arr, list):
        for m in arr:
            if isinstance(m, dict) and m.get("id"):
                mats[m["id"]] = (bucket, m)

print(f"duration = {s(d.get('duration')):.4f}s\n")
print("=" * 78)
if BASE is None:
    print("TIMING  (khong truyen --baseline nen khong co cot delta)")
else:
    print(f"TIMING vs BASELINE  (moc: {BASE_NAME}; delta tinh bang mili giay)")
print("=" * 78)
vtrack = next(t for t in d["tracks"] if t.get("type") == "video")
if BASE is not None and len(BASE) != len(vtrack["segments"]):
    print(f"CANH BAO: moc co {len(BASE)} shot nhung project co {len(vtrack['segments'])} shot. "
          f"Cot delta chi co nghia toi shot {min(len(BASE), len(vtrack['segments']))}.")
for i, seg in enumerate(vtrack["segments"]):
    tt = seg["target_timerange"]; st = seg.get("source_timerange") or {}
    if BASE is not None and i < len(BASE):
        b0, b1 = BASE[i]
        ds = (s(tt["start"]) - b0) * 1000
        dd = (s(tt["duration"]) - b1) * 1000
        warn = "  <<< LECH" if abs(ds) > 40 or abs(dd) > 40 else ""
        print(f"{i+1} {str(seg['id'])[:8]}  start={s(tt['start']):9.4f} (d{ds:+8.1f}ms)  "
              f"dur={s(tt['duration']):8.4f} (d{dd:+8.1f}ms)  src={s(st.get('start')):7.4f}/{s(st.get('duration')):8.4f}{warn}")
    else:
        print(f"{i+1} {str(seg['id'])[:8]}  start={s(tt['start']):9.4f}              "
              f"dur={s(tt['duration']):8.4f}              src={s(st.get('start')):7.4f}/{s(st.get('duration')):8.4f}")

print("\n" + "=" * 78)
print("CHI TIET TUNG SEGMENT")
print("=" * 78)
for i, seg in enumerate(vtrack["segments"]):
    mb, mo = mats.get(seg.get("material_id"), ("?", {}))
    print(f"\n--- SHOT {i+1}  id={str(seg['id'])[:8]}  {mo.get('material_name','?')}")
    print(f"  check_flag = {mo.get('check_flag')}")
    print(f"  clip          = {json.dumps(seg.get('clip'))}")
    print(f"  uniform_scale = {json.dumps(seg.get('uniform_scale'))}")
    for k in ("render_index", "visible", "volume", "reverse", "intensifies_audio"):
        if k in seg: print(f"  {k} = {seg[k]}")
    print("  extra_material_refs:")
    for r in seg.get("extra_material_refs", []):
        rb, ro = mats.get(r, ("MISSING", {}))
        extra = ""
        if rb == "canvases":
            extra = f"  type={ro.get('type')} blur={ro.get('blur')}"
        elif rb == "transitions":
            extra = f"  name={ro.get('name')} dur={s(ro.get('duration')):.4f}s overlap={ro.get('is_overlap')}"
        elif rb == "material_animations":
            extra = "  " + json.dumps(ro.get("animations"))
        print(f"    {rb:24} {str(r)[:8]}{extra}")
    kfs = seg.get("common_keyframes") or []
    if kfs:
        print(f"  common_keyframes ({len(kfs)}):")
        print(json.dumps(kfs, ensure_ascii=False, indent=2))
    else:
        print("  common_keyframes: []")

for bucket in ("transitions", "material_animations", "canvases"):
    arr = (d.get("materials") or {}).get(bucket) or []
    print("\n" + "=" * 78)
    print(f"MATERIALS.{bucket.upper()}  ({len(arr)})")
    print("=" * 78)
    if bucket == "canvases":
        for c in arr:
            print(f"  {str(c.get('id'))[:8]}  type={c.get('type'):14} blur={c.get('blur')}")
    else:
        print(json.dumps(arr, ensure_ascii=False, indent=2))

out = LAB / "oracle_dump.json"
out.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nDa luu ban day du: {out}")
