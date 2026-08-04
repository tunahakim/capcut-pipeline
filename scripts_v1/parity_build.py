#!/usr/bin/env python3
"""
parity_build.py <project-dir> [src-dir]

Dung tron bo 8 shot bang capcut-cli, dung cho probe parity tren may moi.
Tu doc ID segment nen khong phai chep tay. Dung ngay khi co lenh loi.

Sau script nay:  python kb_apply.py <project>  ->  check_sync.py  ->  mo CapCut
[KIEM: du lieu that]
"""
import json, os, pathlib, subprocess, sys

LAB = pathlib.Path(os.environ.get("CAPCUT_LAB", r"D:\Test_tool"))

SHOTS = [
    ("Shot_001_IE3_Launch.png",             0.00,  19.74),
    ("Shot_002_CSS_Revolution.png",        19.74,  34.68),
    ("Shot_003_IE_Acclaimed.png",          34.68,  48.88),
    ("Shot_004_Browser_War_Shifts.png",    48.88,  72.72),
    ("Shot_005_IE3_Engineering_Team.png",  72.72,  91.96),
    ("Shot_006_Cost_Of_Success.png",       91.96, 106.70),
    ("Shot_007_Netscape_Communicator.png",106.70, 132.72),
    ("Shot_008_Netscape_Collapse.png",    132.72,   None),   # None = het audio
]
TRANS = ["dissolve", "black-fade", "blur", "gradient-wipe",
         "dissolve-ii", "dissolve", "black-fade"]      # 7 cai, KHONG dung cube


def sh(cmd, quiet=False):
    p = subprocess.run(cmd, shell=True, capture_output=True)
    out = p.stdout.decode("utf-8", errors="replace").strip()
    err = p.stderr.decode("utf-8", errors="replace").strip()
    if p.returncode != 0:
        print("LOI:", cmd)
        print(out[:400] or err[:400])
        sys.exit(1)
    if not quiet and out:
        print("   ", out[:120])
    return out


def n(x):
    return ("%.3f" % x).rstrip("0").rstrip(".")


def main():
    if len(sys.argv) < 2:
        sys.exit("Dung: python parity_build.py <project-dir> [src-dir]")
    proj = pathlib.Path(sys.argv[1])
    src = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else LAB / "Test_tool_v3"
    if not proj.is_dir():
        sys.exit("Khong thay project: %s" % proj)
    if not src.is_dir():
        sys.exit("Khong thay tai nguyen: %s" % src)

    audio = src / "audio.mp3"
    dur = float(sh('ffprobe -v error -show_entries format=duration -of csv=p=0 "%s"' % audio,
                   quiet=True))
    print("audio = %.6f giay" % dur)

    print("\n=== add-video / add-audio ===")
    for f, a, b in SHOTS:
        end = dur if b is None else b
        img = src / f
        if not img.exists():
            sys.exit("Thieu anh: %s" % img)
        sh('capcut add-video "%s" "%s" "%ss" "%ss" -q' % (proj, img, n(a), n(end - a)))
        print("  %-36s %8s -> %-8s" % (f, n(a), n(end)))
    sh('capcut add-audio "%s" "%s" "0s" -q' % (proj, audio))
    print("  audio.mp3 OK")

    segs = json.loads(sh('capcut segments "%s" --track video' % proj, quiet=True))
    if isinstance(segs, dict):
        segs = segs.get("segments", segs.get("data", []))
    ids = [s["id"] for s in segs]
    print("\n=== ID segment (%d) ===\n  %s" % (len(ids), " ".join(i[:8] for i in ids)))
    if len(ids) != 8:
        sys.exit("Mong doi 8 segment, thay %d" % len(ids))

    print("\n=== bg-blur (level 3) ===")
    for i in ids:
        sh('capcut bg-blur "%s" %s 3 -q' % (proj, i), quiet=True)
    print("  8/8 OK")

    print("\n=== transition (7, deu is_overlap=false) ===")
    for i, slug in zip(ids[:7], TRANS):
        sh('capcut transition "%s" %s %s -q' % (proj, i, slug), quiet=True)
        print("  sau %s  %s" % (i[:8], slug))

    print("\n=== image-anim combo (shot 2 va 7) ===")
    for k in (1, 6):
        sh('capcut image-anim "%s" %s --intro fade-in --outro fade-out -q' % (proj, ids[k]),
           quiet=True)
        print("  shot %d  fade-in/fade-out" % (k + 1))

    print("\n=== add-effect retro-film --full ===")
    sh('capcut add-effect "%s" retro-film --full --intensity 0.6 -q' % proj, quiet=True)
    print("  OK")

    print("\n=== lint ===")
    print(sh('capcut lint "%s" -H' % proj, quiet=True))
    print("\nXONG. Buoc tiep: python kb_apply.py \"%s\"" % proj)


if __name__ == "__main__":
    main()