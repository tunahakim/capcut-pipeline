# Khuon material - CapCut 9.1.0

Moi file la mot material do CHINH CAPCUT ghi ra (phep thu oracle), dung lam khuon de Python dap lai. Phan thu muc theo phien ban CapCut vi schema co the doi.

Cach chup khuon moi: tao doi tuong bang tay trong GUI, dong CapCut bang nut X, doi muoi giay, chay `tools/v4_mold.py <project>`, roi luu ket qua vao day.

| File | Nguon | Trang thai |
|---|---|---|
| filter.json | GUI tha filter "Film", 28/07/2026, project testV4 | da dung trong filter_apply.py |

Con thieu: transition, canvas_blur, video_segment, audio_segment, material_animation, scene_effect, track cua tung loai.

## Canh bao khi chup lai khuon

**Khuon chua truong phu thuoc may va phu thuoc project.** Trong `filter.json` hien tai, `material.path` la duong dan tuyet doi cua profile user `anhlt`, va `segment.target_timerange.duration` la 168733333 tuc do dai rieng cua project tam shot. Chup lai o may khac hoac project khac se diff ra khac o dung hai cho do du khong co gi doi that. Khi diff phai phan loai: hai truong nay **duoc phep** khac, moi truong con lai **bat buoc** khop.

**Tinh trang 02/08/2026: da go chan.** Project `fxprobe01` trong thu muc draft co hai material `type=filter` tha tay tu GUI, la "VHS III" resource_id 6764669298095952396 va "2077" resource_id 7145435245712511489. Ca hai nam trong bucket `materials.effects` tren mot track rieng `type=filter`, **khong** phai bucket ten `filters`. Do la doi chung duong de chay `tools/v4_mold.py`. Ca hai deu FREE trong GUI ban quoc te; chua co filter Pro nao tren may lab, xem `docs/reference-catalog.md`.

Hết nội dung file.