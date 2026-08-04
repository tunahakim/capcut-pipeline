# Nhật ký phiên 01/08/2026 (3) — giao diện tường minh cho `shots_crosscheck` và gộp `fix_fold_path`

**Tóm tắt:** `shots_crosscheck.py` bắt buộc `--project` và `--csv`, bỏ tự dò, thêm đầu báo cáo và hợp đồng mã thoát, bịt lỗi im lặng cột `kb`; tự kiểm ba bộ trên `testV3` khớp dự đoán; gộp `fix_fold_path.py` vào `clone_project.py`

Máy lab. Không dựng project sản xuất, không export. Hai phiên trước trong cùng ngày nằm ở nhật ký (1) và (2).

## Vì sao phải sửa `tools/shots_crosscheck.py`

Đọc mã trước khi sửa, phát hiện ba thứ. Project nhắm cứng là `bench300`, một cái tên **không tồn tại** trong thư mục draft của máy lab. Hàm `find_csvs()` quét đệ quy cả `D:\IT\capcut-lab` trên máy lab, tức bao gồm cả thư mục repo, rồi chọn file CSV đầu tiên có số dòng trùng số segment; bất kỳ file lạc nào cũng thành ứng viên hợp lệ. Và cặp cột `kb_s0`, `kb_s1` được đọc trong `try` với `except KeyError` bỏ qua lặng lẽ, nên một bảng shot thiếu hai cột đó vẫn cho ra dòng `lech kb : 0` — trường thứ năm không hề được kiểm mà báo cáo trông như đã kiểm. Đây là một lỗi im lặng cùng họ với bảy ca trong `failures.md`, chưa từng được ghi nhận.

## Bản vá, hai lượt

Lượt một, chín neo: đổi docstring, thêm `argparse` với `--project` và `--csv` bắt buộc, xoá `find_csvs()` cùng hằng `PROJ` và `LAB`, thêm `resolve_project()` in danh sách project đang có khi tra không thấy, thêm `fold_path()` và `nested_report()`, in đầu báo cáo gồm `draft_fold_path`, kích thước `draft_content.json` gốc so với bản lồng trong `Timelines\` và tên ảnh shot 1 ở cả hai phía, kiểm cột bắt buộc và dừng nếu thiếu, báo `KHONG CO COT` khi vắng cặp cột keyframe, và in kết luận kèm mã thoát.

Lượt hai, năm neo: `argparse` mặc định thoát bằng 2 khi thiếu tham số bắt buộc, đúng mã đã dành cho "chạy xong nhưng có lệch", nên thêm lớp con `ArgParser` thoát bằng 1; đổi tên biến `a` của `parse_args` thành `args` vì `a` bị dùng lại làm biến vòng lặp ở đoạn in bản đồ; và thay `LEVELS.get(lv, "??")` bằng nhánh tường minh, vì mức blur ngoài thang 0 tới 4 sẽ làm `abs("??" - 0.75)` ném `TypeError` giữa chừng.

Hợp đồng mã thoát chốt lại: 0 là sạch cả năm trường, 1 là không chạy được vì sai tham số hoặc thiếu file, 2 là chạy xong nhưng dữ liệu có vấn đề gồm có lệch, lệch số dòng, hoặc thiếu cột keyframe.

## Tự kiểm trên `testV3`, tám shot

Bộ dữ liệu sinh bằng `D:\IT\capcut-lab\data\tmp\gen_cc_fixture.py` trên **máy lab**, ngoài repo, đọc ngược `draft_content.json` của `testV3` bằng chính các hàm của công cụ. Ba bộ: bản sạch, bản gieo sáu hạt lỗi, bản cụt một dòng. Ground truth in ra trước khi nhìn báo cáo, theo quy tắc bốn ở `failures.md` mục 1.

Kết quả khớp cả ba. Bản sạch cho mã thoát 0. Bản gieo lỗi cho mã thoát 2 với phân bố đúng như dự đoán: lệch start 1, dur 1, blur 2, img 1, kb 1, tổng 6; hạt blur mức 9 rơi vào nhánh `MUC BLUR NGOAI THANG 0..4` thay vì ném ngoại lệ. Bản cụt cho mã thoát 2 kèm dòng `SO DONG KHONG KHOP` và không crash, xác nhận bằng thực nghiệm điều trước đó mới chỉ là suy luận từ việc vòng đối chiếu dùng `zip`.

Hai số đo phụ thu được: `draft_fold_path` của `testV3` ghi bằng dấu gạch chéo **xuôi** vì do chính CapCut tạo, còn bản `draft_content.json` lồng trong `Timelines\B88C067B-9DC3-40b8-ABB3-E9505DF69A04` trùng khít 74061 byte với bản gốc.

**Giới hạn bằng chứng, đọc kỹ trước khi trích dẫn phiên này.** Vì CSV sinh ngược từ chính JSON bằng chính các hàm của công cụ, phép kiểm này chỉ chứng minh đường ống chạy và bộ so sánh biết phát hiện khác biệt. Nó **không** chứng minh ngữ nghĩa năm trường khớp với bảng shot do `tools/prod_shots.py` sinh thật. Nghiệm thu thật là chạy trên `prod60` ở **máy render**, chưa làm, đang xếp hàng trong `../TODO.md`.

## Gộp `tools/fix_fold_path.py` vào `scripts_v1/clone_project.py`

`clone_project.py` nay đặt `draft_fold_path` bằng `str(DST.resolve())` ngay trong bước đặt lại dấu thời gian và `draft_name`, rồi in giá trị đó kèm cờ `KHOP` ở báo cáo cuối. Chọn dạng đường dẫn có gạch chéo **ngược** là cố ý, để trùng đúng thứ `fix_fold_path.py` vẫn ghi; nếu đổi sang gạch chéo xuôi cho giống CapCut thì script cũ sẽ báo lệch và ta mất luôn phép kiểm chứng độc lập.

Kiểm chứng: clone `testB_CLEAN` thành `foldtest` trong thư mục draft của **máy lab**, báo cáo in `draft_fold_path ... -> KHOP`, rồi `fix_fold_path.py` chạy trên chính thư mục đó in `da sua : False` với giá trị trước và sau giống nhau. Đã xoá `foldtest`. `fix_fold_path.py` được giữ lại, chỉ đổi docstring, vì nó vẫn là công cụ duy nhất sửa được project bị dời bằng tay.

Ghi nhận một sai sót quy trình: khối lệnh thử clone chạy trong lúc CapCut đang mở sáu tiến trình. Lệnh `Get-Process *CapCut*` đầu khối đã báo, nhưng không ai dừng lại. Kết quả vẫn sạch, không nên lặp lại.