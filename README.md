# capcut-pipeline

Bộ công cụ tự động hoá dựng video documentary dài 55–70 phút bằng **CapCut Desktop 9.1.0** và **capcut-cli 0.15.0**, trên Windows. Đầu vào là một bảng metadata shot cộng file narration và file SRT; đầu ra là một project CapCut đã dựng sẵn, người dùng mở lên xem lại, chỉnh tay chỗ cần nhấn, rồi bấm Export.

Đây là **phòng thí nghiệm đang hoạt động**, không phải công cụ đã phát hành. Repo tồn tại để hai máy dùng chung một nguồn sự thật, và để một trợ lý AI đọc được toàn bộ dự án mà không cần ai dán tài liệu cho nó.

## Nếu bạn là AI

Đọc `docs/START-HERE.md` trước mọi file khác; nó cho bạn thứ tự đọc, luật bất biến và cách làm việc với người dùng. Nhưng đọc mục **Trần kích thước tài liệu và luật đọc file bị cắt** ngay bên dưới trước đã, vì luật đó áp dụng ngay từ lần fetch đầu tiên, kể cả lần fetch chính `docs/START-HERE.md`.

README này cố ý **không** tóm tắt nội dung của `docs/START-HERE.md` hay của bất kỳ file nào khác, và cố ý không chứa con số nào đếm được bằng máy. Mọi bản tóm tắt song song rồi sẽ lệch khỏi bản gốc mà không ai hay; README đã từng lệch đúng như vậy.

Fetch file thô theo mẫu `https://raw.githubusercontent.com/tunahakim/capcut-pipeline/main/<đường-dẫn-file>`, thay `<đường-dẫn-file>` bằng đường dẫn tương đối bất kỳ trong repo, ví dụ `docs/START-HERE.md` hoặc `scripts_v1/fx_audit.py`.

## Trần kích thước tài liệu và luật đọc file bị cắt

Mỗi file trong `docs/` không vượt quá 26 KB; `docs/STATE.md` và `docs/TODO.md` có trần chật hơn, ghi ở đầu mỗi file. Kiểm bằng `python tools/docs_audit.py`, và từ 03/08/2026 lệnh đó **báo lỗi** khi có file vượt trần chứ không chỉ in nhãn, nên `--baseline` không còn chốt được một mốc chuẩn bẩn. Muốn cho một file vượt trần thì thêm trần riêng tường minh cho nó vào `PER_FILE_BUDGET` kèm lý do, để việc vượt trần là quyết định có ghi lại. Đo 03/08/2026 cho thấy nội dung người dùng **dán thẳng vào hội thoại thì không bị cắt**, chỉ kết quả của công cụ fetch mới bị, nên trần 26 KB nay là chốt chống phình chứ không còn là ranh giới sinh tử; cơ chế đầy đủ, ngữ cảnh áp dụng và mô hình đọc ba tầng ở `docs/ai-reading-channel.md`.

Lý do là lịch sử chứ không phải kỹ thuật. Dự án được vận hành bằng cách đưa một AI đọc tài liệu qua `raw.githubusercontent.com`, và công cụ fetch của AI cắt bớt nội dung dài. Ngưỡng cắt **khác nhau theo từng công cụ và từng phiên**, nên đừng tin vào một con số cố định: lần đo đầu cho khoảng 26 KB với văn bản tiếng Việt có dấu, vốn nhiều byte mỗi ký tự trong UTF-8; lần đo ngày 01/08/2026 trên một công cụ khác cho ngưỡng cứng 10000 byte ở chế độ đọc thô, và khi xin phần đuôi thì công cụ trả lời rằng file đã hết. Cùng ngày ghi nhận thêm một kiểu hỏng thứ hai nguy hiểm hơn: nội dung **bị lược mất khúc giữa sau khi fetch đã xong**, đầu và đuôi vẫn còn nguyên nên kết quả trông y như đã đọc đủ.

**Cách fetch đúng, đo ngày 03/08/2026: mỗi file đúng một lần, ở chế độ markdown.** Gọi `https://raw.githubusercontent.com/tunahakim/capcut-pipeline/main/<đường-dẫn-file>` ở chế độ mặc định trả về văn bản đã dựng lại, **không bật chế độ đọc thô**; một lần gọi như vậy lấy trọn được cả file lớn nhất trong `docs/`. Các đường khác đã thử và bị loại: chế độ đọc thô chặn cứng ở 10000 byte **và khai báo sai tổng kích thước**, nó báo `docs/START-HERE.md` đã hết trong khi file dài hơn gấp đôi chỗ nó dừng, rồi trả mã 416 nói không còn dữ liệu khi xin phần đuôi, tức nó nói dối chứ không chỉ cắt; đường `github.com/.../blob/main/<file>?plain=1` trả về trang giao diện của GitHub chứ không phải nội dung file; `cdn.jsdelivr.net` và `raw.githack.com` trả về byte đã nén mà công cụ fetch không giải được. **Chưa kiểm chứng:** chế độ markdown có chuẩn hoá lại định dạng nên không dùng nó để so byte, và chưa ai thử nó trên file `.py` hay `.json` nên chưa biết nó có làm hỏng khối mã hay không.

**Đừng đọc GitHub contents API bằng công cụ fetch.** Phản hồi JSON tốn chừng một KB cho mỗi file mà gần hết là URL không ai dùng, và bản thân nó cũng bị cắt như mọi thứ khác. Số byte của blob chỉ nên tồn tại bên trong script chạy trên máy: `python tools/repo_bytecheck.py` tự gọi API theo từng thư mục, đối chiếu với file trên đĩa, so `HEAD` cục bộ với `main` trên GitHub để bắt trường hợp quên pull, rồi in đúng năm dòng.

Luật bắt buộc với mọi AI đọc repo này qua GitHub. Sau mỗi lần fetch, tự kiểm xem có bị cắt đuôi hay rỗng khúc giữa không. Phép đối chiếu byte có **trần chi phí một lượt**: chạy `python tools/repo_bytecheck.py`, sạch thì đi tiếp ngay. Khớp tuyệt đối hoặc giải thích được bằng ký tự CR thì im lặng đi tiếp; lệch nhỏ mà không giải thích được thì báo đúng một dòng rồi vẫn làm việc tiếp; chỉ dừng hẳn khi thiếu file trên đĩa hoặc lệch đủ lớn để nghi mất đoạn. Đừng đuổi theo lệch một byte: `reference/describe.json` chứa đúng một ký tự CR nằm trong nội dung nên phép trừ CR báo lệch mà file vẫn nguyên vẹn, còn `docs_audit.py` đếm byte trên đĩa có tính CR nên với file CRLF nó báo lớn hơn blob đúng bằng số dòng, lệch về phía cảnh báo sớm nên vô hại. Nghi ngờ thì **nói ngay với người dùng**, đừng đoán và đừng dựa vào bản tóm tắt tự động, vì tóm tắt sẽ làm rơi đúng những con số mà dự án này dựa vào. Không bao giờ viết nội dung thay thế cho một file mà mình không có nguyên văn. Không bao giờ kết luận rằng một hàm hay một câu văn không tồn tại chỉ vì mình không nhìn thấy nó. Khi phát hiện thủng, hai bên chọn một trong hai cách: người dùng dán thẳng nội dung vào hội thoại, hoặc chuyển sang một agent chạy cục bộ đọc file từ ổ đĩa.

Trần kích thước **không áp dụng** cho agent chạy trực tiếp trên máy và đọc file từ ổ đĩa, ví dụ Claude Code; loại đó đọc bao nhiêu cũng được và được phép tạo file mới thoải mái. Vẫn giữ trần để kênh đọc qua GitHub không hỏng. Đồng thời đừng tách quá nhỏ, vì nhiều file vụn khó kiểm soát hơn vài file vừa: nhắm 10 đến 20 KB mỗi file, chỉ tách khi vượt trần.

## Yêu cầu môi trường

Windows 10 hoặc 11. Python 3.13 trở lên, **bản python.org chứ không phải bản Microsoft Store**. Node.js kèm npm. `capcut-cli` phiên bản đúng 0.15.0. ffmpeg và ffprobe trên PATH. CapCut Desktop **đúng phiên bản 9.1.0.3879**, đã tắt tự cập nhật.

Không cần cài thư viện Python nào ngoài thư viện chuẩn. Đây là điểm mạnh đáng giữ: một máy mới chỉ cần Python là chạy được mọi script trong repo.

## Bố cục

```
docs/         tai lieu. Bat dau tu START-HERE.md
pipeline/     lop loi moi, hien moi co khung goi rong
scripts_v1/   script dung that trong day chuyen
tools/        script nghien cuu, do dac va kiem tra
tests/        test tu dong, chua viet
molds/        khuon JSON chup tu CapCut, phan theo phien ban CapCut
reference/    danh muc dinh danh hieu ung va cu phap CLI
fixtures/     moc vang JSON de so parity. KHONG chua media test
manifests/    ban ke data va vendor cua tung may, moi may mot file
artifacts/    bang chung cua tung phien, de nguoi va AI tra lai so
_deprecated/  script da chet, giu lai kem ly do
```

Số lượng script trong `scripts_v1/` và `tools/` cố ý không ghi ở đây. Bảng đầy đủ nằm ở `docs/scripts.md`, sinh tự động bằng `python tools/scripts_index.py --write` từ docstring đầu mỗi file, không sửa tay.

Repo này chỉ là một trong ba nhánh thư mục ngang hàng. Hai nhánh còn lại là `data\` và `vendor\` trên máy lab và trên máy render, cố ý không nằm trên GitHub; mục 3 của `docs/START-HERE.md` nói chúng chứa gì và cách dựng lại chúng trên một máy mới.

## Chạy thử nhanh

```
python scripts_v1/fx_audit.py "<đường-dẫn-project-CapCut>"
```

Script chỉ đọc, in ra tình trạng tài nguyên của mọi transition, effect và filter trong project. Mọi dòng phải báo `OK`.

## Giới hạn đã biết

Chỉ đúng với CapCut 9.1.0. Phiên bản khác thì write-guard của capcut-cli có thể từ chối ghi, và một số tên trường có thể đã đổi. Có quy trình probe hồi quy ở `docs/procedures.md` để phát hiện cái gì đã thay đổi.

Bước xuất file MP4 **bắt buộc làm tay** trong giao diện CapCut. `capcut export` chỉ xuất metadata, còn `capcut render` dựng lại bằng FFmpeg nên bỏ qua mọi hiệu ứng nội bộ của CapCut.

## Lưu ý pháp lý

Repo không chứa và không được chứa bộ cài CapCut hoặc file tài nguyên hiệu ứng của ByteDance. `reference/enums_backup.json` là **danh mục định danh** hiệu ứng, không phải tài nguyên; nó có nguồn từ dự án pyJianYingDraft.