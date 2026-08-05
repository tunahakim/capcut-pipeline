# 04/08/2026 phiên 1 — nhãn KIEM, cảnh báo mất mát của shots_dump, rút gọn README

**Tóm tắt:** Đóng nốt phần tài liệu: `read_src.py` bỏ số dòng mặc định thêm `--linenum`; nhãn `[KIEM: ...]` cho 43 script thành cột riêng của `scripts.md` kèm quy ước in tại chỗ, phân bố 12 that / 8 test / 2 mot lan / 21 chua; `shots_dump.py` cảnh báo hai mức thứ bị mất khi dump ra CSV, nghiệm thu 3/3 trên `fxprobe01`, `testV3`, `testV4`; `README.md` rút từ 10536 còn 6208 byte, năm mảnh chỉ có ở đó chuyển thành mục 7 của `ai-reading-channel.md`; thêm `tools/rlog_index_trim.py` chống phình mục lục; xoá 42 file rác và project `fxlab01`. Đo được: mở project bằng GUI làm `draft_content.json` đổi 33 byte dù không sửa gì
**Phiên:** 09:30 sáng

Phiên làm việc trên máy lab, không chạm máy render, không export. Mở đầu bằng nhận xét của người dùng rằng cả năm phiên ngày 03/08 đều không có tiến triển về tự động hoá; đối chiếu `INDEX.md` xác nhận đúng: bốn trên năm phiên là công cụ để đọc tài liệu và đo chính kênh đọc đó. Trợ lý đề xuất chuyển thẳng sang Ưu tiên 1, người dùng chọn dứt điểm phần tài liệu trước rồi mới phát triển tiếp, nên phiên này đóng nốt các món tài liệu còn treo.

## Việc đã làm

`tools/read_src.py` chuyển mặc định sang không in số dòng, thêm cờ `--linenum` để bật lại, `--grep` vẫn tự bật vì trích dòng mà thiếu số dòng thì vô dụng. Bỏ hai lệnh `print(out[1])` và `print(out[3])` định vị header bằng chỉ số, đổi sang biến, vì chèn thêm một dòng header sẽ làm chúng in sai âm thầm. Header thêm hậu tố khai `so dong: co` hoặc `khong` để nghiệm thu đọc được ngay trên console.

Nhãn mức kiểm chứng: chèn hậu tố `[KIEM: ...]` vào cuối docstring của cả 42 script bằng một script tự dò vị trí dấu đóng docstring qua `ast`, kiểm `compile()` và kiểm lại nhãn nằm trong docstring sau khi chèn. `tools/scripts_index.py` tách nhãn thành cột riêng, giá trị lạ thì hiện kèm dấu hỏi, thiếu khai thì hiện `chua`, và tự in quy ước bốn giá trị vào đầu vùng sinh tự động của `scripts.md` — đặt quy ước cạnh bảng để nó không trôi dạt như khi để ở file khác.

`tools/shots_dump.py` nay khai rõ cái gì mất khi dump draft ra CSV. Trước khi viết, phép đo trên năm project cho thấy câu chữ của `TODO.md` tự mâu thuẫn: yêu cầu cảnh báo mọi track không phải video, trong khi nghiệm thu đòi `testV3` im lặng, mà `testV3` có track audio. Thiết kế chốt lại thành hai mức, và `material_animations` cố ý để ở mức ghi chú chứ không giấu vào danh sách vô hại, vì nó đúng là thứ CSV không giữ.

`README.md` rút gọn: trước khi xoá, đối chiếu với `ai-reading-channel.md` phát hiện năm mảnh chỉ có ở README, gồm luật `docs_audit` báo lỗi cứng, mô tả `repo_bytecheck.py`, toàn bộ quy tắc CR với hai ca dương tính giả đã biết, ghi chú markdown chuẩn hoá định dạng nên không dùng để so byte, và hướng dẫn nhắm 10 đến 20 KB mỗi file. Năm mảnh đó chuyển thành mục 7 của `ai-reading-channel.md` trước, rồi README mới rút. Đây là chuyển chỗ, không phải xoá.

`tools/rlog_index_trim.py` mới, giữ bảng `INDEX.md` ở tối đa N phiên gần nhất và đẩy phần cũ sang `INDEX-archive.md`, mặc định chạy thử không ghi gì.

Dọn dẹp: xoá 42 file rác trong `data\tmp\` và xoá project `fxlab01` trong thư mục draft. Sáu file được cố ý giữ lại, lý do ghi trong `TODO.md`.

## Điều học được

Mở một project bằng GUI CapCut là ghi lại `draft_content.json` kể cả khi không sửa gì, đo được +33 byte trên `fxprobe01`. Đây là bằng chứng trực tiếp cho luật cấm chạy lệnh CLI khi CapCut đang mở.

Chốt thứ hai của script vá, lệch một chỗ là không sửa file nào, đã chặn ba lần ghi hỏng trong phiên: một lần anchor viết thiếu dấu tiếng Việt, một lần chạy lặp trên file đã sửa, và một lần escape `\n` bị nhân đôi khi qua here-string PowerShell nên anchor thành chuỗi backslash-n. Cả ba lần không file nào bị đụng. Ca thứ ba đáng nhớ vì cùng một lỗi escape cũng làm hàm dò CRLF luôn trả 0, tức nếu anchor kia viết đúng thì file CRLF đã bị chèn dòng LF mà không ai biết.

Kênh dán được xác nhận trọn một phiên: nội dung người dùng dán giữ nguyên văn từ đầu tới cuối, kết quả `crawler` mất khúc giữa sau một lượt.

## Còn treo

Hai mươi mốt nhãn `chua` cần chấm lại bằng bằng chứng; hướng rẻ là grep tên script trong nhật ký chứ không bắt mô hình đọc trọn lịch sử. `INDEX.md` vẫn tăng cho tới khi chạm 30 phiên rồi mới phẳng. Nợ `bgblur_frames.py` và `frame_audit.py`, cùng việc thả lại transition Pro để dựng lại đối chứng, chuyển sang phiên sau.
