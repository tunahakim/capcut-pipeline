# TODO — nợ tài liệu và nợ kỹ thuật

**Cập nhật 31/07/2026.** Xếp theo thứ tự dự kiến làm. Việc nào đang chặn việc khác thì ghi rõ.

## Ưu tiên 0 — phiên sau, làm trước mọi việc khác

Việc này người dùng sẽ tự tay dán nội dung đầy đủ từng file cho AI đọc, không đọc qua GitHub, vì nhiều file đã vượt trần 26 KB và bị cắt khi fetch.

**Kiểm tham chiếu chéo trước khi tách bất cứ file nào.** Các file trong `docs/` trỏ lẫn nhau chằng chịt, ví dụ `START-HERE.md` trỏ tới mục số trong `failures.md` và `reference.md`, `procedures.md` trỏ tới `reference.md`, `model.md` trỏ tới `legacy/v0.8-full.md`. Phải quét toàn bộ tham chiếu trước, lập bảng, rồi mới tách và sửa đồng loạt. Tách trước rồi sửa sau sẽ để lại liên kết chết.

**Tách toàn bộ `docs/research-log.md`** thành từng phiên trong `docs/research-log/`, quy ước tên `<ngày>-<số thứ tự phiên trong ngày>-<nhãn ngắn>.md`, phiên mới nhất lên đầu trong `docs/research-log/INDEX.md`. Danh sách dự kiến, lấy theo các tiêu đề hiện có: `2026-07-28-1-mo-dau.md` cho phụ lục E1, `2026-07-29-1-v5.md`, `2026-07-29-2-v6.md`, `2026-07-29-3-v7.md` cho E2 tới E4, `2026-07-30-1-refactor.md`, `2026-07-31-1-parity-300shot.md`, `2026-07-31-2-benchmark-render.md`, và `2026-07-31-3-bgblur-audio.md`. **Đổi tên** file đã tạo ở phiên này từ `2026-07-31-2.md` thành `2026-07-31-3-bgblur-audio.md` cho khớp quy ước. Sau khi tách, sửa mọi chỗ trong `START-HERE.md`, `README.md`, `model.md`, `procedures.md` đang trỏ tới `research-log.md` thành trỏ tới file phiên cụ thể. Xoá `research-log.md` hoặc rút nó về một dòng trỏ sang `research-log/INDEX.md`.

**Viết lại cho gọn mà vẫn đủ**, ưu tiên theo thứ tự này: `START-HERE.md` 28.312 byte, `research-log.md` 31.774 byte, `reference.md` 26.794 byte. `START-HERE.md` đang chứa lẫn quyết định cũ đã bị thay thế và quyết định hiện hành, đây là nguồn nhầm lẫn nguy hiểm nhất trong bộ tài liệu. Nguyên tắc viết lại: quyết định đã bị thay thế thì **xoá khỏi tài liệu chính và ghi vào file phiên tương ứng**, không giữ song song hai bản.

**Hạn chế đã biết cần ghi vào `reference.md` khi viết lại:** `scripts_v1/kb_apply.py` kiểm biên bằng `lim_x = 1 - s` và `lim_y = 1 - KY * s` với `KY` là hằng số toàn cục cho ảnh 1376×768. Hệ quả một, không hỗ trợ Ken Burns phóng tràn viền vì `s > 1` làm vế phải âm và mọi giá trị đều bị từ chối. Hệ quả hai, với ảnh có tỉ lệ khác 1376×768 thì phép kiểm sai lệch một chút so với hình học thật. Cách đi vòng đang dùng: bộ sinh `shots.csv` tự tính biên theo từng ảnh rồi lấy giá trị **chặt hơn** giữa biên thật và biên của `kb_apply.py`, nên không có ảnh nào bị cắt. Muốn bỏ cách đi vòng thì phải tổng quát hoá `kb_apply.py` sang `KX`, `KY` theo từng ảnh, và việc đó cần một phép đo oracle cho ảnh cao hơn khung, hiện **chưa có**.

Gộp bước vá `draft_fold_path` vào `scripts_v1/clone_project.py` để không phải nhớ chạy `tools/fix_fold_path.py` riêng. Nguyên nhân đã xác định ngày 31/07/2026: scaffold mang đường dẫn tuyệt đối của máy đã tạo ra nó, và `clone_project.py` chỉ thay GUID cùng tên project chứ không thay phần `C:/Users/<user>/`. Đây gần như chắc chắn là cơ chế thật đằng sau cảnh báo "scaffold chỉ dùng được trên chính máy đã tạo ra nó" ở `START-HERE.md` mục 3.1; khi viết lại `START-HERE.md` thì sửa cảnh báo đó thành mô tả nguyên nhân kèm cách vá, thay vì để nó là một điều cấm không giải thích.

Viết `tools/data_manifest.py` sinh `artifacts/data_manifest.csv` gồm đường dẫn tương đối, kích thước và SHA256 cho `data\` và `vendor\`, kèm chế độ kiểm để một máy biết mình thiếu hoặc lệch file nào. Tạo thư mục `artifacts/` trong repo cho các artifact văn bản nhỏ. Cân nhắc đưa `Test_tool_v3\` vào `fixtures/`.

Đưa `reh10` vào `fixtures/` làm project đối chứng dương thay cho `parity01` đã mất, kèm `shots_reh.csv` và hai snapshot timing.

## Ưu tiên 1 — làm ngay sau bài render 60 phút có audio

Tách `docs/reference.md`, hiện 26.794 byte, vượt trần 26 KB. Đề nghị cắt làm hai: giữ mục 1 tới 5 cộng 14 trong `reference.md` phần lõi ghi và hình học, chuyển mục 6 tới 13 sang `reference-catalog.md` phần tài nguyên, catalogue, cú pháp CLI và bảng trạng thái. Chỉ tách hai, không tách nhỏ hơn.

Tổng quát hoá phần hình học ở mục 3 của `reference.md`. Hiện `KY` là hằng số tính sẵn cho ảnh 1376×768 trên khung 1920×1080, và tài liệu còn khuyến nghị "chuẩn hoá mọi ảnh về đúng 1920×1080" — khuyến nghị này **đã bị bãi bỏ** vì dự án cần làm cả video vuông và video dọc, và thư mục ảnh thật có đủ kích thước. Công thức thay thế, dùng `CW` và `CH` là kích thước khung, `IMG_W` và `IMG_H` là kích thước từng ảnh:

```
fit = min(CW / IMG_W, CH / IMG_H)
KX  = IMG_W * fit / CW
KY  = IMG_H * fit / CH
|transform.x| <= 1 - KX * s
|transform.y| <= 1 - KY * s
```

Một trong hai giá trị `KX`, `KY` luôn bằng 1, chính là chiều bị giới hạn khi fit. Đặt `KX = 1` thì công thức rút về đúng dạng đang ghi trong tài liệu, nên bản tổng quát tương thích ngược với ba phép đo oracle đã có. Trường hợp ảnh **cao hơn** khung, tức `KX < 1` và `KY = 1`, hiện đang ghi là `[CHUA XAC MINH]`; bản tổng quát suy ra từ đối xứng nhưng **chưa có phép đo oracle nào xác nhận**, phải đo trước khi tin.

Đồng bộ thân mục 10 của `START-HERE.md` với danh sách tám mục trong `failures.md`.

Cập nhật mục 13 của `reference.md`: dòng `bg-blur` kích hoạt chuyển sang **đã kiểm ở ĐẦU RA** ở quy mô 300 shot ngày 31/07/2026; thêm dòng cho Ken Burns 300 shot và transition 299 cái ở quy mô thật.

Cập nhật mục 12 của `reference.md`: con số ngoại suy "60 phút khoảng 5,2 GB" đã bị số đo thật thay thế — `bench300` xuất 60 phút ra 4,07 GB ở 9696 kbps trong khoảng 20 phút trên i5-10400F cộng GTX 1080. Ghi kèm cảnh báo: `bench300` dùng ảnh nhân bản từ một bộ nhỏ nên nén dễ hơn ảnh thật, số này **có thể lạc quan hơn thực tế**, chưa kiểm chứng với bộ ảnh đa dạng.

## Ưu tiên 2 — cấu trúc tài liệu

Di trú bốn phụ lục E1 tới E4 của `research-log.md` sang `docs/legacy/` và các phiên còn lại sang `docs/research-log/<ngày>.md`, chỉ để lại `docs/research-log/INDEX.md` liệt kê các phiên mới nhất lên đầu. `research-log.md` hiện 31.774 byte, vượt trần.

Viết `docs/STATE.md` dưới 3 KB: cái gì đã kiểm chứng, cái gì đang treo, ba việc kế tiếp. Đây là file AI đọc đầu tiên.

Tách `START-HERE.md`, hiện 28.312 byte, vượt trần. Chỉ tách sau khi có `STATE.md`, vì phần lớn nội dung "trạng thái bàn giao" sẽ chuyển sang đó.

Viết `tools/docs_size.py` báo file nào vượt 26 KB, chạy trước mỗi lần push tài liệu.

## Ưu tiên 3 — nợ kỹ thuật

`tools/bench_shots.py` kiểm lề trên số chưa làm tròn và gán cứng hình học cho ảnh 1376×768. **Không vá**, đánh dấu là đã bị `tools/prod_shots.py` thay thế.

`capcut-cli` có đặt được `canvas_config` để tạo project vuông hoặc dọc hay không: **chưa kiểm chứng**. Cần cho mục tiêu video dọc và video vuông.

Chưa có filter free nào được xác minh; filter duy nhất từng chạy là `Film` và nó khoá Pro. Cần mở CapCut vào tab Filters, chọn một mục không có vương miện, bấm mũi tên tải xuống. Việc này cũng tạo ra đối chứng dương mà `tools/v4_mold.py` đang thiếu.

Vá `tools/v4_mold.py` ghi ra `molds/capcut-9.1.0/filter.json` kèm khối `_meta`, mặc định chỉ diff không ghi đè, và khi diff coi `path` cùng `target_timerange.duration` là được phép khác, còn lại bắt buộc khớp.

Viết `tools/shots_dump.py` đọc ngược `draft_content.json` ra `shots.csv` rồi kiểm khứ hồi. Đã có sẵn hạt giống là `tools/shots_crosscheck.py`.

Ba test đầu tiên vào `tests/`: lượng tử hoá frame, công thức lề dạng tổng quát, khứ hồi `shots.csv`.

`run.bat` thật, rồi bắt đầu `pipeline/`.

Thư mục `fixtures/` mới có `README.md`, chưa có bộ đối chứng nào. Project `parity01` đã biến mất khỏi máy render nên hiện dự án **không còn project đối chứng dương nào**. Bài tổng duyệt 8 shot có audio sẽ tạo lại và commit vào đây.