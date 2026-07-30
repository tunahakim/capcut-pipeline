# Model — CapCut hoạt động thế nào

File này **mỏng có chủ ý**. Phần giải thích *vì sao* đã có trong `legacy/v0.8-full.md` khá đầy đủ; ở đây chỉ tóm tắt kết luận và chỉ đường vào đúng mục để đào sâu.

## Kết luận cốt lõi, dạng ngắn

**Kiến trúc lưu trữ.** CapCut 9.1.0 lưu timeline thật trong `Timelines\<main_timeline_id>\`, còn bốn file ở gốc project là mirror. capcut-cli **không biết** thư mục lồng tồn tại. Khi bản lồng rỗng thì CapCut đọc bản gốc; khi bản lồng có nội dung thì nó đọc bản lồng. Mọi thay đổi bằng Python phải ghi ra **cả bốn** file, ở bước cuối cùng. Chi tiết: v0.8-full mục **VII**.

**Tạo project.** Chỉ GUI tạo được scaffold hợp lệ; `compile`, `init`, `quickstart` đều thất bại theo ba cách khác nhau. Scaffold nguyên sinh nặng 101,5 KB và chỉ chứa **4 GUID**, nên nhân bản được. Chi tiết: v0.8-full mục **V** và **VIII.8**.

**Media được copy vào project.** `add-video` chép file vào `<project>\assets\video\` và ghi đường dẫn **tuyệt đối** trỏ vào đó. Project tự chứa, nhưng đổi tên thư mục project sẽ phá vỡ toàn bộ liên kết. Sửa file ảnh gốc sau khi add **không** phản ánh vào project — phải dùng `capcut replace-media`. Chi tiết: v0.8-full mục **IX.1**.

**Resolve tài nguyên.** CapCut resolve theo `resource_id` qua CDN, không theo md5. Nó tự vá `path` cho transition, animation, scene effect; **không** tự vá cho filter. Chi tiết: v0.8-full mục **VIII.5**, **VIII.11**, và `reference.md` mục 7.

**Transition không dịch timeline.** Đo ở ba cấu hình khác nhau (2 transition nhẹ, 7 nhẹ, 7 mạnh) đều cho cùng bộ sai lệch dưới một frame và **không tích luỹ**. Đó là frame quantization ở lần CapCut mở project đầu tiên, hoàn toàn độc lập với số lượng và cường độ transition. `is_overlap: false` nghĩa là transition mượn hình ảnh ở chỗ giáp ranh mà không đụng `target_timerange`. Chi tiết: v0.8-full mục **VIII.4**, **VIII.7**, **VIII.7.1**.

**Bitmask `check_flag`.** Là cờ cho biết tính năng nào đang kích hoạt trên material video. Bit 4096 tương ứng canvas. capcut-cli ghi mặc định 7 và không cập nhật khi thêm `canvas_blur`, nên CapCut thấy material có canvas mà cờ chưa bật. Phát hiện bằng cách diff shot có tick với shot không tick: chênh lệch đúng 4096. Chi tiết: v0.8-full mục **VIII.2**.

**`bg-blur` tạo canvas mới thay vì sửa canvas cũ**, để lại `canvas_color` mồ côi. Vô hại, nhưng đừng giả định "số canvas bằng số segment". Xác định canvas theo `extra_material_refs` của từng segment. Chi tiết: v0.8-full mục **IX.9**.

**Đường thứ ba — Python dập material.** `add-video` sinh cả một chùm material phụ thuộc nhau nên CLI có giá trị thật ở đó; còn `bg-blur` và `transition` chỉ là khuôn nhỏ không phụ thuộc chéo, Python dập được. Bỏ 900 lệnh xuống 301. Đã chứng minh ở mức 4, chưa export. Chi tiết: v0.8-full mục **VIII.16**.

**Write guard.** capcut-cli chấp nhận ghi cho CapCut 6.x–9.x với `schema_int` ngưỡng 360000. 9.1.0 được đánh dấu `untested` với `evidence: none`. Nếu CapCut lên 10.x thì write-guard từ chối ghi. Chi tiết: v0.8-full mục **IX.5**.

## Chỉ mục vào `legacy/v0.8-full.md`

| Mục | Nội dung |
|---|---|
| I | Bối cảnh, ràng buộc timing, tài nguyên test |
| II | Môi trường hệ thống, biến `CAPCUT_LAB` |
| III | Sáu bẫy PowerShell 5.1 |
| IV | Hành vi capcut-cli, danh sách 76 lệnh, cú pháp, `export` vs `render` |
| V | Bốn cách tạo project, ba cách thất bại, cấu trúc scaffold nguyên sinh |
| VI | Bẫy CapCut đổi tên thư mục project |
| VII | Kiến trúc đa timeline, mô hình đọc/ghi, dấu vân tay |
| VIII.1 | Scale tĩnh, phép thử oracle |
| VIII.2 | Canvas blur, bitmask 4096 |
| VIII.3 | Keyframe `KFTypeScaleX` |
| VIII.4, VIII.7, VIII.7.1 | Transition không dịch timeline, ba lần đo |
| VIII.5 | CapCut tự vá đường dẫn, đính chính về md5 |
| VIII.6 | Hệ toạ độ Position và công thức lề, ba phép đo oracle |
| VIII.8 | Clone project |
| VIII.9 | `add-effect` |
| VIII.10 | Ca nghiên cứu `add-filter`, bảng diff 54 dòng |
| VIII.11 | Ngữ nghĩa placeholder, bảng resolve |
| VIII.12 | Lỗi im lặng thứ tư, thang bằng chứng |
| VIII.13 | Ba trạng thái tài nguyên, khoá Pro |
| VIII.14 | Export MP4 thật, 19 khung hình vàng, đo profile transition |
| VIII.15 | Mốc vàng parity |
| VIII.16 | Đường thứ ba, ma trận resolve |
| IX.10 | Ghim phiên bản CapCut, chặn updater, vendor kit |
| IX.12 | Cấu trúc cache, hai kiểu thư mục |
| X | Mã nguồn các script — **KHÔNG ĐÁNG TIN, xem file thật** |
| XI | Quy trình chuẩn |
| XIII | Phương pháp oracle |
| XV | Đánh giá có nên tiếp tục dùng capcut-cli |

---