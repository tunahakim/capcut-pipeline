"""repo_bytecheck.py - đối chiếu working copy với blob trên GitHub theo từng file, báo file thiếu cùng file lệch byte, và từ chối kết luận khi không đọc được GitHub.
Ba đường chạy: mặc định thì hỏi GitHub đúng hai lượt gọi API, một lượt lấy SHA của nhánh main rồi một lượt lấy trọn cây bằng Git Trees API GHIM THEO CHÍNH SHA ĐÓ nên không còn cửa cho phản hồi cũ đã cache; --git-only thì không gọi lượt API nào mà chỉ so git rev-parse HEAD với git rev-parse origin/main, dùng khi hết hạn ngạch hoặc không có mạng; --full thì in thêm mọi file đã khớp.
Ba hàng rào chống kết luận sai, thêm ngày 05/08/2026 sau khi bản cũ nuốt lỗi 403 rồi sinh một loạt dòng LECH giả trong khi repo hoàn toàn sạch và lừa được cả người dùng lẫn trợ lý: mọi lỗi HTTP hay lỗi mạng đều in KHONG DOC DUOC GITHUB kèm hạn ngạch còn lại rồi thoát bằng mã riêng chứ không liệt kê dòng LECH nào; khi HEAD của máy khác SHA của main thì cũng thoát bằng mã riêng và KHÔNG so byte, vì lúc đó là so hai commit khác nhau nên mọi dòng LECH đều vô nghĩa; và khi Git Trees API tự khai truncated thì coi như không đọc được, vì cây thiếu file sẽ biến thành dòng THIEU giả.
Luật so byte: coi là khớp khi số byte trên đĩa bằng số byte của blob, hoặc khi số byte trên đĩa trừ đi số ký tự CR bằng số byte của blob, vì git chuẩn hoá CRLF về LF ở tầng index.
Hạn ngạch API cho IP không đăng nhập là 60 lượt một giờ; bản cũ xin 20 lượt mỗi lần chạy, bản này xin 2.
Mã thoát: 0 sạch, 1 sai tham số hoặc không chạy được git, 2 có lệch byte hoặc thiếu file thật, 3 không đọc được GitHub, 4 HEAD khác main nên chưa so được byte.
[KIEM: du lieu that]"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = "tunahakim/capcut-pipeline"
REF = "main"
API = "https://api.github.com/repos/" + REPO
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MA_SACH = 0
MA_THAM_SO = 1
MA_LECH = 2
MA_MANG = 3
MA_KHAC_MAIN = 4


class LoiGitHub(Exception):
    """Mọi nguyên nhân làm ta không đọc được GitHub: lỗi HTTP, lỗi mạng, hết thời gian chờ, JSON hỏng, cây bị cắt."""


def api_get(url, stat):
    """Gọi một lượt API rồi trả về đối tượng JSON; mọi thất bại đều ném LoiGitHub chứ không trả về giá trị rỗng."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "repo-bytecheck",
        "Accept": "application/vnd.github+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            stat["req"] += 1
            stat["con_lai"] = resp.headers.get("X-RateLimit-Remaining", "?")
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        stat["req"] += 1
        if exc.headers is not None:
            stat["con_lai"] = exc.headers.get("X-RateLimit-Remaining", "?")
        raise LoiGitHub("HTTP %s tai %s" % (exc.code, url))
    except Exception as exc:
        raise LoiGitHub("%s: %s tai %s" % (type(exc).__name__, exc, url))


def git(*args):
    """Chạy một lệnh git trong thư mục repo và trả về ba giá trị: mã thoát, stdout đã cắt trắng, stderr đã cắt trắng."""
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(args),
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except Exception as exc:
        return 1, "", "%s: %s" % (type(exc).__name__, exc)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def in_loi_mang(exc, stat):
    """In khối chẩn đoán chung cho mọi ca không đọc được GitHub, kèm hạn ngạch còn lại và đường đi thay thế."""
    print("=== KHONG DOC DUOC GITHUB ===")
    print("ly do    : %s" % exc)
    print("han ngach: con %s (IP khong dang nhap: 60 luot/gio)" % stat["con_lai"])
    print("da goi   : %d luot trong lan chay nay" % stat["req"])
    print("KHONG ket luan gi ve byte -- moi dong LECH luc nay deu la gia")
    print("thay bang: python tools/repo_bytecheck.py --git-only")


def duong_git_only(fetch):
    """Đường so bằng git thuần, không gọi lượt API nào; dùng khi hết hạn ngạch hoặc không có mạng."""
    print("=== BYTECHECK --git-only: khong goi API nao ===")
    if fetch:
        rc, _, err = git("fetch", "origin", REF)
        print("git fetch origin %s: %s"
              % (REF, "OK" if rc == 0 else "LOI " + err[:200]))
        if rc != 0:
            print("KHONG DOC DUOC GITHUB -- git fetch that bai")
            return MA_MANG
    else:
        print("bo qua git fetch (--no-fetch): origin/%s co the da cu" % REF)
    rc1, head, _ = git("rev-parse", "HEAD")
    rc2, remote, _ = git("rev-parse", "origin/" + REF)
    if rc1 != 0 or rc2 != 0:
        print("KHONG CHAY DUOC GIT")
        return MA_THAM_SO
    print("HEAD local : %s | origin/%s: %s %s"
          % (head[:10], REF, remote[:10], "KHOP" if head == remote else "KHAC"))
    if head != remote:
        print("=== HEAD KHAC MAIN -- chua push hoac chua pull ===")
        return MA_KHAC_MAIN
    print("=== SACH theo git, chua so byte tung file ===")
    return MA_SACH


def main():
    ap = argparse.ArgumentParser(
        description="Doi chieu working copy voi blob GitHub, 2 luot goi API.")
    ap.add_argument("--full", action="store_true",
                    help="in ca danh sach file da khop")
    ap.add_argument("--git-only", action="store_true", dest="git_only",
                    help="khong goi API, chi so HEAD voi origin/main")
    ap.add_argument("--no-fetch", action="store_true", dest="no_fetch",
                    help="di kem --git-only: khong chay git fetch truoc khi so")
    a = ap.parse_args()

    if a.git_only:
        return duong_git_only(not a.no_fetch)

    stat = {"req": 0, "con_lai": "?"}
    rc, head, err = git("rev-parse", "HEAD")
    if rc != 0:
        print("KHONG CHAY DUOC GIT: %s" % err[:200])
        return MA_THAM_SO

    try:
        remote = api_get(API + "/commits/" + REF, stat)["sha"]
    except LoiGitHub as exc:
        in_loi_mang(exc, stat)
        return MA_MANG
    except (KeyError, TypeError) as exc:
        in_loi_mang(LoiGitHub("phan hoi thieu khoa sha: %s" % exc), stat)
        return MA_MANG

    print("=== BYTECHECK ===")
    print("HEAD local : %s | %s GitHub: %s %s"
          % (head[:10], REF, remote[:10],
             "KHOP" if head == remote else "KHAC"))
    if head != remote:
        print("=== HEAD KHAC MAIN -- chua push hoac chua pull, KHONG so byte ===")
        print("so byte luc nay la so hai commit khac nhau, moi dong LECH deu vo nghia")
        print("request=%d han ngach con: %s" % (stat["req"], stat["con_lai"]))
        return MA_KHAC_MAIN

    try:
        cay = api_get(API + "/git/trees/" + remote + "?recursive=1", stat)
    except LoiGitHub as exc:
        in_loi_mang(exc, stat)
        return MA_MANG
    if not isinstance(cay, dict) or "tree" not in cay:
        in_loi_mang(LoiGitHub("phan hoi Trees API khong co khoa tree"), stat)
        return MA_MANG
    if cay.get("truncated"):
        in_loi_mang(LoiGitHub("Trees API bao truncated, cay thieu file"), stat)
        return MA_MANG

    blobs = {}
    bo_qua = []
    for it in cay["tree"]:
        loai = it.get("type")
        if loai == "blob":
            blobs[it["path"]] = it.get("size", -1)
        elif loai != "tree":
            bo_qua.append("%s type=%s" % (it.get("path"), loai))

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
            khop.append("%s  %d%s" % (p, size, " CRLF" if cr else ""))
            if cr:
                crlf += 1
        else:
            lech.append("%s  disk=%d CR=%d blob=%d delta=%d"
                        % (p, len(data), cr, size, len(data) - cr - size))

    print("blob=%d khop=%d (CRLF %d) lech=%d thieu=%d request=%d han ngach con %s"
          % (len(blobs), len(khop), crlf, len(lech), len(thieu),
             stat["req"], stat["con_lai"]))
    for s in lech:
        print("LECH  " + s)
    for s in thieu:
        print("THIEU " + s)
    for s in bo_qua:
        print("BOQUA " + s)
    if a.full:
        for s in khop:
            print("ok    " + s)
    if lech or thieu:
        print("=== CO VAN DE ===")
        return MA_LECH
    print("=== SACH ===")
    return MA_SACH


if __name__ == "__main__":
    sys.exit(main())
