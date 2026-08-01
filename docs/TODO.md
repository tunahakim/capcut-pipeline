# TODO — việc chưa làm

**Cập nhật 01/08/2026.** Trần kích thước file này là **12 KB**, chật hơn trần chung, vì danh sách là thứ dễ phình nhất.

Luật ba file, đọc kèm `STATE.md`: file này chứa **thì tương lai**, tức mọi việc chưa làm kể cả nợ kỹ thuật, vì mỗi món nợ là một việc. `STATE.md` chứa **thì hiện tại đã đo được** và không được liệt kê việc phải làm. `research-log/` chứa **thì quá khứ**. Mỗi mục dưới đây phải có tiêu chí hoàn thành. **Xong thì xoá khỏi file này**, không đánh dấu hoàn thành rồi giữ lại — danh sách đã hoàn thành chính là research-log.

## Ưu tiên 0 — dọn tài liệu, phần còn lại

Chạy `python tools/docs_audit.py --compare` và sửa hết liên kết chết còn lại. Tiêu chí xong: mục `VAN DE` chỉ còn các mục nằm trong danh sách trắng của chính công cụ, rồi chạy `--baseline` để đặt mốc chuẩn mới.

Điền cột mô tả của `docs/scripts.md`, hiện trống toàn bộ, và bổ sung các hàng còn thiếu gồm `tools/bulk_build.py`, `tools/prod_shots.py`, `tools/audio_prep.py`, `tools/img_scan.py`, `tools/timing_snap.py`, `tools/shots_crosscheck.py`, `tools/fix_fold_path.py`, `tools/bgblur_diag.py`, `tools/bgblur_frames.py`, `tools/docs_audit.py`, `tools/split_research_log.py`. Tiêu chí xong: mọi file trong `scripts_v1/` và `tools/` đều có đúng một hàng và một câu mô tả.

Viết `artifacts/README.md`, mỗi file một dòng nói rõ phiên nào sinh ra và nhật ký nào mô tả nó. Cập nhật `fixtures/README.md` cho khớp thực tế.

## Ưu tiên 1 — nợ chặn sản xuất

**Tổng quát hoá hình học sang KX và KY theo từng ảnh.** Công thức đã có ở `reference.md` mục 3.1. Việc cần làm: `tools/img_scan.py` ghi thêm hai cột `kx` và `ky` cho từng ảnh, `tools/prod_shots.py` mang chúng vào `shots.csv`, `scripts_v1/kb_apply.py` và `tools/bench_kb.py` đọc từ CSV thay vì dùng một hằng số chung. Tiêu chí xong: dựng lại `prod60`, trích khung ở giữa mười shot có tỉ lệ ảnh khác nhau, không shot nào hở mép ngoài ý muốn.

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

Dời `scan_paths.py` từ thư mục mẹ `capcut-lab\` vào `data\tmp\`, vì thư mục mẹ chỉ được chứa đúng ba nhánh.

Xoá `data\archive\`, khoảng 60–70 MB rác, sau khi chắc chắn `D:\Test_tool` đã bỏ.

`data\Test_tool_v3\shots.csv` rỗng 0 byte, là file giữ chỗ; xoá hoặc điền theo lược đồ thật khi `tools/shots_dump.py` chốt xong.

## Chờ máy render quay lại

Chạy lại đối chiếu CSV với JSON cho `prod60` sau khi sửa `shots_crosscheck.py`.

Kiểm thị giác bản export `prod60` theo quy tắc in ground truth trước khi nhìn, ở `failures.md` mục 1.

Đo độ nới thực tế của segment audio trên `prod60`; lý thuyết dự đoán +10,5 ms, **chưa kiểm chứng**.

Kéo về máy lab hai thứ không tái tạo được: file `narration59.mp3` và thư mục 326 ảnh gốc ở `D:\IT\capcut-help\Picture`.

## Mảnh nội dung cần bảo toàn

Đã xử lý xong ngày 01/08/2026: khối chỉ dẫn vá lạc chỗ giữa `reference.md` đã được áp vào đúng mục và khối chỉ dẫn đã xoá. Không còn mảnh nào treo.