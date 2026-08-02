# TODO — việc chưa làm

**Cập nhật 01/08/2026.** Trần kích thước file này là **12 KB**, chật hơn trần chung, vì danh sách là thứ dễ phình nhất.

Luật ba file, đọc kèm `STATE.md`: file này chứa **thì tương lai**, tức mọi việc chưa làm kể cả nợ kỹ thuật, vì mỗi món nợ là một việc. `STATE.md` chứa **thì hiện tại đã đo được** và không được liệt kê việc phải làm. `research-log/` chứa **thì quá khứ**. Mỗi mục dưới đây phải có tiêu chí hoàn thành. **Xong thì xoá khỏi file này**, không đánh dấu hoàn thành rồi giữ lại — danh sách đã hoàn thành chính là research-log.

## Ưu tiên 2 — công cụ và test

Vá `tools/v4_mold.py`: đường dẫn ghi ra phải là `molds/capcut-9.1.0/filter.json`, thêm khối `_meta`, mặc định chỉ diff chứ không ghi đè, và khi diff phải phân loại trường — `path` cùng `target_timerange.duration` phụ thuộc máy và project nên được phép khác, các trường còn lại bắt buộc khớp. **Đã gỡ chặn 02/08/2026**: project `fxprobe01` có hai material `type=filter` thả tay từ GUI, nằm ở bucket `materials.effects`. Phải quyết trước khi viết code: `molds/capcut-9.1.0/filter.json` đã tồn tại 3218 byte, chụp từ `testV4` filter Film, và đang là nền của `scripts_v1/filter_apply.py`; hoặc thêm nhóm trường thứ ba là định danh được phép khác, hoặc ghi khuôn mới ra tên khác. Tiêu chí xong: chụp được khuôn, chạy lần hai trên cùng project cho diff sạch, cố ý sửa một trường bắt buộc khớp thì diff bắt được.

**Kiểm khoá Pro cho mọi loại tài nguyên.** `failures.md` mục 1: `fx_audit.py` chỉ chứng minh `path` trỏ tới file có thật, **không bắt được khoá Pro**, nên tài nguyên Pro lọt vào bản dựng chỉ lộ ở bản export cuối. **Chặn vì phương pháp, đo 02/08/2026**: filter trong GUI CapCut quốc tế là namespace khác hẳn 468 mục JianYing, `resource_id` không trùng và `is_vip` không dự đoán được vương miện, nên **chưa tạo được đối chứng dương bằng filter**. Phần còn làm được ngay: đọc cờ VIP của scene-effect, image-intro, image-outro, image-combo từ `capcut enums` rồi ghi vào `reference-catalog.md`; nếu loại nào không có cờ thì ghi rõ là chưa kiểm chứng. Tiêu chí xong cho phần này: bốn con số nằm trong `reference-catalog.md`. Phần `fx_audit.py` báo đỏ phải chờ tìm được một tài nguyên Pro thật làm đối chứng dương, ở loại khác filter hoặc bằng cách liệt kê được catalogue thật của GUI.

Viết `tools/shots_dump.py` đọc ngược `draft_content.json` ra `shots.csv` rồi kiểm khứ hồi; hạt giống là `tools/shots_crosscheck.py`, và giao diện phải theo cùng một luật với nó là bắt buộc `--project` cùng đường dẫn ra tường minh, không tự dò. Việc này đứng trước việc viết test vì `shots.csv` là hợp đồng đầu vào của `pipeline/`. Nguyên mẫu nằm ngoài repo: `data\tmp\gen_cc_fixture.py` trên máy lab đã đọc ngược `draft_content.json` ra bảng shot; dùng lại thay vì viết từ đầu, và chép vào `tools/` một cách có ý thức.

Ba test đầu tiên trong `tests/`: lượng tử hoá frame, công thức lề dạng tổng quát KX KY, khứ hồi `shots.csv`.

**`run.bat` thật cộng khung `pipeline/`, và nối `config.json` vào đường chạy.** Đây là tính năng đích của cả dự án: người dùng sửa đường dẫn trong một file cấu hình rồi gọi một lệnh, không gõ thêm lệnh nào. Hiện `config.example.json` đã nằm trong repo nhưng chưa có mã nào đọc nó, và trình tự chạy vẫn chỉ tồn tại trong `docs/procedures.md` dưới dạng văn xuôi chứ không phải mã. Ba phần: đưa trình tự đã dựng thành công `prod60` thành mã có kiểm điều kiện trước và sau mỗi khâu; đọc mọi đường dẫn từ `config.json`; dừng sạch kèm thông báo đọc được khi một khâu hỏng thay vì chạy tiếp. Tiêu chí xong: trên một máy đã cài đủ, chép `config.example.json` thành `config.json`, điền đường dẫn tới thư mục ảnh, file narration, file SRT và bảng shot, chạy một lệnh duy nhất, rồi mở được project trong CapCut với `fx_audit` báo `OK` toàn bộ và lệch timing 0,0 ms, không gõ thêm lệnh nào ở giữa.

## Nợ nhỏ, làm khi tiện

Xoá project rỗng `fxlab01` trong thư mục draft; nó không chứa gì và không tài liệu nào giải thích.

Thêm cờ `--brief` cho `tools/docs_audit.py`: chỉ in TONG QUAN, VAN DE, SO VOI MOC CHUAN, bỏ ma trận tham chiếu.

Viết hướng dẫn dựng lại máy mới từ bản clone repo: cây ba nhánh phải tạo, biến `CAPCUT_LAB`, lấy `data\scaffold\` và `vendor\` từ đâu. `tools/data_manifest.py` đã là một nửa cơ chế.

Thống nhất giao diện tham số nhóm `scripts_v1` cũ; `clone_project.py` nhận ba tham số vị trí, gõ `--help` thì chết bằng `IndexError`.

Thử áp filter thẳng vào clip bằng CLI hoặc Python thay vì tạo segment trên track filter riêng; GUI cho phép cả hai kiểu.

Project `testB` có `materials.hsl` một mục, không project nào khác có và chưa tài liệu nào nhắc.

`tools/bench_shots.py` kiểm biên trước khi làm tròn; phải đảo thành làm tròn rồi mới kiểm và kẹp, giống `tools/bench_fixkb.py`. Ưu tiên thấp vì `tools/prod_shots.py` đã thay nó.

`preflight.py` lỗi thời ba chỗ, xem `failures.md` mục 6. Cân nhắc bỏ hẳn thay vì vá.

`docs/scripts.md` đang tiến dần tới trần 26 KB; số hiện hành lấy bằng `python tools/docs_audit.py` chứ không chép vào đây. Khi chạm trần thì tách bảng kho lưu trữ sang `docs/scripts-archive.md` và cập nhật `tools/scripts_index.py` cho ghi hai file.

Ba script `tools/bgblur_diag.py`, `tools/bgblur_frames.py` và `tools/frame_audit.py` đã nhận project qua tham số từ 02/08/2026 nhưng mới chạy thử trên `testV3` và `paritytest`; `frame_audit.py` chưa chạy lần nào ngoài `--help` vì máy lab không có bản MP4 nào khớp project đang có. Nghiệm thu đủ khi có bản export ở máy render. Tiêu chí xong: mỗi script chạy trọn một lần trên project có đủ mẫu blur và in ra bảng không rỗng.

Xoá `data\archive\`, khoảng 60–70 MB rác, sau khi chắc chắn `D:\Test_tool` đã bỏ.

`data\Test_tool_v3\shots.csv` **trên máy lab**, nằm ngoài repo, không rỗng 0 byte như từng ghi ở đây mà có 8 dòng thật theo lược đồ `file,start,end`, tức lược đồ cũ của bộ test v3 chứ không phải lược đồ bảng shot hiện hành; nó thiếu `start_s`, `dur_s`, `transition`, `blur`, `kb_s0` và `kb_s1` nên `tools/shots_crosscheck.py` không dùng được nó. Xoá hoặc điền lại theo lược đồ thật khi `tools/shots_dump.py` chốt xong.

Điều kiện bật blur trong `tools/prod_shots.py` là `kx*smin < 1 or ky*smin < 1`, mà `S_HI` bằng 0,92 còn `kx` và `ky` không bao giờ vượt 1, nên vế trái luôn đúng và cột `blur` bằng 3 ở mọi shot. Hoặc thừa nhận blur luôn bật rồi bỏ điều kiện cho khỏi gây hiểu nhầm, hoặc đặt một ngưỡng thật. Suy luận từ mã, **chưa kiểm chứng** bằng cách đếm cột blur trên bảng shot đã sinh.

`vendor\` **trên máy lab** chứa năm thư mục con mà mục 3 của `START-HERE.md` không kể tới: `frames`, `Test_tool_v3`, `snapshots`, `testV3_CLEAN` và `scripts`; ba trong số đó trùng tên với thư mục con của `data\`. Gốc `vendor\` còn có `enums_backup.json` trùng bản với `reference/enums_backup.json` đã nằm trong repo. Từ 02/08/2026 `tools/data_manifest.py` ghi đủ những mục này vào khối `vendor_extra` của bản kê, có kích thước và hash, nhưng khối đó không tham gia phán xử mã thoát, nên hiện trạng được lưu lại làm bằng chứng mà chưa bị phong thành tiêu chuẩn. Phần còn treo là quyết dọn hay hợp thức hoá: dọn thì chuyển dữ liệu làm việc về `data\` rồi xoá khỏi `vendor\`, hợp thức hoá thì viết lại mục 3 của `START-HERE.md` và thêm tên tương ứng vào hằng số `CANON_VENDOR_NAMES`. Tiêu chí xong: khối `vendor_extra` chỉ còn đúng những thứ ta cố ý chấp nhận, và mục 3 kể đúng những gì có thật trên đĩa.

## Chờ máy render quay lại

Nghiệm thu KX và KY. Dựng lại `prod60` bằng `tools/prod_shots.py` mới rồi trích khung ở giữa mười shot có tỉ lệ ảnh khác nhau, **bắt buộc có ít nhất hai ảnh cao hơn khung 16:9**, vì nhánh ảnh cao trong `reference.md` mục 3.1 chưa có phép đo oracle nào. Tiêu chí xong: không shot nào hở mép ngoài ý muốn. Lớp Python đã hoàn tất và đã tự kiểm trên dữ liệu tổng hợp ngày 01/08/2026, phần còn thiếu duy nhất là mắt người nhìn khung hình thật.

Đối chiếu CSV với JSON cho `prod60` bằng `tools/shots_crosscheck.py` đã đổi giao diện ngày 01/08/2026. Việc này chạy **trên máy render**, vì cả thư mục draft chứa `prod60` lẫn bảng shot của nó đều chỉ tồn tại ở đó và không nằm trong repo; máy lab không có bản sao nào. Chạy `python tools/shots_crosscheck.py --project prod60 --csv <đường dẫn thật tới shots.csv của prod60 trên máy render>`; công cụ nay bắt buộc cả hai tham số và không còn cơ chế tự dò, nên gọi thiếu sẽ hỏng ngay chứ không âm thầm đối chiếu nhầm project. Năm dòng đầu báo cáo in `draft_fold_path`, kích thước `draft_content.json` gốc so với bản lồng trong `Timelines\`, và tên ảnh shot 1 ở cả hai phía — đọc năm dòng đó trước, nếu tên ảnh shot 1 lệch thì dừng luôn vì đang so nhầm cặp. Tiêu chí xong: mã thoát 0 kèm dòng "SACH, 0 lech tren ca nam truong". Mã thoát 2 kèm dòng báo thiếu cột `kb_s0` và `kb_s1` **không** được coi là đạt, vì khi đó trường thứ năm chưa hề được kiểm; gặp ca đó thì sinh lại bảng shot bằng `tools/prod_shots.py` rồi chạy lại.

Kiểm thị giác bản export `prod60` theo quy tắc in ground truth trước khi nhìn, ở `failures.md` mục 1.

Đo độ nới thực tế của segment audio trên `prod60`; lý thuyết dự đoán +10,5 ms, **chưa kiểm chứng**.

Kéo về máy lab hai thứ không tái tạo được: file `narration59.mp3` và thư mục 326 ảnh gốc ở `D:\IT\capcut-help\Picture`.

Nghiệm thu `tools/data_manifest.py` giữa hai máy, phần bị chặn còn lại của việc đã làm ngày 02/08/2026. Trên máy render chạy `python tools/data_manifest.py --scan --machine render --data <data trên máy render> --vendor <vendor trên máy render> --out manifests/render.json` rồi commit bản kê; sau đó chạy `python tools/data_manifest.py --compare --mine manifests/lab.json --theirs manifests/render.json`. Tiêu chí xong: báo cáo in ra đúng danh sách những thứ máy lab thiếu so với máy render và ngược lại; mã thoát 0 hoặc 2 đều chấp nhận được miễn là mọi dòng lệch giải thích được, còn mã thoát 1 nghĩa là chưa chạy được. Lưu ý khối `vendor_extra` chắc chắn lệch nhiều và đó là bình thường vì `vendor\` hai máy chưa bao giờ đồng bộ; chỉ `data` và `vendor_canonical` mới đáng xử lý.
