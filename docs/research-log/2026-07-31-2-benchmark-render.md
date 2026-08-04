# Nhật ký phiên 31/07/2026 (chiều) — benchmark máy render, dựng và export 60 phút

**Tóm tắt:** Benchmark máy render: dựng 300 shot đủ hiệu ứng, lệch 0,0 ms, export 60 phút thành công

**Mục tiêu:** dựng một project 60 phút đủ hiệu ứng rồi export thật, để quyết định máy i5-10400F cộng GTX 1080 có đủ làm máy render chính thức không.

**Dựng.** Bốn script mới trong `tools/`: `bench_shots.py` sinh `shots.csv` 300 shot với mọi mốc là bội số 0,1 giây và tổng đúng 3600,0 giây; `bench_build.py` chạy khâu CLI; `bench_kb.py` chạy lớp Python; `bench_fixkb.py` chữa lỗi làm tròn. `bench_kb.py` **không viết lại bộ sinh keyframe** mà nạp `scripts_v1/kb_apply.py` rồi thay biến `PLAN` bằng dữ liệu đọc từ CSV — cách này tránh được nguy cơ lệch schema keyframe và nên giữ làm mẫu.

**Số đo khâu dựng.** 905 lệnh CLI trong 5,4 phút, trung bình 0,355 giây mỗi lệnh, khớp gần như tuyệt đối với mô hình 0,304 giây cố định cộng 0,27 ms mỗi segment rút ra từ Việc A. `draft_content.json` cuối cùng nặng 1,04 MB.

**Kết quả quyết định.** `diff_timing.py before after` cho **0,0 ms trên toàn bộ 300 shot**, duration giữ nguyên 3600,0000 giây. Đây là bằng chứng thực nghiệm cho quy tắc bội số 0,1 giây ở quy mô thật với 300 độ dài khác nhau, mạnh hơn hẳn phép thử 12,000 giây đều nhau hôm trước. Quy tắc chuyển từ suy luận sang đã kiểm chứng.

**Số đo máy render.** Mở project 300 shot gần như tức thời, RAM tăng 1 đến 2 phần trăm, preview mượt. Export 60 phút mất khoảng 20 phút, ra 4,06 GB, 9696 kbps. Không hiện hộp thoại Pro nào. Kết luận: máy đủ mạnh.

**Lỗi phát hiện được.** Một, `bg-blur` mất tác dụng hoàn toàn ở quy mô 300 shot dù mọi kiểm tra tự động đều sạch — lỗi im lặng thứ bảy, xem `failures.md` mục 2.7, chưa xử lý. Hai, `bench_shots.py` kiểm biên trên giá trị chưa làm tròn nên shot 1 vượt mép 5e-7 sau khi ghi CSV; bắt được nhờ shot 1 là probe biên cố ý. Ba, bắt `SystemExit` mà bỏ `e.code` làm mất sạch thông báo lỗi và tốn một vòng chẩn đoán.

**Chưa làm:** filter vẫn bị bỏ khỏi bài đo vì chưa có filter free nào được xác minh.

**Đính chính 01/08/2026.** Câu "Export 60 phút mất khoảng 20 phút" ở trên là **ước đoán, không phải phép đo** — người vận hành không theo dõi trong lúc render. Kiểm lại timestamp của `bench300.mp4` cho tạo lúc 11:40 và sửa lần cuối 11:46, tức khoảng **6 phút**, trùng khít với số đo của `prod60`. Con số đúng là khoảng 6 phút, tức nhanh hơn thời gian thực chừng mười lần. Xem `2026-07-31-5-prod60.md`.