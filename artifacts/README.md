# Artifacts — bằng chứng của các phiên đã đóng

Thư mục này giữ sản phẩm đo đạc của những lần dựng thật: snapshot timing và bảng shot. Nó khác `fixtures/` ở chỗ `fixtures/` là mốc vàng để so đi so lại nhiều lần, còn ở đây là hồ sơ một lần, gắn với một phiên cụ thể. Nguyên tắc: **chỉ thêm, không sửa file cũ**. Muốn đo lại thì sinh file mới mang tên khác, vì sửa đè lên một bằng chứng cũ là làm hỏng khả năng đối chiếu về sau.

| File | Nội dung | Phiên sinh ra | Nhật ký |
|---|---|---|---|
| `prod60_before.json` | Snapshot timing của project `prod60`, 300 shot, chụp sau lớp Python và trước khi mở CapCut | Bài sản xuất thật 60 phút có narration, 31/07/2026 | `../docs/research-log/2026-07-31-5-prod60.md` |
| `prod60_after.json` | Cùng project, chụp sau phiên GUI và sau khi đóng CapCut bằng nút X | Như trên | `../docs/research-log/2026-07-31-5-prod60.md` |
| `shots_prod.csv` | Bảng shot đầu vào của `prod60`, timing khoá theo file narration | Như trên | `../docs/research-log/2026-07-31-5-prod60.md` |
| `reh10_before.json` | Snapshot timing của bản tổng duyệt 10 shot có narration, trước phiên GUI | Tổng duyệt 10 shot, 31/07/2026 | `../docs/research-log/2026-07-31-4-reh10-audio.md` |
| `reh10_after.json` | Cùng bản tổng duyệt, sau phiên GUI | Như trên | `../docs/research-log/2026-07-31-4-reh10-audio.md` |
| `shots_reh.csv` | Bảng shot đầu vào của bản tổng duyệt 10 shot | Như trên | `../docs/research-log/2026-07-31-4-reh10-audio.md` |

Trong cả hai cặp, file `before` và `after` có cùng kích thước byte, phù hợp với kết luận lệch 0,0 ms ghi trong nhật ký. Đó là dấu hiệu chứ không phải phép chứng minh: muốn chắc thì so hash hoặc chạy `python tools/timing_snap.py diff <before> <after>`.

Muốn biết chính xác lệnh nào sinh ra từng file thì tra nhật ký phiên tương ứng ở cột cuối; ở đây cố ý không chép lại, vì chép lại là tạo bản sao thứ hai của cùng một sự thật.