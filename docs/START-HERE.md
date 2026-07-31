**Cập nhật: 31/07/2026. File này được đọc TRƯỚC MỌI FILE KHÁC.**

Nếu bạn là một AI vừa được đưa vào dự án này: đọc hết file này trước, rồi mới quyết định đọc file nào tiếp. Đừng đọc `docs/legacy/v0.8-full.md` trừ khi thật sự cần — nó nặng 299 KB và sẽ ăn phần lớn ngữ cảnh của bạn.

## 1. Dự án này là gì

Pipeline sản xuất video documentary YouTube dài 55–70 phút, phong cách hình ảnh và tiết tấu theo hướng ColdFusion. Quy trình: kịch bản viết tay, TTS tạo narration, stable-ts tạo SRT có timestamp chính xác, AI sinh bảng metadata shot (tên file ảnh, prompt, timestamp bắt đầu và kết thúc), gen ảnh hàng loạt, dựng video, thêm nhạc và hiệu ứng, review, xuất bản.

Khâu đang tự động hoá là **dựng và finishing**, dùng **CapCut Desktop 9.1.0** làm bộ dựng và **capcut-cli 0.15.0** để điều khiển nó bằng cách ghi trực tiếp vào file project JSON. Một bản dựng FFmpeg thuần đã hoàn thành trước đó và được giữ làm phương án dự phòng (`_deprecated/make_video.py`).

Toàn bộ chuỗi từ ảnh cộng audio tới file MP4 **đã được kiểm chứng thành công** trên một project test 8 shot dài 2 phút 48, xuất ra 1920×1080 30fps H.264, 245,6 MB, số frame khớp chính xác duration. Pipeline không còn là giả thuyết. Việc còn lại là mở rộng lên quy mô 250–400 shot và đóng gói thành ứng dụng dùng được.

## 2. Ràng buộc cốt lõi — mọi quyết định kỹ thuật đều phục tùng nó

**Timing khoá cứng theo file audio và file SRT.** Mỗi shot có timestamp bắt đầu và kết thúc xác định trước. Bất kỳ thao tác nào làm dịch chuyển timeline đều làm phụ đề lệch khỏi lời thoại và phá hỏng toàn bộ sản phẩm.

Hệ quả vận hành: mọi tính năng mới đều phải qua một phép đo timing trước và sau khi áp dụng. Tiêu chí pass là mọi `target_timerange.start` không đổi quá một frame (33,3 ms ở 30 fps) **và không tích luỹ** theo thứ tự shot. Công cụ đo là `scripts_v1/check_sync.py` cộng `scripts_v1/diff_timing.py`.

## 3. Ba nhánh, và hai nhánh KHÔNG có trên GitHub

Thư mục mẹ trên máy phát triển là `D:\IT\capcut-lab\`, chứa ba nhánh ngang hàng và độc lập với nhau:

```
D:\IT\capcut-lab\
  capcut-pipeline\   <- repo git, ~2.6 MB, thu duy nhat day len GitHub
  data\              <- ~350 MB, KHONG commit. CAPCUT_LAB tro vao day
  vendor\            <- ~961 MB, KHONG commit, KHONG phat tan
```

Vì `data\` và `vendor\` là **thư mục ngang hàng** với repo chứ không nằm trong nó, git không nhìn thấy chúng dù `.gitignore` ghi gì. `.gitignore` vẫn có hai dòng `/data/` và `/vendor/` làm chốt phòng ngừa, cho trường hợp ai đó trỏ nhầm `CAPCUT_LAB` vào bên trong repo.

### 3.1. `data\` — dữ liệu làm việc

| Thư mục | Nội dung | Dùng để làm gì |
|---|---|---|
| `Test_tool_v3\` | 8 ảnh PNG 1376×768, `audio.mp3` dài 168,724813 giây, `video1.srt` | Bộ test chuẩn của mọi phép thử. **Không** nằm trong repo — máy khác lấy từ `vendor\Test_tool_v3\` hoặc chép tay từ đây |
| `snapshots\` | 15 file JSON ghi timing từng phép đo, gồm bộ `parity_gold_before/after/snap` | Mốc so sánh. Bộ `parity_gold_*` đã chép vào `fixtures/parity-gold/` |
| `frames\` | 19 khung hình trích từ bản export đã kiểm chứng, kèm md5 và màu trung bình RGB | Mốc hồi quy ở đầu ra. So bản dựng mới với bộ này để biết có gì thay đổi |
| `perf\` | Báo cáo do các script đo sinh ra | Nơi ghi kết quả Việc A |
| `exports\` | `export_v4.mp4` 245,6 MB là bản export tham chiếu duy nhất đã kiểm chứng đầy đủ, cộng hai file mp4 rác | Đối chiếu khi cần soi lại khung hình |
| `scaffold\` | `testV3_CLEAN\` và `v2oracle_CLEAN\` — scaffold nguyên sinh do GUI CapCut tạo | Nguyên liệu cho `clone_project.py`. **Chỉ dùng được trên chính máy đã tạo ra nó**, xem cảnh báo dưới |
| `archive\` | Bản sao trùng lặp, ba project cũ, tài liệu nháp cũ, file chờ phân loại. Khoảng 60–70 MB rác | Chưa xoá vì đang còn hai bản. Xoá được sau khi bỏ `D:\Test_tool` |

**Vì sao không commit:** `export_v4.mp4` một mình đã 245 MB; `exports\` và `archive\` là dữ liệu sinh ra được chứ không phải nguồn; và tám ảnh cùng file narration là nội dung của người dùng.

**Cách một máy mới có được nhánh này:** chỉ mốc vàng JSON nằm trong repo, ở `fixtures/parity-gold/`. Media test — tám ảnh, `audio.mp3`, `video1.srt` — cố ý **không** commit, lấy từ `vendor\Test_tool_v3\` hoặc chép tay. Scaffold thì **phải tạo mới trên chính máy đó** chứ không chép sang được.

**CẢNH BÁO về scaffold:** file scaffold chứa đường dẫn tuyệt đối trỏ về profile của user cũ, dạng `C:\Users\anhlt\AppData\Local\CapCut\...`. `clone_project.py` chỉ thay GUID và tên project, **không** thay phần user profile. Chép scaffold sang máy có tên user khác sẽ khiến CapCut báo mất media dù thư mục project không hề bị đổi tên. Trên máy mới luôn tạo scaffold mới bằng GUI: New Project, mở lại lần nữa rồi đóng, xác nhận tên thư mục trùng `draft_name`, rồi copy nguyên thư mục ra thành `scaffold_CLEAN`. Mất hai phút.

### 3.2. `vendor\` — bộ đảm bảo tái lập

Đây là lá chắn chống lại việc dự án phụ thuộc vào bên ngoài. Toàn bộ tài liệu này chỉ đảm bảo đúng cho **CapCut 9.1.0.3879**, nên khả năng cài lại đúng phiên bản đó là điều kiện sống còn.

| Mục | Dung lượng | Nội dung và công dụng |
|---|---|---|
| `CapCut_9.1.0.3879_User_X64_exe_en-US.exe` | 516,54 MB | **Bộ cài đầy đủ**, không phải stub. SHA256 `539F6F5D9851B4787FFAECA8A3D90399D07B1A9EBA4C6AA2C4DC71B62C87A669`. Cài im lặng bằng `/silent_install=1 /install_path="..."` |
| `Cache_effect\` | 405 MB, 14653 file, 4782 thư mục con | Bản sao `%LOCALAPPDATA%\CapCut\User Data\Cache\effect`. Chép sang máy mới thì máy đó không cần mạng để dùng hiệu ứng, và miễn nhiễm với việc ByteDance gỡ tài nguyên khỏi CDN. **Bắt buộc** với filter, vì filter không có cơ chế tự tải |
| `capcut-cli-0.15.0.tgz` | 0,40 MB | Tarball `npm pack`, dùng khi registry npm đổi hoặc gỡ phiên bản |
| `enums_backup.json` | 0,76 MB | Trùng với `reference/enums_backup.json` trong repo |
| `MANIFEST.txt` | | SHA256 từng file, kiểm kê, và danh sách hai file updater cần vô hiệu hoá |
| `README_PARITY.txt` | | Quy trình probe parity kèm tiêu chí pass bằng con số |
| `setup_1_runtimes.ps1`, `setup_2_capcut.ps1` | | Bootstrap máy mới, tách hai file vì sau khi cài Python và Node thì shell đang mở chưa thấy PATH mới |
| `frames\`, `snapshots\`, `scripts\`, `testV3_CLEAN\`, `Test_tool_v3\` | | Bản sao chụp tại thời điểm đóng gói. Chỉ `snapshots\` là trùng với `fixtures/parity-gold/` trong repo; bốn mục còn lại **chỉ có ở đây**, repo không chứa |

**Vì sao không commit:** bộ cài 516 MB là tài sản của ByteDance, phát tán lại là chuyện khác hẳn với lưu bản sao cho mình dùng; `Cache_effect\` 14653 file nhị phân làm mọi lần clone thành cực hình và nó thay đổi liên tục — đã đếm 272 rồi 277 rồi 278 rồi 279 mục qua các phiên — nên sẽ làm phình lịch sử git vô ích.

**Cách một máy mới có được nhánh này, không cần USB:** bộ cài tải trực tiếp từ URL CDN có trong manifest winget, `https://sf16-web-tos-buz.capcutstatic.com/obj/capcut-web-buz-sg/packages/CapCut_9_1_0_3879_capcutpc_0_creatortool.exe`, rồi đối chiếu SHA256 ở trên. Hoặc `winget download ByteDance.CapCut --version 9.1.0.3879 -d <thư-mục>` để winget tự verify hash. Còn `Cache_effect\` thì nếu máy có mạng, CapCut **tự tải** transition, animation và scene effect theo `resource_id` ở lần đầu dùng — chỉ **filter** là bắt buộc phải có cache sẵn hoặc bấm mũi tên tải xuống trong tab Filters một lần.

**Rủi ro tận thế cần biết:** JianYing từ bản 6.0 đã **mã hoá** `draft_content.json`. CapCut quốc tế hiện chưa, nhưng khả năng theo sau là có thật — trong 76 lệnh của capcut-cli có sẵn lệnh `decrypt`, cho thấy vấn đề này không xa lạ. Nếu xảy ra thì mọi hướng ghi file đều chết, cả CLI lẫn Python. Không có cách phòng nào ngoài giữ bản cài cũ. Đây là lý do `vendor\` phải giữ **vĩnh viễn**.

## 4. Cấu trúc repo và thứ tự đọc

```
capcut-pipeline/
  docs/
    START-HERE.md      <- file nay
    reference.md       <- so tra: hang so, cong thuc, catalogue, danh sach den
    failures.md        <- MOI LOAI LOI IM LANG DA GAP. Doc truoc khi ket luan bat cu dieu gi
    model.md           <- CapCut hoat dong the nao: 4 file, Timelines\, resolve tai nguyen
    procedures.md      <- quy trinh dung video, probe parity, dung may moi
    research-log.md    <- nhat ky theo ngay
    scripts.md         <- moi script lam gi
    legacy/v0.8-full.md  <- 299 KB, ban luu tru. CHI doc khi ba file tren khong tra loi duoc
  pipeline/            <- lop loi MOI, moi co khung goi __init__.py. core/ thuan tinh toan, capcut/ biet dinh dang file
  scripts_v1/          <- 13 script DANG CHAY THAT. Day la code song, khong phai di san
  tools/               <- 10 script nghien cuu va tra cuu, khong thuoc runtime
  tests/               <- CON RONG
  molds/capcut-9.1.0/  <- khuon JSON chup tu CapCut, phan theo phien ban CapCut
  reference/           <- enums_backup.json 775 KB catalogue hieu ung, describe.json cu phap 76 lenh CLI
  fixtures/            <- moc vang JSON de so parity. KHONG chua media test
  _deprecated/         <- 28 script da chet, CO commit kem README giai thich vi sao
  config.example.json  run.bat  README.md
```

Thứ tự đọc cho một phiên mới: file này, rồi `reference.md`, rồi `failures.md`. Ba file đó đủ cho hầu hết công việc. `model.md` khi cần hiểu vì sao phải làm thế. `legacy/v0.8-full.md` chỉ khi ba file kia thiếu — và khi đó nên fetch rồi tìm mục cụ thể chứ đừng đọc tuần tự.

## 5. CẢNH BÁO — mã nguồn in trong `legacy/v0.8-full.md` KHÔNG đáng tin

Tài liệu v0.8 dán mã nguồn của nhiều script. Phần lớn đã lỗi thời, và có ít nhất một script (`capcut_post.py`) **chưa bao giờ tồn tại trên đĩa**, nghĩa là mã của nó chưa từng chạy lần nào.

**Nguồn sự thật là file trong `scripts_v1/` và `tools/`.** Nếu cần biết một script chứa gì, hãy fetch chính file đó từ GitHub, hoặc yêu cầu người dùng dán nội dung. Tuyệt đối không suy đoán từ tài liệu.

Đây là bài học đã lặp lại ba lần: mã nằm trong tài liệu mà không có file trên đĩa thì phải coi là **chưa kiểm chứng**, không phải "đã có sẵn".

## 6. Trạng thái bàn giao tại 31/07/2026

### Đã xong

Một, bộ năm file tài liệu đã viết đầy đủ, không còn stub.

Hai, repo đã tạo và đẩy lên GitHub tại `github.com/tunahakim/capcut-pipeline`.

Ba, phép thử trên máy render đã chạy ngày 31/07/2026: parity đạt **0,0 ms tuyệt đối** trên cả `before` lẫn `after`, và bài tải 300 shot đạt. Chi tiết ở `docs/research-log.md`.

Bốn, **Việc A đã đóng.** Lớp ghi là **tuyến tính**, chi phí tách được thành phần cố định khoảng 0,304 giây mỗi lệnh cộng khoảng 0,27 mili giây cho mỗi segment đã tồn tại. Ở mốc 300 segment phần cố định chiếm chừng 88%. Quyết định: giữ kiến trúc một tiến trình CLI cho mỗi thao tác, không gộp lệnh, không viết lại lớp ghi. Được phép bắt đầu viết code trong `pipeline/`.

Năm, **quy tắc thiết kế quan trọng nhất hiện nay, rút ra từ Việc A:** bắt mọi mốc shot về bội số của 1/30 giây ngay ở khâu sinh `shots.csv`. Khi ranh giới đã nằm đúng lưới frame thì CapCut không dịch một mili giây nào, và ràng buộc timing khoá cứng ở mục 2 được bảo toàn tuyệt đối thay vì chỉ "dưới một frame". Đã kiểm chứng trên bài 300 shot bước 12,000 giây.

### Đang dở, thứ tự ưu tiên

Một, vá `tools/v4_mold.py`. Đường dẫn ghi ra phải là `molds/capcut-9.1.0/filter.json`, thêm khối `_meta`, sửa fallback `CAPCUT_LAB` đang trỏ vào `D:\Test_tool` đã chết, và mặc định **chỉ diff chứ không ghi đè**. File đích **đã tồn tại** 3218 byte. Khi diff phải phân loại trường: `path` và `target_timerange.duration` phụ thuộc máy và phụ thuộc project nên **được phép** khác; các trường còn lại **bắt buộc** khớp. Không phân loại thì diff chỉ là nhiễu và sớm muộn khuôn tốt bị đè mất. **Chặn hiện tại:** đo ngày 31/07/2026 trên cả mười một project trong thư mục draft, **không project nào còn material `type=filter`**, kể cả bản do GUI tạo — `strip_filters.py` đã gỡ sạch ở phiên v6. Nghĩa là script vá xong chưa có đối chứng dương để chạy thử. Phải thả tay lại một filter "Film" trong GUI trước, nếu không thì lại rơi vào đúng cái bẫy "mã chưa từng chạy" ở mục 5.

Hai, viết `tools/shots_dump.py` và chốt lược đồ `shots.csv`. Việc này **đứng trước** việc viết test, vì `shots.csv` là hợp đồng đầu vào của `pipeline/` và là nơi quy tắc bội số 1/30 giây phải sống. Viết test trước sẽ phải bịa lược đồ hai lần rồi hai bản lệch nhau.

Ba, viết ba test đầu tiên vào `tests/`.

Bốn, viết `run.bat` thật.

Năm, bắt đầu `pipeline/`.

### Nợ kỹ thuật đã biết

`fixtures/` nay đã tồn tại thật, nhưng **chỉ chứa mốc vàng JSON** ở `fixtures/parity-gold/`. Media test cố ý không commit; xem `fixtures/README.md`. Ý tưởng sinh media test tổng hợp bằng script để bỏ hẳn phụ thuộc này là **chưa kiểm chứng**: `audio.mp3` phải dài đúng 168,724813 giây mà MP3 lượng tử độ dài theo frame, nên chưa chắc dựng lại chính xác được.

`tools/` có **10** script, không phải 7 cũng không phải 9. `docs/scripts.md` thiếu hàng `tools/bulk_build.py`.

`pipeline/` **không** rỗng: đã có `__init__.py` ở `pipeline/`, `pipeline/core/` và `pipeline/capcut/`, mỗi file 25 byte. Chưa có code thật nào.

`preflight.py` lỗi thời ba chỗ, xem `failures.md` mục 6.

`docs/scripts.md` còn trống toàn bộ cột mô tả, 47 hàng.

`data\Test_tool_v3\shots.csv` rỗng 0 byte. Kiểm ngày 31/07/2026: **không script sống nào đọc hoặc ghi file này**, nó chỉ xuất hiện một lần trong `_deprecated/migrate.py` như một mục ánh xạ sang `archive`. Đây là file giữ chỗ chứ không phải đầu ra hỏng. Lược đồ thật sẽ do `tools/shots_dump.py` định nghĩa.

`run.bat` hiện 71 byte, chưa phải bản thật.

**Chưa đo:** thời gian CapCut vẽ xong timeline 300 shot, và RAM đỉnh khi mở project đó. Hai số này không cản trở gì, lấy trong hai phút nếu có dịp ngồi trước máy render.

**Updater trên máy render chưa bị chặn.** Trước phép đo nghiêm túc lần sau phải chặn theo `reference.md` mục 14 — chỉ `CapCut-DiffUpgrade.exe` và `hpatchz.exe`, tuyệt đối không chạm `VEHelper.exe`, `VECrashHandler.exe`, `CapCutService.exe`, và không chặn toàn bộ mạng của CapCut. Nếu không, CapCut có thể tự nhảy phiên bản và mọi mốc so sánh mất giá trị.

## 7. Môi trường máy phát triển

Windows 10 build 19045, PowerShell 5.1, máy văn phòng mười năm tuổi cấu hình yếu. Python **3.14.6** bản python.org user scope (bản 3.13 và bản Microsoft Store đã gỡ sạch). Node v24.14.0, npm 11.9.0. capcut-cli 0.15.0. ffmpeg và ffprobe 8.1.2 full build. CapCut 9.1.0.3879 với updater đã chặn. Git 2.53 với `core.autocrlf=false`, `core.longpaths=true`, `init.defaultBranch=main`.

Ổ C còn khoảng 10,7 GB trên 100 GB — rất sát, và thư mục draft của CapCut nằm ở đó. Ổ D còn khoảng 22 GB. **Luôn kiểm dung lượng trước mỗi việc lớn.**

`LongPathsEnabled` vẫn bằng 0, chưa đặt. Cần quyền Administrator và khởi động lại máy. Chưa gấp nhưng cây `Cache\effect` lồng bốn tầng có nguy cơ vượt 260 ký tự.

Đường dẫn hệ thống:

```
draft CapCut : %LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft
cache hieu ung: %LOCALAPPDATA%\CapCut\User Data\Cache\effect        (279 muc, 30/07/2026)
enums.json cua CLI: %APPDATA%\npm\node_modules\capcut-cli\dist\enums.json
CAPCUT_LAB   : D:\IT\capcut-lab\data
```

Script trong `scripts_v1/` và `tools/` lấy thư mục làm việc theo thứ tự: biến `CAPCUT_LAB` nếu có, nếu không thì dẫn xuất từ vị trí chính file script (`parents[2] / "data"`). Nghĩa là **giữ nguyên bố cục ba nhánh thì không cần đặt biến môi trường**. Không script nào được phép ghi cứng một đường dẫn tuyệt đối.

## 8. Việc A — đo hiệu năng, ngã ba kiến trúc

Bản dựng 300 shot theo quy trình hiện tại cần khoảng 900 lệnh CLI: 300 `add-video`, 1 `add-audio`, 300 `bg-blur`, 299 `transition`. Mỗi lệnh khởi động một tiến trình Node riêng.

Số đo đã có: **9.390 byte mỗi segment** (project đầy đủ tính năng) và **9.498** (project parity), ngoại suy 300 shot ra khoảng **2,8 MB**. Nghĩa là phần bậc hai — mỗi lệnh đọc và ghi lại toàn bộ file — chỉ tốn cỡ nửa phút. Nút thắt thật là **chi phí khởi động tiến trình Node**, cỡ 300–600 ms mỗi lệnh, tức khoảng bảy phút cho 900 lệnh. **Giảm số lệnh quan trọng hơn nhiều so với tránh đọc lại JSON.**

Ba đường cần đo và so:

Đường tuần tự thuần CLI. Chạy tăng dần tới N khoảng 80–100 rồi ngoại suy, bấm giờ **từng lệnh** và fit tuyến tính `t_k = a + b*k` để tách phần hằng số khỏi phần bậc hai. Không chạy đủ 300 rồi mới biết kết quả.

Đường `capcut batch` đọc JSONL từ stdin. Bước đầu tiên là **đọc mã nguồn** capcut-cli tại `%APPDATA%\npm\node_modules\capcut-cli\dist\` để xem hàm lưu draft nằm trong hay ngoài vòng lặp đọc dòng. Đọc mã rẻ hơn đo, và cho luôn schema JSONL mà `capcut describe` không mô tả.

Đường thứ ba, đã chứng minh khả thi: 301 lệnh CLI cộng Python dập transition và canvas_blur. Bỏ hai phần ba số lệnh mà không phải đụng vào phần khó nhất là factory material của `add-video`.

Việc A **không cần mở CapCut**, chạy được trên máy yếu. Vì không mở CapCut nên chất lượng ảnh hoàn toàn không quan trọng: dùng PNG 1376×768 nén tối đa cỡ 30 KB thì mỗi project chỉ 9 MB thay vì 270 MB. Chỉ cần đúng số lượng và đúng kích thước khai báo.

## 9. Cách làm việc với người dùng

Hướng dẫn **từng bước một**, đừng đưa cả loạt lệnh khi bước sau phụ thuộc output bước trước. Người dùng đã phàn nàn về việc này và đã có lần mất phương hướng không biết đang ở bước nào — nên mỗi lượt phải nói rõ **đang ở đâu trong lộ trình**.

Mọi đoạn Python phải ghi ra file `.py` bằng PowerShell heredoc `@'...'@` cộng `[System.IO.File]::WriteAllText(path, $content, (New-Object System.Text.UTF8Encoding($false)))` rồi gọi `python file.py`. **Tuyệt đối không nhúng Python vào dòng lệnh PowerShell** — dấu `\` không phải ký tự escape trong PowerShell, chuyện này đã làm hỏng ba lệnh liên tiếp một lần. Toán tử `>` trong PowerShell 5.1 ghi UTF-16LE, không dùng.

Đưa lệnh chép-dán được ngay, đừng mô tả chung chung. Chỗ nào phải làm tay thì hướng dẫn chi tiết kể cả bấm chuột ở đâu.

Khi hướng dẫn sửa tài liệu: nói rõ **file nào, mục nào**, và chỉ ra **ranh giới đoạn bị thay** — câu mở đầu và câu kết thúc — để người dùng biết chính xác xoá từ đâu tới đâu. Nếu một mục phải vá quá nhiều chỗ lặt nhặt thì viết lại nguyên cả mục cho chép dán một lần, kể cả khi bên trong mục có khối rào mã; thay cả khối là được, không sao. Ba điều **tuyệt đối không làm** khi viết nội dung thay thế. Một, không bọc nội dung thay thế vào khối rào mã kèm nhãn `markdown` — người dùng phải gỡ tay từng cái. Hai, không thêm dấu lớn hơn ">" ở đầu dòng kiểu trích dẫn — không thể replace-all để xoá vì sẽ xoá nhầm cả dấu đó nằm bên trong code. Ba, không tự ngắt dòng giữa câu cho cân lề — mỗi đoạn văn phải là **một dòng liền**, dài bao nhiêu cũng được, vì mọi dòng cụt đều phải nối tay lại khi chép vào file. Nội dung thay thế viết ra đúng như nó sẽ nằm trong file, không hơn không kém.

Kết luận chưa có bằng chứng thực nghiệm phải ghi rõ là **chưa kiểm chứng**. Mỗi phép thử nên có một mục biết chắc pass làm đối chứng dương và một mục nghi ngờ; nếu cả hai fail thì lỗi ở phương pháp, nếu chỉ mục nghi ngờ fail thì lỗi đúng chỗ đang nghi.

Nếu người dùng đề xuất hướng có vấn đề, nói thẳng. Nếu tự phát hiện mình sai, cũng nói thẳng — điều đó có giá trị hơn bảo vệ kết luận cũ.

Không dùng emoji.

## 10. Sáu loại lỗi im lặng — đọc trước khi kết luận bất cứ điều gì

Đây là kiến thức vận hành quan trọng nhất của dự án. Chi tiết ở `failures.md`, nhưng danh sách phải nằm ngay đây vì nó chi phối cách đánh giá mọi phép thử.

Một, `capcut keyframe ... uniform_scale` ghi `property_type: "UNIFORM_SCALE"`, JSON hợp lệ, lệnh trả `ok:true`, CapCut không đọc được. Tên đúng là `KFTypeScaleX`.

Hai, `capcut enums --type transitions` trả về **mảng rỗng** thay vì báo cú pháp sai. Cú pháp đúng là flag trực tiếp: `capcut enums --transitions`.

Ba, `capcut add-filter` ghi material vào sai bucket, sai loại track, và dựa trên mười entry catalogue **bịa** với `resource_id` chạy liên tiếp và không có md5. Hỏng từ dữ liệu nguồn, không vá được, đã bỏ hẳn.

Bốn, filter không có tài nguyên trong cache: panel GUI hiển thị **đúng tên và đúng intensity**, nhưng không render gì. CapCut tra metadata theo `resource_id` từ catalogue nội bộ, hoàn toàn độc lập với việc file có trên đĩa.

Năm, tài nguyên khoá Pro đi qua được **mọi** lớp kiểm chứng kể cả preview, chỉ chặn ở đúng khoảnh khắc bấm Export. Công cụ kiểm kê duy nhất là hộp thoại Export.

Sáu, transition `cube` có `path` là placeholder mà CapCut không tự vá, và nó render ra thành **cắt cứng sạch sẽ** — không khung đen, không artefact, chỉ mất hiệu ứng. Không có cách nào biết trước từ `enums.json`.

Thang bằng chứng, xếp theo độ tin cậy tăng dần: `lint` sạch và `tracks` đúng là **mức 1, không chứng minh gì**; panel GUI hiển thị đúng là **mức 2, cũng không chứng minh gì**; `fx_audit.py` báo `path` trỏ file có thật là mức 3; bật tắt lớp trong GUI hoặc thấy tác dụng thị giác có đối chứng cùng khung hình là mức 4; export MP4 thật rồi đo từng khung là **mức 5, đủ hoàn toàn**.

**Hệ quả bắt buộc: sau khi mở CapCut lần đầu, PHẢI chạy `scripts_v1/fx_audit.py` và kiểm mọi transition, effect, filter đều báo `OK`.** Đây là cách duy nhất bắt được tài nguyên chết.

## 11. Ba điều tuyệt đối không được làm

**Không tạo project bằng `capcut compile --out`, `capcut init`, hay `capcut quickstart`.** CapCut 9.1.0 sẽ từ chối mở. Chỉ GUI tạo được scaffold hợp lệ, và scaffold đó nhân bản được bằng `scripts_v1/clone_project.py`.

**Không chạy lệnh CLI khi CapCut đang mở**, kể cả khi đã thu nhỏ xuống system tray. CapCut có Auto save nên nó ghi định kỳ và sẽ đè mất mọi thay đổi. Kiểm bằng `Get-Process *CapCut*`, output phải rỗng.

**Không chạy lệnh CLI sau khi lớp Python đã propagate.** capcut-cli chỉ đọc và ghi bốn file ở thư mục gốc project, nó **không biết** thư mục `Timelines\<main_timeline_id>\` tồn tại — mà đó mới là nơi CapCut đọc thật khi bản lồng đã có nội dung. Thứ tự bất di bất dịch: mọi lệnh CLI xong hết, rồi mới tới Python, và Python luôn ghi ra cả bốn file.

## 12. Bốn con số cần nhớ

Frame quantization của bộ tám shot chuẩn, đo bốn lần ở bốn cấu hình khác nhau và luôn cùng bộ số: `+0.0 / +26.7 / +20.0 / +20.0 / +13.3 / +6.7 / +0.0 / +13.3 ms`, duration từ 168,7250 lên 168,7333 giây. Việc làm tròn xảy ra ở **lần CapCut mở project đầu tiên**, không phải lúc CLI ghi.

Bit canvas là **4096**. `check_flag` mặc định của material video là 7; có canvas blur thì thành 4103. Luôn dùng phép OR, đừng đặt cứng.

Hệ toạ độ `transform` là NDC, `±1` là mép canvas. `transform.x = số_trên_UI / 1920` và `transform.y = số_trên_UI / 1080` — **mỗi trục chia kích thước canvas của trục đó**. `+Y` là **LÊN TRÊN**, ngược quy ước đồ hoạ thông thường. Số hiển thị trên UI **gấp đôi** số pixel dịch chuyển thật.

Bản export tham chiếu: 12,2 Mbps, 245,6 MB cho 168,7 giây, nội suy 60 phút ra khoảng **5,2 GB**.