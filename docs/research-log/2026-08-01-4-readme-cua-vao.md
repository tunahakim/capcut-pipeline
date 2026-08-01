# Nhật ký phiên 01/08/2026 (4) — README thành cửa vào, và đo quy mô `data\` cùng `vendor\`

Máy lab. Không dựng project, không export, không chạy lệnh CLI nào. Ba phiên trước trong cùng ngày ở nhật ký (1), (2) và (3).

## Vì sao đụng tới README

Người dùng nêu một quan sát: mọi phiên AI trước đều bỏ qua `../../README.md` dù ý đồ ban đầu là AI đọc README rồi mới sang `../START-HERE.md`. Đọc lại thì thấy README đã mục ở đúng những câu **chép lại nội dung file khác**. Nó nói START-HERE chứa trạng thái bàn giao và "danh sách sáu loại lỗi im lặng", trong khi trạng thái đã dời sang `../STATE.md` từ 30/07 và mục 7 của START-HERE cố ý không chứa danh sách đó, còn `../failures.md` nay có tám mục. Nó ghi `tools/` có 10 script trong khi cây git cho 25; con số 13 của `scripts_v1/` thì vẫn đúng. Nó không nhắc `../STATE.md`, `../TODO.md` hay thư mục nhật ký một chữ nào, tức luật ba file vắng mặt hoàn toàn ở cửa vào.

Xác định được ba nguyên nhân. Prompt mở phiên của người dùng liệt kê thứ tự đọc mà không có README. Mục 5 của START-HERE vẽ bản đồ chỉ gồm cây `docs/` và ghi thứ tự "file này, rồi STATE.md, rồi reference.md, rồi failures.md", không có README. Và README nằm ở gốc repo trong khi mọi ví dụ đường dẫn fetch đều trỏ vào `docs/`. Một giả thuyết thứ tư **đã bị bác bỏ**: `../../tools/docs_audit.py` có loại trừ cứng README khỏi phép tìm file mồ côi, nhưng ma trận tham chiếu cho thấy README vốn đã được ba file trỏ tới nên loại trừ đó không che gì; việc gỡ nó hạ xuống nợ nhỏ.

## Bản vá

README viết lại theo nguyên tắc cắt bớt chứ không thêm vào: bỏ mọi câu mô tả nội dung file khác, bỏ mọi con số đếm được bằng máy, bỏ danh sách thư viện chuẩn vì nó đã thiếu `argparse` và `datetime` mà không công cụ nào kiểm được, bỏ chữ "mười lăm phút" ở quy trình probe vì chưa xác minh. Giữ và mở rộng phần nó thật sự sở hữu là trần kích thước tài liệu cùng luật xử lý khi công cụ fetch cắt nội dung. Kết quả 6848 byte, gần bằng bản cũ 6752 byte; dự đoán trước khi sửa là khoảng 4,3 KB nên **dự đoán sai**, phần luật đọc viết dài hơn tính toán.

START-HERE sửa ba chỗ: đoạn mở đầu bỏ bản sao thứ hai của thứ tự đọc và trỏ về mục 5; mục 5 viết lại, đưa README vào bản đồ và lên đầu thứ tự đọc, bổ sung `../TODO.md` cùng thư mục nhật ký vốn có trong bản đồ nhưng thiếu trong thứ tự, và ghi luật ba file ở dạng cô đọng; mục 8 chèn một đoạn buộc AI khai báo lỗ hổng đọc trước khi đề xuất bản vá. Sau khi vá, đồ thị điều hướng thành hai chiều: README trỏ ra 5 chỗ, START-HERE trỏ ngược về README 4 lần, `docs_audit` báo 0 vấn đề và 0 file mồ côi.

## Hai lớp mất chữ của công cụ fetch

Cả hai đều làm kết quả trông như đã đọc đủ. Lớp một: chế độ đọc thô chặn cứng ở 10000 byte, và lần xin phần đuôi tiếp theo trả lời rằng file đã hết. Lớp hai, nặng hơn: nội dung bị lược mất **khúc giữa sau khi fetch đã xong**, đầu và đuôi còn nguyên. Cả tám file tài liệu đọc trong phiên đều thủng khúc giữa; `../../README.md` mất 3768 trên 6752 byte, `../START-HERE.md` mất 10118 trên 14724 byte.

Bắt được lớp một là nhờ một câu **sai** trong README quảng cáo START-HERE có "danh sách sáu loại lỗi im lặng" mà bản đọc được không có mục nào như vậy — một tham chiếu chéo lỗi thời vô tình làm chuông báo. Bắt được lớp hai là nhờ đối chiếu kích thước nhận được với kích thước thật lấy từ `docs_audit` và từ git tree API. Luật rút ra, đã ghi vào README và mục 8 của START-HERE: sau mỗi lần fetch phải đối chiếu độ dài với kích thước thật, không viết nội dung thay thế cho file mình không có nguyên văn, và không kết luận một hàm hay một câu không tồn tại chỉ vì mình không nhìn thấy nó.

## Đo quy mô `data\` và `vendor\` trên máy lab

Chuẩn bị cho `tools/data_manifest.py`. Script thăm dò dùng một lần ở `data\tmp\dm_probe.py`, chỉ đọc, không ghi file nào.

`data\` 364 file 353,1 MB: `exports` 258,4 MB trong 3 file, `archive` 53,8 MB trong 205 file, `frames` 28,5 MB, `Test_tool_v3` 9,8 MB, `perf` 2,0 MB, phần còn lại dưới 0,3 MB. `vendor\` 14770 file 961,6 MB: 9 file ở thư mục gốc chiếm 517,7 MB trong đó riêng bộ cài 516,5 MB, `Cache_effect` 405,2 MB trong 14653 file, `frames` 28,5 MB, `Test_tool_v3` 9,8 MB, phần còn lại dưới 0,2 MB.

Không có đường dẫn nào dài quá 240 ký tự trên cả hai nhánh, nên `LongPathsEnabled` bằng 0 chưa gây rủi ro cho phép quét. Hai tên file chứa dấu tiếng Việt, cả hai nằm trong `data\archive\docs-older\`.

Đọc tuần tự file lớn nhất đạt 65,2 MB/s, suy ra hash toàn bộ 1315 MB mất khoảng 20 giây, nên **không cần cơ chế cache hash**. Con số này chỉ đúng cho file lớn, chưa tính phí mở file cho 14653 file nhỏ, nên tổng thời gian thật **chưa kiểm chứng**.

Phát hiện ngoài dự kiến: `vendor\` chứa năm thư mục con mà mục 3 của `../START-HERE.md` không kể tới, ba trong số đó trùng tên với thư mục con của `data\`. Đã ghi thành một mục nợ nhỏ trong `../TODO.md`, chưa quyết hướng xử lý.
## Đính chính ngày 02/08/2026

Hai chỗ trong phiên này đã được đo lại ở phiên `2026-08-02-1-data-manifest.md` và phải đọc kèm. Dự đoán "hash toàn bộ mất khoảng 20 giây" chỉ đúng khi cache hệ điều hành đã nóng: đo thật trên 1261,3 MB cho 125,0 giây ở lần quét đầu với cache lạnh, tức 10,1 MB/s, rồi 19,6 giây ở lần quét ngay sau đó, tức 64,2 MB/s; riêng `Cache_effect` chiếm 121,8 giây lạnh và 17,9 giây nóng cho 14653 file. Kết luận **không cần cơ chế cache hash** vẫn giữ nguyên, nhưng giá đúng là hai phút cho lần quét nguội chứ không phải hai mươi giây.

Tên thật của bộ cài trong `vendor\` là `CapCut_9.1.0.3879_User_X64_exe_en-US.exe`, đi kèm `CapCut_9.1.0.3879.sha256.txt` và `CapCut_9.1.0.3879_User_X64_exe_en-US.yaml`, không phải cái tên trong URL tải mà mục 3 của `../START-HERE.md` dẫn. Ba file đó nay nằm trong khối canonical của bản kê.