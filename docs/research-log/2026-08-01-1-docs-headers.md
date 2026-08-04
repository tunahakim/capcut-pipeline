# Nhật ký phiên 01/08/2026 (1) — docstring cho toàn bộ script, bảng `scripts.md` tự sinh

**Tóm tắt:** Docstring cho 15 script còn thiếu, chốt luật mô tả sinh tự động từ docstring, `scripts.md` tự sinh bằng `tools/scripts_index.py --write`, dời `split_research_log.py` vào kho lưu trữ, viết `artifacts/README.md`

Làm hoàn toàn trên máy lab. Không mở CapCut, không dựng project, không export. Ổ C còn 11,75 GB lúc bắt đầu và phiên này không đụng tới thư mục draft.

## Mở phiên

`python tools/docs_audit.py --compare` cho `VAN DE` bằng 0 và trùng mốc chuẩn, nên phần liên kết chết của Ưu tiên 0 vốn đã sạch từ phiên trước, không còn việc.

## Việc đã làm

Viết `tools/scripts_index.py` để kiểm kê script và trích docstring. Bản đầu có hai kết quả sai lệch so với `TODO.md`. Thứ nhất, `TODO.md` nói thiếu 11 hàng nhưng thực tế `tools/` có 25 file mà bảng chỉ có 10 hàng, tức thiếu 15; năm file bị bỏ sót khỏi danh sách là `bench_build.py`, `bench_fixkb.py`, `bench_kb.py`, `bench_shots.py` và `frame_audit.py`. Thứ hai, chính công cụ có lỗi: nó dò docstring bằng chuỗi mở `"""` nên bỏ qua docstring có tiền tố chuỗi thô `r"""`, báo nhầm `split_research_log.py` và `docs_audit.py` là thiếu header. Bản sau chuyển sang `ast.get_docstring`, hết lỗi này. Số file thật sự cần viết header là 15.

Viết 15 docstring tiếng Việt có dấu cho `clone_project.py`, `patchpath.py`, `audio_prep.py`, `bulk_build.py`, `enum_list.py`, `fx_list.py`, `syntax.py`, `fix_fold_path.py`, `img_scan.py`, `oracle_read.py`, `timing_snap.py`, `bgblur_diag.py`, `bgblur_frames.py`, `frame_audit.py`, `shots_crosscheck.py`. Nội dung viết dựa trên đọc mã nguồn từng file, không suy đoán. Chèn bằng script dùng một lần ở `data\tmp\hdr_apply.py`, có ba lớp kiểm: đếm ký tự phi ASCII để bắt trường hợp console làm hỏng dấu tiếng Việt lúc dán, `ast.parse` lại từng file sau khi ghi, và `compileall` trên cả hai cây. Kết quả 90 dòng thêm vào, không dòng nào bị xoá.

Chốt một luật kiến trúc tài liệu: **docstring đầu file là nguồn sự thật duy nhất của mô tả script**, còn `docs/scripts.md` là bản sinh ra bằng `python tools/scripts_index.py --write`, ghi vào vùng giữa hai cặp mốc HTML. Lý do giống hệt lý do `STATE.md` không được liệt kê việc phải làm khi `TODO.md` đã có: hai bản mô tả song song của cùng một thứ chắc chắn lệch nhau sau vài phiên. `_deprecated/` nằm ngoài phạm vi, bảng kho lưu trữ chỉ có tên file và kích thước, không có cột mô tả, và không thêm docstring vào hồ sơ đã đóng.

Chạy `data\tmp\fix_rawdoc.py` thêm tiền tố chuỗi thô cho docstring chứa dấu gạch chéo ngược, tìm được hai file là `audit_kit.py` và `v4_mold.py`, hết `SyntaxWarning` về `\p`.

Chuyển `tools/split_research_log.py` sang `_deprecated/`. Nguyên nhân trực tiếp: sau khi bảng sinh từ docstring, mọi tên file nhắc trong docstring trở thành tham chiếu tài liệu và bị `docs_audit` soi, mà docstring của nó trỏ tới `docs/research-log.md` đã xoá sau khi tách, tạo ra một liên kết chết mới. Cách sửa không phải bịt mắt công cụ kiểm mà là công nhận đúng bản chất: đây là công cụ di trú dùng một lần, file nguồn không còn nên nó vĩnh viễn không chạy lại được.

Viết mới `artifacts/README.md` và cập nhật `fixtures/README.md` cho khớp thực tế, bổ sung hai file `parity_gold_snap.json` và `parity_gold_snap_full.json` mà README cũ bỏ sót.

## Số đo cuối phiên

38 script đang dùng, 26 script lưu trữ, 0 file thiếu docstring. `docs/scripts.md` 18,2 KB, bằng 70 phần trăm trần 26 KB. `docs_audit`: `VAN DE` 0, 411 tham chiếu bắt được, 0 file `.md` không ai trỏ tới, giảm từ 2 nhờ `scripts.md` nhận `_deprecated/README.md` và `molds/capcut-9.1.0/_README.md`.

## Phát hiện ảnh hưởng tới việc sau

`tools/img_scan.py` **đã tính và ghi sẵn hai cột `kx`, `ky`** từ trước, với `fit = min(1920/w, 1080/h)`, `kx = w*fit/1920`, `ky = h*fit/1080`. Một phần tư món KX KY của Ưu tiên 1 do đó đã xong mà `TODO.md` chưa biết; đã sửa lại `TODO.md`.

Chênh lệch `duration` giữa hai lược đồ trong `fixtures/parity-gold/` là 168725000 so với 168733333 micro giây, đúng bằng phép ceil lên frame ở 30 fps, khớp luật đã ghi ở `../reference.md`.

`Get-Content` trên PowerShell 5.1 nếu không kèm `-Encoding UTF8` sẽ đọc file UTF-8 của repo theo bảng mã ANSI và hiện mojibake. Mọi lệnh đọc tài liệu từ nay phải kèm tham số đó.

## Chưa kiểm chứng

Phiên này không sinh ra kết luận thực nghiệm nào. Toàn bộ là tài liệu và đọc mã tĩnh, không có phép đo trên CapCut hay bản export.

## Sự cố trong phiên và bản vá công cụ kiểm

`docs/procedures.md` bị dời nhầm sang `docs/research-log/` lúc lưu file nhật ký này, và lọt qua trọn một lần commit rồi push. Điều đáng ghi lại không phải cú lưu file hụt, mà là `tools/docs_audit.py` **không bắt được**: khi tra theo đường dẫn không thấy, nó tra tiếp theo tên file và chỉ cần cả repo có đúng một file trùng tên là báo hợp lệ. Mọi tham chiếu `docs/procedures.md` vì thế vẫn xanh dù file nằm sai thư mục, và ma trận tham chiếu lặng lẽ đổi đích.

Cùng lúc, công cụ báo chết bốn liên kết mà thật ra không chết: hai script dùng một lần trong `data\tmp\` cố ý nằm ngoài repo nên vĩnh viễn không có trong index, một file nhật ký gộp đã xoá được nhắc lại như quá khứ, và một file đã lên kế hoạch chưa viết. Hướng sai là sửa câu văn cho né công cụ; làm vậy là chữa triệu chứng và làm tài liệu mất chính cái đường dẫn khiến câu đó có ích. Hướng đúng là dạy công cụ phân loại.

`tools/docs_audit.py` nay có năm kết cục không tính là lỗi và hai kết cục tính là lỗi. Không tính lỗi: `OK`, `PLANNED` cho file đã lên kế hoạch, `NGOAI` cho đường dẫn bắt đầu bằng `data/` tức thư mục lab ngoài repo, `LICHSU` cho file đã xoá mà tài liệu nhắc lại, `LUUTRU` cho file đã chuyển vào `_deprecated/` sau khi câu văn được viết. Tính lỗi: các loại cũ, cộng thêm `SAI CHO` — file có thật nhưng nằm khác đường dẫn tài liệu ghi, đúng ca `procedures.md`.

Loại `LUUTRU` sinh ra từ chính bản vá này: sau khi thêm `SAI CHO`, công cụ đỏ ở câu "Chuyển `tools/split_research_log.py` sang `_deprecated/`" ngay phía trên. Câu đó đúng vào lúc viết. Bắt sửa nó là bắt sửa quá khứ, trái luật nhật ký chỉ ghi thêm, nên ngoại lệ nằm ở công cụ.

## Cách chạy lại

`python tools/scripts_index.py` in báo cáo gồm số script, danh sách file thiếu docstring và trạng thái bảng có cũ so với mã nguồn hay không. Thêm `--write` để sinh lại hai bảng trong `docs/scripts.md`. Thêm script mới thì viết docstring theo quy ước ghi ở đầu `../scripts.md` rồi chạy lại lệnh đó, đừng sửa bảng bằng tay.