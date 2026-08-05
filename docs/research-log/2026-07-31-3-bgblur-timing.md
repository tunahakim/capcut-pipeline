# Nhật ký nghiên cứu 31/07/2026 (tối) — Đóng ca `bg-blur`, chốt luật timing theo audio

**Tóm tắt:** Đóng ca lỗi im lặng thứ bảy: `bg-blur` không hỏng, quan sát ban đầu sai. Chốt luật bắt lưới 0,1 giây theo ranh giới tuyệt đối, mốc cuối dùng ceil, cộng đuôi cố ý
**Phiên:** 23:37 tối

## Kết quả chính

Ca "lỗi im lặng thứ bảy" khép lại: `bg-blur` **không hỏng**, quan sát ban đầu sai. Chi tiết đầy đủ ở `failures.md` mục 2.8. Tóm tắt số liệu: 153 `canvas_blur` và 147 `canvas_color` trên 300 segment, mỗi segment đúng một ref, không canvas mồ côi, `check_flag` khớp một-đối-một, file gốc và file lồng trùng nhau ở 2.499.852 byte, đối chiếu 300 dòng CSV với JSON cho 0 lệch trên năm trường.

Ba công cụ mới trên máy render: `tools/bgblur_diag.py` chẩn đoán canvas và scale theo segment, `tools/bgblur_frames.py` trích khung từ MP4 đã export tại giữa các shot đã biết trước nhóm, `tools/shots_crosscheck.py` đối chiếu `shots.csv` với `draft_content.json`. Cái thứ ba là hạt giống của `tools/shots_dump.py`.

## Quyết định thiết kế đã chốt

**Timing khi khoá theo file audio thật.** Bắt lưới theo **ranh giới tuyệt đối**, không theo độ dài: mỗi ranh giới cắt lấy `round(t / 0.1) * 0.1`, độ dài shot là hiệu hai ranh giới đã bắt lưới. Làm ngược lại sẽ tích luỹ sai số. Sai lệch mỗi điểm cắt so với mốc lời thoại tối đa 50 ms và **không phụ thuộc tổng độ dài**, nên lời hứa "ảnh, tiếng, phụ đề khớp ở mọi thời điểm" đúng cả với video 10 giờ. Phụ đề không bắt lưới, giữ nguyên timestamp của stable-ts, nên phụ đề so với audio là khớp tuyệt đối.

**Mốc cuối dùng ceil, không dùng round**, cộng thêm một đuôi cố ý sau khi hết narration để phần lẻ nằm trong một khoảng được thiết kế chứ không phải một chỗ sứt mẻ. Track audio **không bắt lưới**: không truyền `duration` cho `capcut add-audio`, để nó tự probe; ranh giới cuối của segment audio bị CapCut ceil lên frame, tối đa 33,3 ms, và vì sau nó không còn segment nào nên không đẩy được gì.

**Mốc lưu bằng số nguyên mili giây, không phải số thực.** Lưới là 100 ms; khi ghi ra CLI thì chia 1000 và in ba chữ số thập phân. Ở quy mô 36.000 giây, cộng nhân trên float sẽ sinh đúng loại lỗi đã cắn `bench_shots.py`. Ở 30 fps thì 100 ms bằng đúng 3 frame nên mọi mốc trên lưới luôn trùng biên frame.

**Cột `blur` sinh theo luật hình học**, không rải ngẫu nhiên: bật blur khi `KX * s < 1` hoặc `KY * s < 1` với `s` nhỏ nhất của shot.

**Ràng buộc "mọi ảnh phải là 1920×1080" bị bãi bỏ.** Code phải chạy với mọi kích thước ảnh và mọi tỉ lệ khung, vì dự án sẽ làm cả video vuông và video dọc. Công thức hình học tổng quát ghi trong `TODO.md`.

**Ngân sách 26 KB mỗi file tài liệu**, lý do và ngoại lệ ghi trong `README.md`.

## Chưa kiểm chứng, đừng tin vội

Khâu audio chưa từng chạy cùng timing khoá cứng ở bất kỳ quy mô nào. Luật ceil ở mốc cuối hoàn toàn là suy luận. Công thức lề tổng quát cho ảnh cao hơn khung chưa có phép đo oracle. Số đo render 4,07 GB trong 20 phút có thể lạc quan vì `bench300` dùng ảnh nhân bản.

## Kế hoạch tiếp theo

Chuẩn bị tài sản gồm audio nối dài khoảng 59 phút và thư mục ảnh đủ kích thước. Viết `tools/prod_shots.py` thay `bench_shots.py`. Tổng duyệt 8 shot có audio để thử luật ceil, sản phẩm commit vào `fixtures/`. Rồi bài 60 phút đầy đủ có narration, xuất MP4, đo lại máy render. Filter tạm để ngoài.