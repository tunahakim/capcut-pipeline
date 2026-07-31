# capcut-pipeline

Bộ công cụ tự động hoá dựng video documentary dài 55–70 phút bằng **CapCut Desktop 9.1.0** và **capcut-cli 0.15.0**, trên Windows.

Đây là **phòng thí nghiệm đang hoạt động**, không phải công cụ đã phát hành. Code trong `scripts_v1/` chạy thật và đã dựng ra một video hoàn chỉnh; lõi trong `pipeline/` đang được viết. Repo tồn tại để hai máy dùng chung một nguồn sự thật, và để một trợ lý AI đọc được toàn bộ dự án mà không cần ai dán tài liệu cho nó.

## Nếu bạn là AI

Đọc **`docs/START-HERE.md`** trước mọi file khác. Nó chứa bản đồ repo, trạng thái bàn giao, các ràng buộc không được vi phạm, danh sách sáu loại lỗi im lặng, và cách làm việc với người dùng.

Sau đó đọc `docs/reference.md` rồi `docs/failures.md`. Ba file đó đủ cho hầu hết công việc.

**Đừng đọc `docs/legacy/v0.8-full.md` một cách tuần tự** — nó nặng 299 KB và sẽ ăn phần lớn ngữ cảnh. Chỉ fetch nó khi cần tra một mục cụ thể.

**Mã nguồn in trong `docs/legacy/v0.8-full.md` không đáng tin.** Nguồn sự thật là file trong `scripts_v1/` và `tools/`.

Đường dẫn để fetch file thô:

`https://raw.githubusercontent.com/tunahakim/capcut-pipeline/main/<đường-dẫn-file>`

AI có thể đọc bất kỳ file nào trong repository bằng cách thay `<đường-dẫn-file>` bằng đường dẫn tương đối của file trong repo.

Ví dụ:

- `docs/START-HERE.md`
  → `https://raw.githubusercontent.com/tunahakim/capcut-pipeline/main/docs/START-HERE.md`

- `docs/reference.md`
  → `https://raw.githubusercontent.com/tunahakim/capcut-pipeline/main/docs/reference.md`

- `scripts_v1/fx_audit.py`
  → `https://raw.githubusercontent.com/tunahakim/capcut-pipeline/main/scripts_v1/fx_audit.py`

## Dự án làm gì

Đầu vào là một bảng metadata shot — tên file ảnh, timestamp bắt đầu và kết thúc — cộng một file audio narration và một file SRT. Đầu ra là một project CapCut đã dựng sẵn: mỗi ảnh thành một shot có hiệu ứng Ken Burns riêng, nền mờ phủ khung, transition giữa các shot, phụ đề có styling, nhạc nền, hiệu ứng phim cũ phủ toàn timeline. Người dùng mở CapCut xem lại, chỉnh tay chỗ nào cần nhấn, rồi bấm Export.

Ràng buộc chi phối mọi thứ: **timing khoá cứng theo audio và SRT**. Video 60 phút chứa 250–400 shot, mỗi shot có mốc thời gian định trước. Lệch một chút là phụ đề rời khỏi lời thoại.

## Yêu cầu môi trường

Windows 10 hoặc 11. Python 3.13 trở lên, **bản python.org chứ không phải bản Microsoft Store**. Node.js kèm npm. `capcut-cli` phiên bản đúng 0.15.0. ffmpeg và ffprobe trên PATH. CapCut Desktop **đúng phiên bản 9.1.0.3879**, đã tắt tự cập nhật.

Không cần thư viện Python nào ngoài thư viện chuẩn. Toàn bộ script chỉ dùng `json`, `pathlib`, `shutil`, `subprocess`, `uuid`, `re`, `os`, `sys`, `hashlib`, `time`, `ast`. Đây là điểm mạnh đáng giữ.

## Bố cục

```
docs/         tai lieu. Bat dau tu START-HERE.md
pipeline/     lop loi moi (dang viet, hien moi co khung goi __init__.py)
scripts_v1/   13 script dang chay that
tools/        10 script nghien cuu va tra cuu
tests/        (con rong)
molds/        khuon JSON chup tu CapCut, phan theo phien ban CapCut
reference/    catalogue hieu ung va cu phap CLI
fixtures/     moc vang JSON de so parity. KHONG chua media test
_deprecated/  script da chet, giu lai kem ly do
```

Repo này chỉ là một trong ba nhánh. Hai nhánh còn lại — `data\` và `vendor\` — cố ý không nằm trên GitHub; xem mục 3 của `docs/START-HERE.md` để biết chúng chứa gì và cách dựng lại chúng trên máy mới.

## Chạy thử nhanh

```
python scripts_v1/fx_audit.py "<đường-dẫn-project-CapCut>"
```

Script chỉ đọc, in ra tình trạng tài nguyên của mọi transition, effect và filter trong project. Mọi dòng phải báo `OK`.

## Giới hạn đã biết

Chỉ đúng với CapCut 9.1.0. Phiên bản khác thì write-guard của capcut-cli có thể từ chối ghi, và một số tên trường có thể đã đổi. Có quy trình probe hồi quy mười lăm phút ở `docs/procedures.md` để phát hiện cái gì đã thay đổi.

Bước xuất file MP4 **bắt buộc làm tay** trong giao diện CapCut. `capcut export` chỉ xuất metadata, còn `capcut render` dựng lại bằng FFmpeg nên bỏ qua mọi hiệu ứng nội bộ của CapCut.

## Lưu ý pháp lý

Repo không chứa và không được chứa bộ cài CapCut hoặc file tài nguyên hiệu ứng của ByteDance. `reference/enums_backup.json` là **danh mục định danh** hiệu ứng, không phải tài nguyên; nó có nguồn từ dự án pyJianYingDraft.

---