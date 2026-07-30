# Nhat ky nghien cuu

Lưu ý: Tài liệu này chưa refactor xong, toàn bộ các phụ lục E1-E5 là copy từ `legacy/v0.8-full.md` sang, file này cần refactor lại.

## PHỤ LỤC E1 — NHẬT KÝ PHIÊN 28/07/2026

Ghi lại theo trình tự để người đọc sau hiểu được đường đi của suy luận, kể cả các nhánh sai.

**Bối cảnh mở đầu.** Phiên bắt đầu bằng một cuộc thảo luận về việc có nên bỏ CapCut chuyển hẳn sang FFmpeg. Lập luận ủng hộ FFmpeg: yêu cầu thực tế chỉ là slideshow có template, và mục tiêu "app portable giải nén là chạy" mâu thuẫn với việc phụ thuộc CapCut Desktop đúng một phiên bản.

**Quyết định giữ CapCut, với ba lý do có sức nặng.** Một là chỉ cần tools tiết kiệm 90% công sức, vài bước thủ công chấp nhận được. Hai là khi cần làm nổi bật một đoạn thì mở CapCut sửa tay dễ hơn nhiều so với sửa script FFmpeg rồi render lại. Ba là việc phủ một hiệu ứng (như phim cũ) lên toàn bộ 60 phút chỉ mất 10 giây trong GUI, còn FFmpeg phải render lại từ đầu. Lý do thứ ba đặc biệt mạnh và đã được xác nhận trong phiên này bằng `add-effect --full`.

**Về câu hỏi "nếu CapCut update thì sao".** Kết luận: capcut-cli **không** bảo vệ được — nó đánh dấu 9.1.0 là `untested` và write-guard sẽ từ chối ghi ở 10.x, tức nó hỏng trước cả code Python. Lá chắn thật nằm ở ba chỗ: ghim phiên bản và lưu bộ cài (IX.10), bộ probe hồi quy (XI.4), và phương pháp oracle (Phần XIII) — thứ có giá trị dài hạn nhất trong toàn bộ tài liệu.

**Điểm nghẽn bộ cài.** File tải từ capcut.com chỉ là stub. Giải bằng manifest winget-pkgs, có URL CDN trực tiếp kèm SHA256 cho từng phiên bản.

**Phiên test v3.** Mục tiêu: mỗi shot mang đồng thời scale nhỏ + blur nền + zoom + pan chéo + transition.

Lỗi đầu tiên gặp phải là escape `\"` trong `python -c` — mất một vòng, dẫn tới quy tắc mới ở III.6.

Hai ẩn số được giải bằng oracle trên `v2oracle`: mẫu số trục Y là 1080, và CapCut không chặn lề.

Lần áp đầu tiên dùng công thức lề **sai** (giả định UI hiển thị pixel thật). Dấu hiệu phát hiện: shot 8 được thiết kế để chạm sát mép nhưng lại còn cách một khoảng rõ rệt. Đây là lý do phải luôn cài một **probe biên** vào phép thử — nếu không có shot 8 thì lỗi này đã trôi qua không ai biết.

Phép đo quyết định: ở Scale 50%, ảnh chạm mép khi UI ghi X=−960, trong khi dịch chuyển thật chỉ 480 px. Từ đó suy ra hệ NDC.

Lần áp thứ hai với công thức đúng: shot 8 **chạm sát mép mà vẫn còn viền blur**. Xác nhận công thức chuẩn xác tới từng pixel.

Timing đo được: lệch tối đa 26,7 ms, không tích luỹ, đạt.

**Phiên test v4.** Mục tiêu: clone project và thử hiệu ứng phức tạp hơn.

Clone chạy đúng ngay lần đầu. Scaffold chỉ có 4 GUID nên phép thay rất gọn. CapCut nhận project ngay, không cần `register`.

Tám quỹ đạo Ken Burns khác nhau đều pass kiểm tra biên và chạy đúng, kể cả shot 4 zoom out (scale giảm từ 0,92 xuống 0,76).

`add-effect --full` với `retro-film` chạy tốt, tạo track riêng, nhãn hiển thị đúng.

`add-filter` phát lộ là **lỗi im lặng thứ ba** — track có nhưng Name trống và Intensity = 0. Phát hiện được nhờ nhìn ảnh chụp màn hình chứ không phải nhờ script, vì mọi kiểm tra tự động (`lint`, `tracks`, `info`) đều báo bình thường. Bài học: **các phép kiểm tra tự động không thay thế được việc nhìn bằng mắt.**

**Ba lỗi im lặng đã gặp cho tới nay**, cùng một dạng và đều tốn nhiều thời gian nhất để phát hiện: `keyframe uniform_scale` (JSON hợp lệ, `ok:true`, CapCut không đọc được), `enums --type X` (trả mảng rỗng thay vì báo cú pháp sai), và `add-filter` (material rỗng ruột). Khi thêm bất kỳ tính năng mới nào, phải giả định nó có thể thuộc loại này và kiểm tra bằng mắt trong GUI.

**Việc còn dở dang khi kết thúc phiên:** oracle cho `add-filter`, export MP4 thật, kiểm chứng animation combo, đo timing nhóm transition mạnh.

## PHỤ LỤC E.2 — NHẬT KÝ PHIÊN 29/07/2026 (v5)

**Mục tiêu:** giải quyết `add-filter`, kiểm chứng animation combo, đo timing nhóm transition mạnh.

**Bước 17 — đo timing và bóc material.** Bảng timing của testV4 (7 transition mạnh + keyframe đầy đủ + combo + effect) trùng khít bảng của v2 và v3: lệch tối đa 26,7 ms, không tích luỹ. Ưu tiên 4 khép lại.

Bóc material phát hiện ngay điểm mấu chốt: filter do CLI tạo nằm ở bucket `video_effects` với `path = ##_material_placeholder_..._##`, còn track của nó là `type: "effect"`.

**Bước 18 — oracle song song.** Thả tay một filter "Film" trong GUI, **giữ nguyên** filter hỏng của CLI làm đối chứng. Diff cho ra 54 dòng, sáu điểm sai cốt lõi. Đây là lần đầu dùng biến thể oracle "so sánh song song trong cùng project" và nó hiệu quả hơn hẳn cách cũ.

Nhân tiện xác nhận bằng mắt: shot 4 zoom out, shot 2 pan ngang trái sang phải, shot 7 zoom kèm chéo từ dưới-phải lên trên-trái — khớp chính xác với PLAN. Mà shot 2 và 7 chính là hai shot mang animation combo, nên **combo không đè keyframe**. Ưu tiên 3 khép lại.

**Bước 19 — tra catalogue, phát hiện nguyên nhân gốc.** `capcut enums --filters` trả về 10 mục với `resource_id` chạy liên tiếp `...117` đến `...126` và **không mục nào có md5**. Dữ liệu bịa. `--filters --jianying` thì có 468 mục đủ md5. `add-filter` hỏng từ nguồn, không vá được.

**Bước 20 — dập khuôn, lần 1.** `filter_apply.py` v1 dập hai filter, mỗi cái nửa timeline. Track hiện nhãn "Film" và "1980" — khuôn đúng. Nhưng đọc kỹ thì `path` của 1980 mà Python ghi (trỏ cache) đã bị **CapCut ghi đè** thành placeholder.

Điều này lật lại chẩn đoán về ý nghĩa chuỗi placeholder lần thứ hai. Chỉ tới bước 21, khi `find_ph.py` cho thấy nó nằm đồng thời ở `transitions[0]` (do CLI ghi) và `effects[1]` (do CapCut ghi) với **cùng một GUID**, mới ra kết luận đúng: hằng số dùng chung, nghĩa là "chưa resolve được".

**Bước 21 — vá công cụ.** Phát hiện `check_sync.py` và `diff_timing.py` **chưa từng được ghi ra đĩa** dù có mã trong tài liệu v0.4, nên một phép đo timing đã bị bỏ sót. Ghi ra rồi đo lại: lớp filter lệch **0,0 ms** trên toàn bộ 8 shot.

Cũng phát hiện `v4_fx.py` hardcode tên snapshot của bước 17, nên bảng timing nó in ra ở mọi lần chạy sau đều là số cũ — một cái bẫy tự tạo, đã cho vào danh sách bỏ.

**Bước 22 — thử path rỗng.** Đặt `path = ""` cho 1980 để xem CapCut có tự tải như với transition. **Không.** Nó ghi đè thành placeholder. Quy tắc cache-first ra đời.

Tab Filters trong GUI cho thấy hai mục tên "1980" đều mang **mũi tên tải xuống**, trong khi "Film" thì không — bằng chứng phụ rất rõ.

**Kiểm kê cuối cùng.** `fx_audit.py` phát hiện thêm hai điều mà không công cụ nào khác bắt được: transition `Cube` chưa resolve tài nguyên (6/7 cái còn lại tốt), và thư mục cache short-id của "Retro Film" đổi qua đổi lại giữa các phiên trong khi md5 giữ nguyên.

**Bài học lớn nhất của phiên:** panel GUI hiển thị đúng tên và đúng intensity **không chứng minh gì cả**, vì CapCut tra metadata theo `resource_id` độc lập với việc tài nguyên có trên đĩa hay không. Đây là lỗi im lặng loại thứ tư, và là loại nguy hiểm nhất vì nó vượt qua được cả bước kiểm tra bằng mắt ở mức panel.

**Còn dở dang:** chứng minh dứt điểm 1980 có render hay không (quan sát đổi màu ở ranh giới chỉ chứng minh Film có tác dụng, chưa chứng minh 1980 tồn tại); truy nguyên nhân `cube`; và quan trọng nhất — **export MP4 thật**, thứ chưa từng làm suốt bốn phiên.

## PHỤ LỤC E.3 — NHẬT KÝ PHIÊN 29/07/2026 (v6)

**Mục tiêu:** export MP4 thật, thứ đã bị hoãn suốt bốn phiên.

**Sự cố nhỏ đầu phiên.** Mở PowerShell mới làm mất sạch biến và hàm của khối X.1. Giải bằng `session.ps1`, đồng thời sửa luôn hai điểm yếu của khối cũ: `$TID` đọc thẳng từ `Timelines\project.json` thay vì gán tay, và bỏ biến `$P4` chỉ giữ `$P`.

**Chặn đứng bởi khoá Pro.** Bấm Export thì CapCut hiện hộp thoại "You're using the following Pro feature", liệt kê đúng một mục: filter "Film". Không hề có cảnh báo nào ở các bước trước — không ở `lint`, không ở `fx_audit.py`, không ở panel, không ở preview. Đây là lỗi im lặng thứ năm và là loại nguy hiểm nhất vì nó vượt qua cả mức bằng chứng 4.

Điểm sáng: hộp thoại đó liệt kê đầy đủ và có nút "Back to edit", nên nó là **công cụ kiểm kê Pro** dùng được, chỉ mất ba mươi giây. Đưa vào quy trình thành bước 11b.

Nhìn lại ảnh chụp màn hình cũ thì viên kim cương tím vẫn nằm đó cạnh tên "Film" — cả hai bên đều đã bỏ qua nó nhiều lần.

**Gỡ lớp filter rồi export.** Cả hai filter đều vô dụng: Film bị chặn, 1980 đã chứng minh không render. `strip_filters.py` gỡ sạch, timing lệch 0,0 ms, lint sạch. Export trọn vẹn 2 phút 48 thành công, 245,6 MB.

**Kết quả kiểm chứng đầu ra.** `nb_frames = 5062` chia 30 ra đúng 168,7333 giây — khớp duration project tới từng frame. Keyframe scale cả hai chiều, keyframe position, canvas blur, scene effect, combo animation đều render đúng.

**Chỗ phép thử đầu tiên có lỗ hổng.** Cách so md5 không phân biệt được transition thật với cắt cứng, vì mọi segment đều có Ken Burns nên hai khung cách nhau 0,26 giây luôn khác nhau. Phải làm vòng hai bằng `tr_profile3.py` đo biến động trên lưới 32×32 với ba cửa sổ đối chứng nằm giữa shot.

Vòng hai cho kết quả sạch. Ken Burns thuần cho `max d = 0,30–0,39` — mốc nền cực thấp, khiến phép đo có sức phân giải cao. Sáu transition tốt vọt lên 45–68 và có hoạt động ở **cả hai phía** ranh giới. `Cube` thì phía trái bằng **0 tuyệt đối trên 17 khung liên tiếp**, rồi một spike đơn tại ranh giới: cắt cứng.

**Một bẫy suýt dẫn tới kết luận sai.** Bảng của `Cube` có khối hoạt động 33–53 kéo dài sau ranh giới, thoạt nhìn giống transition đang chạy lệch. Thực ra đó là **combo animation của shot 2**. Bằng chứng chéo: shot 7 cũng mang combo, và cửa sổ `Flip II` nằm đúng đầu shot 7 cho `phải = 17` bất đối xứng y hệt, nhưng vẫn kèm `trái = 5` của transition thật. Cùng dấu vết phía phải, khác nhau phía trái.

Bài học: khi đo đầu ra, phải biết trước shot nào mang animation, nếu không sẽ quy nhầm chuyển động của animation thành chuyển động của transition.

**Quyết định về phạm vi.** Phụ đề và nhạc nền được chủ động hoãn — làm thủ công trong GUI đủ nhanh, sẽ tự động hoá ở vòng sau. Trọng tâm chuyển sang hiệu năng quy mô lớn và kiến trúc app.

**Trạng thái cuối phiên: toàn bộ chuỗi từ ảnh + audio đến MP4 đã được kiểm chứng ở mức bằng chứng cao nhất. Pipeline không còn là giả thuyết.**

## PHỤ LỤC E.4 — NHẬT KÝ PHIÊN 29/07/2026 (v7)

**Mục tiêu:** chuẩn hoá `CAPCUT_LAB`, hoàn tất vendor kit, chuẩn bị máy sản xuất.

**Chuẩn hoá đường dẫn.** `lab_patch.py` vá bảy file chứ không phải năm như dự đoán — ba file thừa là `v3_check.py`, `v3_fx.py`, `v4_fx.py` thuộc nhóm đã bỏ, sau đó dời sang `_deprecated\`. Kiểm chứng bằng cách trỏ `CAPCUT_LAB` sang thư mục tạm và xác nhận `moved.json` rơi đúng chỗ mới.

Một dương tính giả cần biết: script báo `grab_frames.py con chuoi D:\Test_tool KHONG khop mau` nhưng đó chính là dòng fallback trong header, bắt buộc phải giữ. Căn cứ duy nhất là dòng `tổng: N chỗ còn lại` ở khối kiểm cuối, vì khối đó đã lọc các dòng có `CAPCUT_LAB`.

**Vendor kit.** `winget download` tải thành công 516,54 MB và tự xác minh hash. Nhãn CHƯA KIỂM CHỨNG ở IX.10 được gỡ. Cache hiệu ứng copy sạch 14278 file, không file nào FAILED.

**Trinh sát updater.** Phát hiện thư mục cài có số phiên bản trong tên (`Apps\9.1.0.3879\`), nghĩa là bản mới cài bên cạnh chứ không đè. Xác định cặp updater thật là `CapCut-DiffUpgrade.exe` và `hpatchz.exe`. Bản `setup_2_capcut.ps1` đầu tiên dò bằng regex `updat|upgrad|patch|daemon|service|helper` và quét trúng cả `VEHelper.exe` — nếu chặn nhầm file này có thể hỏng khâu render. Đã đổi sang danh sách cố định. Bài học: **đừng dò tên file thực thi bằng regex khi hậu quả của dương tính giả là hỏng phần mềm.**

**Lỗi lặp lại: script không có trên đĩa.** `Test-Kit` phát hiện `kb_apply.py` và `snap.py` chưa bao giờ được ghi ra file, dù `kb_apply.py` là lớp Python cốt lõi và mã của nó đã nằm trong tài liệu từ v0.4. Nhiều khả năng testV4 được dựng bằng `v4_apply.py` — tên cũ, chưa tổng quát hoá. Kit 0,92 GB đã đóng gói xong ở trạng thái **thiếu script quan trọng nhất** và chỉ được cứu nhờ hàm `Test-Kit` mới thêm. Đây là lần thứ hai của cùng một lỗi, sau `check_sync.py` ở v5.

**Điểm sót về snapshot vàng.** Mọi snapshot hiện có đều thuộc testV4, dùng nhóm transition mạnh kèm `cube`. So máy mới với chúng là so nhầm công thức. Đã tạo bộ `parity_gold_*` bằng đúng công thức `parity_build.py` (nhóm transition nhẹ) để làm mốc chuẩn.

**Chặn updater và xác nhận không tác dụng phụ.** Áp cả hai mức trên máy gốc. CapCut vẫn chạy. Thả thử transition mới thì tải về được, cache tăng 272 → 277 mục — bằng chứng trực tiếp rằng cơ chế resolve theo md5 (VIII.5) vẫn nguyên vẹn. Đây là điều kiện bắt buộc mà nếu chặn sai sẽ phá hỏng, và cách phát hiện duy nhất là thử tay.

**Mốc vàng parity.** Phát hiện một lỗ hổng trong kế hoạch ban đầu: mọi snapshot hiện có đều thuộc testV4 với nhóm transition mạnh, không khớp công thức `parity_build.py`. Đã dựng `paritytest` và chụp ba snapshot mới. Nhân đó tinh chỉnh tiêu chí parity thành hai tầng — so bảng trước-CapCut để kiểm tính tất định của CLI cộng Python với ngưỡng 0,0 ms tuyệt đối, và so bảng sau-CapCut để kiểm hành vi quantization. Tiêu chí "dưới một frame" chỉ áp cho phép so trước-với-sau trên cùng máy, dùng nhầm sang so hai máy sẽ che mất sai khác thật.

**Lần đo timing thứ tư.** Bảng chênh lệch của `paritytest` trùng khít v2, v3, v4 tới từng phần mười mili giây, trên một project clone khác với ID segment hoàn toàn khác. Frame quantization đã có thể coi là hằng số của bộ tám shot này.

## PHỤ LỤC E.5 — NHẬT KÝ PHIÊN 2026-07-30 — Refactor: di trú sang cây ba nhánh và tạo bộ tài liệu

**Bối cảnh.** Thư mục `D:\Test_tool` đã lộn xộn tới mức không set up được trên máy thứ hai: code lẫn ảnh, mp3, srt, snapshot, mp4, script đã chết, tài liệu nháp. Mục tiêu phiên: repo git bài bản có thể clone sang máy render, và bộ tài liệu để AI phiên sau tiếp cận được qua GitHub mà không cần ai dán file.

**Môi trường đã thay đổi.** Python nâng lên **3.14.6** bản python.org; 3.13.14 và bản Microsoft Store đã gỡ sạch. Git 2.53 cấu hình `core.autocrlf=false`, `core.longpaths=true`, `init.defaultBranch=main`. Cache hiệu ứng lên **279 mục**. Ổ C còn 10,7 GB. `LongPathsEnabled` vẫn bằng 0, chưa đặt.

**Ba đính chính về capcut-cli.** `capcut version` không phải lệnh xem phiên bản — CLI hiểu là tên project và báo lỗi, nên mọi script kiểm tra sự tồn tại của CLI bằng lệnh này đều báo âm tính giả. `capcut doctor -H` **không kèm project** cho output khác hẳn mục IX.5 của tài liệu cũ: chỉ có `Platform`, `Node` và danh sách kiểm môi trường, không có khối `Version / Write guard / Schema int` — muốn thấy khối đó phải truyền thêm đường dẫn project. `patch_v8.py` đã xác định là script vá một-lần, đã chạy 29/07 lúc 22:47, có cơ chế tự vô hiệu, xếp `_deprecated`.

**Di trú.** `migrate.py --apply` chép 64 mục 1312,4 MB, không lỗi. Cây mới: `capcut-pipeline\` 2,6 MB / 83 file, `data\` 349,8 MB / 302 file, `vendor\` 961,6 MB / 14770 file. Đổi tên thư mục mẹ thành `D:\IT\capcut-lab`, `CAPCUT_LAB` trỏ `D:\IT\capcut-lab\data`. `D:\Test_tool` còn nguyên làm đường lùi, dự kiến giữ một tuần.

**Smoke test đạt.** `fx_audit.py` và `check_sync.py` chạy đúng ở vị trí mới, snapshot rơi vào chỗ mới. Bảng timing của `paritytest` khớp từng con số với mốc vàng. Lưu ý mức bằng chứng: phép này chỉ **đọc** project đã dựng, nên chưa chứng minh Python 3.14 **sinh ra** cùng kết quả như 3.13.

**Quyết định thiết kế.** Đường dẫn làm việc chuyển từ ghi cứng sang **dẫn xuất theo vị trí file**: `os.environ.get("CAPCUT_LAB") or Path(__file__).resolve().parents[2] / "data"`. Nghĩa là giữ bố cục ba nhánh thì không cần đặt biến môi trường. `.gitattributes` sửa để `.bat`, `.cmd`, `.ps1` giữ CRLF — bản do script sinh ra dùng `* text=auto eol=lf` cho tất cả, sẽ làm `cmd.exe` đọc sai `run.bat`, và nó **ghi đè** `core.autocrlf=false`. `.gitignore` **bỏ chặn** `*.tmp` và `*.bak` vì `template-2.tmp` và `draft_content.json.bak` là thành phần hợp lệ của project CapCut; thêm phủ định cho `_deprecated/backups/*.v8bak` vì hai file đó là bản ghi duy nhất của trạng thái trước lần vá md5.

**Đưa `docs/legacy/older/` ra khỏi repo.** Mười một file nháp cũ 1,5 MB, đã bị v0.8 thay thế, và chứa những kết luận **sau này bị bác bỏ** — công thức lề thiếu một nửa, "resolve theo md5", `KFTypeUniformScale`. Thông tin sai trong repo mà AI đọc được thì tệ hơn không có thông tin. Chuyển sang `data\archive\docs-older\`.

**Hai script hết vai trò.** `audit_kit.py` kiểm kê theo Phụ lục B của tài liệu cũ — danh sách đó sắp thành bản lưu trữ, và nó có hai lỗi cố hữu: `EXPECT_LAB` chứa `capcut_post.py` là file **chưa bao giờ tồn tại** nên báo thiếu mãi mãi, và phần đếm cache tìm **file** tên md5 trong khi md5 là **thư mục** nên luôn in 0. Phần đáng giữ duy nhất là đo bytes-mỗi-segment, sẽ trích thành `tools/probe_drafts.py` khi bắt đầu Việc A. `preflight.py` là công cụ kiểm-trước-khi-di-trú, hết việc.

**Một lỗ hổng logic trong kết luận cũ.** Bảng ma trận ở v0.8 mục VIII.16.4 dẫn `then-and-now` và `white-flash` làm bằng chứng cho ô "CLI ghi + tài nguyên chưa cache". Nhưng `then-and-now` chính là transition được dùng làm **đối chứng dương** trong phép thử `trpath` — chọn *vì* biết chắc sẽ chạy. Và không chỗ nào ghi lại phép chụp cache trước-sau cho riêng hai tài nguyên đó. Ô này vì vậy vẫn dựa trên giả định chưa đo. Cách sửa: khi làm phép thử đóng ô "Python dập + chưa cache", thêm luôn hai nhánh CLI vào cùng thí nghiệm, chụp cache trước-sau, đóng cả hai ô bằng một lần mở CapCut.

**Một dữ kiện gây nhiễu đã làm rõ.** Mục IX.10 ghi thả tay **một** transition làm cache tăng 5 mục; project `truncached` cho thấy CapCut resolve **hai** transition trong draft chỉ tăng 1 mục. Không xung đột: duyệt tab GUI có thể prefetch cả nhóm, còn mở draft chỉ lấy đúng cái được tham chiếu. Hệ quả cho thiết kế phép thử: phép chụp trước-sau phải bao quanh **thao tác mở draft**, và trong phiên đó không mở tab Transitions.

**Bộ tài liệu.** Viết `START-HERE.md`, `README.md`, `reference.md`, `failures.md`, `procedures.md`, `model.md`. `model.md` mỏng có chủ ý, làm chỉ mục vào `legacy/v0.8-full.md`. Chép `fixtures/test-8shot/` và `fixtures/parity-gold/` vào repo để máy khác chỉ cần `git clone` là chạy được probe parity.

---
