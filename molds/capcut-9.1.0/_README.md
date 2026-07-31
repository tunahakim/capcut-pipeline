# Khuon material - CapCut 9.1.0

Moi file la mot material do CHINH CAPCUT ghi ra (phep thu oracle), dung lam khuon de Python dap lai. Phan thu muc theo phien ban CapCut vi schema co the doi.

Cach chup khuon moi: tao doi tuong bang tay trong GUI, dong CapCut bang nut X, doi muoi giay, chay `tools/v4_mold.py <project>`, roi luu ket qua vao day.

| File | Nguon | Trang thai |
|---|---|---|
| filter.json | GUI tha filter "Film", 28/07/2026, project testV4 | da dung trong filter_apply.py |

Con thieu: transition, canvas_blur, video_segment, audio_segment, material_animation, scene_effect, track cua tung loai.

## Canh bao khi chup lai khuon

**Khuon chua truong phu thuoc may va phu thuoc project.** Trong `filter.json` hien tai, `material.path` la duong dan tuyet doi cua profile user `anhlt`, va `segment.target_timerange.duration` la 168733333 tuc do dai rieng cua project tam shot. Chup lai o may khac hoac project khac se diff ra khac o dung hai cho do du khong co gi doi that. Khi diff phai phan loai: hai truong nay **duoc phep** khac, moi truong con lai **bat buoc** khop.

**Tinh trang 31/07/2026: khong con project nao tren may phat trien chua filter do GUI tao.** Da quet ca muoi mot project trong thu muc draft. `strip_filters.py` da go sach filter khoi testV4 o phien v6. Muon chup lai khuon filter thi phai tha tay mot filter trong GUI truoc. Cho toi khi do, `tools/v4_mold.py` **khong co doi chung duong de chay thu**.

Hết nội dung file.