# 05/08-1 — docs_patch có probe, hộp đồ nghề hiện ra đầu phiên

**Tóm tắt:** Trả nợ công cụ trọn cụm Một phần đầu: `tools/docs_patch.py` lên tám op và mười lăm ca selftest với mã thoát 3 đã nghiệm thu, thêm `--probe` cùng `content_file` để tách phép đo neo khỏi lượt viết nội dung, và `tools/scripts_index.py` có `--brief` với `--find` để trợ lý biết hộp đồ nghề tồn tại ngay từ lượt đầu.

**Phiên:** 00:26 khuya

## Selftest tụt xuống 6 trên 7 ngay lượt kiểm đầu phiên

Ca `vuot-tran` mong mã thoát 2 nhưng nhận 0. Nguyên nhân không phải tool mất phép kiểm: ca thử chèn cứng 3000 byte, đủ vượt trần 15 KiB cũ của `docs/STATE.md` nhưng không còn đủ sau khi trần được nới lên 25 KiB ngày 04/08. Ca thử đang giữ bản sao thứ hai của một sự thật mà nguồn thật nằm ở `PER_FILE_BUDGET`, nên hai bản lệch nhau đúng như luật mục 5 của `docs/START-HERE.md` cảnh báo. Sửa bằng cách cho ca thử tự tính lượng chèn từ trần hiện hành, khi đó nâng trần bao nhiêu lần nữa nó vẫn bắt được. Bài học rộng hơn: một phép thử neo vào hằng số chép tay sẽ mục theo thời gian mà không ai hay, và nó mục theo hướng im lặng cho qua chứ không theo hướng báo động.

## Ba câu hỏi chốt bằng cách đọc mã

Op `replace` khớp nguyên văn tuyệt đối, chỉ chuẩn hoá kiểu xuống dòng ở tầng đọc file, không nới lỏng khoảng trắng. Op `replace_between` đếm sentinel trên toàn thân file và đã có mã chặn ca đảo chiều lẫn ca chồng lấn. Nhánh mã thoát 3 có mã thật nhưng **không** tự chạy lệnh khôi phục, nó chỉ in tên file để người dùng tự chạy; docstring cũ viết như thể tool tự làm, đã sửa.

## Mã thoát 3 nghiệm thu hai lần trong một lượt

Cách dựng ca thử: thay một anchor duy nhất bằng một chuỗi đã có sẵn ở chỗ khác trong file nháp, khi đó kiểm trước sạch vì anchor khớp 1 còn kiểm sau thất bại vì chuỗi mới đếm được 2. Ca thử đạt đúng dự đoán. Cùng lượt đó một lượt vá thật cũng trả về 3 ngoài ý muốn, và cái ngoài ý muốn có giá trị hơn vì nó lộ ra lỗi thật: op `replace` với nội dung mới rỗng đăng ký phép kiểm sau kiểu đếm bằng một, mà chuỗi rỗng thì đếm ra số lớn. Nay nội dung mới rỗng đi cùng đường với op `delete`.

## Chiều thứ ba của luật mã hoá

Luật chốt ngày 04/08 mới phủ chiều ghi ra và chiều đọc file. Ngày 05/08 lộ ra chiều thứ ba: script cha bắt stdout của script con bằng `subprocess` với `text=True` mà không khai `encoding` thì Python decode theo locale, gặp chữ có dấu là ném lỗi trong thread đọc và trả về chuỗi rỗng. Hậu quả rất khó thấy: bảng selftest vẫn in đủ mười lăm dòng, cột mã thoát vẫn đúng, chỉ cột nhãn sai hết. Hỏng ồn ào ở tầng thread nhưng im lặng ở tầng kết quả. Khai `encoding` UTF-8 cho mọi lệnh bắt output là hết.

## Quy trình vá tài liệu mới, và cách cũ để quay lại

Cách cũ: một lượt phát trọn đặc tả gồm cả neo lẫn nội dung mới, chạy thử, rồi thêm cờ ghi thật. Nhược điểm không nằm ở số lần gõ lệnh mà nằm ở chỗ mỗi lượt đối đáp gửi lại toàn bộ hội thoại, nên một khối nội dung dài hỏng năm lần thì bị tính tiền năm lượt và chiếm chỗ tới cuối phiên. Cách mới: lượt một chỉ phát đặc tả kế hoạch gồm neo ngắn cộng khoá trỏ tới file nội dung chưa tồn tại, chạy `--probe` cho rẻ; lượt hai mới viết nội dung ra đúng file đó rồi ghi thật. Nội dung nằm trên đĩa chứ không nằm trong lịch sử hội thoại, nên neo hỏng thì chỉ phát lại neo. Nếu cách mới bất cập thì đường về là bỏ khoá trỏ file và quay lại viết trọn đặc tả một lượt, mọi op cũ vẫn giữ nguyên.

## Vì sao năm phiên liền không ai mở danh mục script

Luật cũ viết bằng một trạng thái nội tâm, đọc danh mục khi thấy cần, nhưng không ai thấy cần một công cụ mà mình không biết là có; muốn kích hoạt luật thì phải phát hiện ra một sự vắng mặt, mà vắng mặt thì vô hình. Danh sách tám công cụ hay dùng đặt ở đầu phiên còn làm hại thêm, vì nó tạo cảm giác đã phủ hết trong khi thực tế có 47 script. Danh mục lại nặng gần 30 KB nên có nguy cơ vượt trần fetch, và nó tra xuôi từ tên sang mô tả trong khi nhu cầu thật là tra ngược từ việc sang công cụ. Cách chữa là đẩy chứ không chờ kéo: `--brief` in cả hộp đồ nghề trong khoảng 5 KB và nằm sẵn ở loạt kiểm đầu phiên, `--find` lo phần tra ngược.

## Hai luật bị sửa

Câu hướng dẫn từng bước một bị xoá khỏi mục 8 của `docs/START-HERE.md`, giữ lại đúng mệnh đề cấm gộp khi bước sau phụ thuộc output bước trước. Lý do là chi phí thật của một lượt đối đáp là toàn bộ hội thoại được gửi lại, nên chia nhỏ việc độc lập là tự đốt ngân sách. Luật mã hoá nhận thêm chiều thứ ba nói ở trên.

## Dương tính giả đã đo được

Bộ quét token đường dẫn của `tools/docs_audit.py` bắt mảnh chuỗi định dạng trong mã Python thành tên file thiếu, cụ thể là phần đuôi tài liệu ghép sau một ký tự định dạng, trong khi đuôi txt và json thì lọt. Đây là chặn nhầm chứ không phải bỏ sót, nên hại ít, nhưng nó tốn đúng một lượt sửa đặc tả và đã thành nợ nhỏ.