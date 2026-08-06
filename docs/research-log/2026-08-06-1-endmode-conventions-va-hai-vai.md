# 06/08-1 — end_mode cho docs_patch, tiếng Việt ra console, và mô hình hai vai

**Tóm tắt:** Đóng `end_mode` cùng probe tuần tự cho `tools/docs_patch.py`, chuyển mọi câu văn xuôi in ra console sang tiếng Việt có dấu, dựng `docs/conventions.md` làm nơi ở của luật thao tác, và đổi cách làm việc sang hai vai điều phối cùng thực thi.

**Phiên:** 09:26 sáng

## Việc đã làm

Thêm khoá `end_mode` cho op `replace_between` của `tools/docs_patch.py` và đảo mặc định sang không nuốt neo cuối, gộp cùng lượt với việc sửa nhánh probe để nó dựng bản mới tuần tự trong bộ nhớ thay vì đo từng edit độc lập trên bản gốc. Hai thứ đó là cùng một lỗi bị tách làm hai mục, và ca selftest âm gồm hai edit mà edit trước xoá neo của edit sau không thể đạt nếu thiếu nửa sau. Selftest đi từ 22 lên 27 ca, hai ca then chốt `between-nuot-neo-cuoi` và `probe-tuan-tu-am` đều đạt. Một lượt riêng sau đó chuyển mọi câu văn xuôi in ra console sang tiếng Việt có dấu, giữ nguyên bốn nhóm chuỗi máy đọc.

Dựng `docs/conventions.md` làm nơi ở của luật thao tác, để `docs/START-HERE.md` không phình thêm khi nó đang sống bằng miễn trừ trần. Cùng lượt xoá bốn mục đã đóng khỏi `docs/TODO.md`, chèn mục Ưu tiên 0 và nới tạm trần file đó lên 30 KB.

## Ba lần trượt, đều lặp lại được

Lượt apply đầu tiên bị chặn ở kiểm trước và không ghi file nào, vì ba dòng báo thiếu đường dẫn tới một file mới chưa khai trong `PLANNED` và một dòng báo vượt trần. Bài học đã ghi thành luật: probe sạch không bảo chứng apply chạy.

Script sinh spec dừng đúng chỗ khi phải chèn tự động vào một set literal có phần tử cuối nằm cùng dòng với dấu đóng: nó từ chối đoán mò và thoát mã 1 mà không ghi spec.

Một script khác nổ khi đọc bảng trần bằng `ast.literal_eval`, vì hàm đó không đánh giá được phép nhân. Không liên quan phiên bản Python.

## Quyết định

Bỏ hẳn lưới lọc dò dòng in còn thuần ASCII sau khi file đã sạch: nó in phần lớn là nhãn máy đọc hợp lệ nên tỷ lệ nhiễu quá cao. Điều kiện dựng lại là lọt lỗi ngôn ngữ lần thứ hai, khi đó làm thành một nhánh trong `tools/py_audit.py`.

Đổi cách làm việc sang hai vai: một phiên điều phối đọc trọn bốn file cửa vào và soạn prompt, nhiều phiên thực thi rời chỉ nhận ngữ cảnh đã cấp. Lý do là bốn file cửa vào ngốn phần lớn ngân sách của mọi phiên trong khi chỉ một phiên cần nắm chúng.
