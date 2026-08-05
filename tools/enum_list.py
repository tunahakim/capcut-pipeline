"""enum_list.py
In catalogue transition, image-intro, image-outro và image-combo lấy từ capcut enums, bỏ mục VIP, riêng transition bỏ luôn mục is_overlap vì nó làm dịch timeline.
Vào: không tham số, cần capcut-cli trong PATH. Ra: chỉ in console gồm slug, default_duration và tên hiển thị.
Dùng thay cho capcut enums --type X, vì cú pháp đó trả về mảng rỗng mà không báo lỗi, xem failures.md mục 2.2.
[KIEM: chua]
"""

import subprocess, sys, json

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def run(args):
    p = subprocess.run(args, shell=True, capture_output=True)
    txt = p.stdout.decode('utf-8', errors='replace').strip()
    if not txt:
        print('  (RONG) stderr:', p.stderr.decode('utf-8', errors='replace')[:300])
        return []
    try:
        return json.loads(txt)
    except Exception as e:
        print('  (KHONG PHAI JSON)', e)
        print(txt[:300])
        return []

def show(title, flag, only_safe=False):
    print()
    print('=' * 72)
    print(title)
    print('=' * 72)
    a = run('capcut enums ' + flag)
    print('tong:', len(a))
    n = 0
    for x in a:
        slug = x.get('slug') or ''
        if not slug:
            continue
        if x.get('is_vip'):
            continue
        if only_safe and x.get('is_overlap'):
            continue
        n += 1
        print('  {0:34} {1:>9}  {2}'.format(slug, x.get('default_duration', '?'), x.get('name', '')))
    print('-> dung duoc:', n)

show('TRANSITIONS (is_overlap=false, khong VIP)', '--transitions', only_safe=True)
show('IMAGE INTROS', '--image-intros')
show('IMAGE OUTROS', '--image-outros')
show('IMAGE COMBOS', '--image-combos')