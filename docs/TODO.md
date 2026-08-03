# TODO — việc chưa làm

**Cập nhật 03/08/2026.** Trần file này là **12 KB**, chật hơn trần chung, vì danh sách là thứ dễ phình nhất; trần này chống phình, không liên quan tới fetch — xem `ai-reading-channel.md`.

Luật ba file: file này là **thì tương lai**, gồm mọi việc chưa làm kể cả nợ kỹ thuật; `STATE.md` là **thì hiện tại đã đo được**; `research-log/` là **thì quá khứ**. Mỗi mục phải có tiêu chí hoàn thành, và **xong thì xoá khỏi file này** chứ không đánh dấu rồi giữ lại.

## Ưu tiên 1 — đóng gói thành ứng dụng dùng được

**`run.bat` thật cộng khung `pipeline/`, nối `config.json` vào đường chạy.** Tính năng đích của dự án: sửa đường dẫn trong một file cấu hình rồi gọi một lệnh. `config.example.json` đã có nhưng chưa mã nào đọc nó, và trình tự chạy chỉ tồn tại dưới dạng văn xuôi trong `procedures.md`. Ba phần: đưa trình tự đã dựng thành công `prod60` thành mã có kiểm điều kiện trước và sau mỗi khâu; đọc mọi đường dẫn từ `config.json`; dừng sạch kèm thông báo đọc được khi một khâu hỏng. Tiêu chí xong: chép `config.example.json` thành `config.json`, điền đường dẫn ảnh, narration, SRT và bảng shot, chạy một lệnh duy nhất, rồi mở được project trong CapCut với `fx_audit` báo `OK` toàn bộ và lệch timing 0,0 ms.

**Kiến trúc đã chốt 03/08/2026**, lý lẽ ở `research-log/2026-08-03-1-bgblur-va-oracle-pro.md`; đây chỉ chép phần phải làm. Cài editable qua `pyproject.toml`, **không** đóng gói exe. Ba tầng: hàm thuần trong `pipeline/steps/`, mỗi khâu một file tự khai đầu vào đầu ra kèm kiểm điều kiện trước và sau; rồi CLI có lệnh con; rồi TUI. Thêm tính năng là thả một file vào `steps/` cộng một dòng trong `config.json`. Cổng ports-and-adapters chỉ ở lớp ghi CapCut và lớp media ffmpeg. Bảng shot là nguồn sự thật, draft là phái sinh dựng lại được. `config.json` có số hiệu lược đồ, bản thật để ngoài git, mỗi lượt chạy chụp một bản vào `artifacts/`.

**Module log dùng chung ở tầng core.** Đếm 03/08/2026: **0 trên 40** file `.py` dùng `logging`. Không nhét `logging` vào từng script. Tiêu chí xong: một lượt chạy hỏng để lại đúng một file trong `data\logs` có dấu thời gian, mã thoát và dòng lỗi.

**Lệnh `doctor`, thay hẳn `preflight.py`.** Đọc file khai phiên bản ghim, đối chiếu thứ đang cài, từ chối chạy khi lệch. Được phép tự cài, nhưng **mọi lệnh cài phải ghim phiên bản tường minh**. Git, Node, Python, ffmpeg thì winget lo được; CapCut 9.1.0.3879 phải để tay vì updater đang cố ý chặn. Bootstrap bắt buộc là `.bat` hoặc `.ps1` vì Python không tự cài được Python. Tiêu chí xong: máy trắng chạy bootstrap rồi `doctor` báo xanh toàn bộ.

**TUI, làm sau cùng**, vì phải bọc quanh một CLI đã ổn định. Luật: TUI **không giữ trạng thái**, mọi thứ nó hỏi phải ghi vào `config.json` trước; nó **in ra đúng lệnh CLI tương đương trước khi chạy**; tiến trình phát ra từ core để cả CLI lẫn TUI cùng thấy; màu dùng `rich` nhưng vẫn in chữ OK, LOI, CANH BAO vì màu mất khi copy; khung menu tiếng Việt không dấu. Tiêu chí xong: một người chưa từng gõ lệnh dựng xong một project chỉ bằng menu.

## Ưu tiên 2 — công cụ và test

**Kiểm khoá Pro cho mọi loại tài nguyên.** `failures.md` mục 1: `fx_audit.py` chỉ chứng minh `path` trỏ tới file có thật, **không bắt được khoá Pro**. Hướng đọc cờ từ enums **đã chết hẳn**, đóng bằng oracle 03/08/2026; số đo ở `STATE.md`. Đối chứng dương là transition 6724227090872275463 trong `v2oracle`, nhưng nó **đã bị xoá khỏi project** trong chính phép gỡ chứng minh điều đó, nên tiêu chí dưới đây chưa chạy được: việc đầu tiên là thả lại nó bằng GUI rồi chụp mẫu, tên hiệu ứng tra ở `research-log/2026-08-03-1-bgblur-va-oracle-pro.md`. Tiêu chí xong: `fx_audit.py` báo đỏ 6724227090872275463 và báo xanh 6724846395116753416. Hai việc phụ: kiểm giả thuyết có `request_id` cùng `category_name` là dấu hiệu tài nguyên tải từ CDN; và rà chữ vương miện còn sót trong `failures.md` cùng nhật ký cũ, đổi thành dấu Pro kim cương tím.

Ba test đầu tiên trong `tests/`: lượng tử hoá frame, công thức lề dạng tổng quát KX KY, khứ hồi `shots.csv`.

## Nợ nhỏ, làm khi tiện

**Kiểm chứng ngưỡng fetch ở chế độ markdown, rồi chốt lại trần chung.** Đo 03/08/2026 chỉ chứng minh một file 24,8 KB về trọn; mốc 26 KB suy từ một lượt fetch 28 KB bị cắt mà **không rõ lúc đó dùng chế độ nào**. Tiêu chí xong: fetch markdown một file 30–40 KB rồi hỏi trợ lý ba mốc đầu, giữa, cuối; ghi số đo vào `ai-reading-channel.md` mục 2 rồi nới trần chung theo số đo — đề xuất 40 KB — trong khi bốn file cửa vào giữ trần chật vì phiên nào cũng đọc nguội chúng.

Tìm catalogue tài nguyên thật mà GUI CapCut bản quốc tế đang dùng. Manh mối 03/08/2026: trường `md5` trong enums **chính là tên file trong thư mục cache hiệu ứng**, thư mục cha là `resource_id` với mục tải từ CDN. Tiêu chí xong: liệt kê được danh sách mà `resource_id` trùng với `resource_id` GUI ghi vào `draft_content.json` khi thả tay.

Dòng `tham chieu La Ma` của `tools/docs_audit.py` chưa ai giải thích được. Giả thuyết "đếm theo số file" **đã bị bác**: đo 03/08/2026 cho 38 file `.md` được quét mà dòng này báo 44. Tiêu chí xong: giải thích được cách phân loại, hoặc sửa nếu là lỗi đếm.

Mặc định của `tools/read_src.py` nên là **không in số dòng**, thêm cờ để bật lại. Đo 03/08/2026: trợ lý suy đúng cả bốn số dòng của một file dán không kèm số, mà tiền tố số dòng ngốn chừng một phần tư token của cả lượt; số dòng vẫn cần khi có `--grep` và cho mô hình khác không tự đếm được. Tiêu chí xong: chế độ in trọn mặc định không có số dòng, `--grep` vẫn có, cờ bật lại có ghi trong docstring.

Dọn `data\tmp\`: xoá file cũ không theo khuôn tên `tmp_<YYYYMMDD>_<nhãn>`, trừ `data\tmp\gen_cc_fixture.py` là nguyên mẫu của `tools/shots_dump.py`, nằm ngoài repo nên mất là mất hẳn. Cùng lượt xoá project rỗng `fxlab01` trong thư mục draft.

Viết hướng dẫn dựng lại máy mới từ bản clone repo: cây ba nhánh phải tạo, biến `CAPCUT_LAB`, lấy `data\scaffold\` và `vendor\` từ đâu. `tools/data_manifest.py` đã là một nửa cơ chế.

Thống nhất giao diện tham số nhóm `scripts_v1` cũ; `clone_project.py` nhận ba tham số vị trí, gõ `--help` thì chết bằng `IndexError`.

Thử áp filter thẳng vào clip bằng CLI hoặc Python thay vì tạo segment trên track filter riêng; GUI cho phép cả hai kiểu.

Project `testB` có `materials.hsl` một mục, không project nào khác có và chưa tài liệu nào nhắc.

`tools/bench_shots.py` kiểm biên trước khi làm tròn; phải đảo thành làm tròn rồi mới kiểm và kẹp, giống `tools/bench_fixkb.py`. Ưu tiên thấp vì `tools/prod_shots.py` đã thay nó.

`docs/scripts.md` ở 89% trần 26 KB. Khi chạm trần thì **chọn** giữa hai đường: trần riêng tường minh trong `PER_FILE_BUDGET` kèm lý do, hoặc tách bảng kho lưu trữ sang `docs/scripts-archive.md` rồi cập nhật `tools/scripts_index.py` cho ghi hai file.

`tools/shots_dump.py` mất hiệu ứng thả tay mà không cảnh báo, đo 03/08/2026 trên `fxprobe01`. Tiêu chí xong: gặp track không phải video hoặc bucket `effects` không rỗng thì cảnh báo rõ cái gì sẽ mất.

`tools/bgblur_frames.py` chọn `blur-max` bằng `blur == 1.0` trên số thực, chưa kiểm chứng vì lab chỉ có blur 0,75. Tiêu chí xong: so bằng sai số, hoặc chứng minh CapCut chỉ ghi bốn giá trị rời rạc.

`tools/frame_audit.py` đếm `dark20` cả khung nên không tách viền khỏi nội dung tối, đo được shot không viền vẫn 0,2570. Tiêu chí xong: chỉ đếm pixel trong dải viền dự đoán, hoặc dựng phản ví dụ thật rồi chốt ngưỡng.

Xoá `data\archive\`, khoảng 60–70 MB rác, sau khi chắc chắn `D:\Test_tool` đã bỏ.

`data\Test_tool_v3\shots.csv` **trên máy lab**, ngoài repo, có 8 dòng theo lược đồ cũ `file,start,end` nên thiếu sáu cột của lược đồ hiện hành. Xoá hoặc điền lại khi `tools/shots_dump.py` chốt xong.

Điều kiện bật blur trong `tools/prod_shots.py` là `kx*smin < 1 or ky*smin < 1`, mà `S_HI` bằng 0,92 còn `kx` và `ky` không bao giờ vượt 1, nên vế trái luôn đúng và cột `blur` bằng 3 ở mọi shot. Hoặc thừa nhận blur luôn bật rồi bỏ điều kiện, hoặc đặt một ngưỡng thật. Suy luận từ mã, **chưa kiểm chứng**.

`vendor` **trên máy lab** chứa năm thư mục con mà mục 3 của `START-HERE.md` không kể tới: `frames`, `Test_tool_v3`, `snapshots`, `testV3_CLEAN`, `scripts`; gốc còn có `enums_backup.json` trùng bản với `reference/enums_backup.json`. Từ 02/08/2026 `tools/data_manifest.py` ghi đủ vào khối `vendor_extra`, khối này không tham gia phán xử mã thoát. Tiêu chí xong: khối `vendor_extra` chỉ còn thứ ta cố ý chấp nhận, và mục 3 kể đúng những gì có thật trên đĩa.

## Chờ máy render quay lại

Nghiệm thu KX và KY. Dựng lại `prod60` bằng `tools/prod_shots.py` mới rồi trích khung ở giữa mười shot có tỉ lệ ảnh khác nhau, **bắt buộc có ít nhất hai ảnh cao hơn khung 16:9**, vì nhánh ảnh cao trong `reference.md` mục 3.1 chưa có phép đo oracle nào. Tiêu chí xong: không shot nào hở mép ngoài ý muốn.

Đối chiếu CSV với JSON cho `prod60` bằng `tools/shots_crosscheck.py`, chạy **trên máy render** vì cả draft lẫn bảng shot chỉ có ở đó. Đọc năm dòng đầu báo cáo trước, nếu tên ảnh shot 1 lệch thì dừng ngay vì đang so nhầm cặp. Tiêu chí xong: mã thoát 0 kèm dòng SACH, 0 lech tren ca nam truong. Mã thoát 2 báo thiếu cột `kb_s0` và `kb_s1` **không** tính là đạt; gặp ca đó thì sinh lại bảng bằng `tools/prod_shots.py`.

Kiểm thị giác bản export `prod60` theo quy tắc in ground truth trước khi nhìn, ở `failures.md` mục 1.

Đo độ nới thực tế của segment audio trên `prod60`; lý thuyết dự đoán +10,5 ms, **chưa kiểm chứng**.

Kéo về máy lab hai thứ không tái tạo được: file `narration59.mp3` và thư mục 326 ảnh gốc ở `D:\IT\capcut-help\Picture`.

Nghiệm thu `tools/data_manifest.py` giữa hai máy. Trên máy render chạy `--scan --machine render` rồi commit bản kê, sau đó `--compare --mine manifests/lab.json --theirs manifests/render.json`. Tiêu chí xong: báo cáo in đúng danh sách hai máy thiếu của nhau; mã thoát 0 hoặc 2 đều được miễn mọi dòng lệch giải thích được. Khối `vendor_extra` lệch nhiều là bình thường; chỉ `data` và `vendor_canonical` mới đáng xử lý.
