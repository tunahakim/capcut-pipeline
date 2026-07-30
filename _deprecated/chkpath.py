import json, pathlib, sys
proj = pathlib.Path(sys.argv[1])
for tag, f in (("GOC ", proj / "draft_content.json"),
               ("LONG", proj / "Timelines" / sys.argv[2] / "draft_content.json")):
    if not f.exists():
        print(f"{tag} KHONG TON TAI"); continue
    d = json.loads(f.read_text(encoding="utf-8"))
    mats = d.get("materials", {})
    nseg = sum(len(t.get("segments", [])) for t in d.get("tracks", []))
    print(f"{tag} duration={int(d.get('duration') or 0)/1e6:.3f}s  tracks={len(d.get('tracks',[]))}  segments={nseg}")
    for b in ("videos", "audios"):
        for m in mats.get(b, []):
            p = m.get("path", "")
            print(f"     [{b[:3]}] ton_tai={pathlib.Path(p).exists()!s:5} {p}")
    print()