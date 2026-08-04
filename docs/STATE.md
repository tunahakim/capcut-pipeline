# STATE — trạng thái dự án

**Cập nhật 04/08/2026.** File này là **ảnh chụp thì hiện tại**: cái gì đang đúng ngay bây giờ, máy nào có gì, số đo hiện hành là bao nhiêu, đã kiểm chứng tới mức nào. Không có ngày tháng trong thân bài, không có chữ "đã làm", không có việc phải làm. Cách sửa file này là **ghi đè**, không phải thêm vào — đó là cơ chế chống phình, vì một ảnh chụp không dài ra theo thời gian. Trần kích thước là **15 KB**. Việc phải làm nằm ở `TODO.md`, diễn biến và số liệu lịch sử nằm ở `research-log/INDEX.md`, thứ không đổi theo phiên nằm ở `START-HERE.md`.

## 1. Tóm tắt một câu

Toàn bộ chuỗi từ ảnh cộng narration tới file MP4 60 phút **đã kiểm chứng ở mức bằng chứng cao nhất**, hai lần, trên dữ liệu thật. Việc còn lại là gói nó thành ứng dụng dùng được và trả các món nợ kỹ thuật, không còn câu hỏi khả thi nào để trả lời.

## 2. Hai máy

Máy lab, nơi làm mọi việc soạn code và tài liệu. Windows 10 build 19045, PowerShell 5.1, Python 3.14.6 bản python.org, Node v24.14.0, npm 11.9.0, capcut-cli 0.15.0, ffmpeg và ffprobe 8.1.2, CapCut 9.1.0.3879 updater đã chặn, Git 2.53. PC văn phòng mười năm tuổi, cấu hình yếu. Ổ C còn khoảng 10,7 GB trên 100 GB và thư mục draft của CapCut nằm ở đó, ổ D còn khoảng 17,5 GB. Snapshot của `docs_audit.py` ghi vào `data\perf\` tức trên **ổ D**, không phải ổ C. **Luôn kiểm dung lượng trước mỗi việc lớn.** `LongPathsEnabled` vẫn bằng 0.

Máy render, nơi dựng project lớn và export. MSI MS-7E05, i5-10400F 6 nhân 12 luồng, 16 GB RAM, GTX 1080, Windows 10 build 19042, không có winget. Ổ C là SSD NVMe 238 GB chứa thư mục draft, ổ D là SSD SATA chứa `D:\IT\capcut-lab`. CapCut 9.1.0.3879, updater đã chặn bằng deny ACL trên `CapCut-DiffUpgrade.exe` và `hpatchz.exe`. Thư mục ảnh sản xuất ở `D:\IT\capcut-help\Picture`, 326 ảnh.

**Từ 01/08/2026 máy render tạm không truy cập được, dự kiến ba tới bốn ngày.** Mọi việc cần mở CapCut ở quy mô lớn hoặc cần export đều phải xếp hàng chờ. Máy lab không thay thế được: một bản export 60 phút nặng 4,07 GB trong khi ổ C của máy lab chỉ còn khoảng 10,7 GB.

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

Catalogue filter JianYing: 468 mục, 300 khoá VIP, 168 free, không mục nào thiếu cờ `is_vip`. Cờ đó **không dự đoán được** khoá Pro trong GUI CapCut bản quốc tế, và `resource_id` của hai namespace không trùng nhau; số đo ở `reference-catalog.md`. Thư mục draft trên máy lab có 13 mục: `.recycle_bin` cộng 12 project, sau khi xoá `fxlab01` ngày 04/08/2026. `Test_A_v2` không có thư mục `Timelines\`; `testB_CLEAN` và `Test_A_v2` rỗng. Chỉ **`fxprobe01`** có material `type=filter`, hai mục thả tay từ GUI ngày 02/08/2026, nằm trong bucket `materials.effects` trên một track `type=filter` — **không** phải bucket tên `filters`. `bench300` và `parity01` không tồn tại trên máy lab.

Cờ VIP ở namespace CapCut mặc định, đo 02/08/2026: scene-effect **0 VIP trên 345**, image-intro **0 trên 43**, image-outro **0 trên 23**, image-combo **0 trên 108**. Khoá `is_vip` có mặt trên mọi mục nhưng hằng `false`, và khoá `member` là tên thành viên enum chứ không phải cờ khoá Pro. Quan sát GUI cùng ngày: tab Animation mục Out có rất nhiều mục, đa số đeo dấu Pro kim cương tím, nên **enums không phải catalogue của GUI** và cờ đó không dùng được cho bản quốc tế. Cùng bốn loại ở namespace JianYing thì cờ có phân bố thật: 297/912, 58/95, 54/72, 16/123.

Khoá Pro, đo bằng **oracle** ngày 03/08/2026. Dấu Pro trong GUI CapCut là **viên kim cương tím**, không phải vương miện. CapCut chặn export `v2oracle` và tự khai hộp thoại Pro materials liệt kê đúng một mục tên `Up` ở mốc 00:01:12; transition tương ứng có `resource_id` **6724227090872275463**, `category_name` Classic, có `request_id`. `resource_id` đó **không tồn tại trong namespace `capcut`** của enums, chỉ có ở namespace JianYing dưới tên 向上 với `is_vip` bằng `false`; còn tên `Up` trong namespace `capcut` lại là `resource_id` 6724846395116753416, tức mục FREE. Ba kết luận đã đóng: cờ `is_vip` của enums **vô dụng cho bản quốc tế**, enums **không phủ danh mục GUI**, và **tra theo tên là bẫy**. Trường `md5` trong enums **chính là tên file trong thư mục cache hiệu ứng**, khớp tuyệt đối với `path` mà `draft_content.json` ghi. Xác nhận trực tiếp cùng ngày bằng phép gỡ: xoá đúng transition đó trong GUI thì CapCut cho export thẳng, không còn hộp thoại Pro materials, trong khi transition free 6724846395116753416 vẫn nằm nguyên trong project; vậy CapCut chặn theo từng `resource_id` cụ thể chứ không theo loại tài nguyên. Xoá transition trong GUI **không dịch timeline**, đo trước và sau cho 0,000 ms trên cả 8 shot.

Canvas blur trên bốn project `testV3`, `testV4`, `v2oracle`, `testB`, đo 03/08/2026: giá trị `blur` hằng **0,75 trên toàn bộ 32 segment**, không project nào có hai mức, nên máy lab **không có mẫu đa mức**. `check_flag` tương quan tuyệt đối với loại canvas: 4103 với `canvas_blur` ở 32/32 segment, 7 với `canvas_color` ở 7/7 segment của `v2oracle`. Vị trí ref của `canvas_blur` trong `extra_material_refs` **không cố định**, đo được ba dạng idx 2/7, idx 3/8, idx 3/9; mọi mã giả định chỉ số cố định sẽ gãy âm thầm. Bản lồng trong `Timelines` trùng khít bản gốc ở cả bốn project. `frame_audit.py` đã nghiệm thu ở mức bằng chứng 5 trên `v2oracle`: ba nhãn ra đúng ba dự đoán chốt trước, mâu thuẫn JSON với pixel 0/8. Bộ chọn mẫu của `bgblur_frames.py` nay báo độ phủ, đo được 3/6 vai trên `v2oracle` và 1/6 trên `testV4`. `shots_dump.py` **không** giữ hiệu ứng thả tay: dump `fxprobe01` mất sạch hai filter mà không cảnh báo.

Cơ chế ghi vết, đếm 03/08/2026 trên 40 file `.py` của `tools/` và `scripts_v1/`: **0 file dùng `logging`**, 38 khối `try`, 39 `except`, 1 `raise`, 62 chỗ `sys.exit`, 0 chỗ `traceback`. Có xử lý lỗi nhưng không ghi vết ra file.

Kênh đọc tài liệu qua GitHub, đo 03/08/2026: `repo_bytecheck.py` cho 134 blob, khớp 134, lệch 0, thiếu 0. Trần công cụ fetch là **10000 token mỗi lượt gọi**, không phải byte: 22296 và 24798 byte tiếng Việt về trọn, 32393 byte JSON bị cắt ở 10544 token. Trần tài liệu nay ba lớp; chi tiết ở `ai-reading-channel.md`. Xác nhận thêm 04/08/2026, trọn một phiên từ đầu tới cuối: nội dung người dùng dán thẳng vào hội thoại giữ nguyên văn suốt phiên, trong khi kết quả `crawler` mất khúc giữa chỉ sau một lượt và tự khai số ký tự đã bỏ. Đúng với Claude Opus 5 trên genspark.ai.

Bảng script, đo 04/08/2026: 43 script đang dùng, 26 script lưu trữ, 0 script thiếu docstring. Nhãn mức kiểm chứng khai bằng hậu tố `[KIEM: ...]` trong docstring và hiện thành cột riêng của `scripts.md`: 12 `du lieu that`, 8 `bo test`, 2 `mot lan`, 21 `chua`. Hai mươi mốt nhãn `chua` là do trợ lý không tìm được bằng chứng trong `STATE.md`, không phải bằng chứng rằng script chưa chạy. `scripts.md` nặng 25095 byte, 61 phần trăm trần riêng 40 KB.

`shots_dump.py` nay cảnh báo hai mức khi dump draft ra CSV: `CANH BAO` cho thứ mất hẳn, `GHI CHU` cho thứ đã biết là không thuộc bảng shot, và bucket materials lạ mặc định rơi vào `CANH BAO`. Nghiệm thu 04/08/2026 đạt 3 trên 3 dự đoán chốt trước: `fxprobe01` hai dòng cảnh báo, `testV3` không dòng nào, `testV4` hai dòng.

Mở một project bằng GUI CapCut là **ghi lại `draft_content.json`** kể cả khi không sửa gì: `fxprobe01` đi từ 27423 lên 27456 byte, tăng 33 byte, chỉ vì được mở ra xem; `testV3` và `testV4` không mở nên không đổi byte nào. Đo 04/08/2026.

`README.md` rút từ 10536 xuống 6208 byte sau khi chuyển cơ chế fetch sang `ai-reading-channel.md`, nay chỉ còn luật áp dụng ngay lần fetch đầu. `INDEX.md` có 23 dòng phiên, dưới ngưỡng 30 nên `tools/rlog_index_trim.py` báo chưa cần cắt; cơ chế đã nghiệm thu bằng ngưỡng giả 5, tính đúng 18 dòng phải đẩy và không ghi gì khi chạy thử.

## 5. Việc đang dở và nợ kỹ thuật

Không liệt kê ở đây. Danh sách đầy đủ, có ưu tiên và có tiêu chí hoàn thành, nằm ở `TODO.md`. Giữ hai bản song song thì chắc chắn sẽ lệch nhau.