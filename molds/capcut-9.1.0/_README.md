# Khuon material - CapCut 9.1.0

Moi file la mot material do CHINH CAPCUT ghi ra (phep thu oracle), dung lam khuon de Python dap lai. Phan thu muc theo phien ban CapCut vi schema co the doi.

Cach chup khuon moi: tao doi tuong bang tay trong GUI, dong CapCut bang nut X, doi muoi giay, chay `python tools/v4_mold.py --project <project-dir> --out molds/capcut-9.1.0/<ten>.json --write`. Mac dinh KHONG ghi de: bo `--write` thi chi diff. Project co nhieu material cung loai thi phai them `--pick <ten|rid>`, neu khong script bao loi thay vi lang le chup nham muc cuoi. Khoi `_meta` o dau moi khuon la sieu du lieu chup va bi bo qua khi diff.

| File | Nguon | Trang thai |
|---|---|---|
| filter.json | GUI tha filter "Film", 28/07/2026, project testV4 | da dung trong filter_apply.py |
| filter-vhs3.json | GUI tha filter "VHS III", 02/08/2026, project fxprobe01 | doi chung duong de nghiem thu v4_mold.py |

Con thieu: transition, canvas_blur, video_segment, audio_segment, material_animation, scene_effect, track cua tung loai.

## Canh bao khi chup lai khuon

**Khuon chua truong phu thuoc may va phu thuoc project.** Trong `filter.json` hien tai, `material.path` la duong dan tuyet doi cua profile user `anhlt`, va `segment.target_timerange.duration` la 168733333 tuc do dai rieng cua project tam shot. Chup lai o may khac hoac project khac se diff ra khac o dung hai cho do du khong co gi doi that. Khi diff phai phan loai: tu 02/08/2026 `v4_mold.py` chia ba nhom. MAY/PROJECT gom `material.path` va `segment.target_timerange.duration`, **duoc phep** khac. DINH DANH gom `id`, `material_id`, `effect_id`, `resource_id`, `third_resource_id`, `name`, `category_id`, `category_name`, `request_id`, `md5`, cung **duoc phep** khac vi hai filter khac nhau thi khac nhau mot cach chinh dang. Moi truong con lai **bat buoc** khop, va mot key co ben nay thieu ben kia thi LUON tinh la bat buoc vi do la troi schema.

**Tinh trang 02/08/2026: da go chan.** Project `fxprobe01` trong thu muc draft co hai material `type=filter` tha tay tu GUI, la "VHS III" resource_id 6764669298095952396 va "2077" resource_id 7145435245712511489. Ca hai nam trong bucket `materials.effects` tren mot track rieng `type=filter`, **khong** phai bucket ten `filters`. Do la doi chung duong de chay `tools/v4_mold.py`. Ca hai deu FREE trong GUI ban quoc te; chua co filter Pro nao tren may lab, xem `docs/reference-catalog.md`.

Hết nội dung file.