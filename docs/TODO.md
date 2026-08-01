Đã xử lý xong ngày 01/08/2026: khối chỉ dẫn vá lạc chỗ giữa `reference.md` đã được áp vào đúng mục và khối chỉ dẫn đã xoá. Không còn mảnh nào treo.
# TODO — việc chưa làm

**Cập nhật 01/08/2026.** Trần kích thước file này là **12 KB**, chật hơn trần chung, vì danh sách là thứ dễ phình nhất.

Luật ba file, đọc kèm `STATE.md`: file này chứa **thì tương lai**, tức mọi việc chưa làm kể cả nợ kỹ thuật, vì mỗi món nợ là một việc. `STATE.md` chứa **thì hiện tại đã đo được** và không được liệt kê việc phải làm. `research-log/` chứa **thì quá khứ**. Mỗi mục dưới đây phải có tiêu chí hoàn thành. **Xong thì xoá khỏi file này**, không đánh dấu hoàn thành rồi giữ lại — danh sách đã hoàn thành chính là research-log.

## Ưu tiên 1 — nợ chặn sản xuất

**Sửa `tools/shots_crosscheck.py`** thành bắt buộc nhận `--project` và `--csv` tường minh, bỏ hẳn cơ chế tự dò, in ở đầu báo cáo `draft_fold_path` và tên ảnh của shot 1. Tiêu chí xong: chạy trên `prod60` cho 0 lệch trên cả năm trường.

**Gộp `tools/fix_fold_path.py` vào `scripts_v1/clone_project.py`** để bớt một bước tay dễ quên. Tiêu chí xong: clone xong là `draft_fold_path` đã đúng, kiểm bằng chính script cũ.

**Viết `tools/data_manifest.py`** kiểm kê `data\` và `vendor\` ra bản kê có kích thước và hash, commit bản kê vào repo. Tiêu chí xong: chạy trên máy lab in ra đúng danh sách những thứ đang thiếu so với máy render.

## Ưu tiên 2 — công cụ và test

Thả tay một filter **free** trong GUI để có đối chứng dương, rồi vá `tools/v4_mold.py`: đường dẫn ghi ra phải là `molds/capcut-9.1.0/filter.json`, thêm khối `_meta`, mặc định chỉ diff chứ không ghi đè, và khi diff phải phân loại trường — `path` cùng `target_timerange.duration` phụ thuộc máy và project nên được phép khác, các trường còn lại bắt buộc khớp. Đang bị chặn vì hiện không project nào còn material `type=filter`.

Viết `tools/shots_dump.py` đọc ngược `draft_content.json` ra `shots.csv` rồi kiểm khứ hồi; hạt giống là `tools/shots_crosscheck.py`. Việc này đứng trước việc viết test vì `shots.csv` là hợp đồng đầu vào của `pipeline/`.

Ba test đầu tiên trong `tests/`: lượng tử hoá frame, công thức lề dạng tổng quát KX KY, khứ hồi `shots.csv`.

`run.bat` thật, rồi bắt đầu viết code trong `pipeline/`.

## Nợ nhỏ, làm khi tiện

`tools/bench_shots.py` kiểm biên trước khi làm tròn; phải đảo thành làm tròn rồi mới kiểm và kẹp, giống `tools/bench_fixkb.py`. Ưu tiên thấp vì `tools/prod_shots.py` đã thay nó.

`preflight.py` lỗi thời ba chỗ, xem `failures.md` mục 6. Cân nhắc bỏ hẳn thay vì vá.

`tools/oracle_read.py` còn mặc định `CAPCUT_LAB` là đường dẫn cũ `D:\Test_tool`; sửa thành mặc định giống các công cụ khác. Ngoài ra bảng delta của nó so với một mốc cứng 8 shot của bộ test v3, chạy trên project khác thì cột delta vô nghĩa — hoặc nhận mốc qua tham số, hoặc in cảnh báo.

`tools/bgblur_diag.py`, `tools/bgblur_frames.py` và `tools/frame_audit.py` cứng tên project `bench300`; cho nhận tên project qua tham số dòng lệnh.

`docs/scripts.md` đang 18,2 KB, tức 70 phần trăm trần 26 KB, với 38 script đang dùng. Khi chạm trần thì tách bảng kho lưu trữ sang `docs/scripts-archive.md` và cập nhật `tools/scripts_index.py` cho ghi hai file.

Bổ sung một dòng cho `split_research_log.py` vào `_deprecated/README.md`, file này chuyển vào kho lưu trữ ngày 01/08/2026 vì nguồn của nó đã bị xoá sau khi tách nhật ký.

Dời `scan_paths.py` từ thư mục mẹ `capcut-lab\` vào `data\tmp\`, vì thư mục mẹ chỉ được chứa đúng ba nhánh.

Xoá `data\archive\`, khoảng 60–70 MB rác, sau khi chắc chắn `D:\Test_tool` đã bỏ.

`data\Test_tool_v3\shots.csv` rỗng 0 byte, là file giữ chỗ; xoá hoặc điền theo lược đồ thật khi `tools/shots_dump.py` chốt xong.

Điều kiện bật blur trong `tools/prod_shots.py` là `kx*smin < 1 or ky*smin < 1`, mà `S_HI` bằng 0,92 còn `kx` và `ky` không bao giờ vượt 1, nên vế trái luôn đúng và cột `blur` bằng 3 ở mọi shot. Hoặc thừa nhận blur luôn bật rồi bỏ điều kiện cho khỏi gây hiểu nhầm, hoặc đặt một ngưỡng thật. Suy luận từ mã, **chưa kiểm chứng** bằng cách đếm cột blur trên bảng shot đã sinh.

## Chờ máy render quay lại

Nghiệm thu KX và KY. Dựng lại `prod60` bằng `tools/prod_shots.py` mới rồi trích khung ở giữa mười shot có tỉ lệ ảnh khác nhau, **bắt buộc có ít nhất hai ảnh cao hơn khung 16:9**, vì nhánh ảnh cao trong `reference.md` mục 3.1 chưa có phép đo oracle nào. Tiêu chí xong: không shot nào hở mép ngoài ý muốn. Lớp Python đã hoàn tất và đã tự kiểm trên dữ liệu tổng hợp ngày 01/08/2026, phần còn thiếu duy nhất là mắt người nhìn khung hình thật.

Chạy lại đối chiếu CSV với JSON cho `prod60` sau khi sửa `shots_crosscheck.py`.

Kiểm thị giác bản export `prod60` theo quy tắc in ground truth trước khi nhìn, ở `failures.md` mục 1.

Đo độ nới thực tế của segment audio trên `prod60`; lý thuyết dự đoán +10,5 ms, **chưa kiểm chứng**.

Kéo về máy lab hai thứ không tái tạo được: file `narration59.mp3` và thư mục 326 ảnh gốc ở `D:\IT\capcut-help\Picture`.

## Mảnh nội dung cần bảo toàn

Đã xử lý xong ngày 01/08/2026: khối chỉ dẫn vá lạc chỗ giữa `reference.md` đã được áp vào đúng mục và khối chỉ dẫn đã xoá. Không còn mảnh nào treo.