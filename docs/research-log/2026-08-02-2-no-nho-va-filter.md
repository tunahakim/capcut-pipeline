# Nhật ký phiên 02/08/2026 (2) — dọn nợ nhỏ và đo cờ VIP của filter

Máy lab. Không mở CapCut, không chạy lệnh dựng nào, không export. Phiên trước là `2026-08-02-1-data-manifest.md`.

## Năm món nợ nhỏ đã trả

`../../tools/oracle_read.py` bỏ mặc định `CAPCUT_LAB` là đường dẫn cũ `D:\Test_tool`. Cột delta trước đây luôn tính theo một mốc cứng 8 shot của bộ test v3, nên chạy trên project khác thì in ra con số vô nghĩa mà người đọc tưởng là thật; nay mặc định **không có cột delta**, chỉ hiện khi truyền `--baseline`, nhận `v3` để lấy mốc cũ hoặc đường dẫn một file JSON dạng `[[start, duration], ...]`. Khi số shot của mốc khác số shot của project thì in một dòng cảnh báo và chỉ tính delta tới shot chung cuối cùng.

`../../tools/bgblur_diag.py` trước cứng **hai** project `bench300` và `parity01` chứ không phải một như `../TODO.md` mô tả, và docstring ghi thẳng "không tham số"; nay nhận danh sách tên project qua `nargs="+"`. `../../tools/bgblur_frames.py` trước lấy `sys.argv[1]` làm đường dẫn MP4 nên không thể thêm tên project vào cùng vị trí mà không đổi nghĩa tham số cũ; nay dùng `--project` bắt buộc và `--mp4` tuỳ chọn. `../../tools/frame_audit.py` thực ra **đã** nhận tên project qua `sys.argv[1]` từ trước, mô tả trong TODO không chính xác; cái cứng thật sự là giá trị mặc định `bench300` và đường dẫn MP4 mặc định, nay cả hai thành `--project` và `--mp4` bắt buộc.

Việc tham số hoá làm lộ ra một lỗi thầm lặng sắp sinh: `bgblur_diag.py` ghi cố định `perf/bgblur_diag.txt` và `bgblur_frames.py` ghi cố định `perf/bgblur_frames/`, nên chạy hai project khác nhau sẽ đè kết quả lên nhau mà không báo gì. Đã gắn tên project vào cả hai đường dẫn đầu ra trong cùng bản vá, trước khi lỗi kịp xảy ra lần nào.

`../../tools/docs_audit.py` bỏ vế `p != "README.md"` trong biểu thức dựng danh sách file mồ côi. Kết luận "không đổi hành vi" không phải suy đoán: ma trận tham chiếu do chính công cụ in ra cho thấy README.md được `START-HERE.md` trỏ tới 4 lần, `TODO.md` 1 lần, `2026-07-30-1-refactor.md` 1 lần và `2026-07-31-3-bgblur-timing.md` 1 lần, nên nó luôn nằm trong tập `referenced` và vế kia không bao giờ là vế quyết định. Sau khi bỏ, số file mồ côi vẫn bằng 0.

`scan_paths.py` đã dời từ thư mục mẹ `capcut-lab\` vào `data\tmp\`; thư mục mẹ nay chỉ còn đúng ba nhánh. Thêm một dòng cho `split_research_log.py` vào `../../_deprecated/README.md`.

`../TODO.md` từ 11674 xuống 10273 byte, tức từ 95 xuống 83,6 phần trăm trần 12 KB. Mục về `../scripts.md` được viết lại theo hướng bỏ hẳn con số đếm được bằng máy và trỏ sang `docs_audit.py`, vì cả ba con số cũ trong đó đều đã sai.

## Cờ VIP của filter, đo được

`capcut enums --filters --jianying` trả về một mảng 468 phần tử, mỗi phần tử có `is_vip` ở cấp trên cùng cạnh `slug`, `name`, `md5`, `effect_id`, `resource_id`. Đếm được **300 mục `is_vip: true`, 168 mục `false`, không mục nào thiếu cờ**. Số liệu đã ghi vào `../reference-catalog.md`. Đây mới là nửa đầu của mục kiểm khoá Pro trong `../TODO.md`; nửa sau là cho `fx_audit.py` báo đỏ, chưa làm.

Cảnh báo phương pháp cho phiên sau: `../failures.md` mục 2.5 ghi filter "Film" thả tay từ GUI **không có trong `enums.json` ở bất kỳ namespace nào**. Nghĩa là tập filter hiện trong panel GUI của CapCut bản quốc tế không trùng với 468 mục JianYing này. Nếu thả một filter Pro bất kỳ rồi mong `fx_audit.py` bắt được, phép thử sẽ fail vì phương pháp chứ không vì code. Phải chọn trước một mục có `is_vip: true` **và** có slug Latin để tra được trong GUI. Ứng viên đối chứng dương: `2077`, `90s`, `city-walk`, `160-c`, `400-h`, `800-z`, `fxn`. Ứng viên đối chứng âm: `vhs-iii`, `1980`, `ditto`, `abg`, `ke1`, `kv5-d`. Phần lớn 468 mục có slug rỗng và name tiếng Trung, chỉ gọi được bằng `resource_id` từ Python.

## Kiểm kê project trên máy lab

Thư mục draft có 11 project đọc được: `0728` 1 shot, `trpath` và `truncached` 3 shot, `paritytest`, `Test_A_Basic`, `testB`, `testV3`, `testV4`, `v2oracle` 8 shot, `testB_CLEAN` 0 shot; `Test_A_v2` không có `Timelines/project.json`. **Không project nào có bucket `filters`** — xác nhận bằng phép đo hôm nay điều mà `../../molds/capcut-9.1.0/_README.md` ghi từ 31/07. `bench300` và `parity01` đều không tồn tại trên máy lab. `testV3` có `canvas_blur` thật ở shot 4 mức 0,7500.

## Sáu dương tính giả CRLF, không phải ba

Phiên trước ghi ba file lệch kích thước giữa đĩa và blob GitHub do CRLF. Đối chiếu đầy đủ trong phiên này tìm ra sáu: `../STATE.md` +38, `../procedures.md` +198, `../model.md` +57, `../../_deprecated/README.md` +22, `2026-08-01-1-docs-headers.md` +50, `2026-08-01-4-readme-cua-vao.md` +32. Phần lệch của mỗi file đúng bằng số dòng, `git status` sạch, không mất chữ nào. Ghi lại để phép đối chiếu độ dài sau mỗi lần fetch không báo động nhầm lần nữa.

## Hai kỹ thuật làm việc mới, đã chốt vào mục 8 của START-HERE

Trích dòng thay vì đọc trọn file. Khi trợ lý cần vài dòng trong một file mã dài, viết một script in ra số dòng thật của file, phần đầu file, và những dòng khớp từ khoá kèm ngữ cảnh, đồng thời in rõ mỗi khoảng bị bỏ qua kèm số dòng đã bỏ. Trong phiên này bốn file tổng 29,5 KB được rút còn 264 dòng trích. Dấu khoảng bị bỏ qua là phần quan trọng nhất: nó ngăn việc kết luận nhầm rằng một đoạn mã không tồn tại.

Vá file bằng script thay vì bắt người dùng sửa tay. Script vá đọc file với `newline=""`, tự dò CRLF hay LF rồi đổi khuôn so khớp, đếm số lần khớp của từng đoạn và bắt buộc bằng đúng 1, kiểm hết mọi đoạn rồi mới ghi, có bất kỳ chỗ nào lệch thì in `KHONG KHOP` và thoát mã 1 mà không sửa file nào. Nhiều đoạn vá trên cùng một file phải gộp vào một lần đọc một lần ghi, nếu không đoạn sau ghi đè đoạn trước — lỗi này đã được bắt ở khâu thiết kế chứ chưa kịp gây hại. Mười ba chỗ vá trên bốn file trong phiên này đều báo khớp đúng một lần.

Một bẫy encoding mới: Python 3.14 khi bị pipe sang `Out-File` của PowerShell 5.1 lấy stdout là cp1252 và gãy ngay ở chữ có dấu đầu tiên. Script trích phải tự ghi kết quả ra file UTF-8 rồi mở bằng Notepad, đừng đi qua đường ống.

## Chưa kiểm chứng

Cờ `is_vip` của namespace JianYing có dự đoán đúng biểu tượng khoá Pro trong GUI CapCut hay không. `bgblur_diag.py` chưa chạy trên project có đủ mẫu blur như `bench300`. `frame_audit.py` chưa chạy lần nào ngoài `--help` và ca thiếu tham số, vì máy lab không có bản MP4 nào khớp project đang có. Nhánh in dòng trần khi project nhiều shot hơn mốc của `oracle_read.py` đã kiểm chứng bằng một file mốc 2 dòng chạy trên project 8 shot, không phải bằng project thật nhiều hơn 8 shot.

## Còn lại

Bốn việc của lộ trình phiên này chưa làm: thả tay filter free và filter Pro trong GUI để gỡ chặn khuôn filter, vá `../../tools/v4_mold.py`, cho `fx_audit.py` báo đỏ tài nguyên khoá Pro, và viết `../../tools/shots_dump.py`. Cả bốn đều còn nguyên trong `../TODO.md` kèm tiêu chí xong.

Lưu ý cho việc vá `v4_mold.py`: `../../molds/capcut-9.1.0/filter.json` **đã tồn tại**, 3218 byte, chụp ngày 28/07/2026 từ project `testV4` khi thả tay filter "Film", và đang là nền của `../../scripts_v1/filter_apply.py`. Ghi đè nó bằng khuôn của một filter khác sẽ làm hai chuyện cùng lúc: thay nền của `filter_apply.py`, và làm phép phân loại trường báo đỏ oan vì `resource_id`, `effect_id` và `name` của hai filter khác nhau thì khác nhau một cách chính đáng. Hoặc thêm nhóm trường thứ ba là định danh được phép khác, hoặc ghi khuôn mới ra tên khác và giữ nguyên `filter.json` cũ. Quyết định này chưa được đưa ra.