# Nhật ký phiên 02/08/2026 (4) — v4_mold thành công cụ diff, đóng phần enums của khoá Pro, và shots_dump

**Tóm tắt:** Vá v4_mold thành công cụ diff ba nhóm trường, đóng phần enums của mục khoá Pro, viết shots_dump và kiểm khứ hồi sạch
**Phiên:** 23:47 tối

Máy lab. Có đọc project bằng script, không mở CapCut, không export. Phiên trước là `2026-08-02-3-filter-gui-vip.md`.

## Bước 1 — vá `../../tools/v4_mold.py`

Quyết định trước khi viết code: **giữ nguyên** `molds/capcut-9.1.0/filter.json` và ghi bản chụp mới ra `filter-vhs3.json`, đồng thời vẫn cài nhóm trường thứ ba. Căn cứ là phép đếm trên chính file: `scripts_v1/filter_apply.py` nhắc `mold` 0 lần, `molds` 0 lần, `filter.json` 0 lần, `open(` 0 lần, bốn `read_text` đều của draft. Nghĩa là khuôn **không phải phụ thuộc lúc chạy** mà chỉ là nền thiết kế đã chép cứng vào code, nên ghi đè không đổi hành vi nhưng vẫn xoá mất bằng chứng gốc của filter Film.

Lý do không gộp vào một khuôn: nếu ghi đè kèm nhóm thứ ba thì nhóm được phép khác phải nuốt thêm `value`, `category_id`, `category_name`, `request_id`, ba GUID, `track_render_index` và `target_timerange.start`, khi đó nhóm bắt buộc khớp gần như chỉ còn boolean. `value`, `category_id`, `category_name` cố ý **để ở nhóm bắt buộc** vì chúng là tham số thật.

Công cụ mới: `--project` bắt buộc, `--out` tường minh mặc định trỏ vào `molds/capcut-9.1.0/filter.json`, mặc định **chỉ diff**, muốn ghi phải `--write`. Ba nhóm trường là BẮT BUỘC, MÁY/PROJECT gồm `material.path` và `segment.target_timerange.duration`, ĐỊNH DANH gồm id và các trường định danh. Key có bên này thiếu bên kia **luôn** tính là bắt buộc vì đó là trôi schema. Mã thoát 0 sạch, 1 không chạy được, 2 lệch nhóm bắt buộc.

Một lỗi im lặng của bản cũ được sửa: nó gán `gui = (t, s, mo)` trong vòng lặp nên với project có hai filter GUI, nó **lấy cái cuối** mà không báo gì. `fxprobe01` có đúng hai, thứ tự là VHS III rồi 2077, nên bản cũ sẽ chụp nhầm 2077. Bản mới bắt buộc `--pick` và thoát 1.

Nghiệm thu: chụp được khuôn 3595 byte; chạy lần hai trên cùng project cho 0 lệch ở cả ba nhóm; lật `segment.visible` thì bắt được và trả 2; bỏ `--pick` thì thoát 1. Commit `f7aea30`.

## Bước 2 — cờ VIP của bốn loại, và một sai lầm phương pháp

Số đo ở namespace CapCut: scene-effect 0 VIP trên 345, image-intro 0 trên 43, image-outro 0 trên 23, image-combo 0 trên 108. Cờ `is_vip` **có** trên mọi mục nhưng hằng `false` — khác với "không có cờ", và tài liệu ghi đúng như vậy. Namespace JianYing cùng bốn loại: 297/912, 58/95, 54/72, 16/123. Cách đếm đã hiệu chuẩn trên `--filters --jianying` ra đúng 468/300/168 như tài liệu, và script vá tài liệu bị chặn bằng một file dấu, không hiệu chuẩn thì không ghi.

Suýt kết luận sai hai lần. Lần một, bộ lọc từ khoá tìm cờ khoá Pro bỏ sót khoá `member`; đo lại thì `member` kiểu `str`, mỗi mục một giá trị riêng, là tên thành viên enum kiểu `Zoom_In`, `Alt_BW`, `_70s`, không phải cờ. Lần hai, và nặng hơn: **cả Bước 2 không phải phép thử oracle**. Nó đọc một danh mục tĩnh do capcut-cli đóng gói, nguồn từ pyJianYingDraft, **không** đọc từ bản CapCut đã cài, rồi phát biểu về hành vi của CapCut. Không có bước thử thật, không có đo sau, không có gì để đối chiếu ngược.

Ảnh chụp tab Animation mục Out do người dùng gửi đã chốt lại: GUI có rất nhiều mục và đa số đeo vương miện, enums chỉ có 23 mục và cả 23 đều free. Danh mục enums **không phải** danh mục của GUI. Bài học vận hành: với mọi câu hỏi về hành vi CapCut, mở GUI trước, ghi số vào tài liệu sau.

Không đếm được nhóm Basic để tách phần free vì GUI trộn free với VIP trong mọi nhóm.

## Bước 3 — `../../tools/shots_dump.py`

Nguyên mẫu `data\tmp\gen_cc_fixture.py` 3952 byte dùng lại được gần trọn, kể cả ý hay nhất của nó là `import shots_crosscheck as sc` rồi xài chung `LEVELS`, `mat_index`, `main_track`, `kf_scales`, `resolve_project`, `nested_report`, `load`. Nhờ đó không có bản sao logic nào để lệch về sau. Dùng lại luôn `sc.ArgParser`, lớp ghi đè `error()` để thoát **1** khi sai tham số — đúng cái bẫy trùng mã 2 của argparse.

Ngữ nghĩa mã thoát 2 ở đây là: file CSV đích đã tồn tại và **khác** nội dung vừa dump, khi đó không ghi đè trừ khi có `--force`, và in ra dòng lệch đầu tiên.

Nghiệm thu trên `testV3`: 8 segment, 0 segment thiếu keyframe nên có đủ `kb_s0` và `kb_s1`, ghi 644 byte. Khứ hồi bằng `shots_crosscheck.py` ăn chính bản dump ra `SACH, 0 lech tren ca nam truong`, mã thoát 0, 8 shot có blur và 7 transition khớp hai phía. Dump lại nhận ra giống hệt, thoát 0. Sửa tay `idx` dòng 3 thành 999 thì bắt đúng dòng đó, không ghi đè, thoát 2. Thiếu tham số thoát 1.

## Số đo mới

`docs/scripts.md` từ 21964 lên 22642 byte sau khi `v4_mold.py` đổi docstring. `docs/reference-catalog.md` 8199 lên 9463 byte. Khuôn `filter-vhs3.json` 3595 byte so với `filter.json` 3218 byte, chênh chủ yếu là khối `_meta`.

Hai file CRLF trên đĩa **ngoài** danh sách bảy file đã biết: `molds/capcut-9.1.0/filter.json` cộng 124 byte và `scripts_v1/filter_apply.py` cộng 209 byte. Không phải lỗi, nhưng script vá phải tự giữ kiểu xuống dòng, nếu đọc `read_text` rồi ghi `write_text` sẽ âm thầm đổi CRLF thành LF và làm cả file hiện lên trong `git diff`.

## Chưa kiểm chứng

Giả thuyết 23 mục enums ứng với phần free của tab Out: **không kiểm được** bằng cách đếm nhóm Basic vì GUI trộn free với VIP.

Chưa thả tay một mục có vương miện nào để đọc ngược `resource_id` và đối chiếu với enums. Đây là phép còn thiếu để kết luận dứt điểm, và nó chạy được trên máy lab, không cần export.

Dòng `tham chieu La Ma` của `docs_audit.py` tăng 1 sau một bản vá không chứa số La Mã nào; chưa giải thích được.

## Còn lại

Nghiệm thu ba script blur `bgblur_diag.py`, `bgblur_frames.py`, `frame_audit.py` hoãn sang phiên sau, cố ý, vì ngữ cảnh phiên này không đủ để làm tử tế. Các nợ nhỏ khác còn nguyên trong `../TODO.md`.
