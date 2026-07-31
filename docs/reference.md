# Reference — sổ tra

**Cập nhật 30/07/2026.** File này để tra cứu, không để đọc tuần tự. Mọi con số đều đã kiểm chứng thực nghiệm trừ chỗ ghi rõ `[CHUA XAC MINH]`.

## 1. Hằng số bắt buộc

```
CANVAS_CHECK_FLAG_BIT = 4096      # bit bat checkbox Canvas tren material video
check_flag mac dinh   = 7         # capcut-cli ghi cho material video
check_flag co canvas  = 4103      # = 7 | 4096
check_flag audio      = 1
```

Luôn dùng phép OR `check_flag |= 4096`, không đặt cứng 4103, để giữ các bit khác. Chỉ bật cho material mà segment của nó **thực sự** tham chiếu một `canvas_blur`.

Mức blur theo level của lệnh `bg-blur`: `1 = 0.0625`, `2 = 0.375`, `3 = 0.75`, `4 = 1.0`. Giao diện CapCut hiển thị bốn ô vuông tương ứng. Mục này trong 9.1.0 có nhãn **"Canvas"**, không phải "Background".

## 2. Keyframe

```
property_type dung:  KFTypeScaleX   KFTypePositionX   KFTypePositionY
property_type SAI:   UNIFORM_SCALE  KFTypeUniformScale
curveType         = "Line"
left_control      = {"x": 0.0, "y": 0.0}
right_control     = {"x": 0.0, "y": 0.0}
string_value      = ""
graphID           = ""
time_offset       = TUONG DOI tinh tu dau segment, don vi micro giay
```

`segment.uniform_scale` phải là `{"on": true, "value": 1.0}` để trục Y bám theo `KFTypeScaleX`. Với scale CapCut chỉ cần **một** danh sách `KFTypeScaleX`; với position nó ghi **cả cặp** X và Y kể cả khi Y không đổi — phải bắt chước đúng vậy.

`clip.scale` và `clip.transform` phải đặt bằng giá trị của keyframe **cuối cùng**.

Keyframe `KFTypeAlpha` bị CapCut **âm thầm bỏ qua ở khâu render** trên segment video, ảnh và text, dù preview vẫn hiển thị đúng. Muốn fade thì dùng `capcut image-anim --intro fade-in --outro fade-out`. `[CHUA XAC MINH rieng tren 9.1.0, coi la dung cho toi khi co bang chung nguoc]`

## 3. Hệ toạ độ và công thức lề

`transform` dùng **toạ độ chuẩn hoá NDC**: `±1` là mép canvas, tâm canvas là 0.

```
transform.x = so_tren_UI / 1920         # chieu RONG canvas
transform.y = so_tren_UI / 1080         # chieu CAO canvas, KHONG phai 1920
+X = sang phai      +Y = LEN TREN       # +Y NGUOC quy uoc do hoa thong thuong
dich_chuyen_that_px = so_tren_UI / 2    # so tren UI GAP DOI pixel dich thuc
```

Ba phép đo oracle xác lập điều này: shot 4 với UI Y=100 cho `0.09259259 = 100/1080`; shot 5 với Y=−100 cho giá trị âm trực tiếp; shot 6 với X=400 Y=400 cho `0.20833333 = 400/1920` và `0.37037037 = 400/1080`.

**CapCut không chặn lề.** Đặt scale 80% với position 400/400 thì ảnh chạy ra ngoài khung và bị cắt, không cảnh báo gì. Toàn bộ trách nhiệm giữ ảnh trong khung thuộc về script.

Với ảnh **rộng hơn** canvas, CapCut fit theo chiều rộng:

```
KY = (CW * IMG_H / IMG_W) / CH
   = (1920 * 768/1376) / 1080 = 0.99225        cho anh 1376x768 tren 1920x1080

Dieu kien khong ho mep:
   |transform.x|  <=  1 - s
   |transform.y|  <=  1 - KY * s          voi s la scale tai thoi diem dang xet
```

Kiểm chứng ở `s = 0.5`: `lim_x = 0.5` ứng với UI 960, đo được đúng 960; `lim_y = 0.50388` ứng với UI 544,2, đo được 544.

Vì cả `scale` lẫn `transform` nội suy **tuyến tính** giữa hai keyframe và tập thoả mãn là tập lồi, **chỉ cần kiểm hai điểm đầu và cuối**. Kết luận này **không còn đúng** nếu dùng nhiều hơn hai keyframe hoặc `curveType` khác `"Line"`, vì đường cong ease có thể vọt lố.

Công thức cho ảnh **cao hơn** canvas: `[CHUA XAC MINH]`. Lời giải rẻ hơn là chuẩn hoá mọi ảnh về đúng 1920×1080 ở khâu gen ảnh, khi đó `KY = 1` và công thức rút về `|x| ≤ 1−s`, `|y| ≤ 1−s`.

### 3.1. Lượng tử hoá frame: quy tắc ceil

CapCut làm tròn mỗi **ranh giới cắt** lên frame gần nhất, phép ceil, không phải làm tròn về gần nhất. Duration từng shot là hiệu hai ranh giới đã lượng tử hoá, nên một shot có thể **ngắn đi** dù không shot nào bị dịch.

Kiểm chứng ba ca phân định trên bộ tám shot chuẩn: 592,2 → 593; 1040,4 → 1041; 1466,4 → 1467. Phép làm tròn về gần nhất sẽ cho 592, 1040, 1466 và sai bảng mốc vàng.

Dự báo đã kiểm chứng ngày 31/07/2026: ranh giới nằm đúng lưới frame thì không dịch. Project 300 shot bước 12,000 s tức 360 frame chẵn cho lệch **0,0 ms trên cả 300 shot**, duration giữ nguyên 3600,0000 s.

Quy tắc thiết kế: **bắt mọi mốc shot về bội số của 1/30 giây ở khâu sinh `shots.csv`.** Khi đó CapCut không dịch gì và ràng buộc timing được bảo toàn tuyệt đối.

Trong mục 11, thêm vào cuối:

Xác nhận hai máy ngày 31/07/2026. Máy render (i5-10400F, Windows 10 build 19042, Python 3.14.6) so với mốc vàng: `parity_gold_before → before` lệch 0,0 ms toàn bộ tám shot; `parity_gold_after → after` lệch 0,0 ms toàn bộ tám shot. Cả ba tiêu chí đạt. **Món nợ "chưa xác nhận Python 3.14" đã đóng** — mốc vàng tạo trên 3.13, máy render chạy 3.14.6, kết quả trùng từng chữ số.

Trong mục 12, thay đoạn nói về byte mỗi segment bằng:

Kích thước JSON theo số segment. Segment **trần** do `capcut add-video` sinh ra, không keyframe, không canvas blur, không transition: đo ngày 31/07/2026 trên project 300 shot được **khoảng 2,9 KB mỗi segment**, `draft_content.json` tăng tuyến tính từ 0,01 MB ở 1 shot lên 0,83 MB ở 300 shot. Con số 9390 và 9498 byte ghi ở các bản tài liệu trước là của segment **đầy đủ** có keyframe, canvas blur và transition; phương pháp đo của chúng chưa được ghi lại, dùng để tham khảo chứ đừng dùng để tính toán.

Hiệu năng lớp ghi, đo ngày 31/07/2026, 300 lệnh `add-video` liên tiếp: chi phí mỗi lệnh tách được thành phần cố định khoảng **0,304 s** cộng phần biên khoảng **0,27 ms cho mỗi segment đã tồn tại**. Lệnh đầu 0,32 s, lệnh cuối 0,40 s, tỉ lệ 1,25 lần. Tổng 300 lệnh mất 1,7 phút. Lớp ghi **tuyến tính**; nút thắt là chi phí khởi động tiến trình Node, chiếm chừng 88% thời gian ở mốc 300 segment.

Trong mục 8, thêm ngay dưới dãy số đếm cache:

**Chú ý đơn vị đếm.** Ba công cụ đếm cùng một thư mục cho ba con số khác nhau: lệnh PowerShell đếm thư mục con, `preflight.py` đếm "mục gốc", `fx_audit.py` dùng cách đếm riêng. Ngày 31/07/2026 trên máy render, cùng một thời điểm, ba cách cho 151, 199 và 216. Khi ghi số đếm cache **luôn ghi kèm công cụ nào đếm**, nếu không thì dãy số vô nghĩa.

Đo delta ngày 31/07/2026: mở project 8 shot có 7 transition và 1 effect làm cache tăng **17 mục**. Mở project 300 shot không transition không effect làm cache tăng **0 mục**. Cache chỉ lớn khi có tài nguyên cần resolve.

Trong bảng ở mục 13, sửa và thêm các dòng sau:

| Dựng 300 shot bằng CLI | **Đã kiểm chứng** 31/07/2026, 1,7 phút, lint sạch, CapCut mở mượt |
| Project 60 phút trong CapCut | **Đã kiểm chứng**, kéo timeline mượt, 66,3 MB, chưa đo RAM và thời gian load |
| `kb_apply.py` trên project 300 segment | **Đã kiểm chứng**, chạy được, áp cho 8 shot đầu theo PLAN cứng |

**Siết thêm: lưới an toàn thực tế là 0,1 giây, không phải 1/30 giây.** Ở 30 fps một frame là 33333,333... micro giây, không tròn micro giây, và `capcut-cli` chỉ nhận tham số giây với ba chữ số thập phân. Vì vậy phần lớn bội số của 1/30 giây không biểu diễn được qua CLI và sẽ chịu **hai** lần lượng tử: làm tròn về mili giây rồi mới bị CapCut ceil lên frame. Bội số của **0,1 giây** thì bằng đúng 3 frame, bằng đúng 100000 micro giây, và viết trọn vẹn trong ba chữ số thập phân. **Đã kiểm chứng ngày 31/07/2026 ở quy mô thật:** project `bench300` gồm 300 shot với 300 độ dài khác nhau trong khoảng 6,0 đến 19,4 giây, mọi mốc là bội số 0,1 giây, đo `diff_timing.py` trước và sau khi CapCut mở lần đầu cho **0,0 ms trên toàn bộ 300 shot**, duration giữ nguyên 3600,0000 giây. Đây là bằng chứng mạnh hơn hẳn phép thử 12,000 giây đều nhau trước đó, vì nó phủ nhiều giá trị khác nhau chứ không phải một bước lặp lại.

## 4. Bốn file phải propagate

CapCut 9.1.0 lưu timeline thật trong thư mục lồng. Mọi thay đổi bằng Python phải ghi vào **bốn** file, và đây là bước **cuối cùng** sau tất cả lệnh CLI:

```
<project>\draft_content.json
<project>\template-2.tmp
<project>\Timelines\<main_timeline_id>\draft_content.json
<project>\Timelines\<main_timeline_id>\template-2.tmp
```

`main_timeline_id` đọc từ `<project>\Timelines\project.json`.

Quy tắc đọc/ghi của CapCut, đo bằng thực nghiệm: lúc New Project cả bốn file giống hệt nhau (4265 byte). Khi bản lồng **rỗng** (`duration=0`, `materials={}`) thì CapCut đọc từ **bản gốc**. Khi bản lồng **đã có nội dung** thì CapCut đọc từ **bản lồng** và bỏ qua hoàn toàn bản gốc. Sau mỗi lần CapCut lưu, cả bốn file được đồng bộ về cùng kích thước và timestamp.

`capcut diagnose` báo `Diverged: no` là **sai lệch** — nó chỉ so các mirror ở gốc với nhau, không biết bản lồng tồn tại.

`draft_info.json` **không hề tồn tại** trong scaffold thật. Dòng `draft_info.json missing` của `capcut diagnose` là bình thường.

## 5. Dấu vân tay: ai vừa ghi file

| Đặc điểm | capcut-cli ghi | CapCut ghi |
|---|---|---|
| Dạng float | `0.9`, `1.1` sạch | `0.8999999999999999`, `1.0999999999999999` |
| UUID | chữ **thường** | chữ **HOA** |
| `uniform_scale` | `null` | `{"on": true, "value": 1.0}` |
| material `loudnesses` | không tạo | tự tạo và gắn ref |

`json.dumps(0.9)` của Python luôn ra `0.9`, nên chuỗi float bẩn chắc chắn đến từ thanh trượt trong giao diện.

## 6. Lớp filter — thông số bắt buộc

`capcut add-filter` **hỏng từ dữ liệu nguồn, đã bỏ hẳn**. Dùng `scripts_v1/filter_apply.py`.

| Trường | Giá trị đúng (GUI ghi) | Giá trị sai (CLI ghi) |
|---|---|---|
| bucket material | `materials.effects` | `materials.video_effects` |
| `track.type` | `"filter"` | `"effect"` |
| `apply_target_type` | `0` | `2` |
| `source_platform` | `1` (JianYing) | `0` |
| `sub_type` | `"none"` (chuỗi) | `0` (số) |
| `segment.render_index` | `10000` | `11000` |

`path` dựng theo `Cache/effect/<resource_id>/<md5>`. `value` là cường độ 0.0–1.0, UI hiển thị nhân 100.

**Ràng buộc cache-first, đã chứng minh:** tài nguyên filter **phải có sẵn trong cache**. Đặt `path = ""` thì CapCut ghi đè thành placeholder chứ không tải về. Quy trình cho filter mới: mở CapCut, vào tab Filters, bấm mũi tên tải xuống, đóng CapCut, rồi Python tự động hoá thoải mái.

Filter đã xác nhận chạy được: `Film`, `resource_id 6706773528319906308`, `md5 f6d0e038c2f82b7e262f7a7698e7f642`, `category_id 18582`, `category_name Retro`. **Nó bị khoá Pro** và không có trong `enums.json` ở bất kỳ namespace nào.

## 7. Cơ chế resolve tài nguyên

Marker chưa resolve: `##_material_placeholder_23B2EC28-9736-45F9-966B-EBC7E2D228BE_##`. Đây là **hằng số dùng chung của cả capcut-cli lẫn CapCut**, nghĩa là "tài nguyên này chưa resolve được". Còn sót lại sau khi CapCut đã mở một lần thì đó là **tài nguyên chết**.

| Loại material | CLI ghi `path` gì | CapCut có tự vá? |
|---|---|---|
| transition (đa số) | rỗng | **CÓ** — tải về, điền path đúng |
| transition `cube` | rỗng | **KHÔNG** — đóng dấu placeholder |
| animation intro/outro | đường dẫn **macOS** hardcode | **CÓ** — sửa sang Windows |
| scene effect (`add-effect`) | — | **CÓ** |
| filter (`add-filter`) | placeholder | **KHÔNG** |
| filter Python ghi, path rỗng | — | **KHÔNG** — ghi đè thành placeholder |
| filter Python ghi, path cache có thật | — | giữ nguyên, chạy đúng |

**Khoá tra cứu duy nhất đáng tin là `resource_id`, không phải md5.** CapCut resolve theo `resource_id` qua mạng, CDN trả về md5 hiện hành. md5 trong `enums.json` là ảnh chụp của pyJianYingDraft, đo trên 25 material đối chiếu được thì 6 cái **lệch mà vẫn chạy bình thường**. Bằng chứng quyết định: khuôn material transition do CLI ghi **không hề có trường md5** — chỉ có `effect_id`, `resource_id`, `name`, `duration`, `is_overlap`, `platform`, `type` và hai trường category rỗng.

### Ma trận resolve — còn một ô trống

| | tài nguyên ĐÃ cache | tài nguyên CHƯA cache |
|---|---|---|
| CLI ghi material | OK, nhiều lần | OK (`then-and-now`, `white-flash`) |
| Python dập material | OK (`black-fade`) | **CHƯA BIẾT** |

Ô trống nằm đúng chỗ nguy hiểm. Nếu câu trả lời là "không" thì mỗi lần thêm transition mới trên máy sản xuất sẽ ra **cắt cứng im lặng**, đúng kịch bản `cube`.

**Cảnh báo phương pháp:** không được dùng md5 trong `enums.json` để xác định "tài nguyên này chưa cache" — đó là vòng luẩn quẩn vì md5 chính là thứ đã bị bác bỏ. Phải chụp danh sách thư mục cache **trước và sau**, rồi kiểm xem `path` có trỏ vào thư mục md5 mới xuất hiện không. Lưu ý thêm: duyệt tab Transitions trong GUI có thể prefetch cả nhóm (một lần thả tay làm cache tăng 5 mục), còn mở draft chỉ lấy đúng cái được tham chiếu (hai transition chỉ tăng 1 mục) — nên phép chụp phải bao quanh **thao tác mở draft**, và trong phiên đó không mở tab Transitions.

## 8. Cache hiệu ứng

Vị trí `%LOCALAPPDATA%\CapCut\User Data\Cache\effect`. Cấu trúc **hai tầng**:

```
<thu-muc-goc>\<md5>\        <- md5 la THU MUC
<thu-muc-goc>\<md5>_tmp     <- canh no la mot FILE
```

Đo 29/07/2026: 278 thư mục gốc, 279 thư mục tên md5, **0 file** tên md5. Mọi phép kiểm "đã có trong cache chưa" phải tìm **thư mục con** khớp mẫu 32 ký tự hex, không tìm file, không ghép chuỗi từ md5 biết trước.

Hai kiểu thư mục gốc: **kiểu A** `Cache/effect/<resource_id>/` cho namespace JianYing, 242 trên 278, ổn định; **kiểu B** `Cache/effect/<short-id>/` cho namespace CapCut, 36 trên 278, **short-id thay đổi giữa các phiên** — quan sát "Retro Film" nhảy `1195082 → 11327669 → 1195082` trong khi md5 giữ nguyên. Một tài nguyên có thể nằm dưới cả hai kiểu cùng lúc.

Hệ quả: tra theo `resource_id` trả về rỗng với tài nguyên kiểu B. Đó là **âm tính giả đã biết**, không phải lỗi — đọc kèm cột trạng thái `path`.

Số mục theo thời gian: 272 (v0.5), 277 (v7), 278 (v8), **279 (30/07/2026)**.

## 9. Catalogue

```
capcut enums --transitions | --masks | --image-intros | --image-outros | --image-combos
           | --text-intros | --text-outros | --text-loop-anims | --scene-effects
           | --character-effects | --audio-effects | --fonts | --filters | --bubbles
```

Thêm `--jianying` để lấy namespace JianYing. Cú pháp là **flag**, không phải `--type X`.

| Catalogue | Tổng | Dùng được |
|---|---|---|
| `--transitions` | 116 | **76** (`is_overlap=false`, không VIP, có slug, trừ danh sách đen) |
| `--image-intros` | 43 | 43 |
| `--image-outros` | 23 | 23 |
| `--image-combos` | 108 | 108, không đè keyframe (đã kiểm chứng) |
| `--scene-effects` | 345 | ~47 thuộc nhóm phim cũ/retro |
| `--filters` | 10 | **0 — DỮ LIỆU RÁC**, rid bịa chạy liên tiếp, không md5 |
| `--filters --jianying` | **468** | 468, có md5, cache-first |

**Năm transition nhẹ đã dùng thành công**, đều 466666 µs `is_overlap=false`: `dissolve`, `black-fade`, `blur`, `gradient-wipe`, `dissolve-ii`.

**Sáu transition mạnh đã kiểm chứng ở ĐẦU RA**: `page-turning`, `glitch`, `whirlpool`, `split`, `flip-ii`, `shutter`.

**DANH SÁCH ĐEN**: `cube` (rid `7429600601161338117`) — tài nguyên không resolve được, render ra thành cắt cứng sạch sẽ. Không có cách nào biết trước từ `enums.json`.

Hai transition dùng ở phiên v8: `black-fade` (rid `6724239388189921806`), `then-and-now` (rid `7012818976015127041`).

`default_duration` đa số 466666 µs, riêng `flip` là 1000000 µs. Animation intro/outro không khai báo trong enums, giá trị thực CLI đặt là 500000 µs.

**Luôn dùng slug, đừng dùng name** — có nhiều mục cùng name khác slug (`dissolve` và `dissolve-1` đều tên "Dissolve"). Catalogue JianYing thì phần lớn slug rỗng và name tiếng Trung; những mục đó chỉ gọi được bằng `resource_id` từ Python.

Nhóm scene effect phim cũ: `retro-film`, `film-frame`, `film-frame-2`, `film-2`, `reversal-film`, `rolling-film`, `grain`, `noise`, `noise-1`, `noise-2`, `black-noise`, `old`, `bw-vhs`, `retro-cam`, `old-tv-2`, `tv-lines`, `tv-colored-lines`, `bad-tv`, `light-leak`, `snow-glitch`, `glitch`, `color-glitch`, `level-glitch`, `folds`.

## 10. Cú pháp lệnh CLI

`capcut <lệnh> --help` **không hoạt động** — CLI hiểu `--help` là đường dẫn project. Dùng `python tools/syntax.py` hoặc đọc `reference/describe.json`.

```
capcut add-video  <project> <file-or-url> <start> [duration] [--track-name] [--width] [--height] [--no-probe]
capcut add-audio  <project> <file-or-url> <start> [duration] [--volume]
capcut keyframe   <project> <id> <property> <time> <value> [--easing] | --batch
capcut bg-blur    <project> <id> <level> | --off
capcut transition <project> <id> <slug> [--duration]
capcut image-anim <project> <id> [--intro <slug>] [--outro <slug>] [--combo <slug>]
                                 [--intro-duration] [--outro-duration] [--combo-duration]
capcut add-effect <project> <slug> (<start> <duration> | --full) [--intensity] [--bind <segment-id>]
capcut add-filter <project> <slug> (<start> <duration> | --full) [--intensity]     <- BO HAN
capcut add-sfx    <project> <slug> <start> <duration> [--volume] [--track-name]
capcut add-sticker <project> <resource-id> <start> <duration> [--x] [--y] [--scale] [--rotation]
capcut batch      <project> [--continue-on-error] < operations.jsonl     <- doc JSONL tu STDIN
capcut segments   <project> --track video|audio        <- BAT BUOC co --track
capcut segment    <project> <id>                       <- chi tiet mot segment, KEM material
capcut enums      <category-flag> [--jianying] [-H]
```

Có **76 lệnh**. **Không tồn tại lệnh `scale`** — không có cách nào đặt tỉ lệ tĩnh bằng CLI, phải ghi thẳng `clip.scale` bằng Python.

`capcut export <drafts-dir> --batch` **không phải xuất video**, nó xuất metadata hàng loạt. `capcut render <project> --out x.mp4` dựng lại bằng **FFmpeg**, bỏ qua keyframe, transition, animation, effect, filter; tham số `--scale` là proxy scale để render nhanh, không liên quan `clip.scale`. **Muốn xuất video bắt buộc bấm Export trong GUI.**

`capcut doctor -H` không kèm project chỉ in `Platform`, `Node` và danh sách kiểm môi trường. Muốn thấy khối `Version / Support / Write guard / Schema int` phải truyền thêm đường dẫn project. `capcut version` **không phải** lệnh xem phiên bản — CLI hiểu là tên project và báo lỗi.

Bộ styling của `import-srt`: `--track-name --style-ref <segment-id> --time-offset --font-size --color --align --x --y --alpha --vertical --fixed-width --fixed-height --shadow/--no-shadow --shadow-alpha --shadow-angle --shadow-color --shadow-distance --shadow-smoothing --border-width --border-color --border-alpha --bg-color --bg-alpha --bg-style --bg-round-radius --bg-width --bg-height --bg-h-offset --bg-v-offset --color-cycle --highlight-words --keyword-color --keyword-size`. `--style-ref` cho phép chỉnh một cue bằng tay trong GUI rồi sao chép style sang toàn bộ.

## 11. Mốc vàng parity — bộ tám shot chuẩn

Dựng bằng `scripts_v1/parity_build.py` cộng `scripts_v1/kb_apply.py`.

Trước khi CapCut mở, tức số thô do CLI ghi:

```
shot   start        dur
 1     0.0000     19.7400
 2    19.7400     14.9400
 3    34.6800     14.2000
 4    48.8800     23.8400
 5    72.7200     19.2400
 6    91.9600     14.7400
 7   106.7000     26.0200
 8   132.7200     36.0050
duration = 168.7250
```

Sau khi CapCut mở và lưu, tức đã qua frame quantization:

```
 1     0.0000     19.7667
 2    19.7667     14.9333
 3    34.7000     14.2000
 4    48.9000     23.8333
 5    72.7333     19.2333
 6    91.9667     14.7333
 7   106.7000     26.0333
 8   132.7333     36.0000
duration = 168.7333
```

Chênh lệch: `+0.0 / +26.7 / +20.0 / +20.0 / +13.3 / +6.7 / +0.0 / +13.3 ms`. **Đã đo bốn lần ở bốn cấu hình rất khác nhau và luôn cùng bộ số**, kể cả trên project clone khác với ID segment khác. Frame quantization là hằng số của bộ tám shot này.

Sau `kb_apply.py`: scale `0.86 0.82 0.86 0.76 0.88 0.84 0.88 0.90`, `check_flag = 4103` trên cả tám, `kf = 3` nhóm mỗi shot, shot 2 và shot 7 mang combo animation.

**Ba tiêu chí so giữa hai máy, đừng lẫn:**

So bảng *trước* với *trước* kiểm tính tất định của CLI cộng Python — chưa qua CapCut nên tiêu chí là **0,0 ms tuyệt đối**. So bảng *sau* với *sau* kiểm hành vi quantization của CapCut, cũng **0,0 ms tuyệt đối**. Tiêu chí "dưới 33,3 ms và không tích luỹ" **chỉ dùng cho** phép so trước-với-sau **trên cùng một máy**.

## 12. Thông số đầu ra đã kiểm chứng

```
1920x1080, 30 fps, H.264, bitrate Recommended
nb_frames  = 5062      duration = 168.739002 s      5062/30 = 168.7333 KHOP
size       = 257,505,856 byte  (245.6 MB)
bit_rate   = 12,208,480  (12.2 Mbps)
noi suy 60 phut ~ 5.2 GB
bytes moi segment cua draft_content.json = 9390 (testV4) / 9498 (paritytest)
   -> ngoai suy 300 shot ~ 2.8 MB.  [Phuong phap do: chua ghi ro, can lam ro]
```

Độ dài file xuất khớp duration tới từng frame — không có frame thừa hay thiếu.

Cảnh báo thực dụng: khung tại tâm `Flip II` là **đen tuyệt đối** `RGB=(0,0,0)`, tại tâm `Shutter` rất tối `(51,41,22)`. Đừng lấy thumbnail ở mốc trùng ranh giới transition.

## 13. Bảng trạng thái tính năng

| Tính năng | Trạng thái |
|---|---|
| Tạo project bằng `compile`/`init`/`quickstart` | **Không dùng được** — CapCut từ chối mở |
| Tạo project bằng clone scaffold | **Hoạt động** — `clone_project.py` |
| `add-video`, `add-audio` | Hoạt động, tự đo dimensions và duration nhờ ffprobe |
| `bg-blur` ghi material | Hoạt động, nhưng tạo canvas **mới** để lại canvas cũ mồ côi (vô hại) |
| `bg-blur` kích hoạt | **Cần vá** — phải bật bit 4096 bằng Python |
| Scale tĩnh | **Cần vá** — không có lệnh CLI, ghi thẳng `clip.scale` |
| `keyframe uniform_scale` | **Không hoạt động** — lỗi im lặng |
| Ken Burns zoom / pan / 8 quỹ đạo | **Đã kiểm ở ĐẦU RA** |
| Công thức lề | **Hoạt động** — chạm mép chính xác tới pixel |
| Transition nhóm nhẹ (7 cái cùng lúc) | **Hoạt động**, không dịch timeline |
| Transition nhóm mạnh | **Đã kiểm ở ĐẦU RA**, 6/7 render đúng, `cube` ra cắt cứng |
| `image-anim` intro/outro/combo | **Đã kiểm ở ĐẦU RA**, cùng tồn tại được với keyframe |
| `add-effect --full` | **Hoạt động**, tạo track riêng, nhãn đúng |
| `add-filter` | **BỎ HẲN** |
| Lớp filter bằng Python | **Hoạt động**, timing lệch 0,0 ms, idempotent, cache-first |
| Propagate 4 file | **Bắt buộc**, chạy sau cùng |
| Xuất MP4 | **Đã làm, THÀNH CÔNG** — chỉ bằng GUI |
| Python dập transition + canvas_blur | **Hoạt động** ở mức 4, chưa export |
| Python dập `image-anim` | **Chưa kiểm chứng**, có bằng chứng gián tiếp mạnh |
| `import-srt` | Hoãn, làm tay trong GUI |
| `batch` (JSONL stdin) | **Chưa test** |
| `add-effect --bind` | **Chưa test** |
| `prune` | **Chưa test** — có thể dọn canvas mồ côi |
| Transition `is_overlap=true` | **Chưa test** — rủi ro dịch timeline, tránh dùng |
| Nhạc nền, `audio-fade`, `volume` | Hoãn |

## 14. Đường dẫn hệ thống

```
draft CapCut  : %LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft
cache hieu ung: %LOCALAPPDATA%\CapCut\User Data\Cache\effect
thu muc cai   : %LOCALAPPDATA%\CapCut\Apps\<version>\      <- ten thu muc CO so phien ban
enums.json CLI: %APPDATA%\npm\node_modules\capcut-cli\dist\enums.json   (775 KB)
CAPCUT_LAB    : D:\IT\capcut-lab\data   (may phat trien)
```

Hai file updater phải vô hiệu hoá: `CapCut-DiffUpgrade.exe` và `hpatchz.exe`. **KHÔNG được chặn** `VEHelper.exe`, `VECrashHandler.exe`, `CapCutService.exe`. Ghim winget bằng `winget pin add ByteDance.CapCut --version 9.1.0.3879`. **Không chặn toàn bộ mạng của CapCut** — nó cần mạng để resolve transition và animation lần đầu.

Bộ cài: SHA256 `539F6F5D9851B4787FFAECA8A3D90399D07B1A9EBA4C6AA2C4DC71B62C87A669`, URL `https://sf16-web-tos-buz.capcutstatic.com/obj/capcut-web-buz-sg/packages/CapCut_9_1_0_3879_capcutpc_0_creatortool.exe`, cài im lặng `/silent_install=1 /install_path="..."`, `Scope: user`, `Protocols: capcut`, `ProductCode: CapCut`.

---