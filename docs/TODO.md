# TODO — việc chưa làm

**Cập nhật 02/08/2026.** Trần kích thước file này là **12 KB**, chật hơn trần chung, vì danh sách là thứ dễ phình nhất.

Luật ba file, đọc kèm `STATE.md`: file này chứa **thì tương lai**, tức mọi việc chưa làm kể cả nợ kỹ thuật, vì mỗi món nợ là một việc. `STATE.md` chứa **thì hiện tại đã đo được** và không được liệt kê việc phải làm. `research-log/` chứa **thì quá khứ**. Mỗi mục dưới đây phải có tiêu chí hoàn thành. **Xong thì xoá khỏi file này**, không đánh dấu hoàn thành rồi giữ lại — danh sách đã hoàn thành chính là research-log.

## Ưu tiên 1 — đóng gói thành ứng dụng dùng được

**`run.bat` thật cộng khung `pipeline/`, và nối `config.json` vào đường chạy.** Đây là tính năng đích của cả dự án: người dùng sửa đường dẫn trong một file cấu hình rồi gọi một lệnh, không gõ thêm lệnh nào. Hiện `config.example.json` đã nằm trong repo nhưng chưa có mã nào đọc nó, và trình tự chạy vẫn chỉ tồn tại trong `docs/procedures.md` dưới dạng văn xuôi chứ không phải mã. Ba phần: đưa trình tự đã dựng thành công `prod60` thành mã có kiểm điều kiện trước và sau mỗi khâu; đọc mọi đường dẫn từ `config.json`; dừng sạch kèm thông báo đọc được khi một khâu hỏng thay vì chạy tiếp. Tiêu chí xong: trên một máy đã cài đủ, chép `config.example.json` thành `config.json`, điền đường dẫn tới thư mục ảnh, file narration, file SRT và bảng shot, chạy một lệnh duy nhất, rồi mở được project trong CapCut với `fx_audit` báo `OK` toàn bộ và lệch timing 0,0 ms, không gõ thêm lệnh nào ở giữa.

**Kiến trúc đã chốt 03/08/2026**, lý lẽ đầy đủ ở `research-log/2026-08-03-1-bgblur-va-oracle-pro.md`; đây chỉ chép phần phải làm. Cài tại chỗ dạng editable qua `pyproject.toml`, **không** đóng gói exe. Ba tầng: hàm thuần trong `pipeline/steps/`, mỗi khâu một file tự khai đầu vào đầu ra kèm kiểm điều kiện trước và sau; rồi CLI có lệnh con; rồi TUI. Thêm tính năng nghĩa là thả thêm một file vào `steps/` và thêm một dòng vào `config.json`. Cổng kiểu ports-and-adapters chỉ đặt ở hai chỗ có nguy cơ đổi thật là lớp ghi CapCut và lớp media ffmpeg, không dựng tầng domain riêng. Bảng shot là nguồn sự thật, draft là sản phẩm phái sinh dựng lại được. `config.json` có trường số hiệu lược đồ, bản thật để ngoài git, mỗi lượt chạy chụp một bản vào `artifacts/`.

**Module log dùng chung ở tầng core.** Đếm 03/08/2026: **0 trên 40** file `.py` dùng `logging`. Không nhét `logging` vào từng script. Tiêu chí xong: một lượt chạy hỏng để lại đúng một file trong `data\logs` có dấu thời gian, mã thoát và dòng lỗi, gửi nguyên file được thay vì copy console.

**Lệnh `doctor`, thay hẳn `preflight.py`.** Đọc một file khai phiên bản ghim, đối chiếu với thứ đang cài, từ chối chạy khi lệch. Được phép tự cài, nhưng **mọi lệnh cài phải ghim phiên bản tường minh**, không bao giờ để trình cài chọn bản mới nhất. Lớp nền Git, Node, Python, ffmpeg thì winget lo được; CapCut 9.1.0.3879 phải để tay vì updater đang cố ý chặn. Bootstrap bắt buộc là `.bat` hoặc `.ps1` vì Python không tự cài được Python. Tiêu chí xong: máy trắng chạy bootstrap rồi `doctor` báo xanh toàn bộ.

**TUI, làm sau cùng.** Làm sau vì phải bọc quanh một CLI đã ổn định, không phải vì ít giá trị. Luật: TUI **không giữ trạng thái**, mọi thứ nó hỏi phải ghi vào `config.json` trước rồi lượt chạy mới đọc từ đó; TUI **in ra đúng lệnh CLI tương đương trước khi chạy**; tiến trình phần trăm và thời gian phát ra từ core để cả CLI lẫn TUI cùng thấy; màu dùng `rich`, xanh đạt đỏ hỏng vàng cảnh báo, nhưng vẫn in chữ OK, LOI, CANH BAO vì màu mất khi copy; khung menu viết tiếng Việt không dấu. Tiêu chí xong: một người chưa từng gõ lệnh dựng xong một project chỉ bằng menu.

## Ưu tiên 2 — công cụ và test

**Kiểm khoá Pro cho mọi loại tài nguyên.** `failures.md` mục 1: `fx_audit.py` chỉ chứng minh `path` trỏ tới file có thật, **không bắt được khoá Pro**. Hướng đọc cờ từ enums **đã chết hẳn**, đóng bằng oracle 03/08/2026; số đo ở `STATE.md`. Nay đã có **đối chứng dương thật**: transition `resource_id` 6724227090872275463 trong `v2oracle` bị chính CapCut chặn export, còn 6724846395116753416 trong cùng project thì free. Tiêu chí xong: `fx_audit.py` báo đỏ đúng cái thứ nhất và báo xanh cái thứ hai. Hai việc phụ: kiểm giả thuyết có `request_id` cùng `category_name` là dấu hiệu tài nguyên tải từ CDN; và rà chữ vương miện còn sót trong `failures.md` cùng nhật ký cũ, đổi thành dấu Pro kim cương tím.

Ba test đầu tiên trong `tests/`: lượng tử hoá frame, công thức lề dạng tổng quát KX KY, khứ hồi `shots.csv`.

## Nợ nhỏ, làm khi tiện

Tìm catalogue tài nguyên thật mà GUI CapCut bản quốc tế đang dùng. Manh mối mới 03/08/2026: trường `md5` trong enums **chính là tên file trong thư mục cache hiệu ứng**, và thư mục cha là `resource_id` với mục tải từ CDN. Tiêu chí xong: liệt kê được một danh sách mà `resource_id` trùng với `resource_id` GUI ghi vào `draft_content.json` khi thả tay.

Truy vì sao dòng `tham chieu La Ma` của `tools/docs_audit.py` tăng từ 38 lên 39 sau khi thêm vào `reference-catalog.md` một đoạn không chứa số La Mã nào, ngày 02/08/2026. Không cấp bách, `VAN DE` vẫn 0. Tiêu chí xong: giải thích được cách phân loại, hoặc sửa nếu là lỗi đếm.

Xoá project rỗng `fxlab01` trong thư mục draft; nó không chứa gì và không tài liệu nào giải thích.

Thêm cờ `--brief` cho `tools/docs_audit.py`: chỉ in TONG QUAN, VAN DE, SO VOI MOC CHUAN, bỏ ma trận tham chiếu.

Viết hướng dẫn dựng lại máy mới từ bản clone repo: cây ba nhánh phải tạo, biến `CAPCUT_LAB`, lấy `data\scaffold\` và `vendor\` từ đâu. `tools/data_manifest.py` đã là một nửa cơ chế.

Thống nhất giao diện tham số nhóm `scripts_v1` cũ; `clone_project.py` nhận ba tham số vị trí, gõ `--help` thì chết bằng `IndexError`.

Thử áp filter thẳng vào clip bằng CLI hoặc Python thay vì tạo segment trên track filter riêng; GUI cho phép cả hai kiểu.

Project `testB` có `materials.hsl` một mục, không project nào khác có và chưa tài liệu nào nhắc.

`tools/bench_shots.py` kiểm biên trước khi làm tròn; phải đảo thành làm tròn rồi mới kiểm và kẹp, giống `tools/bench_fixkb.py`. Ưu tiên thấp vì `tools/prod_shots.py` đã thay nó.

`docs/scripts.md` đang tiến dần tới trần 26 KB; số hiện hành lấy bằng `python tools/docs_audit.py` chứ không chép vào đây. Khi chạm trần thì tách bảng kho lưu trữ sang `docs/scripts-archive.md` và cập nhật `tools/scripts_index.py` cho ghi hai file.

`tools/shots_dump.py` bỏ qua mọi hiệu ứng thả tay mà không cảnh báo, đo 03/08/2026 trên `fxprobe01`: hai filter ở `materials.effects` và track `type=filter` mất sạch. Không phải lỗi vì docstring chỉ hứa sáu cột bảng shot, nhưng nó chặn tính năng sửa project dựng tay. Tiêu chí xong: gặp track không phải video hoặc bucket `effects` không rỗng thì in cảnh báo nêu rõ cái gì sẽ mất.

`tools/bgblur_frames.py` chọn vai `blur-max` bằng phép so sánh `blur == 1.0` trên số thực. **Chưa kiểm chứng** là lỗi hay không vì lab chưa có mẫu blur khác 0,75. Tiêu chí xong: so bằng sai số, hoặc chứng minh được CapCut luôn ghi đúng bốn giá trị rời rạc.

`tools/frame_audit.py` đếm `dark20` trên cả khung nên không tách được pixel tối của viền khỏi pixel tối của ảnh; đo 03/08/2026 thấy shot không viền vẫn có `dark20` tới 0,2570. Vùng viền trung bình **chưa có bằng chứng**. Tiêu chí xong: chỉ đếm pixel trong dải viền dự đoán, hoặc dựng được một phản ví dụ thật rồi chốt ngưỡng.

Xoá `data\archive\`, khoảng 60–70 MB rác, sau khi chắc chắn `D:\Test_tool` đã bỏ.

`data\Test_tool_v3\shots.csv` **trên máy lab**, ngoài repo, có 8 dòng theo lược đồ cũ `file,start,end` nên thiếu sáu cột của lược đồ hiện hành và `tools/shots_crosscheck.py` không dùng được. Xoá hoặc điền lại khi `tools/shots_dump.py` chốt xong.

Điều kiện bật blur trong `tools/prod_shots.py` là `kx*smin < 1 or ky*smin < 1`, mà `S_HI` bằng 0,92 còn `kx` và `ky` không bao giờ vượt 1, nên vế trái luôn đúng và cột `blur` bằng 3 ở mọi shot. Hoặc thừa nhận blur luôn bật rồi bỏ điều kiện cho khỏi gây hiểu nhầm, hoặc đặt một ngưỡng thật. Suy luận từ mã, **chưa kiểm chứng** bằng cách đếm cột blur trên bảng shot đã sinh.

`vendor` **trên máy lab** chứa năm thư mục con mà mục 3 của `START-HERE.md` không kể tới: `frames`, `Test_tool_v3`, `snapshots`, `testV3_CLEAN`, `scripts`; gốc còn có `enums_backup.json` trùng bản với `reference/enums_backup.json`. Từ 02/08/2026 `tools/data_manifest.py` ghi đủ vào khối `vendor_extra`, khối này không tham gia phán xử mã thoát. Phần còn treo là quyết dọn hay hợp thức hoá. Tiêu chí xong: khối `vendor_extra` chỉ còn thứ ta cố ý chấp nhận, và mục 3 kể đúng những gì có thật trên đĩa.

## Chờ máy render quay lại

Nghiệm thu KX và KY. Dựng lại `prod60` bằng `tools/prod_shots.py` mới rồi trích khung ở giữa mười shot có tỉ lệ ảnh khác nhau, **bắt buộc có ít nhất hai ảnh cao hơn khung 16:9**, vì nhánh ảnh cao trong `reference.md` mục 3.1 chưa có phép đo oracle nào. Tiêu chí xong: không shot nào hở mép ngoài ý muốn. Lớp Python đã hoàn tất và đã tự kiểm trên dữ liệu tổng hợp ngày 01/08/2026, phần còn thiếu duy nhất là mắt người nhìn khung hình thật.

Đối chiếu CSV với JSON cho `prod60` bằng `tools/shots_crosscheck.py`, chạy **trên máy render** vì cả draft lẫn bảng shot chỉ có ở đó. Gọi `python tools/shots_crosscheck.py --project prod60 --csv <đường dẫn thật>`; đọc năm dòng đầu báo cáo trước, nếu tên ảnh shot 1 lệch thì dừng ngay vì đang so nhầm cặp. Tiêu chí xong: mã thoát 0 kèm dòng SACH, 0 lech tren ca nam truong. Mã thoát 2 báo thiếu cột `kb_s0` và `kb_s1` **không** tính là đạt; gặp ca đó thì sinh lại bảng bằng `tools/prod_shots.py` rồi chạy lượt mới.

Kiểm thị giác bản export `prod60` theo quy tắc in ground truth trước khi nhìn, ở `failures.md` mục 1.

Đo độ nới thực tế của segment audio trên `prod60`; lý thuyết dự đoán +10,5 ms, **chưa kiểm chứng**.

Kéo về máy lab hai thứ không tái tạo được: file `narration59.mp3` và thư mục 326 ảnh gốc ở `D:\IT\capcut-help\Picture`.

Nghiệm thu `tools/data_manifest.py` giữa hai máy. Trên máy render chạy `--scan --machine render` rồi commit bản kê, sau đó `--compare --mine manifests/lab.json --theirs manifests/render.json`. Tiêu chí xong: báo cáo in đúng danh sách hai máy thiếu của nhau; mã thoát 0 hoặc 2 đều được miễn mọi dòng lệch giải thích được, mã thoát 1 là chưa chạy được. Khối `vendor_extra` lệch nhiều là bình thường; chỉ `data` và `vendor_canonical` mới đáng xử lý.
