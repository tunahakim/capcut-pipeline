# Fixtures — mốc vàng để so sánh

Thư mục này chỉ chứa **mốc so sánh dạng JSON**, không chứa media.

`parity-gold/` là bộ mốc của project probe parity tám shot, dùng ở bước 9 của quy trình probe parity trong `docs/procedures.md` mục 2. Bốn file thuộc ba lược đồ khác nhau:

| File | Lược đồ | Vai trò |
|---|---|---|
| `parity_gold_before.json` | `duration` cộng mảng `rows`, mỗi phần tử gồm `n`, `id`, `start`, `dur` | Timing tám shot, chụp sau lớp Python và trước phiên GUI |
| `parity_gold_after.json` | như trên | Cùng project, chụp sau phiên GUI |
| `parity_gold_snap.json` | `source`, `duration`, `tracks`; mỗi track có `type`, `id` và danh sách segment | Bản chụp chi tiết hơn, có ghi rõ đường dẫn file đã đọc để biết lấy từ bản LONG hay bản gốc |
| `parity_gold_snap_full.json` | bản sao nguyên vẹn `draft_content.json` của timeline, gồm `version`, `new_version`, `fps`, `config` | Đối chiếu cấu trúc chứ không chỉ timing |

So `parity_gold_before` với `parity_gold_before` và `parity_gold_after` với `parity_gold_after` giữa hai máy, tiêu chí là **0,0 ms tuyệt đối**. Tiêu chí "dưới một frame" chỉ áp cho trước-với-sau trên cùng một máy.

Hai con số `duration` trong thư mục này khác nhau và **đó là đúng**. Cặp before, after ghi 168725000 micro giây, là độ dài lấy theo file audio. Hai file snap ghi 168733333, là con số sau khi CapCut làm tròn mốc cuối lên frame theo phép ceil: 168,725 giây nhân 30 fps bằng 5061,75 frame nên thành 5062 frame, tức 168,733333 giây. Luật lượng tử hoá frame ở `../docs/reference.md`.

**Media test không nằm ở đây và cố ý không commit.** Bộ tám ảnh PNG 1376×768, `audio.mp3` dài 168,724813 giây và `video1.srt` nằm ở `data\Test_tool_v3\` trên máy phát triển, và trong vendor kit tại `vendor\Test_tool_v3\`. Máy mới chép tay một trong hai nguồn đó vào `data\Test_tool_v3\`.

Lý do không commit: khoảng 10 MB nhị phân không diff được, không bao giờ thay đổi.