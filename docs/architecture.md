# ARCHITECTURE — hợp đồng kiến trúc

**Cập nhật 04/08/2026.** File này giữ thứ **không đổi theo phiên**, cùng tầng với `START-HERE.md`; nó tách ra thành file riêng vì `START-HERE.md` đã dùng 94% trần. Lý do file này tồn tại: trước 04/08/2026 toàn bộ hợp đồng kiến trúc chỉ nằm trong mục Ưu tiên 1 của `TODO.md`, mà `TODO.md` là thì tương lai và **xong việc thì xoá**, nên ngày pipeline chạy được thì kiến trúc cùng lý lẽ của nó biến mất khỏi repo. Việc phải làm vẫn nằm ở `TODO.md`; file này chỉ nói **luật**.

## 1. Bốn tầng và chiều phụ thuộc

Chiều phụ thuộc là một chiều, không có ngoại lệ:

```
__main__.py   ->  steps/  ->  capcut/ , media/  ->  core/
```

`pipeline/core/` là hàm thuần: nhận số và chuỗi, trả số và chuỗi. **Không** được import `subprocess`, **không** đọc ghi đĩa ngoài việc đọc một file văn bản đã được chỉ đường dẫn, **không** biết CapCut hay ffmpeg tồn tại. Đây là tầng duy nhất test được mà không cần máy có CapCut.

`pipeline/capcut/` và `pipeline/media/` là hai cổng duy nhất. `capcut/` gói mọi thứ chạm vào capcut-cli, vào bốn file JSON của project và vào thư mục `Timelines\`. `media/` gói mọi thứ gọi ffmpeg và ffprobe. Ngoài hai thư mục này, **không file nào khác trong `pipeline/` được gọi `subprocess`**.

`pipeline/steps/` là các khâu, mỗi khâu một file. Mỗi khâu tự khai đầu vào, đầu ra, một phép **kiểm điều kiện trước** và một phép **kiểm điều kiện sau**. Khâu được import cả `core` lẫn hai cổng.

`pipeline/__main__.py` chỉ ghép khâu thành lệnh con và in kết quả. Không chứa logic nghiệp vụ.

Luật này kiểm được bằng máy: grep `import subprocess` trong `pipeline/core/` phải cho 0 dòng, grep `import` chéo tầng ngược chiều cũng phải cho 0 dòng. Một test như vậy đáng viết vì nó rẻ và bắt được đúng loại trôi dạt khó thấy nhất.

## 2. Nguồn sự thật

**Bảng shotlist là nguồn sự thật. Draft CapCut là phái sinh, dựng lại được.** Ba chặng, mỗi chặng dựng lại được từ chặng trước:

| Chặng | Vật | Ai tạo | Có commit không |
|---|---|---|---|
| 1 | `<project>.shotlist.tsv`, năm cột người viết | người | không, nằm cạnh media |
| 2 | `shots.csv` mười sáu cột, cùng bản chụp `config.json` | máy | có, vào `artifacts\` mỗi lượt chạy |
| 3 | thư mục draft CapCut | máy | không |

Hệ quả phải nhớ, vì nó là bẫy chắc chắn sẽ cắn người dùng: **hiệu ứng thả tay trong GUI không sống sót qua một lượt dựng lại.** Nếu sửa một mốc trong shotlist rồi chạy lại, bản dựng mới không có những gì đã thả tay. Bằng chứng đã có: `shots_dump.py` dump `fxprobe01` làm mất sạch hai filter thả tay mà không cảnh báo. Quy ước làm việc vì thế là: chốt bảng và timing trước, dựng, rồi mới thả hiệu ứng bằng tay ở lượt cuối; phải sửa bảng thì chấp nhận thả lại. Việc giữ lại hiệu ứng thả tay qua các lượt dựng là **tính năng tương lai**, không thuộc giai đoạn này.

## 3. Cái gì được cấu hình, cái gì không

Được cấu hình, và phải đọc từ `config.json` chứ không hằng số trong mã: danh sách transition cho phép cùng danh sách chặn, kích thước canvas và fps, biên scale Ken Burns, mức canvas blur mặc định, độ dài transition, slug và cường độ scene effect, đuôi cố ý sau narration, ngưỡng cảnh báo shot ngắn, mọi đường dẫn.

**Không** được cấu hình, vì đây là ràng buộc đúng-sai đã kiểm chứng ba lần ở quy mô 300 shot chứ không phải sở thích: luật bắt mọi ranh giới cắt về bội số của 0,1 giây tính theo ranh giới tuyệt đối, và luật dùng `ceil` cộng một đuôi cố ý ở mốc cuối. Mở hai thứ này cho cấu hình là mở đường phá bảo đảm sai lệch dưới 50 ms mà cả dự án dựa vào.

Cũng **không** nên biến `steps/` thành plugin nạp động theo tên trong `config.json`. Với dưới mười khâu, một danh sách tường minh trong `pipeline/__main__.py` dễ đọc và dễ debug hơn, còn nạp động biến một lỗi chính tả tên khâu thành lỗi lúc chạy.

## 4. Hai mức chẩn đoán

Mọi khâu phân biệt đúng hai mức, và cách phân biệt là **hậu quả**, không phải mức độ nghiêm trọng cảm tính.

`CANH BAO` là thứ bỏ qua được: in số dòng, tên cột, giá trị, và **lý do** bỏ qua, rồi chạy tiếp. Ví dụ: một cột để dành mà người dùng đã điền, một shot ngắn hơn ngưỡng, một thư mục cache không thấy.

`LOI` là thứ làm sai timing hoặc làm sai nội dung: gom **hết** mọi lỗi rồi in một lượt, dừng, và không dùng kết quả. Không bao giờ chết ở lỗi đầu tiên, vì như vậy người dùng phải chạy lại hai chục lần cho hai chục lỗi. Ví dụ: mốc không tăng, hai mốc bắt lưới về cùng giá trị làm shot dài 0, thiếu cột bắt buộc, ảnh không tồn tại.

Mã thoát: 0 là xong, 2 là cấu hình hoặc đầu vào không hợp lệ và **chưa ghi gì**. Hai ca đó phải phân biệt được bằng số, vì TUI sẽ đọc mã thoát chứ không đọc chữ.

## 5. Giao diện: TUI là đường vào, CLI là nền

Người dùng làm việc chủ yếu qua TUI, từ đặt cấu hình tới ra lệnh dựng. CLI không phải giao diện phụ mà là **nền** mà TUI gọi, và là đường cho debug cùng tự động hoá. Hệ quả bắt buộc: mọi lệnh CLI phải chạy được **không cần tương tác**, không hỏi gì giữa đường, và mọi thứ TUI hỏi phải được ghi vào `config.json` trước khi chạy. TUI không giữ trạng thái riêng.

## 6. Nợ kiến trúc đã biết

`tools/prod_shots.py` trộn ba việc trong một file: gọi `ffprobe` và `ffmpeg`, tính hình học Ken Burns cùng phân bổ độ dài, rồi ghi CSV. Hai hàm `durations()` và `kb_for()` là logic thuần và test được, nhưng hiện không import được để test vì nằm cùng file với phần chạm đĩa.

`scripts_v1/clone_project.py` đặt toàn bộ mã ở cấp module và đọc thẳng `sys.argv`, nên **import là chạy**. Adapter buộc phải gọi qua `subprocess` rồi phân tích stdout, tức đang dùng văn bản console làm giao diện lập trình.

Danh sách mười một transition tồn tại ba bản: `TRANS` trong `prod_shots.py`, `TRANS` trong `bench_shots.py`, và `transitions.whitelist` trong `config.example.json`. Ba bản song song sẽ trôi khỏi nhau, đúng như README từng trôi.

Việc phải làm cho từng món nằm ở `TODO.md`.