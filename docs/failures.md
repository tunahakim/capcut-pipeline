# Failures — mọi loại lỗi đã gặp và cách bắt

**Đọc file này trước khi kết luận bất cứ điều gì về một tính năng.**

## 1. Thang bằng chứng

| Mức | Bằng chứng | Đủ tin chưa |
|---|---|---|
| 1 | `lint` sạch, `tracks` hiện đúng, `info` bình thường | **Không.** Ba lỗi im lặng đầu đều pass mức này |
| 2 | Panel GUI hiển thị đúng tên và tham số | **Không.** Xem lỗi số 4 |
| 3 | `fx_audit.py` báo `path` trỏ tới file **có thật** | Gần đủ. Không bắt được khoá Pro |
| 4a | Bật/tắt lớp trong GUI, mọi thứ khác giữ nguyên | Cách rẻ và sạch nhất ở preview |
| 4b | Thấy tác dụng thị giác, đối chứng **cùng khung hình** | Đủ cho preview |
| 5 | Export MP4 thật rồi đo từng khung | **Đủ hoàn toàn** |

Mức 4b: đối chứng phải **cùng một khung hình**. So màu giữa giây 30 và giây 120 là vô nghĩa vì hai bức ảnh vốn khác nhau. Phải rê con trỏ qua đúng ranh giới nằm **bên trong một shot**. Và nếu ranh giới là "A → B" thì đổi màu chỉ chứng minh A khác B, chưa chứng minh B tồn tại.

Điều kiện thứ hai của mức 4b, thêm ngày 31/07/2026 sau ca 2.8: **phải biết trước ground truth của từng shot trước khi nhìn**. Khi một tính năng chỉ được bật trên một phần số shot và người quan sát không biết shot nào thuộc nhóm nào, mắt sẽ tự dựng ra kết luận sai với độ tự tin rất cao. Trước mọi phép kiểm thị giác, hãy in ra danh sách shot nào có tính năng, ở cường độ nào, tại mốc thời gian nào, rồi mới mở preview.

## 2. Tám mục lỗi im lặng — bảy lỗi thật và một ca lỗi quan sát

### 2.1. `keyframe uniform_scale`

**Triệu chứng:** lệnh trả `{"ok":true,"added":1}`, JSON ghi ra hợp lệ đúng cấu trúc, `capcut lint` sạch. CapCut hiển thị Scale = 100%, `clip.scale` vẫn `{"x":1,"y":1}`, không có gì xảy ra.

**Nguyên nhân:** CLI ghi `property_type: "UNIFORM_SCALE"`. CapCut cần `"KFTypeScaleX"`. Mọi trường khác của CLI **trùng khít** với những gì CapCut ghi — lỗi gọn trong đúng một chuỗi.

**Cách phát hiện:** phép thử oracle. Làm Ken Burns bằng tay trên một shot chưa đụng, đóng CapCut, đọc ngược file.

**Xử lý:** không dùng lệnh `keyframe`. Ghi keyframe bằng Python (`kb_apply.py`), và xoá mọi keyframe có `property_type` thuộc `{UNIFORM_SCALE, KFTYPEUNIFORMSCALE}` mà CLI đã sinh.

### 2.2. `capcut enums --type X`

**Triệu chứng:** trả về **mảng rỗng**, exit code 0, không báo lỗi.

**Nguyên nhân:** cú pháp đúng là flag trực tiếp, `capcut enums --transitions`.

**Xử lý:** dùng `tools/enum_list.py`. Không bao giờ tin một catalogue rỗng là "không có mục nào".

### 2.3. `capcut add-filter`

**Triệu chứng:** lệnh thành công, `lint` sạch, `capcut tracks` hiện track filter với 1 segment đúng độ dài. Trong CapCut: track **không có nhãn**, panel Filters trường Name **trống rỗng**, Intensity = 0 xám không kéo được, không có tác dụng thị giác nào.

**Hai nguyên nhân độc lập.** Một là ghi sai bucket và sai loại track — sáu điểm khác nhau, xem `reference.md` mục 6. Hai là **catalogue `--filters` của namespace CapCut là dữ liệu rác**: mười `resource_id` chạy liên tiếp từ `...117` đến `...126`, **không mục nào có md5**. ID thật của ByteDance không bao giờ được cấp liên tiếp. Thư mục cache tương ứng không tồn tại và sẽ không bao giờ tồn tại.

**Cách phát hiện:** nhìn ảnh chụp màn hình. Mọi kiểm tra tự động đều báo bình thường.

**Xử lý:** bỏ hẳn lệnh. Dùng `filter_apply.py`, và dùng `capcut enums --filters --jianying` (468 mục có md5) làm catalogue.

### 2.4. Filter không có tài nguyên trong cache

**Triệu chứng:** panel Filters hiển thị **đúng tên và đúng intensity**, không phân biệt được với filter hợp lệ bên cạnh. Nhưng không render gì.

**Nguyên nhân:** CapCut tra **metadata** theo `resource_id` từ catalogue nội bộ, hoàn toàn **độc lập** với việc file tài nguyên có trên đĩa hay không.

**Cách phát hiện:** phép thử tắt-bật lớp (mức 4a) — bật rồi tắt đúng một lớp trong khi mọi thứ khác đứng yên. Cần một **đối chứng dương** trong cùng phiên: một lớp biết chắc hoạt động, để chứng minh cơ chế preview có phản hồi. Dấu hiệu phụ: trong tab Filters, mục chưa có cache mang biểu tượng **mũi tên tải xuống**.

**Xử lý:** cache-first. Bấm mũi tên tải xuống trước, rồi mới tự động hoá.

**Bài học tổng quát:** panel GUI hiển thị đúng **không phải bằng chứng** tính năng hoạt động.

### 2.5. Tài nguyên khoá Pro

**Triệu chứng:** đi qua **mọi** lớp kiểm chứng kể cả preview và `fx_audit.py`. Chỉ chặn ở đúng khoảnh khắc bấm Export, bằng hộp thoại `You're using the following Pro feature`.

**Cách phát hiện:** chỉ hộp thoại Export, hoặc viên **kim cương tím** cạnh tên trong tab Filters/Transitions/Animation. `enums.json` có trường `is_vip` nhưng chỉ phủ mục nằm trong catalogue, mà tài nguyên thả tay từ GUI thường không nằm trong đó. `lint` và `fx_audit.py` không biết gì về Pro.

**Xử lý:** bấm Export, đọc danh sách, bấm **Back to edit**, thay bằng bản miễn phí. Tốn ba mươi giây và bắt được thứ không công cụ nào khác bắt được.

Ví dụ đủ ba mặt: filter "Film" **không có** trong `enums.json` ở bất kỳ namespace nào, **có** trong cache và render đúng ở preview, và **bị khoá Pro**.

### 2.6. Transition `cube` — tài nguyên chết

**Triệu chứng:** `path` vẫn là placeholder sau khi CapCut đã mở, hiển thị và lưu lại nhiều lần. Ở đầu ra nó render thành **cắt cứng sạch sẽ** — không khung đen, không glitch, không artefact, chỉ thiếu hiệu ứng.

**Cách phát hiện:** `fx_audit.py`. Hoặc ở đầu ra: đo biến động giữa các khung liên tiếp trên lưới 32×32 quanh ranh giới. Transition thật có hoạt động ở **cả hai phía** (cột trái 3–6 khung); cắt cứng có cột trái **0 tuyệt đối** rồi một spike đơn tại ranh giới.

**Bẫy khi đọc kết quả đo:** một shot mang **combo animation** sẽ tạo hoạt động ở phía phải ranh giới đầu shot, làm bảng trông bất đối xứng dù transition vẫn tốt. Luôn đối chiếu bằng tay với danh sách shot mang animation trước khi kết luận.

**Xử lý:** danh sách đen. Thay slug khác rồi làm lại.

### 2.7. Đổi tên project trong GUI không cập nhật `draft_fold_path`

**Triệu chứng:** đổi tên project bằng giao diện CapCut. Thư mục trên đĩa đổi tên, `draft_name` trong `draft_meta_info.json` đổi theo, mọi thứ nhìn bình thường. Nhưng `draft_fold_path` vẫn trỏ tới **tên cũ**.

**Đo được ngày 31/07/2026:** project tạo tên `0730`, đổi thành `nativescaffold`. Kết quả `draft_name = nativescaffold` nhưng `draft_fold_path = C:/Users/admin/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/0730`.

**Vì sao nguy hiểm:** `clone_project.py` thay chuỗi `OLD = SRC.name`, tức tên thư mục nguồn. Nếu scaffold từng bị đổi tên thì chữ tên cũ nằm trong `draft_fold_path` sẽ **không** được thay, và cái lệch đó nhân bản vào mọi project clone sau này.

**Xử lý:** không bao giờ đổi tên một project định dùng làm scaffold. Nếu lỡ đổi rồi thì vá `draft_fold_path` bằng Python trước khi clone, rồi quét toàn bộ file text trong project tìm chuỗi tên cũ ở dạng đường dẫn để chắc không còn sót.

**Kèm theo, cùng một phép đo:** `draft_meta_info.json` chứa `draft_root_path` là đường dẫn tuyệt đối của máy. Đây là bằng chứng thực nghiệm cho cảnh báo "scaffold chỉ dùng được trên chính máy đã tạo ra nó" ở `START-HERE.md` mục 3.1 — trước đó cảnh báo này chỉ là khẳng định suông.

Bổ sung 31/07/2026, cùng cơ chế nhưng khác đường vào: **scaffold clone sang máy khác cũng mang theo `draft_fold_path` của máy cũ.** Đo trên máy render: `scaffold\testV3_CLEAN` chứa `draft_fold_path = C:/Users/anhlt/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/testV3`, và `clone_project.py` không sửa trường này vì nó chỉ thay GUID cùng tên project. Sau khi vá bằng `tools/fix_fold_path.py`, project `reh10` mở và lưu bình thường, timing lệch 0,0 ms. Đây là lời giải thích cho cảnh báo "scaffold chỉ dùng được trên chính máy đã tạo ra nó": không phải scaffold hỏng, mà là một trường đường dẫn tuyệt đối chưa được thay. Cách phát hiện: sau mỗi lần clone, in `draft_fold_path` ra và so với thư mục thật.

### 2.8. `bg-blur` "mất tác dụng ở quy mô lớn" — ĐÃ ĐÓNG, là lỗi quan sát

**Triệu chứng ban đầu, ghi ngày 31/07/2026:** sau khi dựng `bench300` gồm 300 shot, quan sát bằng mắt trên preview và trên bản export cho thấy rất nhiều khung hình có ảnh nhỏ hơn khung nhưng nền là màu đen chứ không phải nền mờ, ô Canvas trong panel không được tick. Kết luận ban đầu là `bg-blur` mất tác dụng ở quy mô 300 shot dù mọi kiểm tra tự động đều sạch.

**Kết luận thật:** không có lỗi nào cả. `bench_shots.py` rải blur ngẫu nhiên cho khoảng một nửa số shot, nên 147 trong 300 shot mang `canvas_color` **theo đúng thiết kế**, và canvas màu ở scale nhỏ hơn 1 thì cho nền đen. Các shot đen và shot mờ nằm đan xen nhau chính vì phép rải là ngẫu nhiên.

**Chuỗi bằng chứng khép lại, 31/07/2026.** `tools/bgblur_diag.py` đọc `draft_content.json`: đúng 300 canvas cho 300 segment, không canvas mồ côi, mỗi segment đúng **một** ref canvas, phân bố `canvas_blur` 153 và `canvas_color` 147, `check_flag` 4103 đúng 153 lần và 7 đúng 147 lần, vị trí ref luôn là idx 3, file gốc và file trong `Timelines\` **trùng nhau từng byte** ở 2.499.852 byte. Scale chạy 0,72 đến 0,92 nên viền lộ nền rộng 180 đến 269 pixel mỗi bên, thừa sức nhìn thấy. `tools/bgblur_frames.py` trích khung từ bản export 4,07 GB tại giữa các shot đã biết trước nhóm; các shot `canvas_blur` có nền mờ, các shot `canvas_color` có nền đen. `tools/shots_crosscheck.py` đối chiếu 300 dòng `shots.csv` với JSON: 0 lệch trên `start`, `dur`, `blur`, `image` và cặp scale Ken Burns; 153 blur khớp hai phía; 299 transition khớp hai phía; hai dãy mẫu đan xen trùng nhau từng ký tự trên cả 300 shot.

**Trạng thái tính năng:** canvas blur **đã kiểm chứng ở mức 5** trên 300 shot, gồm cả mức yếu nhất 0,0625 và mức mạnh nhất 1,0. Không còn hạn chế nào cho sản xuất.

**Hai bài học giữ lại.** Một, bổ sung điều kiện ground truth cho mức 4b của thang bằng chứng, xem mục 1. Hai, luật sinh cột `blur` trong sản xuất thật **không được ngẫu nhiên**: nền đen xen kẽ nền mờ giữa các shot liền nhau trông như lỗi. Luật đúng là hình học — bật blur khi ảnh không phủ kín khung ở bất kỳ thời điểm nào, tức khi `KX * s < 1` hoặc `KY * s < 1` với `s` nhỏ nhất của shot. Luật này bao trùm cả trường hợp ảnh lệch tỉ lệ so với khung, vốn lộ nền ngay cả ở scale bằng 1.

## 3. Ba loại lỗi cấu trúc

### 3.1. CapCut đổi tên thư mục project

Tên thư mục trên đĩa và tên hiển thị trong library là **hai thứ khác nhau**. Bấm New Project đặt tên `v2oracle` thì CapCut tạo thư mục theo ngày `0728 (1)`, còn `v2oracle` chỉ nằm ở trường `draft_name`. Khi mở CapCut lần đầu sau khi CLI đã ghi, nó **đổi tên thư mục** để khớp `draft_name` nhưng **không cập nhật** các đường dẫn media tuyệt đối. Kết quả: hộp thoại "Link media — 0/9 media linked", timeline đỏ lòm.

**Phòng tránh:** `clone_project.py` đặt `draft_name` **trùng tên thư mục** ngay từ đầu, nên bẫy này đã bị vô hiệu hoá.

**Nếu gặp: bấm Cancel, KHÔNG bấm "Link media"** — bấm nó sẽ khiến CapCut ghi lại đường dẫn theo thư mục bạn chọn tay, có thể trỏ ra ngoài project. Vá bằng `patchpath.py`, phải sửa **tất cả** tám file kể cả `draft_meta_info.json` (lưu danh mục media của panel bên trái, rất dễ bỏ sót).

### 3.2. capcut-cli mù thư mục `Timelines\`

Xem `reference.md` mục 4. Bằng chứng đo được: ghi `clip.scale = 0.9` cho cả 8 segment vào hai file gốc, mở CapCut lên thì **chỉ shot 3** có scale 90% — đúng cái shot trước đó đã chỉnh bằng tay trong GUI.

### 3.3. CapCut đang chạy sẽ ghi đè mọi thứ

Kể cả khi đã thu nhỏ xuống system tray. CapCut có **Auto save** nên ghi định kỳ. Đã gặp trường hợp chạy 7 lệnh add thành công nhưng mở lại chỉ thấy 1 ảnh. Kiểm bằng `Get-Process *CapCut*`, output phải rỗng.

Khi cần CapCut **lưu đầy đủ** thao tác tay (phiên oracle), đóng bằng **nút X** và đợi mười giây. Khi chỉ mở để xem, kill cho nhanh.

## 4. Bẫy PowerShell 5.1

**Toán tử `>` ghi UTF-16LE**, không phải UTF-8. Đọc bằng Python cho `UnicodeDecodeError: 0xff in position 0`. Không hỗ trợ `-Encoding utf8NoBOM`. Luôn dùng `[System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding($false)))`.

**Dấu `\` KHÔNG phải ký tự escape.** Viết `python -c "... print(f\"{x}\") ..."` thì PowerShell hiểu `\"` là `\` rồi `"` đóng chuỗi, phần còn lại bị tách ra, và nếu có `{` thì nó hiểu là ScriptBlock, báo `ScriptBlock should only be specified as a value of the Command parameter`. Thông báo nói về `python.exe` trong khi thủ phạm là PowerShell. Lỗi này đã làm hỏng ba lệnh liên tiếp.

**Quy tắc tuyệt đối: không nhúng mã Python vào dòng lệnh.** Ghi ra file `.py` bằng heredoc `@'...'@` cộng `WriteAllText`, rồi gọi `python file.py`. Dùng `@'...'@` nháy đơn để PowerShell **không** nội suy `$`.

**Locale tiếng Việt** dùng dấu phẩy thập phân, `2.5` có thể thành `"2,5"`. Ép định dạng invariant: `$x.ToString("0.###", [cultureinfo]::InvariantCulture)`.

**Nội suy biến:** `"$P_CLEAN"` là biến `$P_CLEAN`, phải viết `"$($P)_CLEAN"`.

**stderr của Node bị tô đỏ** kèm khối `NativeCommandError` trông như crash. Đọc dòng đầu, bỏ phần còn lại.

**`Get-ChildItem -Include` chỉ có hiệu lực** khi đường dẫn kết thúc bằng ký tự đại diện hoặc có `-Recurse`. Thiếu dấu sao thì kết quả luôn rỗng.

**`git ls-files` bọc tên file ngoài ASCII vào nháy và escape thành `\303\264`**, khiến `Get-Item` báo `Illegal characters in path`. Tránh tên file có dấu tiếng Việt trong repo — chúng cũng khó fetch qua `raw.githubusercontent.com`.

## 5. Lỗi quy trình đã mắc lặp lại

**Mã trong tài liệu không có file trên đĩa — mắc bốn lần.** `check_sync.py` và `diff_timing.py` (v5), `kb_apply.py` và `snap.py` (v7), `capcut_post.py` (v8, chưa bao giờ tồn tại). Quy tắc: mã nằm trong tài liệu mà không có file trên đĩa thì phải coi là **chưa kiểm chứng**.

**Hardcode tên snapshot.** `v4_fx.py` ghi cứng tên snapshot của một bước cụ thể, nên bảng timing nó in ra ở mọi lần chạy sau đều là số cũ. Cái bẫy tự tạo.

**Dò tên file thực thi bằng regex.** Bản đầu của `setup_2_capcut.ps1` dò updater bằng `updat|upgrad|patch|daemon|service|helper` và quét trúng cả `VEHelper.exe` — chặn nhầm file này có thể hỏng khâu render. Đừng dò bằng regex khi hậu quả của dương tính giả là hỏng phần mềm.

**Dùng md5 để xác định "chưa cache".** `tr_uncached.py` dùng md5 từ `enums.json` để lọc tài nguyên chưa cache, trong khi md5 đó chính là thứ vừa bị chứng minh không đáng tin. Vòng luẩn quẩn, và kết quả là bốc trúng tài nguyên đã cache sẵn.

**So md5 khung hình để phát hiện transition.** Vô dụng khi mọi segment đều có Ken Burns, vì hai khung cách nhau 0,26 giây luôn khác nhau. Phải đo biến động trên lưới nhỏ, có cửa sổ đối chứng nằm giữa shot.

**`robocopy` không xoá file cũ ở đích.** `pack_vendor.ps1` dùng nó nên mười một script đã dọn vẫn nằm trong kit. Phải xoá thư mục đích trước khi đóng gói lại.

## 6. Ba kết luận từng SAI rồi bị bác bỏ

Ghi lại để không ai đi lại đường cũ.

**"CapCut resolve tài nguyên theo md5."** Sai. Tài liệu tới v0.7 ghi vậy. Bằng chứng bác bỏ: khuôn material transition do CLI ghi **không có trường md5**; và đo trên 25 material đối chiếu được thì 6 cái md5 lệch mà vẫn chạy bình thường. Đúng là resolve theo `resource_id`.

**"Tên property_type đúng là `KFTypeUniformScale`."** Sai. Suy từ tài liệu schema của repo. Phép thử oracle cho ra `KFTypeScaleX`.

**"Số trên UI Position là pixel dịch chuyển thật."** Sai, và sai đúng một nửa nên làm tính hụt biên độ 50%. Phép đo quyết định: ở scale 50%, ảnh chạm mép khi UI ghi X=−960, nhưng dịch chuyển thật chỉ 480 px. Phát hiện được nhờ **probe biên** — shot 8 được cố tình đặt đúng giới hạn lý thuyết; không có nó thì lỗi đã trôi qua.

**"md5 là tên FILE trong cache."** Sai. Là tên **thư mục**: 278 thư mục gốc, 279 thư mục md5, **0 file** md5. Đề xuất ở v0.5 "quét tìm file tên `<md5>`" sẽ không bao giờ thấy gì.

**"`preflight.py` kiểm được môi trường."** Đúng một nửa. Ngày 31/07/2026 phát hiện ba chỗ hỏng. Nó gọi `capcut version`, mà CLI coi `version` là đường dẫn project nên luôn báo `capcut-cli KHONG TIM THAY` dù CLI hoạt động tốt — lệnh đúng là `capcut --version`. `LAB` mặc định còn trỏ `D:\Test_tool`. Mục 9 còn kiểm thư mục đích `D:\IT\CapCut`, cái tên không còn tồn tại sau refactor. Mục 1 tới 7 vẫn dùng được, mục 8 và 9 bỏ.

**"`capcut <lệnh-con> --help` xem được cú pháp."** Sai. CLI diễn giải tham số đầu tiên của mọi lệnh con là đường dẫn project, nên `capcut add-video --help` trả về `{"error":"No draft found at: --help"}`. Muốn biết cú pháp thì đọc script trong `scripts_v1/` hoặc chạy `capcut --help` không kèm lệnh con.

## 7. Bốn quy tắc phương pháp

**Mỗi phép thử phải có một mục biết chắc pass và một mục nghi ngờ.** Nếu cả hai fail thì lỗi ở phương pháp; nếu chỉ mục nghi ngờ fail thì lỗi đúng chỗ đang nghi. Ví dụ: filter "Film" đã có cache làm đối chứng dương cho filter "1980" chưa có cache — nhờ vậy tách bạch được "khuôn sai" với "tài nguyên thiếu", hai nguyên nhân cho cùng một triệu chứng.

**Luôn cài một probe biên.** Một mục được đặt đúng giới hạn lý thuyết, để nếu công thức sai thì lộ ra ngay.

**Không suy diễn hành vi của bucket này từ bucket khác.** Transition tự vá được **không** hàm ý filter cũng vậy. Mỗi loại material phải đo riêng.

**Thiếu vắng một tính năng không phải lỗi nếu ta chưa gọi nó.** Phiên 31/07/2026 dựng project 300 shot rồi thấy không có blur nền và không có hiệu ứng nào, thoáng tưởng là hỏng. Thực ra `bulk_build.py` cố ý chỉ gọi `add-video`. Trước khi kết luận một tính năng hỏng, kiểm lại xem lệnh tạo ra nó có thật sự được chạy hay không. Ngược lại mới đáng sợ: thấy một tính năng **xuất hiện** mà ta không hề gọi.

**Kiểm ràng buộc phải chạy trên đúng giá trị sẽ được ghi ra file, không phải giá trị trong bộ nhớ.** `bench_shots.py` kiểm công thức lề trên số thực rồi mới làm tròn `"%.6f"` lúc ghi CSV; phép làm tròn đẩy shot 1 vượt mép 5 phần mười triệu và `kb_apply.py` từ chối ghi. Phát hiện được là nhờ shot 1 vốn là **probe biên cố ý** — thêm một lần nữa xác nhận quy tắc luôn cài một probe biên.

**Bắt `SystemExit` mà bỏ `e.code` sẽ nuốt sạch thông báo lỗi.** `sys.exit("chuỗi")` không in ra stdout; chuỗi nằm trong `e.code`. Script bao ngoài phải in nó ra, nếu không ta chỉ thấy mã thoát 1 mà không biết vì sao.

**Quy tắc bốn: in ground truth ra trước, nhìn sau.** Trước mọi phép kiểm thị giác, sinh ra danh sách shot nào có tính năng đang xét, ở cường độ nào, tại mốc thời gian nào, rồi mới mở preview hoặc trích khung. Không có danh sách đó thì "tôi không thấy tính năng" không phải là bằng chứng, vì người quan sát không phân biệt được giữa tính năng hỏng và tính năng cố ý không bật. Ca 2.8 tốn trọn một vòng chẩn đoán chỉ vì thiếu bước này.

---