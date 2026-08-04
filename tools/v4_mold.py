#!/usr/bin/env python3
r"""
v4_mold.py --project <project-dir> [--out <mold.json>] [--pick <ten|rid>]
           [--write] [--dump] [--capcut-version X]

Boc khuon material "filter" do CHINH CAPCUT ghi ra (phep thu oracle), luu thanh
file khuon de Python dap lai. MAC DINH CHI DIFF, khong ghi de; muon ghi de phai
them --write.

Khuon co bon khoi: _meta, track, segment, material. Khi diff, _meta bi bo qua
hoan toan, phan con lai chia lam ba nhom:
  BAT BUOC     lech la bao do va ma thoat 2. Mot key co ben nay thieu ben kia
               LUON tinh la BAT BUOC, ke ca key dinh danh, vi do la troi schema.
  MAY/PROJECT  material.path va segment.target_timerange.duration.
  DINH DANH    id, material_id, effect_id, resource_id, third_resource_id,
               name, category_id, category_name, request_id, md5.

List duoc coi la mot la, so nguyen khoi chu khong di vao trong.

Ma thoat: 0 sach hoac da ghi, 1 khong chay duoc, 2 co lech nhom BAT BUOC.
Luu y argparse cung tra 2 khi thieu tham so bat buoc -- trung so, khac nghia.
[KIEM: chua]
"""
import argparse, datetime, json, pathlib, platform, sys

TOOL_VERSION = "2"
REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "molds" / "capcut-9.1.0" / "filter.json"
SECTIONS = ("track", "segment", "material")

ALLOW_MACHINE = set([
    "material.path",
    "segment.target_timerange.duration",
])
ALLOW_IDENT = set([
    "track.id",
    "segment.id",
    "segment.material_id",
    "material.id",
    "material.effect_id",
    "material.resource_id",
    "material.third_resource_id",
    "material.name",
    "material.category_id",
    "material.category_name",
    "material.request_id",
    "material.md5",
])


def die(msg):
    print("LOI: " + msg)
    sys.exit(1)


def load_draft(proj):
    tlp = proj / "Timelines" / "project.json"
    if not tlp.is_file():
        die("khong thay " + str(tlp) + " -- project khong co thu muc Timelines")
    try:
        tid = json.loads(tlp.read_text(encoding="utf-8"))["main_timeline_id"]
    except Exception as e:
        die("doc project.json that bai: " + repr(e))
    dcp = proj / "Timelines" / tid / "draft_content.json"
    if not dcp.is_file():
        die("khong thay " + str(dcp))
    try:
        return json.loads(dcp.read_text(encoding="utf-8")), dcp
    except Exception as e:
        die("doc draft_content.json that bai: " + repr(e))


def find_filters(d):
    mats = {}
    for bk, arr in (d.get("materials") or {}).items():
        if isinstance(arr, list):
            for m in arr:
                if isinstance(m, dict) and m.get("id"):
                    mats[m["id"]] = (bk, m)
    found = []
    for t in d.get("tracks", []):
        for s in (t.get("segments") or []):
            bk, mo = mats.get(s.get("material_id"), ("?", {}))
            if mo.get("type") == "filter":
                found.append({"track": t, "segment": s, "material": mo, "bucket": bk})
    return found


def flat(o, pre, out):
    if isinstance(o, dict):
        for k in sorted(o.keys()):
            flat(o[k], (pre + "." + k) if pre else k, out)
    else:
        out[pre] = o


def flatten_mold(mold):
    out = {}
    for sec in SECTIONS:
        flat(mold.get(sec, {}), sec, out)
    return out


def classify(p):
    if p in ALLOW_MACHINE:
        return "MAY"
    if p in ALLOW_IDENT:
        return "ID"
    return "REQ"


def short(v):
    s = json.dumps(v, ensure_ascii=False)
    if len(s) > 60:
        s = s[:57] + "..."
    return s


def do_diff(new_mold, old_mold):
    na = flatten_mold(new_mold)
    oa = flatten_mold(old_mold)
    rows = []
    for k in sorted(set(na) | set(oa)):
        if k not in oa:
            rows.append(("REQ", k, "<<THIEU BEN KHUON>>", short(na[k])))
        elif k not in na:
            rows.append(("REQ", k, short(oa[k]), "<<THIEU BEN CHUP>>"))
        elif na[k] != oa[k]:
            rows.append((classify(k), k, short(oa[k]), short(na[k])))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--pick", default="")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--capcut-version", dest="capcut_version", default="9.1.0.3879")
    a = ap.parse_args()

    proj = pathlib.Path(a.project)
    if not proj.is_dir():
        die("khong thay thu muc project: " + str(proj))
    out = pathlib.Path(a.out)

    d, dcp = load_draft(proj)
    print("project : " + proj.name)
    print("draft   : " + str(dcp))
    print("khuon   : " + str(out))
    print("che do  : " + ("GHI (--write)" if a.write else "CHI DIFF"))
    print("")

    if a.dump:
        print("=" * 74)
        print("TAT CA TRACK - moi truong tru segments")
        print("=" * 74)
        for t in d.get("tracks", []):
            meta = {k: v for k, v in t.items() if k != "segments"}
            print("-- type=%s  %d segment"
                  % (t.get("type"), len(t.get("segments") or [])))
            print(json.dumps(meta, ensure_ascii=False, indent=1))
            print("")

    found = find_filters(d)
    print("=" * 74)
    print("MATERIAL type=filter TIM DUOC: %d" % len(found))
    print("=" * 74)
    for i, f in enumerate(found):
        tr = f["segment"].get("target_timerange") or {}
        print("[%d] bucket=%-13s track=%-7s name=%-14s rid=%-20s start=%d dur=%d"
              % (i, f["bucket"], f["track"].get("type"),
                 f["material"].get("name"), f["material"].get("resource_id"),
                 tr.get("start", -1), tr.get("duration", -1)))
    print("")

    gui = [f for f in found if f["bucket"] == "effects"]
    if not gui:
        die("khong co material filter nao trong bucket materials.effects")
    if a.pick:
        pk = a.pick.lower()
        gui = [f for f in gui
               if pk in str(f["material"].get("name", "")).lower()
               or pk == str(f["material"].get("resource_id"))]
        if len(gui) != 1:
            die("--pick %r khop %d muc, phai khop dung 1" % (a.pick, len(gui)))
    if len(gui) != 1:
        die("co %d filter GUI, phai chi dinh --pick <ten|rid>" % len(gui))

    f = gui[0]
    mold = {
        "_meta": {
            "schema": "capcut-mold/1",
            "tool": "v4_mold.py",
            "tool_version": TOOL_VERSION,
            "captured_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "host": platform.node(),
            "capcut_version": a.capcut_version,
            "project": proj.name,
            "source": "GUI",
            "material_type": "filter",
            "bucket": f["bucket"],
            "track_type": f["track"].get("type"),
            "filter_name": f["material"].get("name"),
            "resource_id": f["material"].get("resource_id"),
        },
        "track": {k: v for k, v in f["track"].items() if k != "segments"},
        "segment": f["segment"],
        "material": f["material"],
    }
    print("da boc khuon: name=%s rid=%s bucket=%s"
          % (mold["_meta"]["filter_name"], mold["_meta"]["resource_id"],
             f["bucket"]))
    print("")

    if a.write:
        out.parent.mkdir(parents=True, exist_ok=True)
        txt = json.dumps(mold, ensure_ascii=False, indent=1)
        with open(str(out), "w", encoding="utf-8", newline=chr(10)) as fh:
            fh.write(txt)
            fh.write(chr(10))
        print("DA GHI: %s (%d byte)" % (str(out), out.stat().st_size))
        sys.exit(0)

    if not out.is_file():
        die("khuon chua ton tai: " + str(out) + " -- chay lai voi --write de tao")
    try:
        old = json.loads(out.read_text(encoding="utf-8"))
    except Exception as e:
        die("doc khuon that bai: " + repr(e))
    if "_meta" not in old:
        print("(khuon tren dia khong co khoi _meta -- ban chup truoc 02/08/2026)")

    rows = do_diff(mold, old)
    nreq = len([r for r in rows if r[0] == "REQ"])
    nmay = len([r for r in rows if r[0] == "MAY"])
    nid = len([r for r in rows if r[0] == "ID"])
    print("=" * 74)
    print("DIFF  khuon-tren-dia  vs  ban-vua-chup")
    print("=" * 74)
    print("BAT BUOC KHOP : %d lech" % nreq)
    print("MAY/PROJECT   : %d lech" % nmay)
    print("DINH DANH     : %d lech" % nid)
    print("")
    if rows:
        for tag, k, ov, nv in rows:
            print("%s[%-3s] %s" % (">> " if tag == "REQ" else "   ", tag, k))
            print("        dia  = %s" % ov)
            print("        chup = %s" % nv)
    else:
        print("SACH - khong lech truong nao")
    print("")
    if nreq:
        print("KET LUAN: %d lech nhom BAT BUOC -> ma thoat 2" % nreq)
        sys.exit(2)
    print("KET LUAN: sach o nhom BAT BUOC -> ma thoat 0")
    sys.exit(0)


if __name__ == "__main__":
    main()
