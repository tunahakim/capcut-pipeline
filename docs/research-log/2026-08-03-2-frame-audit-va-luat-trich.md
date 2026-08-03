# Nhat ky phien 03/08/2026 (2) — nghiem thu `frame_audit.py`, dong oracle khoa Pro bang phep go, va luat trich file moi

May lab. Co mo CapCut, co export that, **co MP4**. Phien truoc la `2026-08-03-1-bgblur-va-oracle-pro.md`.

## Buoc 1 — `../../tools/frame_audit.py` nghiem thu dat, 3 tren 3

Go transition Pro o 72,733 giay cua `v2oracle` trong GUI roi export tron project ra `v2oracle_noPro.mp4`, 245,6 MB, 1920x1080, 30/1 fps, 5062 frame, 168,739 giay.

Du doan da chot tu phien truoc, giu nguyen khong doi: shot 3 tai 41,800 giay ra BLUR, shot 6 tai 99,333 giay ra BLACK, shot 1 tai 9,883 giay ra AMBIG. Ket qua trung ca ba, va `mau thuan JSON vs pixel` bang **0 tren 8**.

So do tung shot: shot 3 co `bar_pred` 0,7519 voi `dark20` 0,0337 nen BLUR rat chac, nguong BLUR la 0,2632. Shot 6 co `bar_pred` 0,3650 voi `dark20` 0,5625 nen BLACK, nguong BLACK la 0,2373. Sau shot con lai co `bar_pred` bang 0,0000 hoac 0,0078, deu duoi cong 0,02 nen ra AMBIG, dung thiet ke.

**Gioi han phat hien duoc, chua kiem chung.** `dark20` dem moi pixel toi trong khung, khong tach duoc pixel toi cua vien khoi pixel toi cua chinh buc anh. Tren `v2oracle` do duoc sau shot khong vien van co `dark20` trung binh 0,2195, rieng shot 5 len 0,2570 va shot 4 len 0,2323. O project nay vo hai vi cong 0,02 chan chung lai. Nhung mot shot co vien trung binh co 0,1 se co nguong BLACK chi 0,065, va noi dung toi mot minh da vuot xa muc do, nen co the gan BLACK cho mot shot that su co blur. Ket luan: `frame_audit.py` dang tin o hai dau vien rat rong va vien rat hep, con **vung vien trung binh chua co bang chung**. Lab chua co phan vi du that.

## Buoc 1b — oracle khoa Pro, dong dinh bang phep go

Phien truoc quy muc Pro ve transition o 72,733 giay bang cach **suy tu moc thoi gian** 00:01:12 trong hop thoai, va tu ghi do la chua kiem chung. Nay lam phep re da de xuat: xoa dung transition do roi export lai.

Ket qua: CapCut **khong bat hop thoai Pro materials nua**, vao thang man hinh tuy chon render. Muc Pro dung la transition `resource_id` **6724227090872275463**. Do truoc, can thiep, do sau, doi chieu nguoc — khong con la suy luan.

Hai he qua co bang chung di kem. Transition free `resource_id` 6724846395116753416 van nam nguyen trong project o ranh gioi 34,700 giay ma export khong bi chan, nen thu CapCut chan la **tung `resource_id` cu the**, khong phai loai tai nguyen transition noi chung. Va **xoa transition trong GUI khong dich timeline**: do truoc va sau bang cung mot script, `d_start_ms` va `d_dur_ms` deu bang 0,000 tren ca 8 shot, lech lon nhat 0,000 ms so voi mot frame 33,333 ms. Truoc phien nay chua co phep do nao cho dieu do.

## Buoc 2 — va `../../tools/bgblur_frames.py` cho no noi ra khi thieu mau

Chan doan: ham `take` lay `cs[:n]`, khi danh sach ung vien rong thi vong lap chay khong lan nao va khong de lai dau vet. Bon vai `blur-max`, `blur-min`, `neg-color`, `blur-mid` cung cap doi chung AB deu di qua dung co che do. Co them mot nguon roi mau thu hai chua ai de y: bo loc `dur >= 4.0` chay truoc moi thu, nen shot ngan cung bi loai im lang.

Ban va them khoi `DO PHU MAU` in ngay sau bon lenh `take`: dem so gia tri `blur` phan biet va so loai canvas phan biet **truoc** khi in bang, neu ten tung vai thieu kem ly do, bao so shot bi loai vi ngan, va noi thang rang bang ben duoi khong phu du danh muc. Ma thoat giu nguyen 0, vi `--mp4` vang mat cung dang tra 0 va doi mot minh cho nay se thanh bat nhat. File tang tu 6423 len 7817 byte.

Nghiem thu bang hai project cho hai ket qua phai khac nhau. `v2oracle` ra **3 tren 6 vai**, thieu `blur-max`, `blur-min`, `blur-mid`. `testV4` ra **1 tren 6 vai**, thieu nam vai con lai, voi dung mot gia tri blur phan biet la 0,75 va dung mot loai canvas.

**Du doan cua nguoi viet sai mot phan, ghi lai nguyen trang.** Du doan `v2oracle` thieu `blur-max`, `blur-min`, `neg-color`; thuc te thieu `blur-mid` chu khong phai `neg-color`, va ly do dua ra cung nguoc. `v2oracle` co 7 shot `canvas_color` nen `neg-color` thua ung vien; thu bi chiem sach la shot `canvas_blur`, ca project chi co dung mot la shot 3 va `AB-pos` da lay mat, nen `blur-mid` het ung vien du 0,75 thoa dieu kien. Dung so vai thieu, sai ten vai. Chinh cho nay minh hoa vi sao ban va can thiet: bang cu ba dong khong cho ai biet vai nao da roi.

## Buoc 3 — `../../tools/shots_dump.py` khong giu duoc hieu ung tha tay

Ground truth `fxprobe01` doc thang tu draft, khop tuyet doi mo ta cu: bucket `materials.effects` dung 2 muc, `VHS III` `resource_id` 6764669298095952396 va `2077` `resource_id` 7145435245712511489, ca hai `type=filter`, `value` 1.0, `apply_target_type` 0; mot track `type=filter` mang 2 segment phu 0,000..5,000 va 5,033..10,000 giay; track video 3 segment, clip thu ba khong co filter.

Dump nguoc ra CSV: dung 3 dong du lieu, cot `transition` bang 0 ca ba, cot `blur` bang 0 ca ba, khong cot nao mang ten filter hay `resource_id` nao. Cot `kb` khong duoc ghi vi ca 3 segment thieu keyframe, dung hop dong da thiet ke.

Doc tron ma thay ro nguyen nhan: `build_rows` chi duyet track do `main_track` tra ve, tuc track `type=video`, va vong lap `extra_material_refs` chi nhan hai bucket `canvases` va `transitions`. Bucket `effects` khong co nhanh nao, track `type=filter` khong duoc cham toi.

Day **khong phai loi** vi docstring chi hua dump sau cot cua bang shot dau vao. Nhung `shots_dump.py` **khong phai cong cu khu hoi cho project co hieu ung tha tay**, va no khong canh bao gi khi gap track `type=filter` hoac bucket `effects` khong rong — cung dang suy giam im lang vua va cho `bgblur_frames.py`. Buoc dung lai roi so `resource_id` da bo, vi mat mat do duoc ngay tai khau dump nen dung lai chi xac nhan thu da biet.

## Luat trich file, thay nguong 4 KB

Nguong cu do bang byte khong phan anh thu that su quan trong la bao nhieu dong bi loai. Phien nay co hai phan vi du lien tiep. Trich `bgblur_frames.py` 154 dong chi loai duoc 5 dong, tiet kiem 3,2 phan tram, doi lai ton mot script, mot vong chay, va nguoi doc mat nguyen van 5 dong nen phai khai bao khong biet chung chua gi. Trich thu `shots_dump.py` 148 dong loai duoc 9 dong, tiet kiem 6,1 phan tram; script tu chuyen sang in tron, va nho doc tron ma nguyen nhan Buoc 3 lo ra ngay trong mot luot thay vi phai hoi them vong nua.

Luat moi da ghi vao muc 8 cua `../START-HERE.md`, ba bac theo so dong that. Ly le nen, nguoi dung neu va da tiep thu: mot luot hoi lai ton nhieu hon vai KB token rat nhieu, va khi muc dich la chan doan nguyen nhan thi doc tron ma thuong tra loi luon.

## Chua kiem chung

`frame_audit.py` goi ffmpeg voi `-ss` dat truoc `-i`, tuc input seeking, nen khung lay duoc co the lech vai frame so voi moc yeu cau tuy vi tri keyframe H.264. Voi ba moc nam giua shot thi lech vai frame khong doi nhan, nhung dieu nay chua do.

Vung vien trung binh cua `frame_audit.py`, nhu da noi o Buoc 1. Phep so sanh `blur == 1.0` tren so thuc trong `bgblur_frames.py`. Gia thuyet tu phien truoc rang co `request_id` cung `category_name` la dau hieu tai nguyen tai tu CDN van chua kiem; phien nay khong dung toi.

## Con lai

Ba no moi sinh trong phien da ghi vao `../TODO.md`. Toan bo no nho du kien cua phien hoan sang phien sau, con nguyen trong `../TODO.md`.
