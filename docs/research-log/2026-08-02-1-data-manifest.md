# Nhật ký phiên 02/08/2026 (1) — `data_manifest.py` và bản kê máy lab

**Tóm tắt:** Viết `data_manifest.py` kiểm kê `data\` và `vendor\`, vendor chia hai khối canonical và extra; sinh `manifests/lab.json`; tự kiểm đủ ba mã thoát bằng đối chứng dương, đối chứng âm và ca thiếu file; đo lại thời gian hash khi cache lạnh và cache nóng; xoá Ưu tiên 1 khỏi `../TODO.md`
**Phiên:** 01:32 khuya

Máy lab. Không mở CapCut, không chạy lệnh CLI, không dựng project nào. Phiên trước là `2026-08-01-4-readme-cua-vao.md`.

## Quyết định về `vendor\` trước khi viết code

Mục nợ nhỏ ngày 01/08 đòi phải quyết hướng xử lý năm thư mục con của `vendor\` **trước khi** bản kê chốt danh sách loại trừ, vì bản kê đóng băng hiện trạng thành tiêu chuẩn. Ba hướng được đặt lên bàn: coi toàn bộ `vendor\` hiện tại là chuẩn, dọn trước rồi mới kê, hoặc kê đủ nhưng chia hai khối. Hướng một bị loại vì `_deprecated/pack_vendor.ps1` dùng robocopy nên kit bootstrap còn chứa mười một script đã dọn, ghi ở `../failures.md` mục 5; đóng băng nguyên trạng là phong cả phần đã cũ thành chuẩn. Hướng hai bị loại vì máy render đang offline nên không xác minh được việc dọn có phá parity không.

Chốt hướng ba. Bản kê ghi đủ mọi thứ dưới `vendor\` kèm kích thước và hash, nhưng chia làm hai khối: `vendor_canonical` gồm đúng những thứ mục 3 của `../START-HERE.md` kể ra và chỉ khối này tham gia phán xử mã thoát, còn `vendor_extra` gồm phần còn lại, vẫn lưu đủ bằng chứng nhưng chỉ in ra dạng thông tin. Người dùng xác nhận thêm một lý lẽ độc lập: `vendor\` hai máy chưa bao giờ đồng bộ, nên khối extra lệch nhau là chuyện bình thường và không được phép làm hỏng kết luận.

## Công cụ

`../../tools/data_manifest.py`, giao diện theo đúng luật của `../../tools/shots_crosscheck.py`: hai chế độ `--scan` và `--compare` tách rời, mọi tham số bắt buộc và tường minh, không một cơ chế tự dò đường dẫn nào. Mã thoát 0 sạch, 1 không chạy được, 2 có khác biệt; chế độ quét trả 2 khi có file đọc không được nên bản kê bị thủng, chế độ so trả 2 khi lệch ở phần phán xử hoặc khi một trong hai bản kê có lỗ — theo đúng tiền lệ "chưa đủ căn cứ tuyên bố sạch" của `shots_crosscheck.py`. Loại trừ `data\tmp\`, `data\archive\`, mọi thư mục tên `__pycache__` và `.git`. `vendor\Cache_effect` gộp thành một mục rollup có số file, tổng byte và một hash tổng hợp dựng từ danh sách đường dẫn, kích thước và hash từng file đã sắp xếp. Có xử lý đường dẫn dài bằng tiền tố mở rộng vì `LongPathsEnabled` trên máy lab vẫn bằng 0.

## Tên canonical phải lấy từ đĩa, không lấy từ tài liệu

Mục 3 của `../START-HERE.md` kể sáu thứ nhưng chỉ nêu tên chính xác của bốn. Thay vì đoán, công cụ khai báo danh sách rồi in bảng phân loại từng mục ở gốc `vendor\` kèm lý do, và in riêng danh sách canonical đã khai báo mà không thấy trên đĩa. Lần chạy thăm dò đầu tiên lộ ra ngay: bộ cài tên thật là `CapCut_9.1.0.3879_User_X64_exe_en-US.exe` chứ không phải tên trong URL tải, và nó đi kèm hai file cùng gốc `.sha256.txt` với `.yaml`. Sau khi sửa hằng số, cơ chế khớp theo mẫu `*.ps1` bị bỏ hẳn, thay bằng chín cái tên tường minh, để việc phân loại không còn mảy may suy đoán; hệ quả có chủ ý là script bootstrap mới thêm về sau sẽ rơi vào extra và hiện ra trong bảng thay vì lặng lẽ thành chuẩn.

## Số đo

`data\` 144 file 299,7 MB sau khi loại `tmp\` và `archive\`. `vendor_canonical` 9 mục 922,1 MB, `vendor_extra` 109 mục 39,4 MB, cộng lại khớp con số ~961 MB mà mục 3 ghi. `Cache_effect` rollup 14653 file 424842366 byte. `manifests/lab.json` 45260 byte.

Thời gian quét đủ 1261,3 MB có hash SHA256 toàn bộ: 125,0 giây ở lần đầu khi cache hệ điều hành lạnh, 19,6 giây ở lần thứ hai khi cache nóng, riêng `Cache_effect` là 121,8 giây so với 17,9 giây. Dự đoán 20 giây của phiên 01/08 (4) khớp trường hợp cache nóng; đã thêm đoạn Đính chính vào phiên đó. Phí mở file cho 14653 file nhỏ là có thật nhưng bị cache che gần hết.

## Tự kiểm ba mã thoát

Theo quy tắc bốn của `../failures.md`, script phá in ground truth ra trước rồi mới chạy phép so. Script dùng một lần ở `data\tmp\mutate_manifest.py` phá chín chỗ trên một bản sao: xoá hai mục `data`, thêm một mục giả, đổi kích thước một mục, đổi hash một mục giữ nguyên kích thước, xoá một mục canonical, làm lệch rollup, và xoá hai mục extra. Kết quả đúng dự đoán từng dòng: tổng phán xử 7 chứ không phải 9, hai mục extra hiện ở khối thông tin và nằm ngoài tổng, rollup báo đúng dạng 14653/14652 file, hai kiểu lệch của file phân biệt được rõ, mã thoát 2. Đối chứng âm so bản kê với chính nó trả 0 kèm cảnh báo cùng tên máy, chứng minh cảnh báo không tự nâng thành lỗi. Ca `--theirs` trỏ vào file không tồn tại trả 1.

Đối chứng âm cũng lộ một khuyết điểm trình bày: khi hai bản kê cùng tên máy, báo cáo in hai dòng nhãn giống hệt nhau. Đã vá bằng cách gắn hậu tố `/mine` và `/theirs` trong đúng trường hợp đó.

## Chuyện đọc tài liệu

Kích thước trên đĩa của ba file lệch với blob trên GitHub: `../STATE.md` +38, `2026-08-01-1-docs-headers.md` +50, `2026-08-01-4-readme-cua-vao.md` +32, trong khi `git status` sạch. Nguyên nhân là ba file này dùng CRLF trên đĩa còn repo lưu LF, phần lệch đúng bằng số dòng. Không mất chữ nào. Ghi lại vì phép đối chiếu độ dài sau mỗi lần fetch sẽ còn gặp lại, và ba con số này là dương tính giả.

Cũng ghi lại một lần nữa: công cụ fetch của phiên AI lược mất khúc giữa của `../TODO.md` và `../START-HERE.md` hai lần liên tiếp, đầu và đuôi vẫn nguyên nên nhìn như đã đọc đủ. Phần thiết kế của Ưu tiên 1 và mục 8 chỉ đọc được trọn vẹn khi người dùng dán thẳng nguyên văn vào phiên.

## Còn lại

Nghiệm thu hai máy chờ máy render, đã ghi thành mục có tiêu chí xong trong `../TODO.md`. Việc quyết dọn hay hợp thức hoá khối extra vẫn treo, nhưng không còn chặn ai vì hiện trạng đã được lưu đủ trong bản kê.