#!/usr/bin/env python3
"""config.py - doc va kiem tra config.json theo luoc do so 1, bung bien moi truong, gom moi loi roi in mot luot.
Vao: duong dan config.json. Ra: doi tuong Config tra cuu bang khoa cham, kem danh sach canh bao; sai thi nem ConfigError.
Ma thoat khi chay truc tiep: 0 hop le, 2 khong hop le hoac khong doc duoc file.
[KIEM: chua]
"""

import json
import os
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SCHEMA = 1
EXIT_OK = 0
EXIT_CONFIG = 2

BLUR_MIN, BLUR_MAX = 0, 4
STRATEGIES = ("cli", "hybrid", "stamp")
BAD_NAME_CHARS = '<>:"/\\|?*'


class ConfigError(Exception):
    """Loi cau hinh. Thuoc tinh errors la danh sach chuoi doc duoc."""

    def __init__(self, errors):
        self.errors = list(errors)
        Exception.__init__(self, "config khong hop le: %d loi" % len(self.errors))


def expand(value):
    """Bung bien moi truong kieu %LOCALAPPDATA% roi tra ve chuoi."""
    return os.path.expandvars(str(value))


class Config:
    def __init__(self, data, source):
        self.data = data
        self.source = Path(source)
        self.warnings = []

    def get(self, dotted, default=None):
        cur = self.data
        for key in dotted.split("."):
            if not isinstance(cur, dict) or key not in cur:
                return default
            cur = cur[key]
        return cur

    def path_of(self, dotted):
        value = self.get(dotted)
        if value is None:
            return None
        return Path(expand(value))

    def dump(self, dest):
        """Chup mot ban config ra dest, dung cho artifacts moi luot chay."""
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(self.data, ensure_ascii=False, indent=2) + "\n"
        dest.write_text(text, encoding="utf-8")
        return dest


def _num(cfg, errs, key, integer, lo=None, hi=None):
    v = cfg.get(key)
    if isinstance(v, bool) or v is None:
        errs.append("%s: thieu hoac sai kieu, can mot so" % key)
        return None
    if integer and not isinstance(v, int):
        errs.append("%s: phai la so nguyen, dang la %r" % (key, v))
        return None
    if not integer and not isinstance(v, (int, float)):
        errs.append("%s: phai la so, dang la %r" % (key, v))
        return None
    if lo is not None and v < lo:
        errs.append("%s = %s: phai lon hon hoac bang %s" % (key, v, lo))
        return None
    if hi is not None and v > hi:
        errs.append("%s = %s: phai nho hon hoac bang %s" % (key, v, hi))
        return None
    return v


def _bool(cfg, errs, key):
    v = cfg.get(key)
    if not isinstance(v, bool):
        errs.append("%s: phai la true hoac false" % key)
        return None
    return v


def _str(cfg, errs, key, allow_empty=False):
    v = cfg.get(key)
    if not isinstance(v, str):
        errs.append("%s: thieu hoac khong phai chuoi" % key)
        return None
    if not allow_empty and not v.strip():
        errs.append("%s: chuoi rong" % key)
        return None
    return v


def _dir(cfg, errs, key, must_exist=True):
    v = _str(cfg, errs, key)
    if v is None:
        return None
    p = Path(expand(v))
    if must_exist and not p.is_dir():
        errs.append("%s: khong thay thu muc %s" % (key, p))
        return None
    return p


def _file(cfg, errs, key):
    v = _str(cfg, errs, key)
    if v is None:
        return None
    p = Path(expand(v))
    if not p.is_file():
        errs.append("%s: khong thay file %s" % (key, p))
        return None
    return p


def _tool(cfg, errs, key):
    v = _str(cfg, errs, key)
    if v is None:
        return None
    resolved = shutil.which(expand(v))
    if resolved is None:
        errs.append("%s = %r: khong tim thay tren PATH" % (key, v))
        return None
    return resolved


def _list_of_str(cfg, errs, key, min_len=0):
    v = cfg.get(key)
    if not isinstance(v, list):
        errs.append("%s: phai la mot danh sach" % key)
        return None
    for i, item in enumerate(v):
        if not isinstance(item, str) or not item.strip():
            errs.append("%s[%d]: phai la chuoi khong rong" % (key, i))
            return None
    if len(v) < min_len:
        errs.append("%s: can it nhat %d muc, dang co %d" % (key, min_len, len(v)))
        return None
    return v


def validate(cfg, check_inputs=True):
    """Kiem toan bo cau hinh. Tra ve danh sach loi; canh bao ghi vao cfg.warnings."""
    errs = []
    warns = []

    schema = cfg.get("schema")
    if schema != SCHEMA:
        errs.append("schema: can %d, dang la %r. File cau hinh nay khong dung phien ban."
                    % (SCHEMA, schema))
        cfg.warnings = warns
        return errs

    name = _str(cfg, errs, "project.name")
    if name is not None:
        bad = [c for c in name if c in BAD_NAME_CHARS]
        if bad:
            errs.append("project.name = %r: chua ky tu khong hop le %s" % (name, "".join(sorted(set(bad)))))

    _dir(cfg, errs, "project.drafts_dir")
    _dir(cfg, errs, "project.scaffold")

    if check_inputs:
        _file(cfg, errs, "inputs.shotlist")
        _dir(cfg, errs, "inputs.images_dir")
        _file(cfg, errs, "inputs.narration")
        _file(cfg, errs, "inputs.srt")

    _dir(cfg, errs, "paths.data_root")
    vendor = cfg.get("paths.vendor_root")
    if isinstance(vendor, str) and not Path(expand(vendor)).is_dir():
        warns.append("paths.vendor_root: khong thay %s. Chi can khi dung lai may."
                     % Path(expand(vendor)))
    cache = cfg.get("paths.cache_dir")
    if isinstance(cache, str) and not Path(expand(cache)).is_dir():
        warns.append("paths.cache_dir: khong thay %s. Filter bat buoc cache-first se hong."
                     % Path(expand(cache)))
    _tool(cfg, errs, "paths.ffmpeg")
    _tool(cfg, errs, "paths.ffprobe")
    _tool(cfg, errs, "paths.capcut_cli")

    _num(cfg, errs, "canvas.width", True, lo=1)
    _num(cfg, errs, "canvas.height", True, lo=1)
    _num(cfg, errs, "canvas.fps", True, lo=1)

    grid = _num(cfg, errs, "timing.grid_ms", True, lo=1)
    if grid is not None and grid != 100:
        warns.append("timing.grid_ms = %d: luat thiet ke da kiem chung ba lan la 100 ms. "
                     "Doi gia tri nay se pha bao dam sai lech duoi 50 ms." % grid)
    _num(cfg, errs, "timing.tail_ms", True, lo=1)
    _num(cfg, errs, "timing.min_shot_warn_s", False, lo=0)

    _num(cfg, errs, "kenburns.seed", True, lo=0)
    smin = _num(cfg, errs, "kenburns.scale_min", False, lo=0.01, hi=1.0)
    smax = _num(cfg, errs, "kenburns.scale_max", False, lo=0.01, hi=1.0)
    if smin is not None and smax is not None and smin > smax:
        errs.append("kenburns.scale_min = %s lon hon scale_max = %s" % (smin, smax))
    _num(cfg, errs, "kenburns.amplitude_factor", False, lo=0.0, hi=1.0)
    _num(cfg, errs, "kenburns.margin_safety", False, lo=0.0, hi=1.0)

    _bool(cfg, errs, "canvas_blur.enabled")
    _num(cfg, errs, "canvas_blur.level", True, lo=BLUR_MIN, hi=BLUR_MAX)

    tr_on = _bool(cfg, errs, "transitions.enabled")
    _num(cfg, errs, "transitions.default_duration_us", True, lo=1)
    _bool(cfg, errs, "transitions.require_is_overlap_false")
    wl = _list_of_str(cfg, errs, "transitions.whitelist", min_len=1 if tr_on else 0)
    bl = _list_of_str(cfg, errs, "transitions.blacklist")
    if wl is not None and bl is not None:
        clash = sorted(set(wl) & set(bl))
        if clash:
            errs.append("transitions: %s nam o ca whitelist lan blacklist" % ", ".join(clash))

    _bool(cfg, errs, "scene_effect.enabled")
    _str(cfg, errs, "scene_effect.slug")
    _num(cfg, errs, "scene_effect.intensity", False, lo=0.0, hi=1.0)

    _bool(cfg, errs, "filters.enabled")
    items = cfg.get("filters.items")
    if not isinstance(items, list):
        errs.append("filters.items: phai la mot danh sach")
    else:
        for i, it in enumerate(items):
            if not isinstance(it, dict):
                errs.append("filters.items[%d]: phai la mot doi tuong" % i)
                continue
            for k in ("name", "resource_id"):
                if not isinstance(it.get(k), str) or not it.get(k).strip():
                    errs.append("filters.items[%d].%s: thieu hoac rong" % (i, k))
            val = it.get("value")
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                errs.append("filters.items[%d].value: phai la mot so" % i)
            elif not 0.0 <= val <= 1.0:
                errs.append("filters.items[%d].value = %s: phai trong khoang 0 toi 1" % (i, val))

    strat = _str(cfg, errs, "runtime.strategy")
    if strat is not None and strat not in STRATEGIES:
        errs.append("runtime.strategy = %r: chi nhan %s" % (strat, " | ".join(STRATEGIES)))

    cfg.warnings = warns
    return errs


def load(path, check_inputs=True):
    """Doc va kiem tra mot file config.json. Nem ConfigError kem danh sach loi doc duoc."""
    p = Path(path)
    if not p.is_file():
        raise ConfigError(["khong thay file cau hinh: %s" % p])
    try:
        raw = p.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise ConfigError(["khong doc duoc %s: %s" % (p, e)])
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ConfigError(["JSON hong o dong %d cot %d: %s" % (e.lineno, e.colno, e.msg)])
    if not isinstance(data, dict):
        raise ConfigError(["goc cua config phai la mot doi tuong JSON"])
    cfg = Config(data, p)
    errs = validate(cfg, check_inputs=check_inputs)
    if errs:
        raise ConfigError(errs)
    return cfg


def main(argv):
    target = argv[1] if len(argv) > 1 else "config.json"
    print("CONFIG   : %s" % Path(target).resolve())
    try:
        cfg = load(target)
    except ConfigError as e:
        print("")
        print("=== LOI (%d) ===" % len(e.errors))
        for line in e.errors:
            print("  LOI  %s" % line)
        print("")
        print("KHONG HOP LE -- chua chay khau nao ca.")
        return EXIT_CONFIG
    for line in cfg.warnings:
        print("  CANH BAO %s" % line)
    print("")
    print("schema   : %d" % cfg.get("schema"))
    print("project  : %s" % cfg.get("project.name"))
    print("drafts   : %s" % cfg.path_of("project.drafts_dir"))
    print("scaffold : %s" % cfg.path_of("project.scaffold"))
    print("shotlist : %s" % cfg.path_of("inputs.shotlist"))
    print("anh      : %s" % cfg.path_of("inputs.images_dir"))
    print("narration: %s" % cfg.path_of("inputs.narration"))
    print("srt      : %s" % cfg.path_of("inputs.srt"))
    print("blur mac dinh: %s muc %s" % (cfg.get("canvas_blur.enabled"), cfg.get("canvas_blur.level")))
    print("luoi     : %d ms | duoi co y %d ms" % (cfg.get("timing.grid_ms"), cfg.get("timing.tail_ms")))
    print("")
    print("HOP LE -- %d canh bao." % len(cfg.warnings))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))