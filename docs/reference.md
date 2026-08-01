# Reference — sổ tra

**Cập nhật 01/08/2026.** File này để tra cứu, không để đọc tuần tự. Mọi con số đều đã kiểm chứng thực nghiệm trừ chỗ ghi rõ `[CHUA XAC MINH]`. Catalogue hiệu ứng và cú pháp 76 lệnh CLI nằm ở `reference-catalog.md`.

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

Keyframe `KFTypeAlpha` bị CapCut âm thầm bỏ qua ở khâu render trên segment video, ảnh và text, dù preview vẫn hiển thị đúng. Muốn fade thì dùng `capcut image-anim --intro fade-in --outro fade-out`. `[CHUA XAC MINH rieng tren 9.1.0, coi la dung cho toi khi co bang chung nguoc]`

## 3. Hệ toạ độ và công thức lề

`transform` dùng **toạ độ chuẩn hoá NDC**: `±1` là mép canvas, tâm canvas là 0.

```
transform.x = so_tren_UI / 1920         # chieu RONG canvas
transform.y = so_tren_UI / 1080         # chieu CAO canvas, KHONG phai 1920
+X = sang phai      +Y = LEN TREN       # +Y NGUOC quy uoc do hoa thong thuong
dich_chuyen_that_px = so_tren_UI / 2    # so tren UI GAP DOI pixel dich thuc
```

Ba phép đo oracle xác lập điều này: shot 4 với UI Y=100 cho `0.09259259 = 100/1080`; shot 5 với Y=−100 cho giá trị âm trực tiếp; shot 6 với X=400 Y=400 cho `0.20833333 = 400/1920` và `0.37037037 = 400/1080`. Xác nhận độc lập ngày 31/07/2026 trên máy render: panel Video của shot 6 project `parity01` hiện `Scale 84%` và `Position Y 130`, khớp `scale=0.84` và `transform.y=+0.12` vì 0,12 nhân 1080 bằng 129,6.

**CapCut không chặn lề.** Đặt scale 80% với position 400/400 thì ảnh chạy ra ngoài khung và bị cắt, không cảnh báo gì. Toàn bộ trách nhiệm giữ ảnh trong khung thuộc về script.

### 3.1. Công thức lề tổng quát theo KX và KY

Gọi ảnh là `W x H`, canvas là `CW x CH`, tỉ lệ ảnh `ar_img = W/H`, tỉ lệ canvas `ar_canvas = CW/CH`. CapCut đặt ảnh ở chế độ chứa trọn, tức thu ảnh cho tới khi vừa khung theo chiều chật hơn. Hai hệ số chiếm chỗ là:

```
neu ar_img >= ar_canvas:      # anh RONG hon khung, vua theo chieu ngang
    KX = 1
    KY = ar_canvas / ar_img
neu ar_img <  ar_canvas:      # anh CAO hon khung, vua theo chieu doc
    KX = ar_img / ar_canvas
    KY = 1

Dieu kien khong ho mep, voi s la scale tai thoi diem dang xet:
    |transform.x|  <=  1 - KX * s
    |transform.y|  <=  1 - KY * s
```

Kiểm chứng nhánh ảnh rộng: ảnh 1376×768 trên khung 1920×1080 cho `ar_img = 1.79167`, `ar_canvas = 1.77778`, nên `KX = 1` và `KY = 0.99225`. Ở `s = 0.5`, `lim_x = 0.5` ứng với UI 960 và đo được đúng 960; `lim_y = 0.50388` ứng với UI 544,2 và đo được 544. Nhánh ảnh cao hơn khung **chưa có phép đo oracle**, mới chỉ là suy luận đối xứng — `[CHUA XAC MINH]`.

Vì cả `scale` lẫn `transform` nội suy tuyến tính giữa hai keyframe và tập thoả mãn là tập lồi, **chỉ cần kiểm hai điểm đầu và cuối**. Kết luận này **không còn đúng** nếu dùng nhiều hơn hai keyframe hoặc `curveType` khác `"Line"`, vì đường cong ease có thể vọt lố.

Lời giải rẻ nhất là chuẩn hoá mọi ảnh về đúng 1920×1080 ở khâu gen ảnh, khi đó `KX = KY = 1` và công thức rút về `|x| ≤ 1−s`, `|y| ≤ 1−s`. Khi không chuẩn hoá được thì `KX` và `KY` phải tính **theo từng ảnh** và đi kèm từng dòng của `shots.csv`; áp một hằng số chung cho cả bộ là sai.

### 3.2. Lượng tử hoá frame và lưới 0,1 giây

CapCut làm tròn mỗi **ranh giới cắt** lên frame gần nhất, phép **ceil**, không phải làm tròn về gần nhất. Duration từng shot là hiệu hai ranh giới đã lượng tử hoá, nên một shot có thể ngắn đi dù không shot nào bị dịch. Việc làm tròn xảy ra ở **lần CapCut mở project đầu tiên**, không phải lúc CLI ghi.

Kiểm chứng ba ca phân định trên bộ tám shot chuẩn: 592,2 → 593; 1040,4 → 1041; 1466,4 → 1467. Phép làm tròn về gần nhất sẽ cho 592, 1040, 1466 và sai bảng mốc vàng.

**Lưới an toàn là 0,1 giây.** Ở 30 fps một frame là 33333,333… micro giây, không tròn micro giây, và `capcut-cli` chỉ nhận tham số giây với ba chữ số thập phân, nên phần lớn bội số của 1/30 giây sẽ chịu **hai** lần lượng tử: làm tròn về mili giây rồi mới bị CapCut ceil lên frame. Bội số của 0,1 giây bằng đúng 3 frame, bằng đúng 100000 micro giây, và viết trọn vẹn trong ba chữ số thập phân.

**Bắt lưới theo ranh giới tuyệt đối, không theo độ dài shot.** Mỗi ranh giới lấy `round(t / 0.1) * 0.1`, độ dài shot là hiệu hai ranh giới đã bắt lưới. Làm ngược lại, tức bắt lưới từng độ dài rồi cộng dồn, sẽ tích luỹ sai số. Sai lệch mỗi điểm cắt so với mốc lời thoại tối đa 50 ms và **không phụ thuộc tổng độ dài**, nên lời hứa ảnh tiếng phụ đề khớp ở mọi thời điểm đúng cả với video rất dài. Phụ đề không bắt lưới, giữ nguyên timestamp của stable-ts, nên phụ đề so với audio khớp tuyệt đối.

**Mốc cuối dùng ceil chứ không dùng round, và luôn cộng một đuôi cố ý** sau khi hết narration, để phần lẻ nằm trong một khoảng được thiết kế chứ không phải một chỗ ngẫu nhiên. Đuôi là bắt buộc; tối thiểu an toàn là một frame tức 33,3 ms, giá trị đang dùng là 2000 ms.

Ba bằng chứng ở quy mô thật, cả ba đều cho **0,0 ms**: `bench300` với 300 shot bước đều 12,000 s; `bench300` bản sau với 300 độ dài khác nhau từ 6,0 tới 19,4 s; và `prod60` với 300 shot khoá theo file narration thật dài 3543,222857 s. Bài `reh10` kiểm chứng riêng luật ceil ở mốc cuối: segment audio bị nới **+8,5 ms** lên biên frame, đuôi cố ý hấp thụ trọn, không shot nào bị đẩy.

## 4. Bốn file phải propagate

CapCut 9.1.0 lưu timeline thật trong thư mục lồng. Mọi thay đổi bằng Python phải ghi vào **bốn** file, và đây là bước **cuối cùng** sau tất cả lệnh CLI:

```
<project>\draft_content.json
<project>\template-2.tmp
<project>\Timelines\<main_timeline_id>\draft_content.json
<project>\Timelines\<main_timeline_id>\template-2.tmp
```

`main_timeline_id` đọc từ `<project>\Timelines\project.json`.

Quy tắc đọc và ghi của CapCut, đo bằng thực nghiệm: lúc New Project cả bốn file giống hệt nhau, 4265 byte. Khi bản lồng **rỗng** thì CapCut đọc từ **bản gốc**. Khi bản lồng **đã có nội dung** thì CapCut đọc từ **bản lồng** và bỏ qua hoàn toàn bản gốc. Sau mỗi lần CapCut lưu, cả bốn file được đồng bộ về cùng kích thước và timestamp.

`capcut diagnose` báo `Diverged: no` là **sai lệch** — nó chỉ so các mirror ở gốc với nhau, không biết bản lồng tồn tại. `draft_info.json` **không hề tồn tại** trong scaffold thật, nên dòng `draft_info.json missing` của `capcut diagnose` là bình thường.

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

**Khoá tra cứu duy nhất đáng tin là `resource_id`, không phải md5.** CapCut resolve theo `resource_id` qua mạng, CDN trả về md5 hiện hành. md5 trong `enums.json` là ảnh chụp của pyJianYingDraft; đo trên 25 material đối chiếu được thì 6 cái lệch mà vẫn chạy bình thường. Bằng chứng quyết định: khuôn material transition do CLI ghi **không hề có trường md5**.

Ma trận resolve còn một ô trống:

| | tài nguyên ĐÃ cache | tài nguyên CHƯA cache |
|---|---|---|
| CLI ghi material | OK, nhiều lần | OK (`then-and-now`, `white-flash`) — nhưng xem cảnh báo |
| Python dập material | OK (`black-fade`) | **CHƯA BIẾT** |

Ô "CLI ghi, chưa cache" thực ra cũng **chưa chắc**: `then-and-now` được chọn làm đối chứng dương *vì* biết trước sẽ chạy, và không chỗ nào ghi lại phép chụp cache trước-sau cho riêng nó. Khi làm phép thử đóng ô "Python dập, chưa cache", thêm luôn nhánh CLI vào cùng thí nghiệm để đóng cả hai bằng một lần mở CapCut.

**Cảnh báo phương pháp:** không được dùng md5 trong `enums.json` để xác định "tài nguyên này chưa cache" — đó là vòng luẩn quẩn vì md5 chính là thứ đã bị bác bỏ. Phải chụp danh sách thư mục cache **trước và sau**, rồi kiểm xem `path` có trỏ vào thư mục md5 mới xuất hiện không. Duyệt tab Transitions trong GUI có thể prefetch cả nhóm, còn mở draft chỉ lấy đúng cái được tham chiếu, nên phép chụp phải bao quanh **thao tác mở draft**, và trong phiên đó không mở tab Transitions.

## 8. Cache hiệu ứng

Vị trí `%LOCALAPPDATA%\CapCut\User Data\Cache\effect`. Cấu trúc **hai tầng**:

```
<thu-muc-goc>\<md5>\        <- md5 la THU MUC
<thu-muc-goc>\<md5>_tmp     <- canh no la mot FILE
```

Đo 29/07/2026: 278 thư mục gốc, 279 thư mục tên md5, **0 file** tên md5. Mọi phép kiểm "đã có trong cache chưa" phải tìm **thư mục con** khớp mẫu 32 ký tự hex, không tìm file, không ghép chuỗi từ md5 biết trước.

Hai kiểu thư mục gốc: **kiểu A** `Cache/effect/<resource_id>/` cho namespace JianYing, 242 trên 278, ổn định; **kiểu B** `Cache/effect/<short-id>/` cho namespace CapCut, 36 trên 278, **short-id thay đổi giữa các phiên** — quan sát "Retro Film" nhảy `1195082 → 11327669 → 1195082` trong khi md5 giữ nguyên. Một tài nguyên có thể nằm dưới cả hai kiểu cùng lúc. Hệ quả: tra theo `resource_id` trả về rỗng với tài nguyên kiểu B; đó là **âm tính giả đã biết**, đọc kèm cột trạng thái `path`.

**Chú ý đơn vị đếm.** Ba công cụ đếm cùng một thư mục cho ba con số khác nhau: lệnh PowerShell đếm thư mục con, `preflight.py` đếm mục gốc, `fx_audit.py` dùng cách đếm riêng. Ngày 31/07/2026 trên máy render, cùng một thời điểm, ba cách cho 151, 199 và 216. Khi ghi số đếm cache **luôn ghi kèm công cụ nào đếm**, nếu không thì dãy số vô nghĩa.

Đo delta ngày 31/07/2026: mở project 8 shot có 7 transition và 1 effect làm cache tăng **17 mục**; mở project 300 shot không transition không effect làm cache tăng **0 mục**. Cache chỉ lớn khi có tài nguyên cần resolve.

## 9. Mốc vàng parity — bộ tám shot chuẩn

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

Chênh lệch: `+0.0 / +26.7 / +20.0 / +20.0 / +13.3 / +6.7 / +0.0 / +13.3 ms`. **Đã đo bốn lần ở bốn cấu hình rất khác nhau và luôn cùng bộ số**, kể cả trên project clone khác với ID segment khác.

Sau `kb_apply.py`: scale `0.86 0.82 0.86 0.76 0.88 0.84 0.88 0.90`, `check_flag = 4103` trên cả tám, `kf = 3` nhóm mỗi shot, shot 2 và shot 7 mang combo animation.

**Ba tiêu chí so, đừng lẫn.** So bảng *trước* với *trước* kiểm tính tất định của CLI cộng Python, tiêu chí là **0,0 ms tuyệt đối**. So bảng *sau* với *sau* kiểm hành vi quantization của CapCut, cũng **0,0 ms tuyệt đối**. Tiêu chí "dưới 33,3 ms và không tích luỹ" **chỉ dùng cho** phép so trước-với-sau **trên cùng một máy**.

Xác nhận hai máy ngày 31/07/2026: máy render với Python 3.14.6 so với mốc vàng tạo trên Python 3.13 cho lệch **0,0 ms** trên cả bảng trước lẫn bảng sau. Món nợ "chưa xác nhận Python 3.14" đã đóng.

## 10. Thông số đầu ra và hiệu năng

Bản export tham chiếu 2 phút 48 của bộ tám shot chuẩn:

```
1920x1080, 30 fps, H.264, bitrate Recommended
nb_frames  = 5062      duration = 168.739002 s      5062/30 = 168.7333 KHOP
size       = 257,505,856 byte  (245.6 MB)
bit_rate   = 12,208,480  (12.2 Mbps)
```

Bản export 60 phút, đo hai lần trên máy render với hai project khác nhau và cho kết quả gần như trùng nhau: khoảng **4,07 GB**, bitrate video chừng **9700 kbps**, thời gian export khoảng **6 phút**, tức nhanh hơn thời gian thực chừng mười lần. CPU và GPU đều dưới 40 phần trăm trong lúc render, nên nút thắt không phải hai thứ đó; chưa xác định là gì. `prod60` cụ thể: 4.373.649.030 byte, 00:59:05, video 9673 kbps, tổng 9862 kbps, audio 189 kbps stereo 44,1 kHz — narration nguồn là mono, CapCut nâng lên stereo khi xuất.

Độ dài file xuất khớp duration tới từng frame, không có frame thừa hay thiếu.

Kích thước JSON theo số segment: segment **trần** do `capcut add-video` sinh ra, không keyframe, không canvas blur, không transition, tốn khoảng **2,9 KB**; `draft_content.json` tăng tuyến tính từ 0,01 MB ở 1 shot lên 0,83 MB ở 300 shot. Project 300 shot **đầy đủ hiệu ứng** cho khoảng **1,0 MB**. Con số 9390 và 9498 byte ghi ở các bản tài liệu trước là của segment đầy đủ nhưng phương pháp đo không được ghi lại, chỉ dùng tham khảo.

Hiệu năng lớp ghi: chi phí mỗi lệnh CLI tách được thành phần cố định khoảng **0,304 giây** cộng phần biên khoảng **0,27 mili giây cho mỗi segment đã tồn tại**. Ở mốc 300 segment phần cố định chiếm chừng 88 phần trăm. Đo thực tế: 300 lệnh `add-video` mất 1,7 phút; 902 lệnh đủ loại của `prod60` mất 5,5 phút, trung bình 0,367 giây mỗi lệnh. Lớp ghi **tuyến tính**; nút thắt là chi phí khởi động tiến trình Node. Kiến trúc một tiến trình CLI cho mỗi thao tác được giữ nguyên, chỉ xem lại nếu tổng số lệnh vượt khoảng 2000.

Cảnh báo thực dụng khi trích khung: khung tại tâm `Flip II` là **đen tuyệt đối** `RGB=(0,0,0)`, tại tâm `Shutter` rất tối `(51,41,22)`. Đừng lấy thumbnail ở mốc trùng ranh giới transition.

## 11. Bảng trạng thái tính năng

| Tính năng | Trạng thái |
|---|---|
| Tạo project bằng `compile`/`init`/`quickstart` | **Không dùng được** — CapCut từ chối mở |
| Tạo project bằng clone scaffold | **Hoạt động** — `clone_project.py`, tự đặt `draft_fold_path` từ 01/08/2026 nên không còn bước tay nào sau đó |
| `add-video`, `add-audio` | Hoạt động, tự đo dimensions và duration nhờ ffprobe |
| `bg-blur` ghi material | Hoạt động, nhưng tạo canvas **mới** để lại canvas cũ mồ côi (vô hại) |
| `bg-blur` kích hoạt | **Cần vá** — phải bật bit 4096 bằng Python. Đã kiểm chứng ở mức 5 trên 300 shot |
| Scale tĩnh | **Cần vá** — không có lệnh CLI, ghi thẳng `clip.scale` |
| `keyframe uniform_scale` | **Không hoạt động** — lỗi im lặng |
| Ken Burns zoom / pan / 8 quỹ đạo | **Đã kiểm ở ĐẦU RA** |
| Công thức lề, nhánh ảnh rộng hơn khung | **Hoạt động** — chạm mép chính xác tới pixel |
| Công thức lề, nhánh ảnh cao hơn khung | **Chưa kiểm chứng** — mới là suy luận đối xứng |
| Transition nhóm nhẹ | **Hoạt động**, không dịch timeline |
| Transition nhóm mạnh | **Đã kiểm ở ĐẦU RA**, 6/7 render đúng, `cube` ra cắt cứng |
| `image-anim` intro/outro/combo | **Đã kiểm ở ĐẦU RA**, cùng tồn tại được với keyframe |
| `add-effect --full` | **Hoạt động**, tạo track riêng, nhãn đúng |
| `add-filter` | **BỎ HẲN** |
| Lớp filter bằng Python | **Hoạt động**, timing lệch 0,0 ms, idempotent, cache-first |
| Propagate 4 file | **Bắt buộc**, chạy sau cùng |
| Dựng 300 shot bằng CLI | **Đã kiểm chứng**, 902 lệnh trong 5,5 phút, lint sạch |
| Project 60 phút trong CapCut | **Đã kiểm chứng**, mở gần như tức thời, kéo timeline mượt, RAM tăng 1–2% |
| `kb_apply.py` trên project 300 segment | **Đã kiểm chứng**, 0,1 giây cho 300 shot |
| Timing khoá theo file audio thật | **Đã kiểm chứng** trên `reh10` và `prod60` |
| Xuất MP4 60 phút | **Đã làm, THÀNH CÔNG** — chỉ bằng GUI |
| Python dập transition + canvas_blur | **Hoạt động** ở mức 4, chưa export |
| Python dập `image-anim` | **Chưa kiểm chứng**, có bằng chứng gián tiếp mạnh |
| `import-srt` | Hoãn, làm tay trong GUI |
| `batch` (JSONL stdin) | **Chưa test** |
| `add-effect --bind` | **Chưa test** |
| `prune` | **Chưa test** — có thể dọn canvas mồ côi |
| Transition `is_overlap=true` | **Chưa test** — rủi ro dịch timeline, tránh dùng |
| Nhạc nền, `audio-fade`, `volume` | Hoãn |

## 12. Đường dẫn hệ thống

```
draft CapCut  : %LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft
cache hieu ung: %LOCALAPPDATA%\CapCut\User Data\Cache\effect
thu muc cai   : %LOCALAPPDATA%\CapCut\Apps\<version>\      <- ten thu muc CO so phien ban
enums.json CLI: %APPDATA%\npm\node_modules\capcut-cli\dist\enums.json   (775 KB)
CAPCUT_LAB    : D:\IT\capcut-lab\data
```

Hai file updater phải vô hiệu hoá: `CapCut-DiffUpgrade.exe` và `hpatchz.exe`. **KHÔNG được chặn** `VEHelper.exe`, `VECrashHandler.exe`, `CapCutService.exe`. Cách chặn đã dùng và đã xác minh ba lớp là deny ACL: `icacls <file> /deny "<DOMAIN>\<user>:(RX,W,D)"`, gỡ bằng `icacls <file> /remove:d "<DOMAIN>\<user>"`. Chọn deny thay vì đổi tên vì deny quyền ghi chặn luôn khả năng CapCut tải bản mới đè lên đúng tên cũ. Máy nào có winget thì ghim thêm bằng `winget pin add ByteDance.CapCut --version 9.1.0.3879`. **Không chặn toàn bộ mạng của CapCut** — nó cần mạng để resolve transition và animation lần đầu.

Bộ cài: SHA256 `539F6F5D9851B4787FFAECA8A3D90399D07B1A9EBA4C6AA2C4DC71B62C87A669`, URL `https://sf16-web-tos-buz.capcutstatic.com/obj/capcut-web-buz-sg/packages/CapCut_9_1_0_3879_capcutpc_0_creatortool.exe`, cài im lặng `/silent_install=1 /install_path="..."`, `Scope: user`, `Protocols: capcut`, `ProductCode: CapCut`.