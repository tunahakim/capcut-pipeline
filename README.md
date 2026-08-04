# capcut-pipeline

Bộ công cụ tự động hoá dựng video documentary dài 55–70 phút bằng **CapCut Desktop 9.1.0** và **capcut-cli 0.15.0**, trên Windows. Đầu vào là một bảng metadata shot cộng file narration và file SRT; đầu ra là một project CapCut đã dựng sẵn, người dùng mở lên xem lại, chỉnh tay chỗ cần nhấn, rồi bấm Export.

Đây là **phòng thí nghiệm đang hoạt động**, không phải công cụ đã phát hành. Repo tồn tại để hai máy dùng chung một nguồn sự thật, và để một trợ lý AI đọc được toàn bộ dự án mà không cần ai dán tài liệu cho nó.

## Nếu bạn là AI

Đọc `docs/START-HERE.md` trước mọi file khác; nó cho bạn thứ tự đọc, luật bất biến và cách làm việc với người dùng. Nhưng đọc mục **Luật đọc file qua GitHub** ngay bên dưới trước đã, vì luật đó áp dụng ngay từ lần fetch đầu tiên, kể cả lần fetch chính `docs/START-HERE.md`.

README này cố ý **không** tóm tắt nội dung của `docs/START-HERE.md` hay của bất kỳ file nào khác, và cố ý không chứa con số nào đếm được bằng máy. Mọi bản tóm tắt song song rồi sẽ lệch khỏi bản gốc mà không ai hay; README đã từng lệch đúng như vậy.

Fetch file thô theo mẫu `https://raw.githubusercontent.com/tunahakim/capcut-pipeline/main/<đường-dẫn-file>`, thay `<đường-dẫn-file>` bằng đường dẫn tương đối bất kỳ trong repo, ví dụ `docs/START-HERE.md` hoặc `scripts_v1/fx_audit.py`.

## Luật đọc file qua GitHub

**Fetch mỗi file đúng một lần, ở chế độ markdown.** Gọi `https://raw.githubusercontent.com/tunahakim/capcut-pipeline/main/<đường-dẫn-file>` ở chế độ mặc định là lấy trọn được cả file lớn nhất trong `docs/`. **Đừng bật chế độ đọc thô**: nó chặn cứng ở 10000 byte và **khai báo sai tổng kích thước**, tức nó nói dối chứ không chỉ cắt.

Sau mỗi lần fetch, tự kiểm xem có bị cắt đuôi hay rỗng khúc giữa không; công cụ tự khai bằng nhãn `partial_content` khi vượt trần. Nghi ngờ thì **nói ngay với người dùng**, đừng đoán và đừng dựa vào bản tóm tắt tự động, vì tóm tắt sẽ làm rơi đúng những con số mà dự án này dựa vào. **Không bao giờ viết nội dung thay thế cho một file mà mình không có nguyên văn. Không bao giờ kết luận rằng một hàm hay một câu văn không tồn tại chỉ vì mình không nhìn thấy nó.** Khi phát hiện thủng, hai bên chọn một trong hai cách: người dùng dán thẳng nội dung vào hội thoại, hoặc chuyển sang một agent chạy cục bộ đọc file từ ổ đĩa.

Muốn đối chiếu byte thì chạy `python tools/repo_bytecheck.py`, đúng một lượt, sạch thì đi tiếp ngay.

Tài liệu trong `docs/` có trần kích thước ba lớp, kiểm bằng `python tools/docs_audit.py`. Cơ chế cắt của công cụ fetch, các số đo ngưỡng, lý do từng lớp trần, những đường fetch đã thử và bị loại, quy tắc CR khi đối chiếu byte, và mô hình đọc ba tầng: tất cả ở `docs/ai-reading-channel.md`, đọc khi cần chứ không nằm trong thứ tự bắt buộc.

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