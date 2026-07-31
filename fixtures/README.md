# Fixtures — mốc vàng để so sánh

Thư mục này chỉ chứa **mốc so sánh dạng JSON**, không chứa media.

`parity-gold/` là bộ snapshot timing chuẩn của bộ tám shot, dùng ở bước 9 của quy trình probe parity trong `docs/procedures.md` mục 2. So `parity_before` với `parity_before` và `parity_after` với `parity_after` giữa hai máy, tiêu chí là **0,0 ms tuyệt đối**. Tiêu chí "dưới một frame" chỉ áp cho trước-với-sau trên cùng một máy.

**Media test không nằm ở đây và cố ý không commit.** Bộ tám ảnh PNG 1376×768, `audio.mp3` dài 168,724813 giây và `video1.srt` nằm ở `data\Test_tool_v3\` trên máy phát triển, và trong vendor kit tại `vendor\Test_tool_v3\`. Máy mới chép tay một trong hai nguồn đó vào `data\Test_tool_v3\`.

Lý do không commit: khoảng 10 MB nhị phân không diff được, không bao giờ thay đổi, và máy render hiện chưa cài git nên vẫn phải chép tay.

Hết nội dung file.