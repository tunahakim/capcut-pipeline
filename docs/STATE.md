# STATE — trạng thái dự án

**Cập nhật 01/08/2026.** File này là **ảnh chụp thì hiện tại**: cái gì đang đúng ngay bây giờ, máy nào có gì, số đo hiện hành là bao nhiêu, đã kiểm chứng tới mức nào. Không có ngày tháng trong thân bài, không có chữ "đã làm", không có việc phải làm. Cách sửa file này là **ghi đè**, không phải thêm vào — đó là cơ chế chống phình, vì một ảnh chụp không dài ra theo thời gian. Trần kích thước là **10 KB**. Việc phải làm nằm ở `TODO.md`, diễn biến và số liệu lịch sử nằm ở `research-log/INDEX.md`, thứ không đổi theo phiên nằm ở `START-HERE.md`.

## 1. Tóm tắt một câu

Toàn bộ chuỗi từ ảnh cộng narration tới file MP4 60 phút **đã kiểm chứng ở mức bằng chứng cao nhất**, hai lần, trên dữ liệu thật. Việc còn lại là gói nó thành ứng dụng dùng được và trả các món nợ kỹ thuật, không còn câu hỏi khả thi nào để trả lời.

## 2. Hai máy

Máy lab, nơi làm mọi việc soạn code và tài liệu. Windows 10 build 19045, PowerShell 5.1, Python 3.14.6 bản python.org, Node v24.14.0, npm 11.9.0, capcut-cli 0.15.0, ffmpeg và ffprobe 8.1.2, CapCut 9.1.0.3879 updater đã chặn, Git 2.53. PC văn phòng mười năm tuổi, cấu hình yếu. Ổ C còn khoảng 10,8 GB trên 100 GB và thư mục draft của CapCut nằm ở đó, ổ D còn khoảng 17,5 GB; ổ C tụt dần vì snapshot của `docs_audit.py` dồn vào `data\perf\`. **Luôn kiểm dung lượng trước mỗi việc lớn.** `LongPathsEnabled` vẫn bằng 0.

Máy render, nơi dựng project lớn và export. MSI MS-7E05, i5-10400F 6 nhân 12 luồng, 16 GB RAM, GTX 1080, Windows 10 build 19042, không có winget. Ổ C là SSD NVMe 238 GB chứa thư mục draft, ổ D là SSD SATA chứa `D:\IT\capcut-lab`. CapCut 9.1.0.3879, updater đã chặn bằng deny ACL trên `CapCut-DiffUpgrade.exe` và `hpatchz.exe`. Thư mục ảnh sản xuất ở `D:\IT\capcut-help\Picture`, 326 ảnh.

**Từ 01/08/2026 máy render tạm không truy cập được, dự kiến ba tới bốn ngày.** Mọi việc cần mở CapCut ở quy mô lớn hoặc cần export đều phải xếp hàng chờ. Máy lab không thay thế được: một bản export 60 phút nặng 4,07 GB trong khi ổ C của máy lab chỉ còn khoảng 10,8 GB.

## 3. Đã kiểm chứng tới đâu

Bản dựng tham chiếu hiện hành là `prod60`: 300 shot, narration thật 59 phút, ảnh thật đủ kích thước, blur nền bật toàn bộ, 299 transition. 902 lệnh CLI trong 5,5 phút, `lint` sạch. Lệch timing **0,0 ms trên toàn bộ 300 shot** sau khi CapCut mở lần đầu. Export ra 4,07 GB, 00:59:05, 1920×1080 30 fps, video 9673 kbps, audio 189 kbps stereo, mất khoảng **6 phút**, tức nhanh hơn thời gian thực chừng mười lần. CPU và GPU đều dưới 40 phần trăm trong lúc render.

Luật timing bắt lưới 0,1 giây theo ranh giới tuyệt đối đã kiểm chứng ba lần ở ba quy mô: 300 shot bước đều, 300 shot với 300 độ dài khác nhau, và 300 shot khoá theo file audio thật. Cả ba đều cho 0,0 ms.

Luật ceil ở mốc cuối cộng đuôi cố ý đã kiểm chứng trên `reh10`: segment audio bị CapCut nới +8,5 ms lên biên frame, đuôi cố ý hấp thụ trọn, không shot nào bị đẩy.

Parity hai máy đã đạt 0,0 ms tuyệt đối trên cả bảng trước lẫn bảng sau, với mốc vàng tạo trên Python 3.13 và máy render chạy 3.14.6.

Canvas blur đã kiểm chứng ở mức bằng chứng cao nhất trên 300 shot. Ca từng bị gọi là lỗi im lặng thứ bảy hoá ra là lỗi quan sát, đã đóng, xem `failures.md` mục 2.8.

## 4. Số đo hiện hành

Hiệu năng lớp ghi: mỗi lệnh CLI tốn phần cố định khoảng **0,304 giây** cộng khoảng **0,27 mili giây cho mỗi segment đã tồn tại**. Ở mốc 300 segment phần cố định chiếm chừng 88 phần trăm. Lớp ghi tuyến tính. Kiến trúc một tiến trình CLI cho mỗi thao tác được giữ nguyên; chỉ xem lại nếu tổng số lệnh vượt khoảng 2.000.

Kích thước JSON: khoảng **2,9 KB cho mỗi segment trần** do `add-video` sinh ra. Project 300 shot đầy đủ hiệu ứng cho `draft_content.json` khoảng 1,0 MB.

Cache hiệu ứng: mở project 8 shot có 7 transition và 1 effect làm cache tăng khoảng 17 mục; mở project 300 shot không transition không effect làm cache tăng 0 mục. Khi ghi số đếm cache **luôn ghi kèm công cụ nào đếm**, vì ba cách đếm cho ba con số khác nhau.

Bản kê hai nhánh ngoài repo, đo ngày 02/08/2026 bằng `tools/data_manifest.py` trên máy lab: `data\` có 144 file 299,7 MB sau khi loại `tmp\` và `archive\`; `vendor\` khối canonical 9 mục 922,1 MB và khối extra 109 mục 39,4 MB; riêng `vendor\Cache_effect` gộp thành một mục rollup 14653 file 424842366 byte. File `manifests/lab.json` nặng 45260 byte. Quét đủ 1261,3 MB kèm hash SHA256 toàn bộ mất khoảng 125 giây khi cache hệ điều hành lạnh và khoảng 20 giây khi cache nóng. Máy render chưa có bản kê.

Catalogue filter JianYing: 468 mục, 300 khoá VIP, 168 free, không mục nào thiếu cờ `is_vip`; chi tiết ở `reference-catalog.md`. Thư mục draft trên máy lab có 11 project đọc được và **không project nào còn material `type=filter`**, đo ngày 02/08/2026. `bench300` và `parity01` không tồn tại trên máy lab.

## 5. Việc đang dở và nợ kỹ thuật

Không liệt kê ở đây. Danh sách đầy đủ, có ưu tiên và có tiêu chí hoàn thành, nằm ở `TODO.md`. Giữ hai bản song song thì chắc chắn sẽ lệch nhau.