# TODO — việc chưa làm

**Cập nhật 05/08/2026.** Trần file này là **25 KB**; chạm trần thì tách file theo chủ đề chứ không nới thêm lần nữa. Trần vẫn chật hơn trần chung, vì danh sách là thứ dễ phình nhất; trần này chống phình, không liên quan tới fetch — xem `ai-reading-channel.md`.

Luật ba file: file này là **thì tương lai**, gồm mọi việc chưa làm kể cả nợ kỹ thuật; `STATE.md` là **thì hiện tại đã đo được**; `research-log/` là **thì quá khứ**. Mỗi mục phải có tiêu chí hoàn thành, và **xong thì xoá khỏi file này** chứ không đánh dấu rồi giữ lại.

## Ưu tiên 0 — đóng nốt tầng tooling và tài liệu trước khi vào pipeline

Các mục dưới đây làm xong rồi mới chạm `pipeline/steps/`. Lý do xếp trước: mục đích của chúng là để lúc dựng pipeline không còn phải quay lại sửa tool hay tài liệu nữa. Luật viết tool và luật vá tài liệu đã tách sang `docs/conventions.md`, đừng chép lại vào đây.

**Nhóm công cụ phiên.** Viết `tools/session_open.py` gói trọn lượt kiểm đầu phiên thành một lệnh. Đầu chương trình in phiên bản shell và Python đang chạy, rồi in danh sách các bước sắp chạy kèm kết quả mong đợi ngắn gọn của từng bước, để đọc console là biết bước nào lệch. Mỗi bước bọc output bằng một dòng nhận diện mở và một dòng đóng có tên file tool. Sau mỗi bước in một dòng phán quyết ba phần: mã thoát, nhãn ASCII `DAT` hoặc `KHONG DAT`, rồi một câu tiếng Việt có dấu nói rõ mong đợi gì và thực tế ra sao; dòng phán quyết thiếu câu tiếng Việt thì coi như chưa xong. Chạy hết mọi bước rồi mới tổng kết chứ không dừng ở bước hỏng, cuối cùng in `SACH` hoặc `BAN` kèm danh sách bước hỏng và thoát khác 0. Bắt buộc về kỹ thuật: không bắt output của tiến trình con, gọi `subprocess.run` trần để con ghi thẳng ra console và giữ nguyên stderr, và `sys.stdout.flush()` ngay trước mỗi lần spawn vì thiếu dòng này thì output đảo thứ tự. Giá trị kỳ vọng của từng tool nhúng vào chính file này, đó là chỗ duy nhất chúng được phép tồn tại. Tiêu chí xong: một lệnh duy nhất thay được trọn khối mở phiên, và một tool cố tình làm hỏng khiến nó in `BAN` kèm đúng tên bước đó.

**Sửa `tools/read_src.py`, cùng lượt.** Ngưỡng in trọn hiện chỉ đếm dòng nên một file ít dòng mà mỗi dòng rất dài vẫn lọt qua. Đổi thành điều kiện AND: dưới 250 dòng và dưới 20 KB. Khi không in trọn thì nói rõ lý do là do byte hay do dòng, kèm gợi ý dùng `--grep`. Tiêu chí xong: một file ít dòng nhưng nặng byte bị trích chứ không in trọn, và dòng lý do nói đúng vế nào đã chặn.

**Sửa `tools/scripts_index.py`, cùng lượt.** Thêm `--doc <file...>` in trọn docstring gốc đọc từ đĩa. Thêm `--out <path>` ghi kết quả của chế độ đang chạy ra file UTF-8 không BOM xuống dòng LF. Cho `--brief` nhận danh sách file tuỳ chọn. Bỏ chỗ cắt mô tả ở số ký tự cố định, thay bằng lấy trọn câu đầu cắt ở dấu chấm, vì đọc sót mục đích tệ hơn là dòng dài; câu mục đích nào quá dài thì in một dòng nhắc sửa docstring nguồn chứ đừng cắt hiển thị. Mọi cờ mới theo luật không ngầm định ở `docs/conventions.md`. Tiêu chí xong: `--doc` in đúng nguyên văn docstring của một file bất kỳ, và `--brief` không còn dấu ba chấm cắt giữa câu.

**PowerShell 7.** Cài `pwsh` song song, không gỡ 5.1, rồi đo lại năm phép của mục 8 `docs/START-HERE.md`: toán tử `>` ghi mã hoá gì, `Out-File -Encoding utf8` có BOM không, console còn cần `chcp` không, heredoc `@'...'@` còn nguyên hành vi không, `$LASTEXITCODE` sau `git commit` trên cây sạch có đổi không. Làm trước mục tài liệu để mục 8 chỉ phải viết lại đúng một lần. Trần chi phí một lượt: có phép nào lệch bất ngờ thì dừng, ở lại 5.1, ghi lại vào đây. Tiêu chí xong: năm phép đều có số đo, và mục 8 nói đúng shell đang dùng.

**Tài liệu, làm một đợt.** Thêm vào `PER_FILE_BUDGET` của `tools/docs_audit.py` một lớp thứ tư nghĩa là không đo trần: `cap_for()` trả giá trị rỗng thì bỏ qua phép so nhưng vẫn in kích thước ở một khối riêng để không mất khả năng quan sát. Áp cho `docs/scripts.md` vì file đó sinh tự động, dài theo số script, thuộc tầng dán nên không dính ngưỡng token, và không tồn tại hành động hợp lệ nào để nó tụt xuống dưới trần. Hai chốt ghi ngay tại chỗ khai để lớp này không bị lạm dụng: mỗi mục phải ghi tên script sinh ra file đó, và lớp này chỉ dành cho file thuộc tầng dán, còn file nào trợ lý có thể phải tự fetch thì trần vẫn là ngưỡng kỹ thuật thật. Xoá mục miễn trừ còn lại của `docs/START-HERE.md` khỏi `docs/budget-waivers.json` sau khi rút gọn file đó. Thêm banner đầu `docs/scripts.md` nói file này dành cho người đọc trên GitHub, còn trợ lý AI thì dùng `--brief` đầu phiên và `--doc <file>` khi cần cách dùng. Viết lại mục 8 `docs/START-HERE.md` một lần theo số PowerShell mới: sửa dòng tiêu đề mục 8 bị lặp hai lần, xoá ba ngưỡng của `tools/read_src.py` vì chính câu văn đó nói ngưỡng nằm trong mã, xoá bản sao thứ ba của `PER_FILE_BUDGET`, chuyển mọi số đo còn sót sang `docs/STATE.md`, và trỏ sang `docs/conventions.md` thay vì chép lại luật. Dọn `docs/STATE.md` theo một luật duy nhất: một con số chỉ được ở lại nếu lượt kiểm đầu phiên không tự in ra nó trong vài giây, nên số nào `session_open` đã in thì xoá, còn số mua bằng oracle như thời gian mỗi lệnh CLI, kích thước segment, hằng số hiệu ứng, định danh tài nguyên, dung lượng ổ đĩa, mốc dựng thật thì giữ. Chuyển mọi đoạn kể lịch sử trong `docs/STATE.md` sang `docs/research-log/`. Thêm vào `README.md` một luật bắt buộc về nội dung bốn file cửa vào, vì luật hiện nằm rải trong từng file và vẫn bị ghi nhầm khiến chúng phình liên tục: `README.md` là cổng vào và luật đọc, `START-HERE.md` là thứ không đổi theo phiên, `STATE.md` là ảnh chụp thì hiện tại và sửa bằng cách ghi đè, `TODO.md` là thì tương lai và xong việc thì xoá khỏi file, `research-log/` là thì quá khứ và chỉ ghi thêm; trước khi viết bất cứ dòng nào vào bốn file đó phải tự hỏi dòng này thuộc thì nào, vì viết sai chỗ là tạo ra một bản song song và bản song song chắc chắn sẽ lệch. Tiêu chí xong: `tools/docs_audit.py --brief` sạch và không còn mục miễn trừ nào, `docs/START-HERE.md` xuống dưới 90 phần trăm trần. Cần hơn hai lượt vá thì dừng và để phần còn lại cho phiên sau.

**Docstring không dấu còn lại.** Viết lại docstring trong `scripts_v1/` và `pipeline/` cho `python tools/py_audit.py --brief` về 0 `LOI`. Đã quyết làm, không giáng luật xuống `CANH BAO`. Lấy nguyên liệu bằng `python tools/docstring_dump.py --scope scripts_v1/` rồi `--scope pipeline/`, làm hai lô. Vài file là `__init__.py` nên docstring rất ngắn và neo dễ trùng giữa các file, phải kiểm neo theo từng file chứ không theo toàn repo. Viết tiếng Việt có dấu, không hard wrap, giữ nguyên hậu tố `[KIEM: ...]` ở dòng cuối vì `tools/scripts_index.py` đọc nhãn đó. Script sinh spec tự trích neo bằng `ast.get_source_segment` và bắt buộc nhận cả tiền tố `r` của docstring raw string. Việc này máy móc và không đóng góp gì cho mục tiêu CapCut tự động, nên ngân sách phiên còn ít thì để lại. Tiêu chí xong: `python tools/py_audit.py --brief` cho 0 `LOI`, và `docs/scripts.md` sinh lại không vỡ.

**Ba việc sửa dần khi đụng tới, không mở chiến dịch.** Rà luật không ngầm định cho các tool cũ. Rà luật mã thoát có nghĩa cho các tool còn lại trong chuỗi mở phiên, ưu tiên tool chạy mỗi phiên. Không bồi thêm gì vào `tools/preflight.py`: file đó có phần đã chết gồm biến `LAB` mặc định trỏ sai và mục kiểm thư mục đích của một cuộc refactor đã xong, và lệnh `doctor` sẽ thay hẳn nó.

**Hai nợ nhỏ phát sinh 06/08/2026.** Dòng đầu bảng của `tools/rlog_index.py` in cột Phiên lặp hai lần, `05/08-4 05/08-4 chiều`, đúng một file bị. Và nhánh kiểm ngôn ngữ trong `tools/py_audit.py` chưa làm, chỉ làm nếu lọt lỗi câu văn xuôi thuần ASCII lần thứ hai; điều kiện và lý do ghi ở `docs/conventions.md` mục 1.

## Ưu tiên 1 — đóng gói thành ứng dụng dùng được

**`run.bat` thật cộng khung `pipeline/`, nối `config.json` vào đường chạy.** Tính năng đích của dự án: sửa đường dẫn trong một file cấu hình rồi gọi một lệnh. Từ 04/08/2026 đã có `pipeline/config.py` đọc và kiểm lược đồ số 1, và `pipeline/core/shotlist.py` đọc bảng năm cột người viết; còn thiếu `pipeline/steps/`, `pipeline/__main__.py`, và mọi khâu thật. Trình tự chạy vẫn chỉ tồn tại dưới dạng văn xuôi trong `procedures.md`. Ba phần: đưa trình tự đã dựng thành công `prod60` thành mã có kiểm điều kiện trước và sau mỗi khâu; đọc mọi đường dẫn từ `config.json`; dừng sạch kèm thông báo đọc được khi một khâu hỏng. Tiêu chí xong: chép `config.example.json` thành `config.json`, điền đường dẫn ảnh, narration, SRT và bảng shot, chạy một lệnh duy nhất, rồi mở được project trong CapCut với `fx_audit` báo `OK` toàn bộ và lệch timing 0,0 ms.

**Kiến trúc đã chốt, luật đầy đủ nằm ở `architecture.md`**, lý lẽ ở `research-log/2026-08-03-1-bgblur-va-oracle-pro.md` và `research-log/2026-08-04-2-pipeline-config-shotlist.md`; đây chỉ chép phần phải làm. Cài editable qua `pyproject.toml`, **không** đóng gói exe. Ba tầng: hàm thuần trong `pipeline/steps/`, mỗi khâu một file tự khai đầu vào đầu ra kèm kiểm điều kiện trước và sau; rồi CLI có lệnh con; rồi TUI. Thêm tính năng là thả một file vào `steps/` cộng một dòng trong `config.json`. Cổng ports-and-adapters chỉ ở lớp ghi CapCut và lớp media ffmpeg. Bảng shot là nguồn sự thật, draft là phái sinh dựng lại được. `config.json` có số hiệu lược đồ, bản thật để ngoài git, mỗi lượt chạy chụp một bản vào `artifacts/`.

**Module log dùng chung ở tầng core.** Đếm 03/08/2026: **0 trên 40** file `.py` dùng `logging`. Không nhét `logging` vào từng script. Tiêu chí xong: một lượt chạy hỏng để lại đúng một file trong `data\logs` có dấu thời gian, mã thoát và dòng lỗi.

**Lệnh `doctor`, thay hẳn `preflight.py`.** Đọc file khai phiên bản ghim, đối chiếu thứ đang cài, từ chối chạy khi lệch. Được phép tự cài, nhưng **mọi lệnh cài phải ghim phiên bản tường minh**. Git, Node, Python, ffmpeg thì winget lo được; CapCut 9.1.0.3879 phải để tay vì updater đang cố ý chặn. Bootstrap bắt buộc là `.bat` hoặc `.ps1` vì Python không tự cài được Python. Tiêu chí xong: máy trắng chạy bootstrap rồi `doctor` báo xanh toàn bộ.

**TUI là đường vào mặc định của người dùng, nhưng làm sau cùng**, vì phải bọc quanh một CLI đã ổn định; CLI là nền, không phải giao diện phụ, nên mọi lệnh CLI phải chạy được không cần tương tác. Luật: TUI **không giữ trạng thái**, mọi thứ nó hỏi phải ghi vào `config.json` trước; nó **in ra đúng lệnh CLI tương đương trước khi chạy**; tiến trình phát ra từ core để cả CLI lẫn TUI cùng thấy; màu dùng `rich` nhưng vẫn in chữ OK, LOI, CANH BAO vì màu mất khi copy; khung menu tiếng Việt không dấu. Tiêu chí xong: một người chưa từng gõ lệnh dựng xong một project chỉ bằng menu.

## Ưu tiên 2 — công cụ và test


**Quyết định số phận nhãn `OK-BASENAME` trong `tools/docs_audit.py`.** Đếm 04/08/2026 được **281** ref, tức tên file viết trần đang lọt sạch khỏi khối `VAN DE`. Không biến thành lỗi cứng vì mốc chuẩn vỡ ngay và không ai sửa nổi 281 chỗ trong một phiên. Hai hướng: một khối `CANH BAO` riêng đếm theo file để giảm dần theo phiên, hoặc một danh sách miễn trừ cho nhật ký cũ rồi bắt cứng ở `docs/` hiện hành. Việc này phải làm **trước** lượt refactor cây thư mục, vì đó là lúc tên file trần thành lỗi thật. Tiêu chí xong: chọn được một hướng, và con số 281 giảm hoặc được giải thích trọn vẹn.

**Nghiệm thu ba phép kiểm còn lại của `pipeline/core/shotlist.py`.** Đối chứng âm ngày 04/08 cho 6 dòng `LOI` trong khi dự đoán 10, vì `load()` chỉ gọi `check_images` và `check_transitions` khi `parse_text` sạch, và warnings bị bỏ khi đã có lỗi. Ba phép kiểm ảnh thiếu, transition trong blacklist, transition ngoài whitelist, cùng đường `CANH BAO` cho ba cột để dành `motion blur fx`, đều **chưa kiểm chứng**. Tiêu chí xong: một bảng sai chỉ ở phần nội dung, cấu trúc hợp lệ, cho đủ bốn loại chẩn đoán đó.

**Làm rõ bước tạo scaffold rồi biến nó thành script.** `procedures.md` mục 3 viết "copy nguyên thư mục ra `scaffold_CLEAN`" nghe như thao tác tay, nhưng người dùng khẳng định chưa bao giờ copy tay: chỉ mở CapCut, tạo project, đóng, mở lại. Việc đầu tiên là đọc `research-log/` tìm phiên đã dựng scaffold để biết thật sự chuyện gì xảy ra, rồi sửa `procedures.md` cho khớp. Nếu đúng là chưa có script thì viết `tools/scaffold_make.py`: nhận thư mục project vừa tạo bằng GUI, kiểm `draft_name` trùng tên thư mục, kiểm đủ bốn file gốc, kiểm timeline rỗng, copy ra khuôn rồi đặt cờ chỉ đọc. Tiêu chí xong: `procedures.md` mô tả đúng thứ có thật, và bước tạo khuôn không còn chỗ nào phải copy tay.

**Kiểm cây thư mục repo có tuân thủ `architecture.md` chưa, rồi refactor nếu chưa.** Không gấp nhưng phải làm. Trợ lý hướng dẫn lấy cây thư mục đầy đủ rồi đối chiếu bốn tầng và chiều phụ thuộc ở `architecture.md` mục 1. Thời điểm nên làm: **sau khi `build` chạy được đầu-cuối một lần trên bộ 8 shot**, không sớm hơn vì đang di chuyển thứ chưa biết có đúng không, không muộn hơn vì mỗi khâu mới thêm một chỗ phải sửa. Làm trên branch riêng `refactor-arch`. Vì đổi vị trí và tên file sẽ làm lệch tài liệu cùng các file mã khác, phải quét toàn bộ **trước và sau**: grep tên file trong `docs/` và trong mã, chạy `tools/docs_audit.py` để bắt tham chiếu chết, rồi dựng lại bộ 8 shot so timing. Tiêu chí xong: `docs_audit.py` sạch, bộ 8 shot cho 0,0 ms, và một test grep chứng minh `pipeline/core/` không import `subprocess` cùng không import ngược tầng.

**Kiểm khoá Pro cho mọi loại tài nguyên.** `failures.md` mục 1: `fx_audit.py` chỉ chứng minh `path` trỏ tới file có thật, **không bắt được khoá Pro**. Hướng đọc cờ từ enums **đã chết hẳn**, đóng bằng oracle 03/08/2026; số đo ở `STATE.md`. Đối chứng dương là transition 6724227090872275463 trong `v2oracle`, nhưng nó **đã bị xoá khỏi project** trong chính phép gỡ chứng minh điều đó, nên tiêu chí dưới đây chưa chạy được: việc đầu tiên là thả lại nó bằng GUI rồi chụp mẫu, tên hiệu ứng tra ở `research-log/2026-08-03-1-bgblur-va-oracle-pro.md`. Tiêu chí xong: `fx_audit.py` báo đỏ 6724227090872275463 và báo xanh 6724846395116753416. Hai việc phụ: kiểm giả thuyết có `request_id` cùng `category_name` là dấu hiệu tài nguyên tải từ CDN; và rà chữ vương miện còn sót trong `failures.md` cùng nhật ký cũ, đổi thành dấu Pro kim cương tím.

Ba test đầu tiên trong `tests/`: lượng tử hoá frame, công thức lề dạng tổng quát KX KY, khứ hồi `shots.csv`.

## Tính năng tương lai, không làm trong giai đoạn này

**Giữ lại hiệu ứng thả tay qua các lượt dựng lại.** Chụp bản sao draft trước mỗi lượt dựng là phần rẻ và thuộc khâu `build`. Phần khó là ghép hiệu ứng người thả tay từ bản cũ sang bản mới: hiệu ứng neo vào `segment id` sinh ngẫu nhiên mỗi lần dựng, nên phải nhận diện thứ gì do người thêm, ánh xạ theo `idx` chứ không theo ID, rồi ghi lại đủ bốn file cộng bản lồng trong `Timelines\`. Cần một lượt oracle riêng và một đối chứng thật; làm ẩu thì hiệu ứng rơi nhầm shot mà không ai thấy. Chỉ làm sau khi pipeline đã chạy được đầu-cuối.

## Nợ nhỏ, làm khi tiện

Sửa dòng tiêu đề bị lặp trong `docs/START-HERE.md`: dãy heading đang là 1 tới 9 nhưng số 8 xuất hiện hai lần. Gộp vào lượt rút gọn file đó. Tiêu chí xong: `python D:\IT\capcut-lab\data\tmp\tmp_20260805_quet_cat_dau.py` không còn dòng `DAY HEADING DUT QUANG`.

Số dòng mà nhánh đoán hard wrap của `tools/py_audit.py` báo lệch một nhịp so với dòng docstring thật ở vài chỗ. Ưu tiên thấp vì hard wrap chỉ là `CANH BAO`. Tiêu chí xong: số dòng báo ra trỏ đúng dòng cần sửa.

Dòng tóm tắt của **hai** file nhật ký lệch so với ô tương ứng trong `docs/research-log/INDEX.md`, `tools/rlog_index.py --backfill` báo `LECH BANG` hai lần. Tiêu chí xong: chọn một bản làm chuẩn cho từng file rồi để bảng sinh lại từ file.

`tools/docs_audit.py` bắt mảnh chuỗi định dạng trong mã Python thành đường dẫn thiếu; cân nhắc bỏ qua token có ký tự phần trăm liền trước. Nợ dòng mô tả `--brief` của `tools/v4_mold.py` đã đóng ngày 05/08/2026 bằng cách đặt câu mô tả lên dòng đầu docstring.

Khuôn sinh spec cho `tools/docs_patch.py` đã lặp nguyên si bốn lần trong phiên 05/08-2 dưới dạng script dùng một lần trong `data\tmp\`. Không đóng gói thành tool nhận tham số vì nội dung vá là văn bản nhiều dòng, nhét qua dòng lệnh còn khổ hơn; `--example` đã chữa phần rủi ro thật là người viết không nhớ khuôn. Xem lại sau vài phiên: nếu vẫn lặp thì cân nhắc một file khuôn mẫu trong `tools/` để chép đầu mỗi lượt.

Chấm lại 21 nhãn `[KIEM: chua]` bằng bằng chứng thay vì suy đoán; nhãn hiện tại do trợ lý gán từ `STATE.md` nên `chua` phần lớn nghĩa là không có bằng chứng chứ không phải chắc chắn chưa chạy. Viết một script trong `tools/` grep tên từng file `.py` trong `docs/research-log/*.md` rồi in ra script nào được nhắc ở phiên nào; chạy trên đĩa nên tốn 0 token của trợ lý và cho con trỏ bằng chứng để chấm nhanh. Tiêu chí xong: mỗi script hoặc đổi sang nhãn có bằng chứng, hoặc được xác nhận đúng là chưa ai chạy.

Tìm catalogue tài nguyên thật mà GUI CapCut bản quốc tế đang dùng. Manh mối 03/08/2026: trường `md5` trong enums **chính là tên file trong thư mục cache hiệu ứng**, thư mục cha là `resource_id` với mục tải từ CDN. Tiêu chí xong: liệt kê được danh sách mà `resource_id` trùng với `resource_id` GUI ghi vào `draft_content.json` khi thả tay.

Dòng `tham chieu La Ma` của `tools/docs_audit.py` chưa ai giải thích được. Giả thuyết "đếm theo số file" **đã bị bác**: đo 03/08/2026 cho 38 file `.md` được quét mà dòng này báo 44. Tiêu chí xong: giải thích được cách phân loại, hoặc sửa nếu là lỗi đếm.

Sáu file trong `data\tmp\` được cố ý giữ, chỉ xoá khi dự án đã hoàn thiện chứ không xoá theo lượt dọn thường kỳ: `data\tmp\gen_cc_fixture.py` là nguyên mẫu của `tools/shots_dump.py`, `data\tmp\hdr_apply.py`, `data\tmp\filters_jy.json` là bản dump catalogue filter JianYing, `data\tmp\fxsnap_fxlab01_0_root.json` cùng `data\tmp\fxsnap_fxlab01_0_nested_8ef75577.json` là bằng chứng duy nhất còn lại về project `fxlab01` đã xoá ngày 04/08, và `data\tmp\keep_audit_brief.py`. Mọi file khác không theo khuôn `tmp_<YYYYMMDD>_<nhãn>` thì xoá được.

Viết hướng dẫn dựng lại máy mới từ bản clone repo: cây ba nhánh phải tạo, biến `CAPCUT_LAB`, lấy `data\scaffold\` và `vendor\` từ đâu. `tools/data_manifest.py` đã là một nửa cơ chế.

Thống nhất giao diện tham số nhóm `scripts_v1` cũ; `clone_project.py` nhận ba tham số vị trí, gõ `--help` thì chết bằng `IndexError`.

Thử áp filter thẳng vào clip bằng CLI hoặc Python thay vì tạo segment trên track filter riêng; GUI cho phép cả hai kiểu.

Gỡ ba bản song song của danh sách mười một transition: `TRANS` trong `tools/prod_shots.py`, `TRANS` trong `tools/bench_shots.py`, và `transitions.whitelist` trong `config.example.json`. Luật ở mục 5 của `START-HERE.md` cấm chép cùng một sự thật ra hai chỗ. Tiêu chí xong: `config.json` là nguồn duy nhất, mã nhận danh sách qua tham số. Cùng lượt đó gỡ luôn `CW, CH`, `GRID_MS`, `S_LO, S_HI` khỏi thân `prod_shots.py`, gỡ `IMG_W, IMG_H = 1376.0, 768.0` đã lỗi thời khỏi `bench_shots.py`, và thống nhất ba giá trị seed đang lệch nhau 731, 20260731, 20260730.

Tách hai hàm thuần `durations()` và `kb_for()` của `tools/prod_shots.py` sang `pipeline/core/`, và tách phần gọi `ffprobe` cùng `ffmpeg` sang cổng media. Hai hàm đó chỉ nhận số trả số nên test được, nhưng hiện không import được để test vì nằm cùng file với phần chạm đĩa. Cùng nhóm: bọc thân `scripts_v1/clone_project.py` vào một hàm `clone(scaffold, drafts_dir, name)` trả về dict, giữ `if __name__ == "__main__"` để dòng lệnh cũ không đổi, vì hiện import là chạy nên adapter buộc phải phân tích stdout.

Chốt `runtime.strategy` trong `config.json`. Ba giá trị `cli | hybrid | stamp` mà hai nhánh chưa ai viết là nợ chứ không phải linh hoạt; số đo hiệu năng đã có ở `STATE.md` và kiến trúc một tiến trình CLI cho mỗi thao tác đã được giữ nguyên. Tiêu chí xong: hoặc chỉ còn `cli`, hoặc hai nhánh kia có mã thật.

Project `testB` có `materials.hsl` một mục, không project nào khác có và chưa tài liệu nào nhắc.

`tools/bench_shots.py` kiểm biên trước khi làm tròn; phải đảo thành làm tròn rồi mới kiểm và kẹp, giống `tools/bench_fixkb.py`. Ưu tiên thấp vì `tools/prod_shots.py` đã thay nó.

`tools/bgblur_frames.py` chọn `blur-max` bằng `blur == 1.0` trên số thực, chưa kiểm chứng vì lab chỉ có blur 0,75. Tiêu chí xong: so bằng sai số, hoặc chứng minh CapCut chỉ ghi bốn giá trị rời rạc.

`tools/frame_audit.py` đếm `dark20` cả khung nên không tách viền khỏi nội dung tối, đo được shot không viền vẫn 0,2570. Tiêu chí xong: chỉ đếm pixel trong dải viền dự đoán, hoặc dựng phản ví dụ thật rồi chốt ngưỡng.

Xoá `data\archive\`, khoảng 60–70 MB rác, sau khi chắc chắn `D:\Test_tool` đã bỏ.

`data\Test_tool_v3\shots.csv` **trên máy lab**, ngoài repo, có 8 dòng theo lược đồ cũ `file,start,end` nên thiếu sáu cột của lược đồ hiện hành. Xoá hoặc điền lại khi `tools/shots_dump.py` chốt xong.

Điều kiện bật blur trong `tools/prod_shots.py` là `kx*smin < 1 or ky*smin < 1`, mà `S_HI` bằng 0,92 còn `kx` và `ky` không bao giờ vượt 1, nên vế trái luôn đúng và cột `blur` bằng 3 ở mọi shot. Hoặc thừa nhận blur luôn bật rồi bỏ điều kiện, hoặc đặt một ngưỡng thật. Suy luận từ mã, **chưa kiểm chứng**.

`vendor` **trên máy lab** chứa năm thư mục con mà mục 3 của `START-HERE.md` không kể tới: `frames`, `Test_tool_v3`, `snapshots`, `testV3_CLEAN`, `scripts`; gốc còn có `enums_backup.json` trùng bản với `reference/enums_backup.json`. Từ 02/08/2026 `tools/data_manifest.py` ghi đủ vào khối `vendor_extra`, khối này không tham gia phán xử mã thoát. Tiêu chí xong: khối `vendor_extra` chỉ còn thứ ta cố ý chấp nhận, và mục 3 kể đúng những gì có thật trên đĩa.

## Chờ máy render quay lại

Nghiệm thu KX và KY. Dựng lại `prod60` bằng `tools/prod_shots.py` mới rồi trích khung ở giữa mười shot có tỉ lệ ảnh khác nhau, **bắt buộc có ít nhất hai ảnh cao hơn khung 16:9**, vì nhánh ảnh cao trong `reference.md` mục 3.1 chưa có phép đo oracle nào. Tiêu chí xong: không shot nào hở mép ngoài ý muốn.

Đối chiếu CSV với JSON cho `prod60` bằng `tools/shots_crosscheck.py`, chạy **trên máy render** vì cả draft lẫn bảng shot chỉ có ở đó. Đọc năm dòng đầu báo cáo trước, nếu tên ảnh shot 1 lệch thì dừng ngay vì đang so nhầm cặp. Tiêu chí xong: mã thoát 0 kèm dòng SACH, 0 lech tren ca nam truong. Mã thoát 2 báo thiếu cột `kb_s0` và `kb_s1` **không** tính là đạt; gặp ca đó thì sinh lại bảng bằng `tools/prod_shots.py`.

Kiểm thị giác bản export `prod60` theo quy tắc in ground truth trước khi nhìn, ở `failures.md` mục 1.

Đo độ nới thực tế của segment audio trên `prod60`; lý thuyết dự đoán +10,5 ms, **chưa kiểm chứng**.

Kéo về máy lab hai thứ không tái tạo được: file `narration59.mp3` và thư mục 326 ảnh gốc ở `D:\IT\capcut-help\Picture`.

Nghiệm thu `tools/data_manifest.py` giữa hai máy. Trên máy render chạy `--scan --machine render` rồi commit bản kê, sau đó `--compare --mine manifests/lab.json --theirs manifests/render.json`. Tiêu chí xong: báo cáo in đúng danh sách hai máy thiếu của nhau; mã thoát 0 hoặc 2 đều được miễn mọi dòng lệch giải thích được. Khối `vendor_extra` lệch nhiều là bình thường; chỉ `data` và `vendor_canonical` mới đáng xử lý.

## Nợ ghi thêm cuối phiên 06/08-1

Rà trùng khối này với mục Ưu tiên 0 rồi gộp làm một, vì nó viết lúc cuối phiên khi không còn nguyên văn file trong ngữ cảnh nên có thể chép lại thứ đã có.

Hạ trần `docs/TODO.md` trong `PER_FILE_BUDGET` của `tools/docs_audit.py` về lại 25 KB sau khi rút gọn file này; trần 30 KB hiện hành là nới tạm ngày 06/08/2026 để chèn mục Ưu tiên 0. Tiêu chí xong: trần về 25 KB và `python tools/docs_audit.py --brief` vẫn thoát 0.

Thêm `docs/conventions.md` vào bản đồ tài liệu ở mục 5 của `docs/START-HERE.md`, ghi rõ nó bắt buộc với AI điều phối và không nằm trong thứ tự đọc của AI thực thi. Gộp vào lượt viết lại mục 8. Tiêu chí xong: bản đồ liệt kê đủ mọi file trong `docs/`.

Ba chỗ trong mục 8 của `docs/START-HERE.md` đang nói ngược với thứ có thật trên đĩa, sửa cùng lượt viết lại: ba ngưỡng dòng của `tools/read_src.py`, câu nói `docs/TODO.md` chật hơn trần mặc định trong khi nó đang rộng hơn, và dòng tiêu đề mục 8 lặp hai lần liên tiếp.
