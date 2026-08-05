# Nhật ký phiên 03/08/2026 (1) — nghiệm thu hai script blur, oracle khoá Pro trên transition Up, và chốt hướng đóng gói

**Tóm tắt:** Nghiệm thu `bgblur_diag.py` và `bgblur_frames.py` trên bốn project; `blur` hằng 0,75 nên máy lab không có mẫu đa mức, bộ chọn mẫu suy giảm im lặng; vị trí ref canvas_blur không cố định. Oracle khoá Pro đóng dứt điểm bằng chính hộp thoại Pro materials của CapCut trên transition `Up` 6724227090872275463: cờ `is_vip` của enums vô dụng cho bản quốc tế, enums không phủ danh mục GUI, tra theo tên là bẫy, và `md5` trong enums chính là tên file cache. Chốt hướng đóng gói ba tầng steps–CLI–TUI, cài editable, ghim phiên bản, module log dùng chung
**Phiên:** 09:28 sáng

Máy lab. Có mở CapCut, có thử export nhưng bị CapCut chặn nên **không có MP4**. Phiên trước là `2026-08-02-4-shots-dump-va-oracle.md`.

## Bước 1 — `../../tools/bgblur_diag.py` và `../../tools/bgblur_frames.py` đạt, `frame_audit.py` vẫn treo

`bgblur_diag.py` chạy trọn trên bốn project `testV3`, `testV4`, `v2oracle`, `testB`, in bảng không rỗng, đọc được cả bản gốc lẫn bản lồng trong `Timelines`; bản lồng trùng khít bản gốc ở cả bốn. `bgblur_frames.py` chạy trọn trên `v2oracle` và `testV4`, bảng không rỗng.

Đo được: giá trị `blur` bằng **0,75 trên toàn bộ 32 segment blur của cả bốn project**, không project nào có hai mức. Bộ chọn mẫu của `bgblur_frames.py` hứa sáu vai gồm mức 4, mức 1 và mức giữa, nhưng thực tế trả ba vai trên `v2oracle` và **đúng một vai** trên `testV4`, **không hề cảnh báo là thiếu mẫu**. Đây là suy giảm im lặng, cần vá cho nó nói ra.

`check_flag` tương quan tuyệt đối với loại canvas trên mẫu này: 4103 đi với `canvas_blur` ở cả 32 segment, 7 đi với `canvas_color` ở cả 7 segment của `v2oracle`.

Vị trí ref của `canvas_blur` trong `extra_material_refs` **không cố định**: đo được ba dạng là idx 2 trong 7, idx 3 trong 8, idx 3 trong 9. Mọi mã giả định chỉ số cố định sẽ gãy âm thầm.

`frame_audit.py` vẫn chưa nghiệm thu được vì không có MP4. Dự đoán đã chốt trước khi export, theo luật in ground truth trước khi nhìn: trên `v2oracle` thì shot 3 tại giây 41,800 phải ra BLUR, shot 6 tại giây 99,333 phải ra BLACK, shot 1 tại giây 9,883 phải ra AMBIG vì viền dự đoán bằng không. Giữ nguyên dự đoán này cho phiên sau. Cảnh báo của người dùng, cần tôn trọng khi chạy: một vài project có filter Film áp cho cả video nên có viền đen quanh mép ngoài; nếu `frame_audit.py` chạy nhầm project đó thì phép đếm pixel tối sẽ kết luận BLACK sai. Đã kiểm `v2oracle` không có bucket filter nào, nên project này sạch.

## Bước 2 — oracle khoá Pro, đóng dứt điểm

Không cần thả tay tài nguyên mới. Khi export `v2oracle`, CapCut tự bật hộp thoại **Pro materials** liệt kê đúng một mục tên **Up** ở mốc **00:01:12** và chặn export. Dấu Pro của CapCut là **viên kim cương tím**, không phải vương miện; các tài liệu trước dùng chữ vương miện là nói ước lệ; `STATE.md` đã sửa 03/08/2026, phần còn sót ở `failures.md` và các nhật ký cũ đã ghi thành việc trong `../TODO.md`.

`v2oracle` có đúng hai transition, cả hai đều tên `Up`. Suy từ mốc thời gian, mục bị chặn là cái gắn ở ranh giới seg4 sang seg5, tức 72,733 giây bằng 00:01:12, `resource_id` **6724227090872275463**, `category_name` Classic, có `request_id`, cache ở thư mục mang tên chính `resource_id`. Mục còn lại `resource_id` 6724846395116753416 không có `category_name`, không có `request_id`, cache ở thư mục `670867`.

Tra `../../reference/enums_backup.json`: `resource_id` 6724227090872275463 **không tồn tại trong namespace `capcut`**, chỉ có ở `/jianying/transitions/[21]` dưới tên 向上 với `is_vip` bằng **False**. Tên `Up` trong namespace `capcut` lại trỏ tới `resource_id` **khác** là 6724846395116753416, tức đúng cái free.

Ba kết luận. Cờ `is_vip` của enums **vô dụng cho bản quốc tế**, đã chứng minh bằng oracle. Enums **không phủ danh mục GUI**, vì một mục GUI đang dùng thật lại vắng mặt ở namespace `capcut`. Và **tra theo tên là bẫy**, vì tên `Up` cho ra đúng cái free trong khi cái bị khoá mang tên Trung văn ở namespace khác.

Mối nối mới, có giá trị cho việc tìm catalogue thật: trường `md5` trong enums **chính là tên file trong `Cache\effect\`**. `df9bc16697464de201a4924de49234a2` và `349746a951e130fe896415f51c9eb36a` khớp tuyệt đối với hai đường dẫn cache mà `draft_content.json` ghi.

## Quyết định kiến trúc cho việc đóng gói

Chốt hướng, chưa viết mã. Không đóng gói thành exe, vì bản dựng sẽ thành bản sao thứ hai của mã nguồn và mỗi lần sửa phải build lại. Thay bằng cài tại chỗ dạng editable qua `pyproject.toml`, khi đó cập nhật một tính năng chỉ là `git pull --rebase`.

Ba tầng: hàm thuần trong `pipeline/steps/`, rồi CLI có lệnh con làm giao diện chính, rồi TUI làm lớp vỏ. TUI chỉ hiển thị và nhận lệnh, mọi trạng thái ghi ra file, mọi nghiệp vụ nằm ở core. TUI phải in ra đúng lệnh CLI tương đương trước khi chạy. Làm TUI sau cùng vì nó phải bọc quanh một CLI đã ổn định, không phải vì nó ít giá trị.

Về ports và adapters: chỉ đặt cổng ở hai chỗ thật sự có nguy cơ đổi, là lớp ghi vào CapCut và lớp media ffmpeg. Không dựng tầng domain riêng, vì số học timing vốn đã thuần.

Về cài đặt: tự động được, nhưng mọi lệnh cài phải ghim phiên bản tường minh, không bao giờ để trình cài tự chọn bản mới nhất. Lớp nền Git, Node, Python, ffmpeg thì winget lo được; CapCut 9.1.0.3879 phải để tay vì updater đang cố ý chặn. Cần một file khai phiên bản ghim để bootstrap và `doctor` cùng đọc. Bootstrap bắt buộc là `.bat` hoặc `.ps1` vì Python không tự cài được Python.

Tên đúng của màn hình menu là **TUI**, text-based user interface; loại đánh số rồi gõ số gọi là console menu hay menu-driven CLI. Màu dùng thư viện `rich` chứ đừng tự in mã ANSI, vì console PowerShell 5.1 cần bật virtual terminal mới hiểu; `rich` tự lo và tự tắt màu khi đầu ra bị pipe. Màu **không được là kênh thông tin duy nhất**, vẫn phải in chữ OK, LOI, CANH BAO vì màu mất sạch khi copy text. Lý do TUI đáng làm, người dùng nêu và đã tiếp thu: người dùng chính không phải dev, tài liệu nhiều tới mức khó biết mở file nào, và có thể có thành viên mới khi kênh chạy.

Về log: đếm được trên 40 file `.py` của `tools/` và `scripts_v1/` là **0 file dùng `logging`**, 38 khối `try`, 39 `except`, 62 chỗ `sys.exit`, 0 chỗ `traceback`. Nghĩa là có xử lý lỗi nhưng không ghi vết. Hướng đã chốt: một module log dùng chung ở tầng core, ghi ra `data\logs\` kèm dấu thời gian, không nhét `logging` vào từng script.

## Chưa kiểm chứng

Việc quy mục Pro về transition ở 72,733 giây là **suy từ mốc thời gian**, chưa xác nhận trực tiếp. Phép làm chắc rất rẻ: xoá đúng transition đó trong GUI rồi export lại, hết chặn là đóng đinh.

Giả thuyết rằng có `request_id` và `category_name` là dấu hiệu tài nguyên tải từ CDN, còn thiếu hai trường đó là bản dựng sẵn trong bộ cài. Nếu đúng thì đây là dấu hiệu nhận biết rẻ hơn nhiều so với đi tìm catalogue.

Liên hệ giữa cột `blur` trong `shots.csv` và giá trị 0,75 trong JSON vẫn chưa xác lập; hai phát biểu đó khác nhau và mới một cái có bằng chứng.

## Còn lại

`frame_audit.py` chưa nghiệm thu, nay còn vướng thêm việc phải gỡ transition Pro mới export được `v2oracle`. Toàn bộ nợ nhỏ của phiên này hoãn, còn nguyên trong `../TODO.md`.
