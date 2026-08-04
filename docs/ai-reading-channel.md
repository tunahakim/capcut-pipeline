# Kênh đọc tài liệu của trợ lý AI — cơ chế và giới hạn

**Cập nhật 03/08/2026.** File này **không nằm trong thứ tự đọc bắt buộc**. Đọc khi cần hiểu vì sao tài liệu có trần kích thước, vì sao trợ lý đôi khi mất nguyên văn giữa phiên, và cách gửi tài liệu cho trợ lý sao cho rẻ nhất. Nội dung ở đây nói về **công cụ**, không nói về CapCut, nên nó tách khỏi `STATE.md` để ảnh chụp dự án không bị pha loãng.

## 1. Ngữ cảnh đo được — đổi một thứ là phải đo lại

Mọi kết luận dưới đây chỉ chắc chắn với đúng bộ bốn này:

- Giao diện web: **genspark.ai**
- Mô hình: **Claude Opus 5**
- Công cụ đọc web của mô hình: **`crawler`**, gọi tới `raw.githubusercontent.com`
- Ngày đo: **03/08/2026**

Đổi web, đổi mô hình, hoặc đổi công cụ đọc thì phải làm lại phép thử ở mục 4 trước khi tin. Ví dụ đã biết: một mô hình khác có thể không tự đếm được số dòng, nên `tools/read_src.py` vẫn giữ cờ bật số dòng dù mặc định là tắt.

## 2. Hai chế độ của `crawler`, và cái bẫy

`crawler` có hai chế độ. Chế độ **đọc thô** chặn cứng **10000 byte** mỗi lượt gọi, và tệ hơn là nó **khai báo sai tổng kích thước**: xin phần đuôi thì nó trả lời file đã hết, trong khi file dài hơn gấp đôi chỗ nó dừng. Đó là nói dối, không phải cắt. Chế độ **markdown** lấy trọn file, nhưng nó cũng có trần, và **đơn vị của trần là token chứ không phải byte**. Đo 03/08/2026 cho ba số: `docs/failures.md` 22296 byte văn xuôi tiếng Việt về **trọn**; `docs/START-HERE.md` 24798 byte về **trọn**; `fixtures/parity-gold/parity_gold_snap.json` 32393 byte **bị cắt**, và lần này công cụ tự khai tường minh, nguyên văn `Document is too large (10544 tokens). Only showing first 10000 tokens.` kèm nhãn `partial_content`. Vậy trần là **10000 token mỗi lượt gọi**, còn số byte tương ứng thì phụ thuộc loại nội dung: JSON ASCII nhiều dấu ngoặc cho khoảng 3,07 byte một token nên nó chạm trần từ khoảng 30 KB, còn văn xuôi tiếng Việt có dấu cho khoảng 2,5 đến 2,8 byte một token nên trần rơi vào khoảng **25 đến 28 KB**. Con số 26 KB của `BUDGET` nằm đúng giữa dải đó, tức nó không tuỳ ý mà là ngưỡng token dịch sang byte cho đúng loại nội dung mà `docs/` chứa. Một hướng đã đóng nhờ số đo này: **không** được nới `BUDGET` chung lên 40 KB, vì một file `.md` tiếng Việt 40 KB rơi vào khoảng 14 đến 16 nghìn token nên chắc chắn bị cắt. Cùng lượt đó đóng thêm một câu hỏi treo trong `README.md`: chế độ markdown **không** làm hỏng khối JSON, nội dung về đúng dạng đọc được, nên nó dùng được cho `.json`; với `.py` thì vẫn **chưa kiểm chứng**.

Vì vậy luật là **mỗi file đúng một lần, chế độ markdown**. Đã thử và loại: đường `?plain=1` trả về trang giao diện GitHub; `cdn.jsdelivr.net` và `raw.githack.com` trả byte đã nén mà công cụ không giải được; GitHub contents API vừa tốn vừa cũng bị cắt.

## 3. Cơ chế cắt thật sự — nó nhắm vào kết quả công cụ, không nhắm tin nhắn

Đây là phát hiện quan trọng nhất, và nó lật lại giả thuyết cũ.

Nội dung fetch về **đủ** ngay lượt đầu. Nhưng chỉ sau một hai lượt trao đổi, khúc giữa của nó **bị xoá khỏi ngữ cảnh** của trợ lý, còn đầu và đuôi vẫn nguyên — nên kết quả trông y như đã đọc đủ. Chỗ bị xoá để lại một dấu vết đọc được, đại ý *"đã bỏ N ký tự của kết quả công cụ lượt trước để tiết kiệm ngữ cảnh, chạy lại công cụ nếu cần bản đầy đủ"*.

Ba điều suy ra từ chính dấu vết đó. Một, cơ chế nhắm vào **kết quả công cụ**, không nhắm tin nhắn người dùng. Hai, nó chỉ áp cho lượt **đã cũ**, khớp với quan sát rằng lần đọc đầu luôn đủ. Ba, nó bỏ đi vì coi kết quả fetch là thứ **lấy lại được**; tin nhắn người dùng thì không lấy lại được, nên có lý do thiết kế để không bỏ.

Hệ quả cho trợ lý: **dấu vết đó là tín hiệu duy nhất đáng tin** về việc mình đang thủng. Cảm giác "tôi vẫn nhớ file đó" thì không đáng tin — đã ghi nhận cả hai kiểu sai trong cùng một phiên, vừa dựng lại đúng nguyên văn một đoạn đã mất, vừa phủ nhận sự tồn tại của một script có thật.

## 4. Phép thử canary — phương pháp để đo lại về sau

Cách làm, 03/08/2026. Người dùng dán toàn văn `docs/TODO.md` vào hội thoại, chèn thêm **ba dòng canary** là ba chuỗi ngẫu nhiên do chính người dùng đặt, chuỗi mà trợ lý chưa từng thấy nên không thể tái tạo từ bản fetch cũ. Ba mốc đặt ở đầu, giữa và cuối vùng mà trợ lý đã tự khai là bị mất sau khi fetch. Ba mốc chứ không một, để nếu chỉ một phần sống sót thì còn biết phần nào. Sau đó tiếp tục làm việc bình thường, có gọi `crawler` xen giữa, và mỗi lượt trợ lý báo lại còn thấy canary hay không.

Kết quả: sau **bốn lượt** và **ba lần fetch** xen giữa, cả ba mốc còn nguyên văn và nguyên vị trí, trong khi kết quả `crawler` mất khúc giữa chỉ sau một lượt. Kèm một phép thử phụ đạt: trợ lý đoán đúng cả bốn số dòng của một file được dán **không** kèm số dòng, nên `read_src.py` mặc định không cần in số dòng.

Khi lặp lại phép thử, đừng dùng nội dung có sẵn trong repo làm mốc, và đừng để mốc duy nhất ở đoạn đuôi file, vì đuôi là vùng sống sót tốt nhất kể cả khi đã bị cắt.

## 5. Mô hình làm việc ba tầng

Suy ra từ mục 3 và 4:

- File **làm việc xuyên suốt phiên**: người dùng **dán thẳng** vào hội thoại. Không bị cắt, nên đây là cách duy nhất giữ được nguyên văn tới cuối phiên.
- File **đọc một lần rồi thôi**: để trợ lý **tự fetch**, đỡ công người dùng. Chấp nhận rằng nguyên văn sẽ mất sau một hai lượt, nên phải dùng ngay trong lượt đó.
- Chỉ cần **một đoạn ngắn**: dùng `tools/read_src.py` có `--grep`, hoặc một lệnh `Select-String`, thay vì kéo cả file.

Trần **26 KB** vì thế không còn là ranh giới sinh tử, nhưng nó **vẫn được giữ**, và từ 03/08/2026 nó được khai làm **ba lớp** trong `PER_FILE_BUDGET` của `tools/docs_audit.py`, mỗi lớp một lý do khác nhau. Lớp **fetchable** giữ mặc định 26 KB, gồm mọi file trợ lý có thể phải tự fetch giữa phiên, tức `research-log/`, `procedures.md`, `model.md`, `reference-catalog.md`; ở đây trần có nghĩa kỹ thuật thật vì vượt nó là bị cắt. Lớp **dán** được nới lên 40 KB kèm lý do ghi ngay tại chỗ khai: `scripts.md` sinh tự động nên dài theo số script, còn `reference.md` và `failures.md` là sổ tra dày lên theo kiến thức đã đo được; ba file này thuộc tầng dán ở mục 5 nên không dính ngưỡng token, và chặn chúng ở 26 KB là chặn sai chỗ. Lớp **chống phình** thì chật hơn mặc định và **không liên quan gì tới fetch**: `STATE.md` và `TODO.md` cùng 15 KB. Bốn file cửa vào vẫn giữ trần chật, nhưng lý do đã đổi: không phải vì fetch mà vì phiên nào trợ lý cũng đọc nguội chúng từ đầu phiên, nên mỗi KB ở đó là token trả lại mãi. Luật vận hành rút ra ở đây quan trọng hơn mọi con số trên: **cắt chữ để tụt xuống dưới trần là việc không tạo ra giá trị nào cho pipeline**, nên khi một file thuộc lớp dán chạm trần thì đường xử lý là khai trần riêng hoặc tách file theo chủ đề, chứ không phải viết lại câu văn cho ngắn.

Bốn file cửa vào `README.md`, `START-HERE.md`, `STATE.md`, `TODO.md` vẫn phải nằm dưới trần fetch-an-toàn, vì đầu phiên trợ lý đọc nguội khi chưa có ai dán gì cho nó.

## 6. Đường thứ ba, bỏ qua toàn bộ vấn đề này

Agent chạy trực tiếp trên máy và đọc file từ ổ đĩa thì không dính trần lẫn cắt. Việc phẫu thuật tài liệu hàng loạt hợp với loại đó hơn. Trần vẫn giữ để kênh đọc qua GitHub không hỏng.

## 7. Đối chiếu byte và trần đo bằng công cụ

`python tools/repo_bytecheck.py` tự gọi GitHub contents API theo từng thư mục, đối chiếu với file trên đĩa, so `HEAD` cục bộ với `main` trên GitHub để bắt trường hợp quên pull, rồi in đúng năm dòng. Đó là lý do không ai nên gọi contents API bằng công cụ fetch: phản hồi JSON tốn chừng một KB cho mỗi file mà gần hết là URL không ai dùng, và bản thân nó cũng bị cắt như mọi thứ khác. Số byte của blob chỉ nên tồn tại bên trong script chạy trên máy.

Phép đối chiếu byte có **trần chi phí một lượt**: chạy đúng một lần, sạch thì đi tiếp ngay. Khớp tuyệt đối hoặc giải thích được bằng ký tự CR thì im lặng đi tiếp; lệch nhỏ mà không giải thích được thì báo đúng một dòng rồi vẫn làm việc tiếp; chỉ dừng hẳn khi thiếu file trên đĩa hoặc lệch đủ lớn để nghi mất đoạn. Đừng đuổi theo lệch một byte, vì có hai ca dương tính giả đã biết. `reference/describe.json` chứa đúng một ký tự CR nằm trong nội dung nên phép trừ CR báo lệch mà file vẫn nguyên vẹn. Và `tools/docs_audit.py` đếm byte trên đĩa có tính CR, nên với file CRLF nó báo lớn hơn blob đúng bằng số dòng; lệch về phía cảnh báo sớm nên vô hại.

Chế độ markdown của công cụ fetch **chuẩn hoá lại định dạng**, nên tuyệt đối không dùng kết quả fetch để so byte. Muốn so byte thì dùng `repo_bytecheck.py` chạy trên đĩa.

Trần kích thước kiểm bằng `python tools/docs_audit.py`, và từ 03/08/2026 lệnh đó **báo lỗi** khi có file vượt trần chứ không chỉ in nhãn, nên `--baseline` không còn chốt được một mốc chuẩn bẩn. Muốn cho một file vượt trần thì thêm trần riêng tường minh cho nó vào `PER_FILE_BUDGET` kèm lý do, để việc vượt trần là quyết định có ghi lại.

Về cỡ tài liệu: đừng tách quá nhỏ, vì nhiều file vụn khó kiểm soát hơn vài file vừa. Nhắm 10 đến 20 KB mỗi file, chỉ tách khi vượt trần.
