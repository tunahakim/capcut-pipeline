#!/usr/bin/env python3
"""shotlist.py - doc va kiem bang shotlist.tsv nam cot do nguoi viet, bat moc ve luoi 100 ms, gom loi roi in mot luot.
Vao: van ban TSV co dong tieu de, cot bat buoc idx start image, cot tuy chon transition note, ba cot de danh motion blur fx chi sinh CANH BAO.
Ra: danh sach Shot kem ms da bat luoi va do dai suy ra tu hai moc lien nhau; LOI thi nem ShotlistError con CANH BAO thi tra ve de goi in.
Hai muc: LOI la thu pha timing nen dung ngay va khong dung ket qua, CANH BAO la thu bo qua duoc va chay tiep.
Ma thoat khi chay truc tiep: 0 hop le, 2 co LOI.
[KIEM: bo test]
"""

import re
import sys
from pathlib import Path

REQUIRED = ("idx", "start", "image")
OPTIONAL = ("transition", "note")
RESERVED = ("motion", "blur", "fx")
EXIT_OK = 0
EXIT_BAD = 2

RE_HMS = re.compile(r"^(\d+):([0-5]?\d):([0-5]?\d)([.,](\d{1,3}))?$")
RE_MS = re.compile(r"^(\d+):([0-5]?\d)([.,](\d{1,3}))?$")
RE_SEC = re.compile(r"^(\d+)(\.(\d{1,3}))?$")


class ShotlistError(Exception):
    def __init__(self, errors):
        self.errors = list(errors)
        Exception.__init__(self, "shotlist khong hop le: %d loi" % len(self.errors))


class Shot:
    __slots__ = ("idx", "start_ms", "dur_ms", "image", "transition", "note", "row")

    def __init__(self, idx, start_ms, image, transition, note, row):
        self.idx = idx
        self.start_ms = start_ms
        self.dur_ms = None
        self.image = image
        self.transition = transition
        self.note = note
        self.row = row

    def __repr__(self):
        return "Shot(%d, %d ms, %r)" % (self.idx, self.start_ms, self.image)


def _frac_ms(text):
    if not text:
        return 0
    return int((text + "000")[:3])


def parse_start(text):
    """Doi mot o start thanh mili giay. Nhan hh:mm:ss,mmm | hh:mm:ss.mmm | mm:ss.mmm | giay tran dau cham."""
    s = str(text).strip()
    if not s:
        raise ValueError("o rong")
    m = RE_HMS.match(s)
    if m:
        return (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))) * 1000 + _frac_ms(m.group(5))
    m = RE_MS.match(s)
    if m:
        return (int(m.group(1)) * 60 + int(m.group(2))) * 1000 + _frac_ms(m.group(4))
    m = RE_SEC.match(s)
    if m:
        return int(m.group(1)) * 1000 + _frac_ms(m.group(3))
    if "," in s:
        raise ValueError("%r: dang giay tran phai dung dau cham, khong dung dau phay" % s)
    raise ValueError("%r: khong nhan dang duoc moc thoi gian" % s)


def snap(ms, grid_ms=100):
    """Bat mot moc TUYET DOI ve boi so gan nhat cua luoi. Khong bao gio bat theo do dai shot."""
    return int(round(float(ms) / grid_ms)) * grid_ms


def parse_text(text, grid_ms=100):
    """Phan tich van ban TSV thanh (shots, errors, warnings). Khong doc dia, khong goi tien trinh ngoai."""
    errs, warns = [], []
    lines = [ln for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return [], ["file rong"], warns

    head = [c.strip() for c in lines[0].lstrip("\ufeff").split("\t")]
    if len(head) == 1 and "," in head[0]:
        return [], ["dong tieu de khong co ky tu tab. File phai la TSV, khong phai CSV"], warns
    for col in REQUIRED:
        if col not in head:
            errs.append("thieu cot bat buoc %r. Cot doc duoc: %s" % (col, ", ".join(head)))
    known = set(REQUIRED) + set() if False else set(REQUIRED) | set(OPTIONAL) | set(RESERVED)
    for col in head:
        if col not in known:
            errs.append("cot la %r khong thuoc luoc do. Cot cho phep: %s"
                        % (col, ", ".join(REQUIRED + OPTIONAL + RESERVED)))
    dup = sorted(set(c for c in head if head.count(c) > 1))
    if dup:
        errs.append("cot trung ten: %s" % ", ".join(dup))
    if errs:
        return [], errs, warns

    shots = []
    for n, ln in enumerate(lines[1:], start=2):
        if not ln.strip():
            warns.append("dong %d rong, bo qua" % n)
            continue
        cells = ln.split("\t")
        if len(cells) > len(head):
            errs.append("dong %d: co %d o, nhieu hon %d cot tieu de" % (n, len(cells), len(head)))
            continue
        cells += [""] * (len(head) - len(cells))
        row = dict(zip(head, [c.strip() for c in cells]))
        for col in RESERVED:
            if row.get(col):
                warns.append("dong %d cot %r = %r: cot nay chua duoc dung o phien ban nay, "
                             "gia tri bi bo qua. Ly do: nhanh ma tuong ung chua kiem chung."
                             % (n, col, row[col]))
        try:
            idx = int(row["idx"])
        except ValueError:
            errs.append("dong %d: idx = %r khong phai so nguyen" % (n, row["idx"]))
            continue
        try:
            start_raw = parse_start(row["start"])
        except ValueError as e:
            errs.append("dong %d shot %s: start %s" % (n, row["idx"], e))
            continue
        if not row["image"]:
            errs.append("dong %d shot %d: cot image rong" % (n, idx))
            continue
        shots.append(Shot(idx, snap(start_raw, grid_ms), row["image"],
                          row.get("transition", ""), row.get("note", ""), n))

    if not shots:
        errs.append("khong doc duoc dong shot nao")
        return shots, errs, warns

    for i, sh in enumerate(shots):
        if sh.idx != i + 1:
            errs.append("dong %d: idx = %d nhung phai la %d. idx phai lien tuc tu 1." % (sh.row, sh.idx, i + 1))
    if shots[0].start_ms != 0:
        errs.append("shot 1 bat dau o %d ms, phai bat dau tu 0" % shots[0].start_ms)
    for a, b in zip(shots, shots[1:]):
        if b.start_ms < a.start_ms:
            errs.append("shot %d bat dau %d ms, som hon shot %d o %d ms. start phai tang."
                        % (b.idx, b.start_ms, a.idx, a.start_ms))
        elif b.start_ms == a.start_ms:
            errs.append("shot %d va shot %d cung bat dau o %d ms sau khi bat luoi %d ms, "
                        "shot %d se dai 0. Hai moc qua gan nhau."
                        % (a.idx, b.idx, a.start_ms, grid_ms, a.idx))
        else:
            a.dur_ms = b.start_ms - a.start_ms
    if shots[-1].transition:
        errs.append("shot cuoi (%d) co transition = %r. Shot cuoi khong co ranh gioi sau no."
                    % (shots[-1].idx, shots[-1].transition))
    return shots, errs, warns


def check_images(shots, images_dir):
    """Kiem moi ten anh co that trong images_dir. Tra ve danh sach loi."""
    errs = []
    root = Path(images_dir)
    for sh in shots:
        if Path(sh.image).name != sh.image:
            errs.append("shot %d: image = %r phai la ten file tran, khong duong dan" % (sh.idx, sh.image))
        elif not (root / sh.image).is_file():
            errs.append("shot %d: khong thay anh %s" % (sh.idx, root / sh.image))
    return errs


def check_transitions(shots, whitelist, blacklist):
    errs = []
    wl, bl = set(whitelist or ()), set(blacklist or ())
    for sh in shots:
        if not sh.transition:
            continue
        if sh.transition in bl:
            errs.append("shot %d: transition %r nam trong blacklist" % (sh.idx, sh.transition))
        elif wl and sh.transition not in wl:
            errs.append("shot %d: transition %r khong co trong whitelist" % (sh.idx, sh.transition))
    return errs


def close_tail(shots, total_ms):
    """Dong do dai shot cuoi bang tong da bat luoi. Tra ve danh sach loi."""
    if total_ms is None:
        return ["chua biet tong do dai nen khong tinh duoc do dai shot cuoi"]
    if total_ms <= shots[-1].start_ms:
        return ["tong %d ms khong lon hon moc bat dau shot cuoi %d ms" % (total_ms, shots[-1].start_ms)]
    shots[-1].dur_ms = total_ms - shots[-1].start_ms
    return []


def warn_short(shots, min_shot_warn_s):
    out = []
    lim = int(round(float(min_shot_warn_s) * 1000))
    for sh in shots:
        if sh.dur_ms is not None and sh.dur_ms < lim:
            out.append("shot %d chi dai %.1f s, ngan hon nguong %.1f s" % (sh.idx, sh.dur_ms / 1000.0, lim / 1000.0))
    return out


def load(path, images_dir=None, whitelist=None, blacklist=None,
         grid_ms=100, min_shot_warn_s=0.0, total_ms=None):
    """Doc mot file shotlist tu dia roi kiem het moi phep. Nem ShotlistError kem toan bo LOI."""
    p = Path(path)
    if not p.is_file():
        raise ShotlistError(["khong thay shotlist: %s" % p])
    shots, errs, warns = parse_text(p.read_text(encoding="utf-8-sig"), grid_ms=grid_ms)
    if not errs:
        if images_dir:
            errs += check_images(shots, images_dir)
        errs += check_transitions(shots, whitelist, blacklist)
        warns += close_tail(shots, total_ms)
    if errs:
        raise ShotlistError(errs)
    warns += warn_short(shots, min_shot_warn_s)
    return shots, warns


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="Doc va kiem shotlist.tsv. Khong ghi gi.")
    ap.add_argument("config", nargs="?", default="config.json")
    ap.add_argument("--shotlist", default=None, help="ghi de duong dan trong config")
    ap.add_argument("--total-ms", type=int, default=None)
    a = ap.parse_args(argv[1:])

    from pipeline import config as cfgmod
    try:
        cfg = cfgmod.load(a.config, check_inputs=False)
    except cfgmod.ConfigError as e:
        for line in e.errors:
            print("  LOI  config: %s" % line)
        return EXIT_BAD

    target = a.shotlist or cfg.path_of("inputs.shotlist")
    print("SHOTLIST : %s" % Path(target).resolve())
    try:
        shots, warns = load(target,
                            images_dir=cfg.path_of("inputs.images_dir"),
                            whitelist=cfg.get("transitions.whitelist"),
                            blacklist=cfg.get("transitions.blacklist"),
                            grid_ms=cfg.get("timing.grid_ms", 100),
                            min_shot_warn_s=cfg.get("timing.min_shot_warn_s", 0.0),
                            total_ms=a.total_ms)
    except ShotlistError as e:
        print("")
        print("=== LOI (%d) ===" % len(e.errors))
        for line in e.errors:
            print("  LOI  %s" % line)
        print("")
        print("KHONG HOP LE -- khong dung ket qua nay.")
        return EXIT_BAD

    for line in warns:
        print("  CANH BAO %s" % line)
    print("")
    print("idx  start_ms  dur_ms  transition      image")
    for sh in shots:
        print("%3d  %8d  %6s  %-14s  %s"
              % (sh.idx, sh.start_ms, "n/a" if sh.dur_ms is None else sh.dur_ms,
                 sh.transition or "-", sh.image))
    known = [sh.dur_ms for sh in shots if sh.dur_ms is not None]
    print("")
    print("shot     : %d | transition: %d" % (len(shots), sum(1 for s in shots if s.transition)))
    if known:
        print("do dai   : min %.1f s | max %.1f s" % (min(known) / 1000.0, max(known) / 1000.0))
    print("HOP LE -- %d canh bao." % len(warns))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))