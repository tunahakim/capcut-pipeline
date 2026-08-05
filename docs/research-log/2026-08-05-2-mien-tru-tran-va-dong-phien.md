# Phiên 05/08-2 — miễn trừ trần có hạn, dòng khai Phiên, và một tool đo mã hoá

**Tóm tắt:** Cài cơ chế miễn trừ trần có hạn qua `cap_for()` dùng chung hai tool, hoàn tất dòng khai Phiên cho 26 file nhật ký, và viết `tools/py_audit.py` đo được 136 lỗi mã hoá đang chờ sửa.

**Phiên:** 12:10 trưa

## Việc đã đóng

Ba chỗ của `tools/docs_patch.py`. Ca selftest `md-khong-dau` từng bám vào `docs/TODO.md` và sắp trượt vì trần chứ không vì mục đích của nó, nay chạy trên file `.md` tạm; đây là lần thứ hai một phép thử neo vào trạng thái file khác suýt mục theo hướng im lặng cho qua, sau ca `vuot-tran` hôm 05/08-1. Hai đường đếm neo của `run_probe()` và `apply_edits()` nay gọi chung `do_vung()`, và một hàm thứ hai `doc_than()` cũng được tách vì lệch BOM cùng lệch newline là hai đường riêng đang đồng ý ngẫu nhiên y hệt. Ca `do-vung-mot-duong` không nhìn mã thoát mà so trực tiếp hai con số hai bên in ra, đo được 3603 bằng 3603. `delete_block` gặp khối không có dòng trống phía sau thì dừng bằng mã 2 thay vì xoá tới hết file. Selftest đi từ 15 lên 22 ca.

Miễn trừ trần có hạn. `cap_for(rel, size)` đặt trong `tools/docs_audit.py` làm nguồn sự thật duy nhất, `tools/docs_patch.py` nhập qua `NS_NAMES` thay vì tự đọc lại `PER_FILE_BUDGET` — đúng cái bẫy hai đường song song mà lượt trước vừa đóng. Nghiệm thu bằng bốn lượt chạy cho bốn kết quả khác nhau, tiêm bảng miễn trừ giả qua biến môi trường `DOCS_WAIVERS`, và lượt thứ tư gỡ biến ra phải trùng khít lượt đầu để chứng minh không rò rỉ. Nhân đó neo lại ca `vuot-tran` cũ vào một bảng rỗng, vì nó đang đọc bảng thật và sẽ mục im lặng đúng ngày ai đó cấp miễn trừ cho `docs/STATE.md`. Đường `CON HAN` sau đó chạy thật trên `docs/START-HERE.md`: file đang vượt trần vẫn ghi được và chỉ nhận một dòng cảnh báo kèm lý do cùng ngày hết hạn.

Dòng khai Phiên. Bảng `INDEX.md` là nguồn duy nhất của thông tin buổi nên mọi thứ phải chèn ngược trước khi sinh lại bảng, và cột buổi không đồng nhất nên tool chấp nhận cả dòng không buổi, nhãn phiên bản kiểu `(v5)`, lẫn buổi viết dài. Giờ lấy từ `CreationTime` chỉ khi ngày trùng tên file, và 9 trên 26 file không thoả nên để trống thay vì bịa. Sau lượt chèn, `dong GIU O CU buoi` về 0, tức bảng không còn là nguồn của bất cứ thứ gì mà chỉ còn là bản sinh ra.

## Bẫy dấu, lần thứ ba

`SUMMARY_KEY` có dấu trong khi docstring của chính file ghi không dấu, đã sửa hôm 05/08-1 sau bốn lượt debug. Lần này `PHIEN_KEY` được chọn có dấu ngay từ đầu và không nới ra để nhận cả hai biến thể, vì nới là cố ý giữ hai bản của một sự thật. Thứ mới là nhánh chẩn đoán: khi không tìm thấy dòng khai, tool quét lại bằng hai bậc so khớp bỏ dấu rồi in số dòng cùng `ascii()` của dòng gần giống kèm câu nói thẳng rằng nhiều khả năng thiếu dấu. Một dòng in đó thay được cả bốn lượt debug, và ca selftest `tom-tat-thieu-dau` giữ cho nó không mục.

## Hai luật làm việc rút ra

Lượt chạy thử ở giữa probe và apply là thừa, và người dùng phát hiện ra chứ không phải trợ lý: `--apply` chạy lại trọn bộ kiểm trước rồi từ chối ghi khi có lỗi, nên nó đã bao gồm lượt chạy thử. Quy trình còn hai bước, probe rồi apply. Bằng chứng là output hai lượt giống hệt nhau, và mã thoát 2 luôn kèm dòng `KHONG SUA FILE NAO`.

Luật gửi output đã vào mục 8 của `docs/START-HERE.md`: mỗi lệnh kèm một dòng nói rõ gửi gì, đạt thì gửi dòng tổng kết cùng các con số đã dự đoán trước, hỏng thì gửi khối lỗi cộng mười dòng ngay trước nó. Lý do là người dùng đã hai lần phải gửi trọn output vì mô tả dấu hiệu đạt viết bằng văn xuôi dài, và một trong hai lần đó gồm bốn bảng gần như y hệt nhau.

## Công cụ tự phản ánh

Theo đề nghị của người dùng, `tools/docs_patch.py` nay có `--example` in spec mẫu hợp lệ cho cả tám op, và mọi lượt thoát mã 1 vì spec sai tự nhắc chạy lệnh đó. Lý lẽ: rủi ro thật không phải hình dạng JSON, vì bảng `NEED` đã kiểm đủ khoá bắt buộc, mà là người viết spec không biết luật tồn tại. Cùng lý lẽ đó đã sinh ra `--brief` của `tools/scripts_index.py` hôm 05/08-1.

Hai dương tính giả của bộ quét đường dẫn lộ ra trong phiên: tên file nhật ký giả do selftest tạo, và tên file ví dụ trong chính spec mẫu. Cả hai chữa bằng `allow_paths` chứ không sửa mã, vì tool đang làm đúng việc của nó. Nhân đó bỏ hẳn cảnh báo `OK-BASENAME` cho file `.py` và gộp trùng lặp, vì token trần trong mã nguồn gần như luôn là tên biến; mười dòng cảnh báo về `INDEX.md` trong một lượt là bằng chứng.

## Việc chưa làm và vì sao

`tools/repo_bytecheck.py` nuốt lỗi 403 vẫn nguyên. Đầu phiên nó chạy sạch, 152 blob, HEAD trùng `origin/main`, nên trợ lý hạ ưu tiên — và đó là quyết định sai theo đúng luật của dự án, vì tool chạy đúng hôm nay không chứng minh gì về đường lỗi. Mục 6 rút gọn `docs/START-HERE.md` cũng chưa làm, nhưng lần này việc hoãn có dấu vết máy đọc được: một mục miễn trừ hết hạn ngày 12/08/2026, quá hạn thì mã thoát khác 0 và món nợ tự quay lại đòi.

`tools/py_audit.py` viết xong và chạy được, đo 77 file `.py` ra 136 lỗi trên 74 file. Không sửa gì trong phiên này vì ngân sách ngữ cảnh không đủ, và sửa vội một trăm chỗ mã hoá là cách tốt nhất để tạo ra lỗi im lặng mới. Hai điều phải kiểm trước khi tin con số: `_deprecated/` chưa bị loại trừ, và nhánh đoán hard wrap đang báo cả hai tool vừa nghiệm thu sạch.
