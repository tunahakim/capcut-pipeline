#!/usr/bin/env python3
"""
tr_uncached.py <project-dir> build|check

Dong o con thieu: Python ghi transition + tai nguyen CHUA CO trong cache
-> CapCut co tu tai ve khong?

Sua loi cua tr_pytest.py: trong Cache/effect, ten md5 la THU MUC chu khong
phai FILE. Chon slug bang 2 dieu kien dong thoi: khong co thu muc
<resource_id>, va khong co thu muc <md5> o bat ky dau.
Doi chung duong = mot slug chua cache khac do CLI ghi.
"""
import copy, json, os, pathlib, re, shutil, subprocess, sys, uuid

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
SRC = LAB / "Test_tool_v3"
CACHE = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"
STATE = LAB / "perf" / "tr_uncached.json"
HEX32 = re.compile(r"^[0-9a-f]{32}$")
PH = "##_material_placeholder"

if len(sys.argv) < 3:
    sys.exit("Dung: python tr_uncached.py <project-dir> build|check")
PROJ = pathlib.Path(sys.argv[1])
MODE = sys.argv[2]
STATE.parent.mkdir(parents=True, exist_ok=True)


def snap_cache():
    tops, md5s = set(), set()
    if CACHE.is_dir():
        for t in CACHE.iterdir():
            if not t.is_dir():
                continue
            tops.add(t.name)
            for c in t.iterdir():
                if c.is_dir() and HEX32.match(c.name):
                    md5s.add(c.name)
    return tops, md5s


def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True)
    return (p.returncode,
            p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


def targets():
    tid = json.loads((PROJ / "Timelines" / "project.json")
                     .read_text(encoding="utf-8"))["main_timeline_id"]
    t = [PROJ / "draft_content.json", PROJ / "template-2.tmp",
         PROJ / "Timelines" / tid / "draft_content.json",
         PROJ / "Timelines" / tid / "template-2.tmp"]
    t = [x for x in t if x.exists()]
    if len(t) != 4:
        sys.exit("Chi thay %d/4 file dich" % len(t))
    return tid, t


if MODE == "build":
    tops, md5s = snap_cache()
    print("Cache truoc: %d thu muc goc | %d thu muc md5" % (len(tops), len(md5s)))

    rc, so, se = sh("capcut enums --transitions")
    pool = [x for x in json.loads(so)
            if x.get("slug") and x.get("md5") and not x.get("is_overlap")
            and not x.get("is_vip") and x["slug"] != "cube"
            and x["md5"] not in md5s
            and str(x["resource_id"]) not in tops]
    if len(pool) < 2:
        sys.exit("Chi con %d slug chua cache - khong du de thu" % len(pool))
    A, B = pool[0], pool[1]
    print("\nCHON (ca hai deu KHONG co thu muc rid VA KHONG co thu muc md5):")
    for tag, x in (("PYTHON", A), ("CLI   ", B)):
        print("  %s ghi -> %-22s rid=%-21s md5=%s  %s"
              % (tag, x["slug"], x["resource_id"], x["md5"], x["name"]))

    print("\n=== CLI: 3 anh + audio ===")
    imgs = sorted(SRC.glob("Shot_00[123]*.png"))
    for i, img in enumerate(imgs):
        rc, so, se = sh('capcut add-video "%s" "%s" "%ds" "6s" -q' % (PROJ, img, i * 6))
        if rc != 0:
            sys.exit("add-video loi: %s" % se[:200])
    sh('capcut add-audio "%s" "%s" "0s" "18s" -q' % (PROJ, SRC / "audio.mp3"))
    rc, so, se = sh('capcut segments "%s" --track video' % PROJ)
    data = json.loads(so)
    arr = data.get("segments", data) if isinstance(data, dict) else data
    ids = [x["id"] for x in arr]
    print("  %d segment: %s" % (len(ids), " ".join(i[:8] for i in ids)))

    print("\n=== DOI CHUNG DUONG: CLI ghi '%s' len shot 2 ===" % B["slug"])
    rc, so, se = sh('capcut transition "%s" %s %s -q' % (PROJ, ids[1], B["slug"]))
    if rc != 0:
        sys.exit("transition loi: %s" % se[:200])

    tid, tg = targets()
    d = json.loads(tg[0].read_text(encoding="utf-8"))
    trs = d["materials"]["transitions"]
    if len(trs) != 1:
        sys.exit("Mong doi 1 transition, thay %d" % len(trs))
    new = copy.deepcopy(trs[0])
    new["id"] = str(uuid.uuid4())
    new["name"] = A["name"]
    new["effect_id"] = A.get("effect_id", "")
    new["resource_id"] = A["resource_id"]
    if new.get("third_resource_id"):
        new["third_resource_id"] = A["resource_id"]
    if "path" in new:
        new["path"] = ""
    new["duration"] = int(A.get("default_duration") or 466666)
    trs.append(new)
    vt = [t for t in d["tracks"] if t.get("type") == "video"][0]
    vt["segments"][0].setdefault("extra_material_refs", []).append(new["id"])
    print("\n=== PYTHON dap '%s' len shot 1 ===" % A["slug"])
    print(json.dumps(new, ensure_ascii=False, indent=1))

    payload = json.dumps(d, ensure_ascii=False)
    json.loads(payload)
    for t in tg:
        shutil.copy2(t, str(t) + ".unbak")
        t.write_text(payload, encoding="utf-8")
    print("\n  da ghi 4 file")
    rc, so, se = sh('capcut lint "%s" -H' % PROJ)
    print("  lint: %s" % (so or se).strip()[:200])

    STATE.write_text(json.dumps({"py": A, "cli": B,
                                 "tops": sorted(tops), "md5s": sorted(md5s)},
                                ensure_ascii=False), encoding="utf-8")
    print("\nXONG BUILD.")

elif MODE == "check":
    st = json.loads(STATE.read_text(encoding="utf-8"))
    old_tops, old_md5 = set(st["tops"]), set(st["md5s"])
    tops, md5s = snap_cache()
    tid, tg = targets()
    d = json.loads((PROJ / "Timelines" / tid / "draft_content.json")
                   .read_text(encoding="utf-8"))
    who = {str(st[k]["resource_id"]): (n, st[k]) for k, n in
           (("py", "PYTHON ghi"), ("cli", "CLI ghi"))}

    print("=" * 72)
    print("CACHE: %d -> %d thu muc goc | %d -> %d thu muc md5"
          % (len(old_tops), len(tops), len(old_md5), len(md5s)))
    print("  thu muc goc MOI : %s" % sorted(tops - old_tops))
    print("  thu muc md5 MOI : %s" % sorted(md5s - old_md5))
    print("=" * 72)

    verdict = {}
    for m in d["materials"].get("transitions", []):
        p = m.get("path", "")
        rid = str(m.get("resource_id"))
        tag, meta = who.get(rid, ("?", {}))
        if not p:
            stt = "PATH RONG - KHONG RESOLVE"
        elif PH in p:
            stt = "PLACEHOLDER - KHONG RESOLVE"
        elif pathlib.Path(p).exists():
            stt = "OK - DA RESOLVE"
        else:
            stt = "PATH SAI"
        verdict[tag] = stt
        pmd5 = [s for s in p.replace("\\", "/").split("/") if HEX32.match(s)]
        print("\n  %-12s %-20s rid=%s" % (tag, m.get("name"), rid))
        print("    path = %s" % (p[:110] or "(rong)"))
        print("    %s" % stt)
        if pmd5:
            print("    md5 trong path = %s | md5 trong enums = %s | %s"
                  % (pmd5[-1], meta.get("md5"),
                     "khop" if pmd5[-1] == meta.get("md5") else "LECH"))

    a = verdict.get("PYTHON ghi", "?")
    b = verdict.get("CLI ghi", "?")
    print("\n" + "=" * 72)
    print("  PYTHON ghi, chua cache : %s" % a)
    print("  CLI    ghi, chua cache : %s   <- doi chung duong" % b)
    if a.startswith("OK") and b.startswith("OK"):
        print("  => CapCut TU TAI cho ca material do Python ghi.")
        print("     Duong thu ba mo hoan toan, khong can cache-first cho transition.")
    elif b.startswith("OK"):
        print("  => CapCut CHI tu tai cho material do CLI ghi.")
        print("     Transition do Python dap phai CACHE-FIRST giong filter.")
    else:
        print("  => Doi chung duong cung hong -> loi phuong phap hoac mat mang.")
else:
    sys.exit("mode phai la build hoac check")