# Phiên 05/08-3 — cứu ba vết cắt của STATE.md và đóng nhóm 42 lỗi mã hoá

**Tóm tắt:** Truy nguyên và vá ba đoạn bị lượt vá kết phiên trước xoá mất khỏi `docs/STATE.md`, rồi đóng nhóm 42 script thiếu `sys.stdout.reconfigure` bằng một spec sinh tự động.

**Phiên:** 16:00 chiều

## Việc đã đóng

Ba vết cắt trên `docs/STATE.md`. Người dùng hỏi đúng câu quyết định: nếu tool khớp nhầm thì mọi file khác cũng bị ảnh hưởng, nên phải biết nguyên nhân chứ không chỉ vá. Ba phép kiểm độc lập cùng trả lời: `git show --stat a186383` cho thấy commit đó chỉ chạm hai file; một script quét toàn repo bằng ba dấu hiệu là dòng bắt đầu bằng khoảng trắng, ba dòng trống liên tiếp và dãy heading đứt quãng không tìm thấy nạn nhân nào khác cùng kiểu; và `git show 5e1f9e1` cho nguyên văn phần mất. Nguyên nhân là spec dùng `replace_between` với neo `end` là dòng mở đầu đoạn kế tiếp rồi quên chép `end` vào `new`, còn `tol_bytes` mặc định che trọn 36 và 50 byte hụt. Tool chạy đúng đặc tả; người viết spec sai. Phép quét bắt thêm một vết khác loại ở `docs/START-HERE.md` là dòng tiêu đề mục 8 bị lặp.

Bài học phương pháp lặp lại lần thứ hai trong ngày: một neo tôi gõ tay từ output đã sai đúng một ký tự có dấu, `\u1eb1n` thay vì `\u1eb3n`, và probe báo khớp 0 lần. Từ đó mọi neo đều do script trích thẳng từ file trên đĩa chứ không gõ lại, và cả ba lượt vá sau đó đều khớp một lần ngay từ lần probe đầu.

Nhóm 42 script thiếu `sys.stdout.reconfigure`. Một script trong `data\tmp\` phân tích cây cú pháp tìm dòng import cuối cùng ở mức ngoài cùng của mỗi file, kiểm dòng đó khớp đúng một lần, tự thêm `import sys` cho ba file chưa có, rồi sinh spec 42 edit cho `tools/docs_patch.py`. Probe sạch 42 trên 42, apply ghi 42 file một lượt và thêm 213 dòng. Đối chứng sau khi sửa là chạy lại `tools/docs_audit.py`, `tools/rlog_index.py` và `tools/nl_audit.py`, cả ba trùng khít lượt trước.

`tools/py_audit.py` có `--exclude` nhận tiền tố lặp lại được, mặc định bỏ qua `_deprecated/`, và `--tat-ca` để quét cả thư mục bị loại. Nhờ vậy con số 136 tách ra thành 41 lỗi của script đã chết và 95 lỗi là nợ thật, tức lần đầu biết nợ to bằng nào.

Đối chứng nhánh đoán hard wrap trước khi tin nó, theo đúng yêu cầu của người dùng là đừng sửa mò. In độ dài từng dòng docstring của hai file bị báo: dãy dòng đều 71 tới 85 ký tự rồi rơi xuống dòng cụt là hard wrap thật, còn đoạn tiếng Việt thêm gần đây là một dòng liền 243 tới 403 ký tự. Phép đoán đúng, giữ nguyên.

`tools/docstring_dump.py` mới, để phiên sau lấy nguyên liệu docstring bằng một dòng lệnh thay vì dán tay 32 file vào hội thoại.

## Việc chưa đóng

Hai nhóm còn lại của món nợ mã hoá, 21 chỗ `subprocess` và 32 docstring, ghi ở `docs/TODO.md`. Ba mục khác của phiên là `end_mode`, sửa `tools/repo_bytecheck.py` nuốt lỗi 403, và rút gọn `docs/START-HERE.md` đều chưa động tới; miễn trừ trần của file đó còn hạn tới 12/08/2026 nên chưa chặn cổng.
