# 2026-08-04-2 — lớp cấu hình và bộ đọc shotlist

**Tóm tắt:** Dựng lớp cấu hình `pipeline/config.py` theo lược đồ số 1 và bộ đọc bảng shot `pipeline/core/shotlist.py` năm cột TSV, cả hai nghiệm thu hai chiều bằng đối chứng dương và đối chứng âm; chốt hợp đồng kiến trúc bốn tầng ở `../architecture.md`

## Bối cảnh

Phiên trước đã đóng phần tài liệu. Phiên này bắt đầu Ưu tiên 1: đóng gói thành ứng dụng dùng được. Máy render vẫn không truy cập được nên mọi việc cần `prod60` bị chặn.

## Quyết định đã chốt và lý do

**Đường đi có ba chặng, không phải hai.** Đọc `tools/prod_shots.py` mới thấy nó **rải ngẫu nhiên**: ảnh qua `rng.shuffle(pool)`, độ dài shot do `durations()` bốc rồi cân cho khớp tổng, transition là `rng.choice(TRANS)`. Nó khoá đúng **tổng** thời lượng theo file audio nhưng không có liên hệ nào giữa lời thoại ở giây thứ 412 với ảnh xuất hiện ở giây thứ 412. Hợp lý cho việc nó sinh ra là đo sức máy render, nhưng nghĩa là **đường từ kịch bản tới `shots.csv` chưa tồn tại trong repo**. Đó là chỗ bảng shotlist lấp vào.

**Bảng người viết là TSV, cấu hình là JSON.** Cấu hình lồng ba tầng, có mảng, có kiểu phân biệt, nên JSON là bắt buộc; biểu diễn nó bằng TSV là tự phát minh một định dạng rồi tự viết parser cho nó. Bảng shot thì phẳng tuyệt đối, hàng trăm dòng, người sửa bằng Sheets, git diff đúng một dòng khi đổi một shot, và tốn khoảng một phần tư tới một phần năm số token của JSON cùng nội dung. Chọn tab chứ không chọn phẩy vì locale Việt trên Windows dùng phẩy làm dấu thập phân nên Excel đổi dấu phân cách sang chấm phẩy — hành vi Windows đã biết, **chưa kiểm chứng trên máy lab**.

**Tên file `<project>.shotlist.tsv`, viết thường hết.** Windows không phân biệt hoa thường nhưng git thì có, nên một file đổi từ `ShotList` sang `shotlist` sẽ thành hai file khác nhau khi máy render pull về.

**Năm cột dùng ngay: `idx start image transition note`.** Không có cột `end` và không có cột `duration`: các shot nối liền nhau theo bước 2 của `procedures.md`, nên độ dài shot `i` là `start[i+1] - start[i]` và shot cuối đóng bằng độ dài audio. Cho gõ cả `start` lẫn `end` là tạo hai nguồn sự thật cho cùng một ranh giới.

**Ba cột `motion blur fx` để dành**: đọc được, nhưng chỉ sinh `CANH BAO` kèm lý do rồi bỏ qua giá trị. Lý do chưa dùng: `motion` phụ thuộc lớp keyframe mà nhánh ảnh cao hơn khung 16:9 chưa có phép đo oracle nào, `fx` cần một lượt oracle riêng.

**Thêm cột về sau gần như miễn phí, và lượt trước tôi nói ngược lại nên phải sửa.** TSV đọc theo tên cột, nên hai quy ước chốt ngay bây giờ làm việc thêm cột rẻ: ô trống nghĩa là dùng mặc định, cột vắng mặt nghĩa là cả bảng dùng mặc định. Cái đắt thật không phải cột trong file mà là nhánh mã phía sau cột.

**Blur không có luật hình học.** Điều kiện `kx*smin < 1 or ky*smin < 1` trong `prod_shots.py` với `S_HI` bằng 0,92 thì vế trái luôn đúng, nên cột `blur` bằng 3 ở mọi shot: đó là hằng số 3 đội lốt công thức. Xác nhận bằng mã ở dòng 163. Ảnh đúng 16:9 vẫn có thể thu nhỏ rồi blur nền vì đó là lựa chọn thẩm mỹ. Vậy mặc định khai ở `config.json`, ép tay ở bảng, không có công thức.

**Mốc `start` nhận cả dấu phẩy.** SRT thật do công cụ nhận dạng giọng nói xuất ra dùng dấu phẩy: `00:00:05,712`. Kế hoạch ban đầu là từ chối dấu phẩy để chống bẫy locale, làm vậy thì chép mốc từ SRT vào bị chặn ngay dòng đầu. Sửa lại: dạng có hai dấu hai chấm thì phẩy hay chấm đều là dấu thập phân, riêng dạng giây trần bắt buộc dấu chấm vì `7,4` ở đó không phân biệt được với lỗi.

**Hai mức chẩn đoán, và `LOI` gom hết rồi in một lượt.** Chi tiết ở `architecture.md` mục 4.

**Tạo `docs/architecture.md`.** Toàn bộ hợp đồng kiến trúc trước đó chỉ nằm trong Ưu tiên 1 của `TODO.md`, mà luật ba file quy định `TODO.md` xong thì xoá, nên ngày pipeline chạy được là ngày kiến trúc mất khỏi repo. `START-HERE.md` đang 94% trần nên không nhồi vào đó được.

## Số đo và phép nghiệm thu

`pipeline/config.py`, lược đồ số 1. Đối chứng âm trên `config.example.json`: đúng 5 dòng `LOI` liệt kê một lượt, `EXIT=2`. Đối chứng dương trên `config.json` thật của máy lab: `HOP LE`, 0 cảnh báo, `EXIT=0`, `%LOCALAPPDATA%` bung đúng.

Ba thông tin đo được trên đĩa lab: thư mục scaffold có đúng hai khuôn `testV3_CLEAN` và `v2oracle_CLEAN`, **không có** `scaffold_CLEAN`; cache hiệu ứng thật là `%LOCALAPPDATA%\CapCut\User Data\Cache\effect` và `Test-Path` cho `True`, còn tên `Cache_effect` trong `STATE.md` là tên bản sao trong `vendor\` nên hai thứ khác nhau chứ không mâu thuẫn; `data\Test_tool_v3\shots.csv` có đúng ba cột `file, start, end` và 8 dòng, khớp mô tả trong `TODO.md`.

`pipeline/core/shotlist.py`. Đối chứng dương trên bộ 8 shot sinh từ `shots.csv` cũ: `HOP LE`, `EXIT=0`, 0 cảnh báo, tám mốc bắt lưới cho 0, 19700, 34700, 48900, 72700, 92000, 106700, 132700 ms, shot cuối đóng bằng `--total-ms 168800` cho 36100 ms, ngắn nhất 14,2 giây dài nhất 36,1 giây. Đối chứng âm trên bảng cố ý sai sáu kiểu: `EXIT=2`, 6 dòng `LOI`.

**Dự đoán chốt trước bị sai một phần, ghi lại để không tự tin nhầm.** Tôi dự đoán mười lỗi, thực tế sáu. Bốn thứ không xuất hiện: ảnh không tồn tại, transition trong blacklist, transition ngoài whitelist, và dòng `CANH BAO` cho cột `motion`. Nguyên nhân là `load()` chỉ gọi `check_images` và `check_transitions` khi `parse_text` không có lỗi, còn warnings bị bỏ khi đã có lỗi. Hành vi chấp nhận được vì kiểm cấu trúc trước rồi mới kiểm nội dung, nhưng hệ quả là **ba phép kiểm đó cùng đường cảnh báo cột để dành chưa được nghiệm thu**, đã ghi thành mục trong `TODO.md`.

## Ba chỗ tôi tự sửa mình trong phiên

Nói "thêm cột sau khi có bảng 300 dòng thì đắt" — sai với định dạng đọc theo tên cột.

Nói sẽ trỏ `config.example.json` vào `testV3_CLEAN` — sai, vì file ví dụ phục vụ máy mới còn `testV3_CLEAN` là đặc thù lịch sử của máy lab; giữ `scaffold_CLEAN` trong ví dụ và để nó báo lỗi khi chạy trực tiếp, đó là hành vi đúng.

Nói bước copy scaffold ra khuôn là thao tác tay vì không thấy script nào làm việc đó — kết luận sai kiểu bị luật repo cấm. Người dùng khẳng định chưa bao giờ copy tay. Đã ghi thành mục cần làm rõ bằng cách đọc nhật ký cũ.

## Lỗ hổng đọc của phiên

Đã đọc nguyên văn: bốn file bắt buộc, `procedures.md`, `config.example.json`, `clone_project.py`, `prod_shots.py`, `bench_shots.py`. **Chưa đọc**: `reference.md`, `model.md`, `failures.md`, `scripts.md`, `ai-reading-channel.md`, và 40 script còn lại. Mọi nhận xét kiến trúc trong phiên chỉ dựa trên phần đã đọc.

`repo_bytecheck.py` báo 403 hết hạn ngạch ngay lượt đầu phiên, nên phép đối chiếu byte của phiên này dựa vào `git pull --rebase` báo `Already up to date` cộng `git rev-parse HEAD` trùng mốc kết phiên trước.