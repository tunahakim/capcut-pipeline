#!/usr/bin/env python3
"""
tr_pytest.py <project-dir> build|check

Kiem chung: Python co the tu ghi material transition (path rong) va canvas_blur
khong, hay bat buoc phai qua capcut-cli.

BO CUC PHEP THU (theo XIII.2 - luon co doi chung duong):
  shot 1  transition do PYTHON ghi, path rong   <- doi tuong nghi ngo
  shot 2  transition do CLI    ghi, path rong   <- DOI CHUNG DUONG
  shot 3  canvas_blur do PYTHON ghi + check_flag|=4096 + scale 0.8

Chon transition co md5 CHUA nam trong cache, de that su kiem tra co che tai ve.
Khuon material lay tu chinh material ma CLI vua ghi -> khong doan mo ta nao.

  build : dung project (chay CLI truoc, Python sau, propagate 4 file)
  check : doc nguoc sau khi CapCut da mo va dong
"""
import copy, json, os, pathlib, re, shutil, subprocess, sys, uuid

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))
SRC = LAB / "Test_tool_v3"
CACHE = pathlib.Path.home() / "AppData/Local/CapCut/User Data/Cache/effect"
PICK = LAB / "perf" / "tr_pick.json"
PH = "##_material_placeholder"
CANVAS_BIT = 4096

if len(sys.argv) < 3:
    sys.exit("Dung: python tr_pytest.py <project-dir> build|check")
PROJ = pathlib.Path(sys.argv[1])
MODE = sys.argv[2]
PICK.parent.mkdir(parents=True, exist_ok=True)


def cached_md5():
    s = set()
    if CACHE.is_dir():
        for p in CACHE.rglob("*"):
            if p.is_file() and re.fullmatch(r"[0-9a-f]{32}", p.name):
                s.add(p.name)
    return s


def targets():
    pj = PROJ / "Timelines" / "project.json"
    if not pj.exists():
        sys.exit("Khong thay Timelines/project.json")
    tid = json.loads(pj.read_text(encoding="utf-8"))["main_timeline_id"]
    t = [PROJ / "draft_content.json", PROJ / "template-2.tmp",
         PROJ / "Timelines" / tid / "draft_content.json",
         PROJ / "Timelines" / tid / "template-2.tmp"]
    t = [x for x in t if x.exists()]
    if len(t) != 4:
        sys.exit("Chi thay %d/4 file dich" % len(t))
    return tid, t


def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def vtrack(d):
    v = [t for t in d["tracks"] if t.get("type") == "video"]
    if len(v) != 1:
        sys.exit("Co %d track video, mong doi 1" % len(v))
    return v[0]


# ==================== BUILD ====================
if MODE == "build":
    have = cached_md5()
    print("Cache hien co %d file ten md5" % len(have))

    rc, so, se = sh("capcut enums --transitions")
    if rc != 0 or not so.strip():
        sys.exit("Khong doc duoc enums: %s" % se[:200])
    pool = [x for x in json.loads(so)
            if x.get("slug") and x.get("md5") and not x.get("is_overlap")
            and not x.get("is_vip") and x.get("slug") != "cube"
            and x["md5"] not in have]
    if len(pool) < 2:
        sys.exit("Khong du transition CHUA cache de thu (con %d)" % len(pool))
    A, B = pool[0], pool[1]
    print("\nCHON (deu chua co trong cache):")
    print("  PYTHON ghi -> slug=%-20s rid=%-21s md5=%s  %s"
          % (A["slug"], A["resource_id"], A["md5"], A.get("name")))
    print("  CLI    ghi -> slug=%-20s rid=%-21s md5=%s  %s"
          % (B["slug"], B["resource_id"], B["md5"], B.get("name")))
    PICK.write_text(json.dumps({"py": A, "cli": B}, ensure_ascii=False, indent=1),
                    encoding="utf-8")

    # ---- 3 shot bang CLI ----
    print("\n=== CLI: add-video x3 + add-audio ===")
    imgs = sorted(SRC.glob("Shot_00[123]*.png"))
    if len(imgs) != 3:
        sys.exit("Can dung 3 anh Shot_001..003 trong %s" % SRC)
    for i, img in enumerate(imgs):
        rc, so, se = sh('capcut add-video "%s" "%s" "%ds" "6s" -q' % (PROJ, img, i * 6))
        print("  add-video %d rc=%d %s" % (i + 1, rc, se.strip()[:120]))
        if rc != 0:
            sys.exit("dung lai")
    rc, so, se = sh('capcut add-audio "%s" "%s" "0s" "18s" -q' % (PROJ, SRC / "audio.mp3"))
    print("  add-audio rc=%d" % rc)

    rc, so, se = sh('capcut segments "%s" --track video' % PROJ)
    data = json.loads(so)
    arr = data.get("segments", data) if isinstance(data, dict) else data
    ids = [x.get("id") if isinstance(x, dict) else str(x) for x in arr]
    print("  ID segment:", ids)
    if len(ids) != 3:
        sys.exit("Doc duoc %d ID, mong doi 3" % len(ids))

    # ---- DOI CHUNG DUONG: CLI ghi transition len shot 2 ----
    print("\n=== CLI: transition '%s' len shot 2 ===" % B["slug"])
    rc, so, se = sh('capcut transition "%s" %s %s' % (PROJ, ids[1], B["slug"]))
    print("  rc=%d %s" % (rc, (so or se).strip()[:200]))
    if rc != 0:
        sys.exit("dung lai")

    # ---- PYTHON: moi thu con lai ----
    tid, tg = targets()
    d = json.loads(tg[0].read_text(encoding="utf-8"))
    mats = d.setdefault("materials", {})
    trs = mats.setdefault("transitions", [])
    if len(trs) != 1:
        sys.exit("Mong doi dung 1 transition do CLI ghi, thay %d" % len(trs))
    mold = trs[0]
    print("\n=== KHUON do CLI ghi ===")
    print(json.dumps(mold, ensure_ascii=False, indent=1))

    # dap transition moi tu khuon, chi doi 5 truong dinh danh
    new = copy.deepcopy(mold)
    new["id"] = str(uuid.uuid4())
    new["name"] = A.get("name") or A["slug"]
    new["effect_id"] = A.get("effect_id", "")
    new["resource_id"] = A["resource_id"]
    if "third_resource_id" in new and new["third_resource_id"]:
        new["third_resource_id"] = A["resource_id"]
    if "path" in new:
        new["path"] = ""
    if A.get("default_duration"):
        new["duration"] = int(A["default_duration"])
    trs.append(new)
    print("\n=== PYTHON dap transition ===")
    print(json.dumps(new, ensure_ascii=False, indent=1))

    vt = vtrack(d)
    segs = vt["segments"]
    segs[0].setdefault("extra_material_refs", []).append(new["id"])
    print("  gan vao shot 1 (%s)" % str(segs[0]["id"])[:8])

    # canvas_blur do Python dap, mo phong hanh vi cua bg-blur
    cvs = mats.setdefault("canvases", [])
    old_ids = {c["id"] for c in cvs}
    ref_old = [r for r in segs[2].get("extra_material_refs", []) if r in old_ids]
    if not ref_old:
        sys.exit("Shot 3 khong tham chieu canvas nao")
    proto = next(c for c in cvs if c["id"] == ref_old[0])
    blur = copy.deepcopy(proto)
    blur["id"] = str(uuid.uuid4())
    blur["type"] = "canvas_blur"
    blur["blur"] = 0.75
    if "color" in blur:
        blur["color"] = ""
    cvs.append(blur)
    segs[2]["extra_material_refs"] = [r for r in segs[2]["extra_material_refs"]
                                      if r != ref_old[0]] + [blur["id"]]
    vids = {m["id"]: m for m in mats.get("videos", [])}
    mv = vids.get(segs[2].get("material_id"))
    old_flag = int(mv.get("check_flag", 0))
    mv["check_flag"] = old_flag | CANVAS_BIT
    segs[2].setdefault("clip", {})["scale"] = {"x": 0.8, "y": 0.8}
    print("\n=== PYTHON dap canvas_blur len shot 3 ===")
    print("  canvas moi %s type=%s blur=%s" % (blur["id"][:8], blur["type"], blur["blur"]))
    print("  check_flag %d -> %d | scale 0.8" % (old_flag, mv["check_flag"]))

    payload = json.dumps(d, ensure_ascii=False)
    json.loads(payload)
    print()
    for t in tg:
        shutil.copy2(t, str(t) + ".trbak")
        t.write_text(payload, encoding="utf-8")
        print("  ghi:", t.relative_to(PROJ))

    rc, so, se = sh('capcut lint "%s" -H' % PROJ)
    print("\nlint rc=%d\n%s" % (rc, (so or se).strip()[:600]))
    print("\nXONG BUILD. Bay gio:")
    print("  1. Mo CapCut, mo project 'trpath'")
    print("  2. Nhin ranh gioi 1-2 va 2-3: ca hai phai co bieu tuong transition")
    print("  3. Bam shot 3, panel Video > Basic: checkbox Canvas phai duoc TICK,")
    print("     kieu Blur, va anh thu nho co vien mo")
    print("  4. Dong bang nut X, doi 10 giay")
    print("  5. Chay:  python tr_pytest.py <proj> check")

# ==================== CHECK ====================
elif MODE == "check":
    have = cached_md5()
    pick = json.loads(PICK.read_text(encoding="utf-8")) if PICK.exists() else {}
    tid, tg = targets()
    d = json.loads((PROJ / "Timelines" / tid / "draft_content.json").read_text(encoding="utf-8"))
    mats = d.get("materials", {})
    segs = vtrack(d)["segments"]

    who = {}
    for k, tag in (("py", "PYTHON ghi"), ("cli", "CLI ghi")):
        if k in pick:
            who[str(pick[k]["resource_id"])] = (tag, pick[k]["md5"])

    print("=" * 74)
    print("KET QUA: TRANSITION")
    print("=" * 74)
    seg_of = {}
    for i, s in enumerate(segs, 1):
        for r in s.get("extra_material_refs", []):
            seg_of[r] = i
    verdict = {}
    for m in mats.get("transitions", []):
        p = m.get("path", "")
        if not p:
            st = "PATH RONG - CHUA RESOLVE"
        elif PH in p:
            st = "PLACEHOLDER - CHUA RESOLVE"
        elif pathlib.Path(p).exists():
            st = "OK - CAPCUT DA RESOLVE"
        else:
            st = "PATH SAI, FILE KHONG CO"
        rid = str(m.get("resource_id"))
        tag, md5 = who.get(rid, ("?", None))
        incache = (md5 in have) if md5 else None
        verdict[tag] = st
        print("\n  sau shot %s | %-12s | %s" % (seg_of.get(m["id"], "?"), tag, m.get("name")))
        print("    rid=%s  dur=%s  overlap=%s" % (rid, m.get("duration"), m.get("is_overlap")))
        print("    path=%s" % (p[:100] if p else "(rong)"))
        print("    TRANG THAI: %s" % st)
        if md5:
            print("    md5 %s co trong cache: %s" % (md5, incache))

    print("\n" + "=" * 74)
    print("KET LUAN TRANSITION")
    print("=" * 74)
    a = verdict.get("PYTHON ghi", "khong thay")
    b = verdict.get("CLI ghi", "khong thay")
    print("  PYTHON ghi : %s" % a)
    print("  CLI    ghi : %s   <- doi chung duong" % b)
    if b.startswith("OK") and a.startswith("OK"):
        print("  => DUONG THU BA MO. Python dap duoc transition, bo 299 lenh CLI.")
    elif b.startswith("OK") and not a.startswith("OK"):
        print("  => CapCut PHAN BIET nguon goc. Phai giu `capcut transition`.")
    else:
        print("  => Doi chung duong CUNG HONG -> loi o phuong phap hoac o mang,")
        print("     khong ket luan gi ve Python. Kiem tra mang roi lam lai.")

    print("\n" + "=" * 74)
    print("KET QUA: CANVAS BLUR do Python dap (shot 3)")
    print("=" * 74)
    cv = {c["id"]: c for c in mats.get("canvases", [])}
    vids = {m["id"]: m for m in mats.get("videos", [])}
    for i, s in enumerate(segs, 1):
        refs = [cv[r] for r in s.get("extra_material_refs", []) if r in cv]
        mv = vids.get(s.get("material_id"), {})
        sc = (s.get("clip") or {}).get("scale", {}).get("x")
        print("  shot %d  check_flag=%-6s scale=%-6s canvas=%s"
              % (i, mv.get("check_flag"), sc,
                 [(c.get("type"), c.get("blur")) for c in refs]))
    print("\n  Mong doi: shot 3 check_flag co bit 4096 (vd 4103), canvas_blur 0.75,")
    print("  va trong GUI checkbox Canvas DA TICK. Shot 1-2 giu check_flag=7.")

    print("\n=== SO MUC CACHE HIEN TAI: %d thu muc goc | %d file md5 ==="
          % (len([x for x in CACHE.iterdir() if x.is_dir()]), len(have)))
else:
    sys.exit("mode phai la build hoac check")