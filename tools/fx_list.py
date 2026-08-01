"""fx_list.py
Lọc catalogue scene-effect và filter theo bộ từ khoá phong cách phim cũ, bỏ mục VIP, và in thêm 25 scene effect đầu tiên để tham khảo.
Vào: không tham số, cần capcut-cli trong PATH. Ra: chỉ in console.
Nhánh filter ở đây chỉ để dò tên; catalogue --filters của namespace CapCut là dữ liệu rác, muốn ID dùng được phải qua tools/filt_enum.py, xem failures.md mục 2.3.
"""

import subprocess, json

def run(a):
    p = subprocess.run(a, shell=True, capture_output=True)
    t = p.stdout.decode("utf-8", errors="replace").strip()
    if not t:
        print("  (RONG)", p.stderr.decode("utf-8", errors="replace")[:200]); return []
    try: return json.loads(t)
    except Exception as e:
        print("  (LOI)", e); return []

def show(title, flag, kw=None, limit=None):
    print("\n" + "=" * 72); print(title); print("=" * 72)
    a = run("capcut enums " + flag)
    print("tong:", len(a))
    n = 0
    for x in a:
        s = x.get("slug") or ""
        if not s or x.get("is_vip"): continue
        name = (x.get("name") or "")
        if kw and not any(k in s.lower() or k in name.lower() for k in kw): continue
        n += 1
        if limit and n > limit: break
        print("  {0:34} {1}".format(s, name))
    print("-> in ra:", min(n, limit or n))

FILM = ["film", "old", "retro", "vintage", "grain", "vhs", "tv", "noise",
        "dust", "scratch", "projector", "crt", "8mm", "glitch", "light", "flare"]
show("SCENE EFFECTS - loc tu khoa phim cu", "--scene-effects", FILM)
show("FILTERS - loc tu khoa retro", "--filters", FILM)
show("SCENE EFFECTS - 25 cai dau (tham khao)", "--scene-effects", None, 25)