# START HERE — đọc trước mọi file khác

**Cập nhật 01/08/2026.**

Nếu bạn là AI vừa được đưa vào dự án: đọc hết file này, rồi theo đúng thứ tự đọc ở mục 5. Nếu bạn tới đây mà chưa qua `README.md` thì quay lại đọc nó trước, vì luật xử lý khi công cụ fetch cắt mất nội dung nằm ở đó và nó áp dụng ngay từ lần fetch đầu tiên.

File này chỉ chứa những thứ **không đổi theo phiên**: dự án là gì, luật bất biến, bố cục thư mục, cách làm việc. Mọi số đo và tiến độ nằm ở `STATE.md`.

## 1. Dự án này là gì

Pipeline sản xuất video documentary YouTube dài 55–70 phút, phong cách hình ảnh và tiết tấu theo hướng ColdFusion. Quy trình: kịch bản viết tay, TTS tạo narration, stable-ts tạo SRT có timestamp chính xác, AI sinh bảng metadata shot, gen ảnh hàng loạt, dựng video, thêm nhạc và hiệu ứng, review, xuất bản.

Khâu đang tự động hoá là **dựng và finishing**, dùng **CapCut Desktop 9.1.0** làm bộ dựng và **capcut-cli 0.15.0** để điều khiển nó bằng cách ghi trực tiếp vào file project JSON. Một bản dựng FFmpeg thuần đã hoàn thành trước đó và được giữ làm phương án dự phòng ở `_deprecated/make_video.py`.

## 2. Ràng buộc cốt lõi — mọi quyết định kỹ thuật đều phục tùng nó

**Timing khoá cứng theo file audio và file SRT.** Mỗi shot có timestamp bắt đầu và kết thúc xác định trước. Bất kỳ thao tác nào làm dịch chuyển timeline đều làm phụ đề lệch khỏi lời thoại và phá hỏng toàn bộ sản phẩm.

**Luật thiết kế bắt buộc, đã kiểm chứng ba lần ở quy mô 300 shot: bắt mọi ranh giới cắt về bội số của 0,1 giây, tính theo ranh giới tuyệt đối chứ không theo độ dài shot.** Mỗi ranh giới lấy `round(t / 0.1) * 0.1`, độ dài shot là hiệu hai ranh giới đã bắt lưới. Làm ngược lại sẽ tích luỹ sai số. Sai lệch mỗi điểm cắt so với mốc lời thoại tối đa 50 ms và không phụ thuộc tổng độ dài, nên lời hứa "ảnh, tiếng, phụ đề khớp ở mọi thời điểm" đúng cả với video rất dài. Phụ đề không bắt lưới, giữ nguyên timestamp của stable-ts.

Lý do chọn 0,1 giây chứ không phải 1/30 giây: một frame ở 30 fps là 33333,333… micro giây, không tròn micro giây, và capcut-cli chỉ nhận tham số giây với ba chữ số thập phân, nên phần lớn bội số của 1/30 giây sẽ chịu hai lần lượng tử. Bội số của 0,1 giây bằng đúng 3 frame, bằng đúng 100000 micro giây, và viết trọn trong ba chữ số thập phân.

**Mốc cuối dùng ceil chứ không dùng round, và luôn cộng một đuôi cố ý sau khi hết narration.** Đuôi là bắt buộc, không phải tuỳ chọn; tối thiểu an toàn là một frame, giá trị đang dùng là 2000 ms.

Hệ quả vận hành: mọi tính năng mới đều phải qua một phép đo timing trước và sau khi áp dụng. Tiêu chí pass là mọi `target_timerange.start` không đổi quá một frame và **không tích luỹ**. Công cụ đo là `tools/timing_snap.py`, hoặc cặp cũ `scripts_v1/check_sync.py` cộng `scripts_v1/diff_timing.py`.

## 3. Ba nhánh thư mục, hai nhánh không có trên GitHub

Thư mục mẹ là `D:\IT\capcut-lab\`, chứa ba nhánh ngang hàng và độc lập. Thư mục mẹ **chỉ chứa đúng ba nhánh này, không để file rời**, vì file rời không thuộc nhánh nào thì không ai biết nó có được sao lưu hay không.

```
D:\IT\capcut-lab\
  capcut-pipeline\   <- repo git, ~2.6 MB, thu duy nhat day len GitHub
  data\              <- ~350 MB, KHONG commit. CAPCUT_LAB tro vao day
  vendor\            <- ~961 MB, KHONG commit, KHONG phat tan
```

Vì `data\` và `vendor\` là thư mục **ngang hàng** với repo chứ không nằm trong nó, git không nhìn thấy chúng dù `.gitignore` ghi gì. `.gitignore` vẫn có hai dòng `/data/` và `/vendor/` làm chốt phòng ngừa.

`data\` là dữ liệu làm việc: `Test_tool_v3\` bộ test chuẩn 8 shot, `snapshots\` timing từng phép đo, `frames\` khung hình mốc hồi quy, `perf\` báo cáo do script sinh, `exports\` bản export tham chiếu, `scaffold\` scaffold nguyên sinh do GUI tạo, `tmp\` script và file dùng một lần, `archive\` rác chờ xoá. Không commit vì phần lớn là media của người dùng hoặc dữ liệu sinh ra được.

`vendor\` là bộ đảm bảo tái lập, giữ **vĩnh viễn**: bộ cài CapCut 9.1.0.3879 đầy đủ 516,54 MB với SHA256 `539F6F5D9851B4787FFAECA8A3D90399D07B1A9EBA4C6AA2C4DC71B62C87A669`, bản sao `Cache_effect\` 405 MB, tarball `capcut-cli-0.15.0.tgz`, `MANIFEST.txt`, `README_PARITY.txt`, hai script bootstrap máy mới. Tải lại bộ cài từ `https://sf16-web-tos-buz.capcutstatic.com/obj/capcut-web-buz-sg/packages/CapCut_9_1_0_3879_capcutpc_0_creatortool.exe` rồi đối chiếu SHA256, hoặc `winget download ByteDance.CapCut --version 9.1.0.3879`.

**`data\` là cục bộ của từng máy và không bao giờ đồng bộ. Luật một chiều: thứ gì trong `data\` là bằng chứng mà phiên sau cần đọc thì phải được nâng lên repo.**

**Cảnh báo về scaffold:** file scaffold chứa đường dẫn tuyệt đối trỏ về profile của user đã tạo ra nó. `clone_project.py` thay GUID, tên project và `draft_fold_path`, nhưng **không** thay phần user profile nằm trong những đường dẫn khác, nên scaffold mang từ máy này sang máy kia vẫn còn dấu vết của máy cũ. Trên máy mới nên tạo scaffold mới bằng GUI: New Project, mở lại lần nữa rồi đóng, xác nhận tên thư mục trùng `draft_name`, rồi copy nguyên thư mục ra thành `scaffold_CLEAN`.

**Rủi ro tận thế cần biết.** JianYing từ bản 6.0 đã **mã hoá** `draft_content.json`. CapCut quốc tế hiện chưa, nhưng khả năng theo sau là có thật — trong 76 lệnh của capcut-cli có sẵn lệnh `decrypt`, cho thấy vấn đề này không xa lạ. Nếu xảy ra thì mọi hướng ghi file đều chết, cả CLI lẫn Python. Không có cách phòng nào ngoài giữ bản cài cũ, và đó là lý do `vendor\` phải giữ **vĩnh viễn**.

## 4. Quy ước nơi ghi file

| Loại đầu ra | Ghi vào | Có commit không |
|---|---|---|
| Báo cáo, số đo, log do script sinh | `data\perf\` | Không |
| Snapshot timing | `data\snapshots\` | Không |
| Script và file dùng một lần rồi bỏ | `data\tmp\` | Không |
| Project dựng thử | thư mục draft của CapCut | Không |
| Bằng chứng của một phiên, cần đọc lại về sau | `artifacts\` trong repo | Có, kèm một dòng trong `artifacts\README.md` |
| Mốc vàng dùng cho phép so tự động của `tests\` | `fixtures\` trong repo | Có |
| Bản kê `data\` và `vendor\` của một máy | `manifests\` trong repo | Có, mỗi máy một file |
| Khuôn JSON chụp từ CapCut | `molds\capcut-9.1.0\` | Có |
| Bất cứ thứ gì | không bao giờ ghi vào `vendor\` | — |

Phân biệt `fixtures\` với `artifacts\`: `fixtures\` là tiêu chuẩn dùng để so tự động, đổi nội dung ở đó nghĩa là đổi tiêu chuẩn. `artifacts\` là bằng chứng bất biến của một phiên cụ thể, để người và AI tra lại số, không dùng làm mốc so tự động.

## 5. Bản đồ tài liệu và thứ tự đọc

```
README.md            <- cua vao: luat doc file bi cat, moi truong, bo cuc, phap ly
docs/
  START-HERE.md      <- file nay: dieu huong, luat bat bien, cach lam viec
  STATE.md           <- anh chup thi hien tai: so do, may nao co gi
  TODO.md            <- thi tuong lai: viec chua lam, xep theo uu tien
  reference.md       <- so tra: hang so, cong thuc, catalogue, danh sach den
  reference-catalog.md  <- catalogue hieu ung va cu phap 76 lenh CLI
  failures.md        <- MOI LOAI LOI IM LANG DA GAP + thang bang chung
  model.md           <- CapCut hoat dong the nao: 4 file, Timelines\, resolve tai nguyen
  procedures.md      <- quy trinh dung video, probe parity, dung may moi
  scripts.md         <- moi script lam gi, sinh tu dong tu docstring
  research-log/      <- thi qua khu: nhat ky theo phien, xem INDEX.md
  legacy/v0.8-full.md  <- 299 KB, ban luu tru
```

Thứ tự cho một phiên mới: `README.md`, rồi file này, rồi `STATE.md`, rồi `TODO.md`, rồi `reference.md`, rồi `failures.md`, rồi `research-log/INDEX.md` cùng nhật ký một hoặc hai phiên gần nhất. `model.md` khi cần hiểu vì sao phải làm thế. `procedures.md` khi cần quy trình. `scripts.md` khi cần biết script nào làm gì. `reference-catalog.md` khi cần tra hiệu ứng hoặc cú pháp lệnh. `legacy/v0.8-full.md` chỉ khi các file kia thiếu, và khi đó tìm mục cụ thể chứ đừng đọc tuần tự.

Luật ba file, để tài liệu không phình và không tự mâu thuẫn: file này giữ thứ **không đổi theo phiên**; `STATE.md` là **ảnh chụp thì hiện tại**, sửa bằng cách ghi đè chứ không thêm vào; `TODO.md` là **thì tương lai**, xong việc thì xoá khỏi đó chứ không đánh dấu hoàn thành; `research-log/` là **thì quá khứ**, chỉ ghi thêm, không sửa lặng lẽ. Cùng một sự thật không được chép ra hai chỗ.

**Mã nguồn in trong `legacy/v0.8-full.md` không đáng tin.** Phần lớn đã lỗi thời, và có ít nhất một script chưa bao giờ tồn tại trên đĩa, nghĩa là mã của nó chưa từng chạy. Nguồn sự thật là file trong `scripts_v1/` và `tools/`. Bài học đã lặp ba lần: mã nằm trong tài liệu mà không có file trên đĩa thì phải coi là **chưa kiểm chứng**, không phải "đã có sẵn".

**Trần kích thước mỗi file tài liệu là 26 KB**, riêng `STATE.md` và `TODO.md` chật hơn, ghi ở đầu mỗi file. Lý do lịch sử, ngưỡng cắt đã đo được, và luật bắt buộc phải làm gì khi nghi mình đọc thiếu, tất cả nằm ở `README.md`. Kiểm bằng `python tools/docs_audit.py`.

## 6. Ba điều tuyệt đối không được làm

**Không tạo project bằng `capcut compile --out`, `capcut init`, hay `capcut quickstart`.** CapCut 9.1.0 sẽ từ chối mở. Chỉ GUI tạo được scaffold hợp lệ, và scaffold đó nhân bản được bằng `scripts_v1/clone_project.py`.

**Không chạy lệnh CLI khi CapCut đang mở**, kể cả khi đã thu nhỏ xuống system tray, vì Auto save sẽ đè mất mọi thay đổi. Kiểm bằng `Get-Process *CapCut*`, output phải rỗng.

**Không chạy lệnh CLI sau khi lớp Python đã propagate.** capcut-cli chỉ đọc và ghi bốn file ở thư mục gốc project, nó không biết thư mục `Timelines\<main_timeline_id>\` tồn tại — mà đó mới là nơi CapCut đọc thật khi bản lồng đã có nội dung. Thứ tự bất di bất dịch: mọi lệnh CLI xong hết, rồi mới tới Python, và Python luôn ghi ra cả bốn file.

## 7. Lỗi im lặng — đọc `failures.md` trước khi kết luận bất cứ điều gì

Đây là kiến thức vận hành quan trọng nhất của dự án. Danh sách đầy đủ và cách bắt từng loại nằm ở `failures.md`; đừng chép lại vào đây, vì hai bản song song sẽ lệch nhau.

Điều cần nhớ ở mức điều hướng là **thang bằng chứng**: `lint` sạch và `tracks` đúng không chứng minh gì; panel GUI hiển thị đúng tên và tham số cũng không chứng minh gì; chỉ có export MP4 thật rồi đo từng khung mới là bằng chứng đủ. Và trước mọi phép kiểm thị giác, phải in ra ground truth — shot nào có tính năng, ở cường độ nào, tại mốc nào — rồi mới nhìn.

**Sau khi mở CapCut lần đầu, phải chạy `scripts_v1/fx_audit.py` và kiểm mọi transition, effect, filter đều báo `OK`.** Đây là cách duy nhất bắt được tài nguyên chết.

## 8. Cách làm việc với người dùng

Hướng dẫn **từng bước một**, đừng đưa cả loạt lệnh khi bước sau phụ thuộc output bước trước, và mỗi lượt nói rõ **đang ở đâu trong lộ trình**. Mỗi phiên nhắc người dùng kiểm tra đã `git pull --rebase` và đã push chưa.

Mọi đoạn Python phải ghi ra file `.py` bằng PowerShell heredoc `@'...'@` cộng `[System.IO.File]::WriteAllText(path, $content, (New-Object System.Text.UTF8Encoding($false)))` rồi gọi `python file.py`. **Tuyệt đối không nhúng Python vào dòng lệnh PowerShell** — dấu `\` không phải ký tự escape trong PowerShell. Toán tử `>` trong PowerShell 5.1 ghi UTF-16LE, không dùng. Tránh trộn `Write-Host` với luồng output vì nó làm mất cột và đảo thứ tự; ép qua `Format-Table` rồi `Out-String`. Mọi khối lệnh mở đầu bằng `Get-Process *CapCut*`.

Console của script nên in **ASCII không dấu**, vì PowerShell 5.1 hay hỏng encoding. Nội dung file thì ghi UTF-8 không BOM, có dấu bình thường.

Đưa lệnh chép-dán được ngay. Chỗ nào phải làm tay thì hướng dẫn chi tiết kể cả bấm chuột ở đâu.

Khi hướng dẫn sửa tài liệu: nói rõ **file nào, mục nào**. Vá một phần thì đưa hai khối riêng có tiêu đề "TÌM ĐOẠN NÀY" và "THAY BẰNG", đoạn cần tìm phải đủ dài và duy nhất để định vị chính xác, kèm dòng tiêu đề hoặc dòng liền trước nếu cần. Thêm nội dung mới thì nói rõ chèn vào file nào, sau tiêu đề hoặc mục nào. Nếu một mục phải vá quá nhiều chỗ lặt vặt, hoặc thay đổi vượt quá 40% tài liệu, thì viết lại nguyên cả mục hoặc nguyên cả file trong một khối thay vì vá lẻ.

Mọi đoạn người dùng phải chép vào file đặt trọn trong **một khối rào mã có nhãn ngôn ngữ** đúng loại, kể cả khi nội dung là Markdown. Nếu bên trong đã chứa khối rào ba backtick thì khối bọc ngoài dùng **bốn backtick**. Luật này thay cho luật cũ cấm bọc nội dung Markdown vào khối rào mã.

**KHÔNG hard wrap.** Đây là luật bị quên nhiều nhất dù đã nhắc kỹ, nên tách riêng ra đây: không tự ngắt dòng để giới hạn độ rộng 80 hay 100 ký tự, không ngắt dòng giữa câu. Mỗi đoạn văn là **một dòng liền**, dài bao nhiêu cũng được; chỉ xuống dòng khi sang đoạn mới, sang mục danh sách mới, hoặc sang dòng mới của bảng.

Nội dung trong khối phải **nguyên văn và đầy đủ**: không rút gọn, không dùng dấu ba chấm thay cho phần bỏ đi, không viết "giữ nguyên phần còn lại", không chèn bình luận vào giữa. Mọi giải thích, ghi chú và lý do sửa để **bên ngoài** khối. Không thêm dấu lớn hơn ở đầu dòng kiểu trích dẫn. Giữ nguyên dấu nháy thẳng, dấu gạch ngang, thụt lề và ký tự đặc biệt của bản gốc, không tự làm đẹp chính tả hay định dạng ở chỗ không được yêu cầu sửa. Nội dung thay thế viết ra đúng như nó sẽ nằm trong file.

Luật này áp dụng cho mọi văn bản đưa ra để người dùng chép, kể cả prompt và checklist, không riêng file tài liệu.

Quyết định đã bị thay thế thì **xoá khỏi tài liệu chính** và ghi vào file phiên tương ứng, không giữ song song hai bản.

Kết luận chưa có bằng chứng thực nghiệm phải ghi rõ là **chưa kiểm chứng**. Mỗi phép thử nên có một mục biết chắc pass làm đối chứng dương và một mục nghi ngờ; nếu cả hai fail thì lỗi ở phương pháp, nếu chỉ mục nghi ngờ fail thì lỗi đúng chỗ đang nghi.

Trước khi đề xuất bất kỳ bản vá nào, **khai báo lỗ hổng đọc của mình**. Sau mỗi lần fetch, đối chiếu độ dài nhận được với kích thước thật của file, lấy từ `tools/docs_audit.py` hoặc từ git, rồi nói ngay tên file và chỗ thiếu nếu có. Không viết nội dung thay thế cho một file mà mình không có nguyên văn, và không kết luận rằng một hàm hay một câu văn không tồn tại chỉ vì mình không nhìn thấy nó. Luật đầy đủ ở `README.md`.

Nếu người dùng đề xuất hướng có vấn đề, nói thẳng. Nếu tự phát hiện mình sai, cũng nói thẳng. Không dùng emoji.

## 9. Bốn con số cần nhớ

Bit canvas là **4096**. `check_flag` mặc định của material video là 7; có canvas blur thì thành 4103. Luôn dùng phép OR.

Hệ toạ độ `transform` là NDC, `±1` là mép canvas. `transform.x = số_trên_UI / 1920` và `transform.y = số_trên_UI / 1080` — mỗi trục chia kích thước canvas của trục đó. `+Y` là **LÊN TRÊN**, ngược quy ước đồ hoạ thông thường. Số hiển thị trên UI **gấp đôi** số pixel dịch chuyển thật.

CapCut làm tròn mỗi ranh giới cắt **lên** frame gần nhất, phép ceil, không phải làm tròn về gần nhất. Việc làm tròn xảy ra ở lần CapCut mở project đầu tiên, không phải lúc CLI ghi.

Bản export 60 phút 1920×1080 30 fps H.264 ra khoảng **4,07 GB** ở bitrate chừng 9700 kbps.

Chi tiết công thức, catalogue và cú pháp lệnh: `reference.md`.