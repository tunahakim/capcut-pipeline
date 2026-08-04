# 03/08/2026, phiên tối 2 — đo cơ chế cắt ngữ cảnh, siết `--baseline`

**Tóm tắt:** Đo cơ chế cắt ngữ cảnh của trợ lý: nội dung người dùng dán thẳng **không** bị cắt, chỉ kết quả công cụ fetch mới bị và chỉ ở lượt đã cũ; canary ba mốc sống sót bốn lượt với ba lần fetch xen giữa. Ghi được bộ ngữ cảnh genspark.ai + Claude Opus 5 + công cụ `crawler`, tách thành `../ai-reading-channel.md`. Trần 26 KB đổi lý do từ giới hạn fetch sang chống phình. `docs_audit.py` đưa vượt trần vào khối `VAN DE`, `--baseline` từ chối ghi khi còn vấn đề, mã thoát 2, thêm `--brief`; nghiệm thu hai chiều, mốc chuẩn không đổi dấu thời gian. Đính chính mục khoá Pro: đối chứng dương đã bị xoá cùng phép gỡ nên tiêu chí xong chưa chạy được

Phiên này gần như không chạm vào CapCut. Nó trả lời một câu hỏi hạ tầng đã âm thầm làm chậm mọi phiên trước, và bịt một lỗi đã gây hỏng hai lần trong ngày.

## 1. Câu hỏi mở phiên

Người dùng đặt đúng câu hỏi then chốt: **nội dung do người dùng dán trực tiếp có bị cắt như kết quả fetch không?** Nếu có thì phải giữ trần 26 KB, vì fetch vẫn là đường nhanh nhất. Nếu không thì mô hình làm việc đổi hẳn, và những phiên chỉ ngồi viết lại câu văn cho vừa trần là chi phí bỏ đi được.

Giả thuyết của người dùng là cơ chế tóm tắt, kiểu đọc 50 trang báo rồi giữ bản tổng hợp. Đo ra thì gần đúng nhưng khác một điểm quyết định: không phải tóm tắt lại, mà **xoá hẳn khúc giữa và để lại dấu vết đọc được**. Nhờ dấu vết đó trợ lý tự phát hiện được mình đang thủng thay vì tưởng mình còn nhớ.

## 2. Phép thử canary, và kết quả

Phương pháp đầy đủ ghi ở `../ai-reading-channel.md` mục 4. Kết quả: **canary sống sót trọn bốn lượt** với ba lần `crawler` xen giữa, trong khi kết quả `crawler` mất khúc giữa sau một lượt. Kèm hai dữ kiện phụ.

Một, tên công cụ đọc và chế độ chặn 10000 byte lộ ra từ chính dấu vết cắt, nên bộ ngữ cảnh **genspark.ai + Claude Opus 5 + `crawler`** nay đã ghi được thành văn. Đây là thứ trước đây không ai biết để ghi, và thiếu nó thì mọi luật đọc trong repo đều là luật không có điều kiện áp dụng.

Hai, trợ lý đoán đúng **cả bốn** số dòng của `TODO.md` từ một bản dán **không** kèm số dòng, nên `read_src.py` in số dòng là tiện nghi chứ không phải nhu cầu.

Cảnh giác đáng ghi lại: trong cùng phiên, trợ lý **dựng lại đúng nguyên văn** một câu đã mất khỏi ngữ cảnh, rồi lại **phủ nhận sự tồn tại** của `tools/read_src.py` là script có thật. Sai cả hai chiều, nên độ tự tin của trợ lý không dùng làm thước đo được; chỉ dấu vết cắt mới là tín hiệu cơ học.

## 3. `docs_audit.py`: cảnh báo vượt trần vào khối `VAN DE`

Chẩn đoán: phép so trần nằm trong `report()` và chỉ để in nhãn `VUOT %d%%` ra bảng. Nó chưa bao giờ chạm vào danh sách `problems`, mà `problems` mới là thứ dựng khối `VAN DE`. Còn `--baseline` thì ghi đè mốc chuẩn **vô điều kiện**. Đó là toàn bộ cơ chế của hai lần lỗi trong ngày: mốc chuẩn được chốt lại trong lúc có file đang vượt trần.

Sửa: phép so trần chuyển vào `scan()` để sinh vấn đề loại `VUOT TRAN` — vào `scan()` chứ không phải `report()`, vì `report()` chỉ được phép in, và vì snapshot JSON cũng cần ghi lại vấn đề này. `--baseline` từ chối ghi khi `problems` không rỗng. Mã thoát đổi thành 2 khi có vấn đề, theo quy ước 1-là-không-chạy-được 2-là-có-lệch của `data_manifest.py`.

Cố ý: số byte để trong ô `extra`, **ngoài** khoá so sánh `(kind, src, token)` của `--compare`, nên một file đã vượt trần rồi phình thêm sẽ không bị đếm thành vấn đề mới.

Nghiệm thu hai chiều. Chiều âm: `VAN DE (0)`, mã thoát 0, không làm đỏ thứ gì đang xanh. Chiều dương: dựng một file tạm 27024 byte trong `docs/`, nhận đúng `VUOT 102%`, `VAN DE (1)` có dòng `VUOT TRAN`, mã thoát 2, câu `KHONG ghi moc chuan`, và **dấu thời gian của mốc chuẩn không đổi tới từng giây** trước và sau lượt `--baseline`. Dấu thời gian là bằng chứng, câu in ra chỉ là lời tự khai.

Nhân đó thêm cờ `--brief`: bảng kích thước chỉ in file từ 70% trần trở lên cùng file có trần riêng, phần còn lại gộp thành một dòng đếm; ma trận tham chiếu và danh sách mồ côi chỉ còn con số. Lý do rất cụ thể: người dùng dán output này cho trợ lý mỗi phiên, và riêng khối ma trận chiếm chừng ba phần tư output mà cả phiên không ai dùng tới.

## 4. Món nợ "tham chieu La Ma" — thêm một bằng chứng phủ định

Giả thuyết cũ là dòng đếm này đếm theo số file. Nhật ký phiên trước đã bác. Phiên này có thêm một phản ví dụ rẻ tiền từ chính output: audit đếm **36** file `.md` mà dòng La Mã là **44**. Đếm theo file thì hai số phải bằng nhau. Con số trong `../TODO.md` cũng đã lạc hậu hai bậc, nay sửa lại.

## 5. Đính chính một kết luận cũ

Mục kiểm khoá Pro trong `../TODO.md` viết ở thì hiện tại rằng "nay đã có đối chứng dương thật" là transition `6724227090872275463` trong `v2oracle`. Câu đó nay **sai**: chính phép gỡ ngày 03/08 đã xoá transition ấy khỏi project để chứng minh CapCut chặn export vì nó, nên `resource_id` thì còn ghi lại được mà **mẫu trên đĩa thì không còn**. Tiêu chí xong của mục đó vì thế chưa chạy được cho tới khi có ai thả lại transition đó bằng GUI.

Bài học vận hành, không phải bài học kỹ thuật: lần đó trợ lý báo "xong việc rồi, xoá cũng được" nên người dùng xoá mất đối chứng. **Đối chứng dương là tài sản, không phải rác.** Trước khi xoá một mẫu đã dựng được bằng tay, phải kiểm xem còn mục nào trong `../TODO.md` đang lấy nó làm tiêu chí hoàn thành hay không.

## 6. Lượt vá tài liệu: ba chốt kiểm, ba lỗi bị bắt trước khi vào git

Bản thân lượt vá của phiên này là phép thử cho các chốt vừa dựng, và cả ba chốt đều bắt được lỗi thật.

Một, `../STATE.md` lẫn xuống dòng, 50 CRLF trên 52 LF, nên hàm `rd()` của script vá dừng trước khi ghi file nào. `git diff` rỗng mà `git ls-files --eol` cho `i/lf w/mixed`, tức blob trên GitHub vẫn sạch và chỉ bản trên đĩa bị lẫn; `git checkout -- docs/STATE.md` dựng lại đúng bản blob, LF thuần, 10177 byte. Bài học: khi đĩa và index lệch nhau về xuống dòng thì `git ls-files --eol` mới là lệnh phán xử, không phải `git diff`, vì git chuẩn hoá khi so nên không thấy thứ mà công cụ đọc byte thấy.

Hai, hai chuỗi tài liệu trong script vá bị **hard wrap** quanh mốc 90 ký tự. `docs_audit.py` đếm byte nên không bắt được, và nếu chạy thì hai file mới đã ra đời sai luật ngay từ dòng đầu; chỉ mắt người đọc lại script trước khi chạy mới thấy. Đây là luật bị quên nhiều nhất, và lần này nó bị quên bởi chính lượt viết tài liệu về cách đọc tài liệu.

Ba, ngay lượt `--brief` đầu tiên sau khi vá, khối `VAN DE` báo hai mục: `../TODO.md` 13420 byte vượt trần riêng 12 KB, và một `FILE THIEU` trỏ tới `data\tmp\gen_cc_fixture.py` vì bản TODO mới nhắc file đó bằng tên trần, thiếu đoạn đường dẫn đầu, nên audit đi tìm trong repo và không thấy. Bản TODO ấy đáng ra là bản đã cắt gọn. Nghĩa là phép so trần vừa chuyển vào `scan()` lập tức bắt đúng loại lỗi nó được viết ra để bắt, và bắt chính lượt vá đã sinh ra nó — trước hôm nay chuyện này sẽ trôi qua với một nhãn `VUOT 109%` in ra rồi không ai đọc, và mốc chuẩn lại được chốt bẩn lần thứ ba trong ngày. Lượt cắt thứ hai còn thừa 793 byte và cũng bị chốt tự kiểm trong chính script vá chặn lại, phải cắt lần thứ ba mới lọt.

Chốt thêm một con số cho món nợ La Mã: sau khi thêm hai file mới, audit quét **38** file `.md` mà dòng La Mã vẫn **44**.

Quyết định về trần, ghi lại để phiên sau khỏi bàn lại: giữ trần, nhưng phân tầng theo vai trò file. Bốn file cửa vào giữ trần chật vô điều kiện, vì đầu mỗi phiên trợ lý đọc nguội chúng khi chưa ai dán gì, nên mỗi KB ở đó là token phải trả lại cho mọi phiên về sau — đây là trần chi phí, không phụ thuộc ngưỡng fetch. Phần tài liệu còn lại thì trần chỉ còn là chống phình, và mốc 26 KB đang dựa một phần vào số liệu không rõ nguồn, nên đề xuất nới lên 40 KB sau khi phép thử ngưỡng markdown trong `../TODO.md` cho số đo. Không bỏ trần hẳn: `docs_audit.py` là thứ duy nhất trong repo tự phát hiện tài liệu phình.

