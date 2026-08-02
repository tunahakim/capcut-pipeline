# Reference catalog — catalogue hiệu ứng và cú pháp CLI

**Cập nhật 01/08/2026.** Tách khỏi `reference.md` để giữ cả hai file dưới trần 26 KB. Hằng số, công thức và bảng trạng thái tính năng nằm ở `reference.md`.

## 1. Catalogue

```
capcut enums --transitions | --masks | --image-intros | --image-outros | --image-combos
           | --text-intros | --text-outros | --text-loop-anims | --scene-effects
           | --character-effects | --audio-effects | --fonts | --filters | --bubbles
```

Thêm `--jianying` để lấy namespace JianYing. Cú pháp là **flag**, không phải `--type X`; dùng `--type` sẽ trả về mảng rỗng thay vì báo lỗi.

| Catalogue | Tổng | Dùng được |
|---|---|---|
| `--transitions` | 116 | **76** (`is_overlap=false`, không VIP, có slug, trừ danh sách đen) |
| `--image-intros` | 43 | 43 |
| `--image-outros` | 23 | 23 |
| `--image-combos` | 108 | 108, không đè keyframe (đã kiểm chứng) |
| `--scene-effects` | 345 | ~47 thuộc nhóm phim cũ/retro |
| `--filters` | 10 | **0 — DỮ LIỆU RÁC**, rid bịa chạy liên tiếp, không md5 |
| `--filters --jianying` | **468** | **168 free**, 300 mục khoá VIP. Mọi mục có md5, cache-first |

Cờ `is_vip` của namespace JianYing, đo ngày 02/08/2026: 468 mục, **300 mục `is_vip: true`, 168 mục `false`, không mục nào thiếu cờ**. Cờ nằm ở cấp trên cùng của mỗi mục, cạnh `slug`, `name`, `md5`, `effect_id`, `resource_id`. Mục free có slug Latin: `1980`, `abg`, `ditto`, `ke1`, `kv5-d`, `vhs-iii`. Mục VIP có slug Latin: `160-c`, `2077`, `400-h`, `800-z`, `90s`, `city-walk`, `fxn`. Phần lớn số còn lại slug rỗng và name tiếng Trung. **Đã đo ngày 02/08/2026, và câu trả lời là không.** Tra 13 slug Latin trong ô tìm kiếm tab Filters của GUI bản quốc tế: chỉ `vhs-iii`, `1980` và `2077` tìm thấy, mười mục còn lại không có mục nào trùng tên, riêng `ke1` trả về "no content"; `1980` và `2077` mỗi tên hiện **hai** mục trùng tên. Cả ba mục tìm thấy đều **không có vương miện**, kể cả `2077` vốn `is_vip: true`. Nặng hơn cả chuyện cờ VIP: `resource_id` **không trùng nhau**. Thả tay "VHS III" ra `6764669298095952396` trong khi JianYing ghi `7127669764905782542`; thả tay "2077" ra `7145435245712511489` trong khi JianYing ghi `7131347316111314189`. Kết luận: filter trong GUI CapCut quốc tế là **một namespace khác hẳn** 468 mục JianYing, trùng tên chứ không trùng tài nguyên, nên cờ `is_vip` của JianYing **không dùng được** để dự đoán khoá Pro trong GUI. Cùng chiều với `failures.md` mục 2.5, nơi filter "Film" thả tay từ GUI không có trong `enums.json` ở bất kỳ namespace nào. Hệ quả: 468 mục JianYing vẫn dùng được qua `scripts_v1/filter_apply.py` theo đường cache-first, nhưng **không có cách nào biết trước** mục nào khoá Pro trong bản quốc tế.

Hình dạng material filter do GUI ghi ra, đo trên `fxprobe01` ngày 02/08/2026: nằm ở `materials.effects` với `"type": "filter"`, trên một track riêng `"type": "filter"` có `name` rỗng — **không** phải bucket tên `filters`. `effect_id`, `resource_id` và `third_resource_id` bằng nhau; `value` là cường độ; `category_name` là `heycan_search_filter` khi thả từ kết quả tìm kiếm; `path` trỏ vào `Cache/effect/<resource_id>/<md5>` bằng gạch chéo xuôi. Độ dài mặc định khi kéo một filter xuống timeline khoảng 3 giây.

**Năm transition nhẹ đã dùng thành công**, đều 466666 µs `is_overlap=false`: `dissolve`, `black-fade`, `blur`, `gradient-wipe`, `dissolve-ii`.

**Sáu transition mạnh đã kiểm chứng ở ĐẦU RA**: `page-turning`, `glitch`, `whirlpool`, `split`, `flip-ii`, `shutter`.

**DANH SÁCH ĐEN**: `cube`, `resource_id 7429600601161338117` — tài nguyên không resolve được, render ra thành cắt cứng sạch sẽ, không khung đen, không artefact. Không có cách nào biết trước từ `enums.json`.

Hai transition dùng ở phiên v8: `black-fade` (rid `6724239388189921806`), `then-and-now` (rid `7012818976015127041`).

`default_duration` đa số 466666 µs, riêng `flip` là 1000000 µs. Animation intro/outro không khai báo trong enums, giá trị thực CLI đặt là 500000 µs.

**Luôn dùng slug, đừng dùng name** — có nhiều mục cùng name khác slug, ví dụ `dissolve` và `dissolve-1` đều tên "Dissolve". Catalogue JianYing thì phần lớn slug rỗng và name tiếng Trung; những mục đó chỉ gọi được bằng `resource_id` từ Python.

Nhóm scene effect phim cũ: `retro-film`, `film-frame`, `film-frame-2`, `film-2`, `reversal-film`, `rolling-film`, `grain`, `noise`, `noise-1`, `noise-2`, `black-noise`, `old`, `bw-vhs`, `retro-cam`, `old-tv-2`, `tv-lines`, `tv-colored-lines`, `bad-tv`, `light-leak`, `snow-glitch`, `glitch`, `color-glitch`, `level-glitch`, `folds`.

## 2. Cú pháp lệnh CLI

`capcut <lệnh> --help` **không hoạt động** — CLI hiểu tham số đầu tiên của mọi lệnh con là đường dẫn project, nên nó báo `No draft found at: --help`. Dùng `python tools/syntax.py` hoặc đọc `reference/describe.json`.

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

`capcut doctor -H` không kèm project chỉ in `Platform`, `Node` và danh sách kiểm môi trường. Muốn thấy khối `Version / Support / Write guard / Schema int` phải truyền thêm đường dẫn project. `capcut version` **không phải** lệnh xem phiên bản — CLI hiểu là tên project và báo lỗi, nên mọi script kiểm tra sự tồn tại của CLI bằng lệnh này đều cho âm tính giả.

Bộ styling của `import-srt`: `--track-name --style-ref <segment-id> --time-offset --font-size --color --align --x --y --alpha --vertical --fixed-width --fixed-height --shadow/--no-shadow --shadow-alpha --shadow-angle --shadow-color --shadow-distance --shadow-smoothing --border-width --border-color --border-alpha --bg-color --bg-alpha --bg-style --bg-round-radius --bg-width --bg-height --bg-h-offset --bg-v-offset --color-cycle --highlight-words --keyword-color --keyword-size`. `--style-ref` cho phép chỉnh một cue bằng tay trong GUI rồi sao chép style sang toàn bộ.