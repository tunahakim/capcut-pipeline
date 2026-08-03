# 03/08/2026 phiên 3 — tối ưu kênh đọc tài liệu của trợ lý

Phiên này không chạm CapCut. Mục tiêu duy nhất: cắt chi phí ngữ cảnh của khâu "AI đọc tài liệu và tự kiểm đã đọc đủ chưa", vốn ngốn gần hết ngữ cảnh đầu phiên mà không sinh ra kết quả nào.

## Đo được về cách fetch

Chế độ đọc thô của công cụ fetch chặn cứng ở 10000 byte **và khai báo sai tổng kích thước**: với `docs/START-HERE.md` (blob 22358 byte) nó báo body chỉ dài 9105 byte, rồi trả mã 416 "hết dữ liệu" khi xin phần đuôi. Đây là kiểu hỏng nguy hiểm hơn cắt đuôi thường, vì nó tự khẳng định là đã đọc đủ. Chế độ markdown mặc định của cùng URL lấy trọn file trong một lần gọi. Ba đường khác đã thử và loại: `github.com/.../blob/main/<file>?plain=1` trả về trang giao diện GitHub chứ không phải nội dung; `cdn.jsdelivr.net` lỗi giải nén brotli; `raw.githack.com` trả byte đã nén. **Chưa kiểm chứng:** chế độ markdown chuẩn hoá định dạng nên không dùng để so byte, và chưa thử trên file `.py` hay `.json`.

Đọc GitHub contents API bằng công cụ fetch là lãng phí lớn nhất đã tìm ra: chừng một KB JSON cho mỗi file mà gần hết là URL không dùng, listing thư mục gốc 13245 byte lại còn bị cắt. Chuyển hẳn phép đối chiếu byte vào script chạy trên máy.

## Đối chiếu byte

`tools/repo_bytecheck.py` duyệt contents API theo từng thư mục, so với file trên đĩa, so `HEAD` cục bộ với `main` trên GitHub, in đúng năm dòng. Kết quả trên máy lab: 129 blob, khớp 129, trong đó 38 file dùng CRLF trên đĩa, lệch 0, thiếu 0, 20 request.

Luật so byte phải là `disk == blob` **hoặc** `disk-CR == blob`. Chỉ trừ CR là sai: `reference/describe.json` có đúng một ký tự CR nằm trong nội dung nên phép trừ báo lệch 1 byte trong khi `disk` bằng `blob` tuyệt đối. Đây là dương tính giả thứ tám của họ CRLF. Ghi thêm: `docs_audit.py` đếm byte đĩa có tính CR nên với file CRLF nó báo lớn hơn blob đúng bằng số dòng, lệch về phía cảnh báo sớm nên vô hại.

Trần chi phí mới cho cả khâu này: **một lệnh, một lượt**. Khớp hoặc giải thích được bằng CR thì im lặng đi tiếp; lệch nhỏ không giải thích được thì báo một dòng rồi vẫn làm; chỉ dừng khi thiếu file hoặc lệch đủ lớn để nghi mất đoạn.

## Ba luật mới vào tài liệu

`tools/read_src.py` thay hẳn việc viết lại script trích trong hội thoại. Nó tự đếm dòng, tự áp ngưỡng ba bậc, in rõ chọn nhánh nào và vì sao. Nhờ đó trợ lý không còn phải hỏi "file này bao nhiêu dòng" trước khi quyết định, tức bớt một vòng đối đáp mỗi lần đọc mã. Chạy thử trên chính `repo_bytecheck.py`: 106 dòng, tự chọn in trọn, đúng nhánh.

Thứ tự đọc đầu phiên rút từ bảy file xuống **bốn**: README, START-HERE, STATE, TODO. Còn lại đọc ngay trước việc cần tới. Lý do đo được ngay trong phiên: ngữ cảnh trợ lý bị nén dần, và nó ăn đúng khúc giữa của những file nạp sớm nhất, cụ thể là mục 6 tới 8 của START-HERE và mục "Trần kích thước" của README, trong khi đầu và đuôi còn nguyên nên nhìn vẫn như đã đọc đủ. Đọc sớm là đọc để mất.

Luật công cụ tái sử dụng: đoạn mã sắp phải viết lần thứ hai thì thành script trong `tools/`, commit và push để máy kia dùng được, hội thoại chỉ đưa lệnh chạy. Kèm mệnh đề chống cứng nhắc theo yêu cầu của người dùng: việc một hai dòng thì viết thẳng PowerShell, đừng sinh file chỉ để chạy một lần; ba điều không nới là không nhúng Python vào dòng lệnh PowerShell, không dùng toán tử `>`, và luôn xác nhận lại sau khi sửa.

## Dữ kiện mới cho món nợ "tham chieu La Ma"

Sau khi vá thêm chữ vào README và START-HERE, "tham chieu bat duoc" tăng 636 lên 645 nhưng "tham chieu La Ma" **đứng yên ở 44**, tức nó không đếm theo lượng chữ. Dự đoán chốt trước khi thêm file này: nếu nó đếm theo số file `.md` thì lượt audit kế tiếp phải ra **45**. Vẫn **chưa kiểm chứng** cho tới khi đọc mã `docs_audit.py`.
