# Phiên 04/08/2026 lần 4 — trả nợ công cụ: replace_between, mã hoá, ký tự xuống dòng, mục lục nhật ký

**Tóm tắt:** Ba mục nợ công cụ trả trọn trước khi động vào `pipeline/steps/`, theo yêu cầu của người dùng là tool phải tốt trước khi ghi kết quả. `tools/docs_patch.py` thêm op `replace_between` có van `expect_bytes`, selftest lên 7 trên 7; nhánh nhập luật từ bản `tools/docs_audit.py` đã vá chạy được lần đầu sau khi cấp `__file__`, trước đó ném `NameError` nên bản viết ở phiên 3 chưa từng chạy. Tám ca đo mã hoá bác hướng nâng PowerShell 7: nguyên nhân hỏng chữ có dấu là Python tụt về cp1252 khi stdout bị pipe, không phải shell. Viết `tools/nl_audit.py` quét 142 file, bắt 2 file lẫn CRLF với LF và 1 file UTF-16LE. Viết `tools/rlog_index.py`, chèn ngược dòng tóm tắt vào 25 file nhật ký.

**Phiên:** 19:30 tối tới 23:30 khuya

## Vì sao đổi lộ trình

Kế hoạch đầu phiên là `pipeline/steps/`, nhưng người dùng đổi thứ tự sang cụm nợ công cụ với lý do đúng: cả hai tool phải sửa đều là tool của khâu kết phiên, tức đúng chỗ ngữ cảnh mỏng nhất, nên sửa lúc còn 90% rẻ hơn nhiều lần sửa lúc còn 10%. Phiên này tiêu gần hai phần ba ngữ cảnh cho ba mục nợ, nhưng ba lần van an toàn đã chặn được một lượt ghi sai, và hai lỗi có sẵn từ phiên trước bị phơi ra thay vì chờ tới lúc không còn chỗ xoay.

## Mã hoá: chẩn đoán cũ sai, cách chữa mới rẻ hơn

`docs/TODO.md` ghi việc là nâng PowerShell rồi bỏ luật in ASCII, tức giả định nguyên nhân là PowerShell 5.1. Giả định đó sai. `tools/enc_probe.py` đo tám ca với chuỗi thử 20 ký tự khai trước bằng codepoint, và kết quả cho thấy console trực tiếp đã sạch sẵn ở code page 437 vì Python 3.6 trở lên ghi bằng `WriteConsoleW`; chỗ hỏng chỉ xuất hiện khi stdout bị pipe, lúc đó Python chọn `cp1252` theo locale và ném `UnicodeEncodeError`. PowerShell 7 không sửa khâu đó vì khâu đó không thuộc shell. Cách chữa là gọi `sys.stdout.reconfigure` trong script, cộng `[Console]::OutputEncoding` nếu muốn output qua pipe đọc được. Không có tác dụng phụ nào lên công cụ native.

Một sai lệch đáng ghi: ở lượt đầu probe báo `NGUON HONG`, và trợ lý dự đoán đó là dấu hiệu heredoc bị méo lúc dán. Dự đoán sai. So từng codepoint thì 19 trên 20 ký tự trùng khít, ký tự lệch là do chính trợ lý khai nhầm `1EED` là chữ ữ trong khi đó là chữ ử. Bằng chứng lại chứng minh điều mạnh hơn: đường đi từ hội thoại qua heredoc tới đĩa sạch, và probe đủ nhạy để bắt lệch một codepoint trên hai mươi.

Một quan sát chưa giải thích được, ghi lại nguyên trạng: Python đọc `GetConsoleOutputCP` ra 65001 sau khi đặt `[Console]::OutputEncoding` sang UTF-8, nhưng `chcp` ở lệnh kế tiếp báo 437. Hai tầng lệch nhau. Hệ quả thực dụng là đừng dựa vào cấu hình shell, hãy chữa ở phía script, vì phía script là thứ đi theo file qua cả hai máy.

## Ký tự xuống dòng: một lỗi im lặng ba công cụ không thấy

`tools/rlog_index.py` chết ở `docs/research-log/2026-08-01-4-readme-cua-vao.md` vì file đó lẫn 32 CRLF với 5 LF. Thay vì sửa mỗi cái vừa lộ, phiên này quét cả repo bằng `tools/nl_audit.py` mới, và quyết định đó đúng: có 2 file lẫn chứ không phải 1, cái thứ hai là `_deprecated/Test_tool_v2__snap.py` với đúng 1 LF ở dòng 85 giữa 93 CRLF. Trợ lý dự đoán 1 file và không file mã nào bị lẫn, sai cả hai; dự đoán đúng duy nhất là năm dòng LF nằm liền cụm chứ không rải đều, tức dấu vết một lần vá.

Điều đáng lo hơn là ba công cụ đã chạy sạch trên hai file đó mà không thấy gì. Sau khi chuẩn hoá, `git diff` cũng không in dòng nào, chỉ cảnh báo CRLF sẽ bị thay bằng LF; nguyên nhân là khai báo `text=auto eol=lf` ở tầng thuộc tính git nên index luôn giữ LF, chứ không phải `core.autocrlf` như trợ lý đoán ban đầu. Nghĩa là lượt chuẩn hoá này là chuyện của riêng ổ đĩa máy lab.

Cùng lượt quét lộ thêm `reference/describe.json` không decode được UTF-8, byte đầu `0xff`, tức UTF-16LE có BOM. Đó chính xác là dấu vết của toán tử chuyển hướng trong PowerShell 5.1 mà tài liệu đã cấm từ lâu. Cố ý không sửa trong phiên này vì đổi mã hoá một file danh mục là đổi nội dung, và nếu có script nào đang đọc nó bằng mã hoá cũ thì việc chuyển sẽ làm chết script đó âm thầm.

## replace_between và hàm chưa từng chạy

Op mới nhận hai sentinel, mỗi cái phải khớp đúng 1 lần, vùng bị thay gồm cả hai sentinel, và đặc tả bắt buộc khai `expect_bytes` để lệch quá biên độ thì dừng. Hai ca âm bắt đúng: sentinel cuối khớp nhiều lần, và vùng thật 3603 byte so với dự kiến 50.

Lượt vá thật đầu tiên sau đó bị chặn bằng `NameError: name '__file__' is not defined`. Đường nhập trần từ bản đã vá trong bộ nhớ đã tồn tại từ phiên 3 dưới tên `budgets_from_text`, docstring khai nó như tính năng có thật, nhưng nó chưa bao giờ chạy được vì namespace của `exec` thiếu `__file__`. Đúng bài học đã lặp nhiều lần trong dự án: mã có mặt không phải bằng chứng mã chạy được. Sau khi cấp `__file__`, nhánh đó chạy lần đầu và được dùng ngay trong lượt kết phiên để nới trần `docs/STATE.md` từ 15 lên 25 KB có hiệu lực trong cùng một lượt ghi.

## Mục lục nhật ký

`tools/rlog_index.py` có hai chế độ: sinh bảng, và chèn ngược. Thứ tự bắt buộc là chèn ngược trước, vì trước đó nguồn duy nhất của ô tóm tắt chính là cái bảng sắp bị ghi đè. Chèn ngược 25 file, kiểm sau 25 trên 25, không file nào vượt trần, và quét lại newline vẫn sạch.

Bảng chưa được sinh lại trong phiên này, cố ý: cột Phiên đang giữ thông tin buổi như 04/08 tối, và đó là nguồn duy nhất còn lại của thông tin ấy. Sinh bảng bây giờ sẽ xoá vĩnh viễn buổi trước khi có chỗ nào lưu nó. Người dùng đề xuất lấy giờ từ ngày tạo file, và phép đo cho thấy cách đó chỉ tin được khi ngày của `CreationTime` trùng ngày trong tên file: file ngày 28/07 mang ngày tạo 01/08, file ngày 01/08 mang ngày tạo 02/08, còn file ngày 04/08 thì đúng.
