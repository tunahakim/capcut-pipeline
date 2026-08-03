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

`crawler` có hai chế độ. Chế độ **đọc thô** chặn cứng **10000 byte** mỗi lượt gọi, và tệ hơn là nó **khai báo sai tổng kích thước**: xin phần đuôi thì nó trả lời file đã hết, trong khi file dài hơn gấp đôi chỗ nó dừng. Đó là nói dối, không phải cắt. Chế độ **markdown** lấy trọn file; đo được một lượt gọi lấy đủ file 23,7 KB không đứt khúc.

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

Trần **26 KB** vì thế không còn là ranh giới sinh tử. Nhưng nó **vẫn được giữ**, vì lý do đã đổi: giữ file vừa tầm để còn kiểm soát được, và chống phình. Muốn một file vượt trần thì thêm trần riêng tường minh cho nó vào `PER_FILE_BUDGET` trong `tools/docs_audit.py` kèm lý do, để việc vượt trần là một quyết định có ghi lại chứ không phải trôi dạt. Trần riêng của `STATE.md` và `TODO.md` **không liên quan gì tới fetch** — hai file đó tự khai lý do là chống phình, nên chúng giữ nguyên vô điều kiện.

Bốn file cửa vào `README.md`, `START-HERE.md`, `STATE.md`, `TODO.md` vẫn phải nằm dưới trần fetch-an-toàn, vì đầu phiên trợ lý đọc nguội khi chưa có ai dán gì cho nó.

## 6. Đường thứ ba, bỏ qua toàn bộ vấn đề này

Agent chạy trực tiếp trên máy và đọc file từ ổ đĩa thì không dính trần lẫn cắt. Việc phẫu thuật tài liệu hàng loạt hợp với loại đó hơn. Trần vẫn giữ để kênh đọc qua GitHub không hỏng.
