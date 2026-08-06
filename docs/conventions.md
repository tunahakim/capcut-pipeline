# Quy ước viết tool và vá tài liệu

**Cập nhật 06/08/2026.** File này giữ những luật kỹ thuật lặp lại ở mọi phiên, tách khỏi mục 8 của `docs/START-HERE.md` vì mục đó đã chạm trần kích thước và vì các luật này còn dài ra theo thời gian trong khi mục 8 phải giữ được vai trò điều hướng. Không nằm trong thứ tự đọc bắt buộc; đọc ngay trước lúc viết tool mới hoặc vá tài liệu.

## 1. Luật ngôn ngữ khi in ra console

Mọi câu văn xuôi in ra console phải là **tiếng Việt có dấu**. Nhãn trần như `DAT`, `LAN 0`, `SACH`, `VAN DE (0)` là chưa đủ: người đọc console không được phép phải mở mã nguồn mới hiểu tool vừa phán gì. Mỗi dòng kết luận phải kèm một câu có dấu nói rõ **mong đợi gì và thực tế ra sao**.

Bốn nhóm dưới đây **giữ ASCII tuyệt đối**, vì chúng là dữ liệu chứ không phải câu chữ.

Nhóm thứ nhất, khoá và giá trị máy đọc: khoá JSON `name`, `op`, `start`, `end`, `expect_bytes`, `end_mode`, `content_file`, `ngay_cap`, `het_han`, `ly_do`; hai giá trị `giu` và `gom` được kiểm bằng `END_MODES`; tên tám op; và các chuỗi trạng thái mà `tools/docs_audit.py` trả về rồi `tools/docs_patch.py` so bằng toán tử bằng, gồm `SAI CHO`, `MISSING`, `MULTI`, `OK-BASENAME`, `CON HAN`, `QUA HAN`. Đổi bất kỳ cái nào là hỏng logic ngay chứ không phải hỏng hiển thị.

Nhóm thứ hai, nhãn đầu dòng và dòng phán quyết mà tool khác grep: `=== KIEM TRUOC: SACH ===`, `=== DA GHI n FILE, KIEM SAU SACH ===`, `=== KIEM SAU THAT BAI ===`, `=== LOI (n) ===`, `=== PROBE: n muc, m muc hong ===`, `KET QUA: n/n ca dat`, cùng các nhãn `ANCHOR`, `VUNG THAY`, `KIEM SAU`, `CANH BAO`, `GHI CHU`, `MIEN TRU`, `VUOT TRAN`, `KHONG KHOP`, `OK`, `THAT BAI`. Giữ nguyên, chỉ thêm câu có dấu vào phần văn xuôi phía sau.

Nhóm thứ ba, một ca đặc biệt: chuỗi `thuc=` trông như chữ thiếu dấu nhưng thực chất là khoá máy đọc, vì hàm `lay_so()` tìm đúng chuỗi đó rồi đọc con số đằng sau để ca `do-vung-mot-duong` đối chiếu probe với apply. Giữ nó ASCII, và để `dự kiến=` cùng `biên độ=` có dấu bên cạnh.

Nhóm thứ tư, marker của selftest: mỗi marker là một mẩu văn xuôi cắt ra từ chuỗi `print`, nên thêm dấu vào chuỗi mà quên marker sẽ làm ca đó chuyển thành `THAT BAI`. Phải đổi **đồng bộ cả cặp** trong cùng một lượt.

Không lo lệch cột khi thêm dấu: `%-22s` của Python đệm theo ký tự chứ không theo byte, mà chữ Việt dựng sẵn là một ký tự.

Luật này áp cho **code mới và code đang sửa vì lý do khác**, không quét lại toàn repo. Lưới lọc thủ công liệt kê mọi dòng `print` còn thuần ASCII đã dùng đúng một lần ngày 06/08/2026 rồi bỏ, vì sau khi file đã sạch thì gần như mọi dòng nó in ra đều là nhãn máy đọc hợp lệ, tỷ lệ nhiễu trên tín hiệu quá cao nên sớm muộn sẽ bị lướt qua. Chỉ dựng lại nó nếu lọt lỗi loại này lần thứ hai, và khi đó dựng thành một nhánh kiểm trong `tools/py_audit.py` chứ không phải một khối lệnh rời.

## 2. Luật mã thoát

Mọi tool tự chạy được, tức có khối `__main__`, phải in ngay trước khi thoát một dòng dạng `MA THOAT <n> -- <câu tiếng Việt có dấu>` nói mã đó nghĩa là gì và người dùng cần làm gì tiếp. Token `MA THOAT` và con số giữ ASCII để tool khác grep và để `tools/session_open.py` so khớp nguyên văn; phần diễn giải bắt buộc có dấu. Docstring đầu file phải liệt kê đủ bảng mã thoát.

Script gọi script khác, gồm `tools/session_open.py` và mọi khối PowerShell trong hướng dẫn, **không được in trần** `$LASTEXITCODE`. Phải in kèm diễn giải, ưu tiên chuyển tiếp nguyên dòng `MA THOAT` của tool con.

Áp cho code mới và code đang sửa vì lý do khác, không quét lại toàn repo.

## 3. Luật không ngầm định

Mọi cờ mới phải khai **phạm vi tường minh**. Gọi trống thì in cách dùng rồi thoát khác 0, không tự đoán rằng người dùng muốn chạy trên tất cả. Muốn tất cả thì gõ `--all`.

## 4. Luật vá tài liệu bằng tools/docs_patch.py

Bốn luật dưới đây rút ra sau tám lượt vá liên tiếp.

Neo phải do **script trích thẳng từ file trên đĩa**, không gõ tay từ hội thoại. Khi tiền tố có dấu thì định vị bằng một chuỗi ASCII duy nhất nằm trong dòng đó, rồi lấy trọn dòng từ đĩa làm neo.

Chọn op theo cỡ việc: đoạn dài dùng `replace_between` với hai neo ngắn và duy nhất chứ đừng dán cả đoạn cũ làm neo; xoá một mục dùng `delete_block`; file mới dùng `create` với `content_file`.

Spec nhiều edit trên cùng một file phải **xếp edit dùng neo chạy trước edit xoá neo**, và đặt edit xoá trước edit chèn khi phần chèn có thể tạo ra bản sao của một neo sắp dùng.

Script sinh spec phải **so số edit sinh được với số mong đợi**, rồi thoát mã 1 mà không ghi spec nào nếu thiếu.

Về `end_mode` của `replace_between`: mặc định là `giu`, tức vùng bị thay gồm neo đầu và dừng ngay **trước** neo cuối, nên `new` không được chép lại neo cuối, chép vào thì neo cuối lặp hai lần. Đặt `end_mode` bằng `gom` để nuốt luôn neo cuối như bản trước ngày 06/08/2026, khi đó `new` phải chép lại neo cuối nếu còn muốn giữ nó. Mặc định đảo chiều vì một spec quên chép `end` vào `new` đã xoá mất ba đoạn của `docs/STATE.md` mà không ai thấy: thừa thì dễ sửa, mất thì khoai.

## 5. Luật chống quên sau khi fetch

Kết quả `crawler` bị cắt khỏi ngữ cảnh của trợ lý sau một hai lượt, trong khi nội dung người dùng dán thẳng vào hội thoại thì giữ nguyên văn suốt phiên. Vì vậy: không trích dẫn, không kết luận, không viện dẫn nội dung một file đã fetch ở lượt trước; hoặc xin dán lại, hoặc nói thẳng là không còn nguyên văn. Cảm giác nhớ được không phải bằng chứng. Fetch chỉ dành cho thứ dùng xong ngay trong lượt đó. Cơ chế đầy đủ ở `docs/ai-reading-channel.md`.