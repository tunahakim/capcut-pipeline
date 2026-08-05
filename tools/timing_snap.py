"""timing_snap.py snap <project-dir> <out.json> | timing_snap.py diff <trước.json> <sau.json>
Chụp và so sánh timing của mọi track trong project, thay cho cặp scripts_v1/check_sync.py và scripts_v1/diff_timing.py.
Vào: project ở chế độ snap, hai file snapshot ở chế độ diff. Ra: file JSON gồm duration và danh sách start, duration của từng segment, hoặc bảng lệch tính bằng mili giây kèm lệch start lớn nhất.
Đọc bản LONG trước, chỉ quay về bản gốc khi bản LONG không có segment nào.
[KIEM: du lieu that]
"""

import json, pathlib, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MODE = sys.argv[1]

def load(proj):
    p = pathlib.Path(proj)
    tid = json.loads((p / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
    nested = p / "Timelines" / tid / "draft_content.json"
    src = nested if nested.exists() else (p / "draft_content.json")
    d = json.loads(src.read_text(encoding="utf-8"))
    if not any((t.get("segments") or []) for t in (d.get("tracks") or [])):
        d = json.loads((p / "draft_content.json").read_text(encoding="utf-8"))
        src = p / "draft_content.json"
    return d, str(src)

def snap(proj, out):
    d, src = load(proj)
    rec = {"source": src, "duration": d.get("duration"), "tracks": {}}
    for t in (d.get("tracks") or []):
        ty = t.get("type")
        segs = sorted((t.get("segments") or []),
                      key=lambda s: (s.get("target_timerange") or {}).get("start", 0))
        if not segs:
            continue
        rec["tracks"].setdefault(ty, [])
        for i, s in enumerate(segs, 1):
            tr = s.get("target_timerange") or {}
            rec["tracks"][ty].append({"i": i, "id": s.get("id"),
                                      "start": tr.get("start"), "dur": tr.get("duration")})
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out).write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("nguon    : %s" % src)
    print("duration : %s us = %.4f s" % (rec["duration"], (rec["duration"] or 0) / 1e6))
    for ty, arr in rec["tracks"].items():
        print("track %-6s: %d segment" % (ty, len(arr)))
    print("snapshot : %s" % out)

def diff(a, b):
    A = json.loads(pathlib.Path(a).read_text(encoding="utf-8"))
    B = json.loads(pathlib.Path(b).read_text(encoding="utf-8"))
    print("duration : %.4f -> %.4f s  (lech %+.1f ms)"
          % ((A["duration"] or 0) / 1e6, (B["duration"] or 0) / 1e6,
             ((B["duration"] or 0) - (A["duration"] or 0)) / 1000.0))
    for ty in sorted(set(A["tracks"]) | set(B["tracks"])):
        ta, tb = A["tracks"].get(ty, []), B["tracks"].get(ty, [])
        print("")
        print("track %s: %d -> %d segment" % (ty, len(ta), len(tb)))
        print("  %-4s %-14s %-14s %-11s %s" % ("i", "start truoc", "start sau", "lech ms", "dur lech ms"))
        mx = 0.0
        for x, y in zip(ta, tb):
            ds = ((y["start"] or 0) - (x["start"] or 0)) / 1000.0
            dd = ((y["dur"] or 0) - (x["dur"] or 0)) / 1000.0
            mx = max(mx, abs(ds))
            print("  %-4d %-14.4f %-14.4f %-11.1f %.1f"
                  % (x["i"], (x["start"] or 0) / 1e6, (y["start"] or 0) / 1e6, ds, dd))
        print("  lech start lon nhat: %.1f ms" % mx)

if MODE == "snap":
    snap(sys.argv[2], sys.argv[3])
elif MODE == "diff":
    diff(sys.argv[2], sys.argv[3])
else:
    sys.exit("Dung: timing_snap.py snap <proj> <out.json> | diff <a.json> <b.json>")