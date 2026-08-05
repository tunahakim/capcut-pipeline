"""Doi chieu working copy voi blob GitHub theo tung thu muc; bao thieu file va lech byte. [KIEM: du lieu that]"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = "tunahakim/capcut-pipeline"
REF = "main"
API = "https://api.github.com/repos/" + REPO
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def api_get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "repo-bytecheck",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def walk(path, blobs, stat):
    items = api_get(API + "/contents/" + path + "?ref=" + REF)
    stat["req"] += 1
    if not isinstance(items, list):
        raise RuntimeError("phan hoi khong phai danh sach tai: " + path)
    for it in items:
        if it["type"] == "file":
            blobs[it["path"]] = it["size"]
        elif it["type"] == "dir":
            walk(it["path"], blobs, stat)
        else:
            stat["bo_qua"].append(it["path"] + " type=" + it["type"])


def local_head():
    try:
        r = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        return r.stdout.strip() if r.returncode == 0 else "?"
    except Exception:
        return "?"


def main():
    ap = argparse.ArgumentParser(description="Compare working copy with GitHub blobs.")
    ap.add_argument("--full", action="store_true", help="list every matching file too")
    args = ap.parse_args()

    blobs = {}
    stat = {"req": 0, "bo_qua": []}
    try:
        walk("", blobs, stat)
        remote = api_get(API + "/commits/" + REF)["sha"]
        stat["req"] += 1
    except Exception as e:
        print("LOI goi API: " + str(e))
        return 1

    khop = []
    crlf = 0
    lech = []
    thieu = []
    for p in sorted(blobs):
        size = blobs[p]
        disk = os.path.join(ROOT, p.replace("/", os.sep))
        if not os.path.isfile(disk):
            thieu.append(p)
            continue
        with open(disk, "rb") as f:
            data = f.read()
        cr = data.count(13)
        if len(data) == size or (len(data) - cr) == size:
            khop.append(p + "  " + str(size) + (" CRLF" if cr else ""))
            if cr:
                crlf += 1
        else:
            lech.append(p + "  disk=" + str(len(data)) + " CR=" + str(cr)
                        + " blob=" + str(size)
                        + " delta=" + str(len(data) - cr - size))

    head = local_head()
    print("=== BYTECHECK ===")
    print("HEAD local : " + head[:10] + " | main GitHub: " + remote[:10]
          + (" KHOP" if head.startswith(remote[:10]) else " KHAC -- can pull hoac push"))
    print("blob=" + str(len(blobs)) + " khop=" + str(len(khop))
          + " (CRLF " + str(crlf) + ") lech=" + str(len(lech))
          + " thieu=" + str(len(thieu)) + " request=" + str(stat["req"]))
    for s in lech:
        print("LECH  " + s)
    for s in thieu:
        print("THIEU " + s)
    for s in stat["bo_qua"]:
        print("BOQUA " + s)
    if args.full:
        for s in khop:
            print("ok    " + s)
    print("=== SACH ===" if not lech and not thieu else "=== CO VAN DE ===")
    return 0 if not lech and not thieu else 2


if __name__ == "__main__":
    sys.exit(main())