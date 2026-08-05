#!/usr/bin/env python3
"""
bench_build.py <project-dir> <shots.csv> <assets-dir>
Khau CLI cua project benchmark. CHAY TRUOC bench_kb.py.
Sau script nay TUYET DOI khong chay them lenh ghi nao cua CLI.
[KIEM: chua]
"""
import csv, json, os, pathlib, subprocess, sys, time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROJ = sys.argv[1]
CSVF = pathlib.Path(sys.argv[2])
ASSETS = pathlib.Path(sys.argv[3])
EFFECTS = ["retro-film"]

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\IT\capcut-lab\data"))
PERF = LAB / "perf"
PERF.mkdir(parents=True, exist_ok=True)
T = {}


def sh(cmd):
    # enc: tu decode
    p = subprocess.run(cmd, shell=True, capture_output=True)
    if p.returncode != 0:
        print("\nLOI:", cmd)
        print((p.stdout + b"\n" + p.stderr).decode("utf-8", "replace")[:500])
        sys.exit(1)
    return p.stdout.decode("utf-8", "replace").strip()


def load_doc():
    p = pathlib.Path(PROJ)
    d = json.loads((p / "draft_content.json").read_text(encoding="utf-8"))
    if any((t.get("segments") or []) for t in (d.get("tracks") or [])):
        return d
    tid = json.loads((p / "Timelines" / "project.json").read_text(encoding="utf-8"))["main_timeline_id"]
    return json.loads((p / "Timelines" / tid / "draft_content.json").read_text(encoding="utf-8"))


def video_ids():
    for t in load_doc().get("tracks", []):
        if t.get("type") == "video":
            segs = sorted(t.get("segments") or [], key=lambda s: s["target_timerange"]["start"])
            return [s["id"] for s in segs]
    return []


rows = list(csv.DictReader(CSVF.open(encoding="utf-8")))
n = len(rows)
missing = [r["image"] for r in rows if not (ASSETS / r["image"]).exists()]
if missing:
    sys.exit("Thieu %d anh, vi du: %s" % (len(missing), missing[:3]))
print("bench_build: %d shot | %s" % (n, PROJ))

t0 = time.time()
print("\n=== 1/5 add-video (%d lenh) ===" % n)
a = time.perf_counter()
for i, r in enumerate(rows):
    sh('capcut add-video "%s" "%s" "%ss" "%ss" -q' % (PROJ, ASSETS / r["image"], r["start_s"], r["dur_s"]))
    if (i + 1) % 25 == 0:
        print("  %4d/%d  %5.1f phut" % (i + 1, n, (time.time() - t0) / 60))
T["add_video"] = time.perf_counter() - a

ids = video_ids()
print("\nID segment doc duoc: %d (can %d)" % (len(ids), n))
if len(ids) != n:
    sys.exit("So segment khong khop, dung lai")

blur = [(ids[i], r["blur"]) for i, r in enumerate(rows) if int(r["blur"]) > 0]
print("\n=== 2/5 bg-blur (%d lenh) ===" % len(blur))
a = time.perf_counter()
for sid, lv in blur:
    sh('capcut bg-blur "%s" %s %s -q' % (PROJ, sid, lv))
T["bg_blur"] = time.perf_counter() - a

tr = [(ids[i], r["transition"]) for i, r in enumerate(rows) if r["transition"]]
print("=== 3/5 transition (%d lenh) ===" % len(tr))
a = time.perf_counter()
for sid, slug in tr:
    sh('capcut transition "%s" %s %s -q' % (PROJ, sid, slug))
T["transition"] = time.perf_counter() - a

an = [(ids[i], r["intro"], r["outro"]) for i, r in enumerate(rows) if r["intro"] or r["outro"]]
print("=== 4/5 image-anim (%d lenh) ===" % len(an))
a = time.perf_counter()
for sid, ia, oa in an:
    f = ""
    if ia:
        f += " --intro %s" % ia
    if oa:
        f += " --outro %s" % oa
    sh('capcut image-anim "%s" %s%s -q' % (PROJ, sid, f))
T["image_anim"] = time.perf_counter() - a

print("=== 5/5 add-effect --full (%d lenh) ===" % len(EFFECTS))
a = time.perf_counter()
for e in EFFECTS:
    sh('capcut add-effect "%s" %s --full --intensity 0.6 -q' % (PROJ, e))
T["add_effect"] = time.perf_counter() - a

print("\n=== lint ===")
print(sh('capcut lint "%s" -H' % PROJ))

total = time.time() - t0
ncmd = n + len(blur) + len(tr) + len(an) + len(EFFECTS)
dc = pathlib.Path(PROJ) / "draft_content.json"
rep = {"n_shot": n, "n_cmd": ncmd, "total_s": total,
       "per_cmd_s": total / ncmd, "phases": T,
       "json_mb": dc.stat().st_size / 1048576.0}
out = PERF / ("bench_build_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
print("\nTong %d lenh trong %.1f phut, trung binh %.3f giay/lenh" % (ncmd, total / 60, total / ncmd))
print("draft_content.json: %.2f MB" % rep["json_mb"])
print("Da ghi:", out)
print("\nBUOC TIEP: python tools/bench_kb.py \"%s\" \"%s\"" % (PROJ, CSVF))