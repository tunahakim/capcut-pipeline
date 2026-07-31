# Procedures — quy trình

## 1. Quy trình dựng một video

Thứ tự bắt buộc. Đảo thứ tự sẽ mất dữ liệu.

**Bước 0.** Kiểm `Get-Process *CapCut*` phải rỗng. Kiểm dung lượng ổ chứa thư mục draft.

**Bước 1.** Tạo project mới bằng clone:
```
python scripts_v1/clone_project.py "<scaffold_CLEAN>" "<drafts-dir>" "<ten_project_moi>"
```
Vì `draft_name` trùng tên thư mục nên không còn bẫy đổi tên.

**Bước 2.** Chuẩn bị `shots.csv` từ bảng metadata: **nối liền các khoảng hở** — mỗi shot chạy tới đúng lúc shot sau bắt đầu, shot đầu bắt đầu từ 0, shot cuối kết thúc bằng độ dài audio đo bằng `ffprobe`. Lý do nối liền: khoảng hở thành khung đen, và transition chỉ đo được ý nghĩa khi hai segment kề sát nhau.

**Bước 3.** Chạy **toàn bộ** lệnh ghi của CLI trong một khối: `add-video`, `add-audio`, `bg-blur`, `transition`, `image-anim`, `add-effect`, `import-srt`, `add-sfx`. **Không dùng `add-filter`.**

**Bước 4.** Lấy ID segment thật bằng `capcut segments <project> --track video -H`. ID sinh ngẫu nhiên mỗi lần, không tái dùng được từ project khác.

**Bước 5.** `capcut lint <project> -H` phải sạch.

**Bước 6.** Chạy lớp Python: `python scripts_v1/kb_apply.py <project>`. **Sau bước này tuyệt đối không chạy thêm lệnh ghi nào của CLI.**

**Bước 7.** `python scripts_v1/check_sync.py <project> before` — dòng `4 FILE GIONG NHAU` phải là `CO`.

**Bước 8.** Mở CapCut, xem preview, chỉnh tay chỗ cần nhấn, đóng bằng **nút X**, đợi mười giây.

**Bước 9 — KIỂM KÊ TÀI NGUYÊN, bắt buộc:** `python scripts_v1/fx_audit.py <project>`. Mọi dòng phải báo `OK`. Dòng nào báo `PLACEHOLDER`, `RONG` hoặc `PATH SAI` là tài nguyên chết. Bước này đứng **trước** đo timing và kiểm Pro, vì nếu phải thay tài nguyên thì mọi phép đo sau đó phải làm lại.

**Bước 10.** Đo timing: `check_sync.py <project> after` rồi `diff_timing.py before after`. Tiêu chí: lệch lớn nhất dưới 33,3 ms **và không tích luỹ**.

**Bước 11 — KIỂM KHOÁ PRO.** Mở CapCut, bấm Export. Nếu hiện hộp thoại Pro thì đọc danh sách, bấm **Back to edit**, thay tài nguyên, làm lại từ Bước 3.

**Bước 12 — Export.** 1920×1080, 30 fps, H.264, bitrate Recommended, không bật tuỳ chọn nâng cao. Không có đường CLI. Video 60 phút thì cân nhắc chọn vùng In/Out để kiểm thử trước.

**Bước 13 — Kiểm chứng đầu ra.** `grab_frames.py` với mốc thời gian sửa cho khớp bảng shot, và `tr_profile3.py` nếu có transition cần xác nhận. So với bộ khung hình vàng của lần dựng trước.

## 2. Probe parity — bắt buộc trước khi tin một máy mới

```
1. python scripts_v1/clone_project.py "<scaffold_CLEAN>" "<drafts-dir>" paritytest
2. python scripts_v1/parity_build.py <project>
3. python scripts_v1/kb_apply.py <project>
4. python scripts_v1/check_sync.py <project> parity_before
5. Mo CapCut, doi timeline hien day du, dong bang nut X, doi 10 giay
6. python scripts_v1/fx_audit.py <project>       -> moi dong phai OK
7. python scripts_v1/check_sync.py <project> parity_after
8. python scripts_v1/diff_timing.py parity_before parity_after
9. So parity_before va parity_after voi fixtures/parity-gold/
```

Tiêu chí pass, xem `reference.md` mục 11. Nhắc lại: so *trước với trước* và *sau với sau* giữa hai máy phải **0,0 ms tuyệt đối**; tiêu chí "dưới một frame" chỉ dùng cho *trước với sau trên cùng máy*.

**md5 của khung hình SẼ khác giữa hai máy** vì encoder không tất định. Chỉ so màu trung bình RGB, đừng so md5.

## 3. Dựng máy mới

Cài **CapCut từ vendor kit hoặc từ URL CDN**, không tải từ capcut.com — file trên trang chủ là stub và sẽ kéo về bản mới nhất. Đối chiếu SHA256. Ngay sau khi cài, chặn hai file updater **trước khi mở CapCut lần đầu**.

Chép `Cache_effect\` nếu có; nếu máy có mạng thì transition, animation và scene effect tự tải được, chỉ filter là bắt buộc cache-first.

Cài Python **bản python.org, không dùng bản Microsoft Store**. Cài Node.js, `npm i -g capcut-cli@0.15.0` ghim đúng phiên bản. Cài ffmpeg bằng `winget install Gyan.FFmpeg`.

`git clone` repo. Đặt `CAPCUT_LAB`, hoặc bỏ qua nếu giữ bố cục ba nhánh — script tự dẫn xuất từ vị trí file.

**Tạo scaffold mới bằng GUI trên chính máy đó**, không chép từ máy khác nếu tên user Windows khác nhau. New Project, mở lại lần nữa rồi đóng, xác nhận tên thư mục trùng `draft_name`, copy nguyên thư mục ra `scaffold_CLEAN`.

Chạy probe parity trước khi tin máy mới.

**Mở cửa sổ PowerShell mới sau mỗi lần cài phần mềm** — cửa sổ cũ giữ PATH cũ.

## 4. Phương pháp oracle

**Nguyên tắc: để chính CapCut ghi ra đáp án, rồi đọc ngược file.** Thay vì đoán cấu trúc JSON rồi thử-sai, làm thao tác đó bằng tay trong giao diện, đóng CapCut, rồi đọc file xem nó ghi gì.

Tạo project mới hoàn toàn sạch — không dùng lại project đã bị chỉnh tay, vì khi đó mọi thứ đọc ra đều kèm câu hỏi "cái này do ai ghi".

Gộp **tất cả** câu hỏi chưa biết vào **một** phiên GUI, mỗi shot gánh một câu hỏi, chừa ít nhất hai shot làm đối chứng. Trong phiên đó tuyệt đối không kéo clip, không cắt, không xoá, không kéo mép clip — chỉ chỉnh thông số trong panel phải và thả hiệu ứng.

Đóng bằng nút X, đợi mười giây, đọc ngược bằng `tools/oracle_read.py`.

**Kiểm chứng chiều ngược lại:** dùng Python ghi cấu trúc vừa học lên một shot đối chứng còn trắng, mở CapCut xem có giống shot do GUI tạo không. Chỉ khi phép A/B này pass mới coi là đã giải quyết.

**Biến thể tốt hơn — oracle song song:** để CLI và GUI cùng tạo hai đối tượng cùng loại **trong cùng một project**, rồi diff từng trường (`tools/v4_mold.py`). Loại bỏ hoàn toàn nhiễu do khác project, khác thời điểm. Điều kiện: **không xoá đối tượng hỏng của CLI trước khi diff** — đây là lỗi rất dễ mắc vì bản năng đầu tiên khi thấy thứ gì hỏng là dọn nó đi.

## 5. Đo đầu ra bằng số

**md5 khung** trả lời "hai khung có giống hệt nhau không". Vô dụng khi mọi segment đều có chuyển động.

**Màu trung bình RGB** (thu nhỏ khung về 1×1) trả lời về ám màu, khung đen, fade.

**Biến động giữa các khung liên tiếp trên lưới 32×32** là cách mạnh nhất, bắt được cả biến đổi hình học mà màu trung bình không đổi. Bắt buộc có **cửa sổ đối chứng nằm giữa shot** để lấy mốc nền, và đọc riêng phía trái với phía phải ranh giới. Ken Burns thuần cho mốc nền 0,30–0,39; transition thật vọt lên 45–68.

Đọc cả cửa sổ bằng **một** lệnh ffmpeg với `-ss` cộng `-t` thay vì tua nhiều lần.

## 6. CHECKLIST MÁY RENDER — phiên 30/07/2026

**Trạng thái: đã chạy xong ngày 31/07/2026, cả ba giai đoạn đều đạt.** Parity 0,0 ms tuyệt đối, bài tải 300 shot đạt. Giữ checklist này làm quy trình cho máy tiếp theo. Hai số còn thiếu: thời gian CapCut vẽ xong timeline 300 shot và RAM đỉnh. Và **updater trên máy render vẫn chưa bị chặn** — phải làm trước phép đo nghiêm túc lần sau.

Hai mục tiêu: xác nhận code chạy trên máy đó đúng như máy hiện tại với project 2 phút 48; xác nhận CapCut mở nổi project 60 phút vài trăm ảnh (chưa render).

### Giai đoạn 1 — cài đặt, khoảng 40 phút

Bắt đầu tải bộ cài CapCut **ngay lập tức** để nó chạy song song với các việc khác:
```
winget download ByteDance.CapCut --version 9.1.0.3879 -d C:\kit
```
Hoặc `curl.exe -L -o C:\kit\capcut.exe "<URL trong reference.md muc 14>"` rồi `Get-FileHash -Algorithm SHA256`.

Trong lúc chờ: cài Python từ python.org, Node.js, `winget install Gyan.FFmpeg`, rồi **mở cửa sổ PowerShell mới**, rồi `npm i -g capcut-cli@0.15.0`. Kiểm bằng `capcut describe` — đừng dùng `capcut version`.

`git clone <repo>` vào `D:\IT\capcut-lab\capcut-pipeline` (hoặc ổ tương đương), tạo `D:\IT\capcut-lab\data`.

Cài CapCut: `capcut.exe /silent_install=1 /install_path="C:\CapCut910"`. **Chặn updater trước khi mở lần đầu:** tìm `%LOCALAPPDATA%\CapCut\Apps\9.1.0.3879\`, đổi tên `CapCut-DiffUpgrade.exe` và `hpatchz.exe` thành `.disabled`. `winget pin add ByteDance.CapCut --version 9.1.0.3879`.

Mở CapCut, đăng nhập, tắt auto-update trong Settings. Bấm New Project đặt tên `scaffoldbase`, đóng, **mở lại lần nữa rồi đóng**, rồi copy thư mục đó ra `D:\IT\capcut-lab\data\scaffold\scaffold_CLEAN`.

### Giai đoạn 2 — probe parity, khoảng 15 phút

Chép media test vào `data\Test_tool_v3\` — tám ảnh PNG, `audio.mp3`, `video1.srt`. Bộ này **không có trong repo**, lấy từ `vendor\Test_tool_v3\` hoặc chép tay từ máy phát triển. Rồi chép `fixtures/parity-gold/*` từ repo vào `data\snapshots\`.

Chạy đúng chín bước ở mục 2 phía trên. Đây là **cửa ải**: nếu bảng timing không khớp mốc vàng thì dừng lại, mọi số đo sau đó vô nghĩa.

Nếu parity pass và còn thời gian: mở CapCut, bấm Export, bấm giờ. Con số này cho tỉ lệ để ngoại suy ra 60 phút.

### Giai đoạn 3 — thử tải project 300 shot

Cần một script chưa có. Ghi `tools/bulk_build.py` bằng nội dung dưới đây. **Script này CHƯA CHẠY LẦN NÀO — coi là chưa kiểm chứng, và chạy thử với `--n 10` trước khi chạy 300.**

```python
#!/usr/bin/env python3
"""
bulk_build.py  <project-dir> --src <thu-muc-anh> [--n 300] [--dur 12]
Dung N shot tu cac anh co san trong <thu-muc-anh>, lap lai vong tron.
KHONG them audio: phep thu nay chi do kha nang MO project, khong do render.
CHUA KIEM CHUNG - chay thu voi --n 10 truoc.
"""
import argparse, pathlib, subprocess, sys, time

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--src", required=True)
ap.add_argument("--n", type=int, default=300)
ap.add_argument("--dur", type=float, default=12.0)
a = ap.parse_args()

imgs = sorted(p for p in pathlib.Path(a.src).iterdir()
              if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
if not imgs:
    sys.exit("Khong thay anh nao trong %s" % a.src)
print("co %d anh nguon, dung %d shot moi shot %.2fs -> tong %.1f phut"
      % (len(imgs), a.n, a.dur, a.n * a.dur / 60))

t0 = time.time()
times = []
for i in range(a.n):
    img = imgs[i % len(imgs)]
    st = i * a.dur
    t1 = time.time()
    r = subprocess.run(["capcut", "add-video", a.project, str(img),
                        "%.3fs" % st, "%.3fs" % a.dur, "-q"],
                       shell=True, capture_output=True)
    dt = time.time() - t1
    times.append(dt)
    if r.returncode != 0:
        print("LOI o shot %d: %s" % (i + 1, r.stderr.decode("utf-8", "replace")[:300]))
        sys.exit(1)
    if (i + 1) % 25 == 0 or i == 0:
        print("  shot %4d  lenh nay %.2fs  trung binh %.2fs  da troi %.1f phut"
              % (i + 1, dt, sum(times) / len(times), (time.time() - t0) / 60))

print()
print("XONG %d shot trong %.1f phut" % (a.n, (time.time() - t0) / 60))
print("lenh dau %.2fs | lenh cuoi %.2fs | trung binh %.2fs"
      % (times[0], times[-1], sum(times) / len(times)))
print("-> lenh cuoi cham hon lenh dau %.1f lan (phan bac hai)"
      % (times[-1] / times[0] if times[0] else 0))
```

Ghi nó bằng heredoc `@'...'@` cộng `WriteAllText` như quy tắc ở `failures.md` mục 4.

Chạy:
```
python scripts_v1/clone_project.py "<scaffold_CLEAN>" "<drafts-dir>" bigtest
python tools/bulk_build.py "<drafts-dir>\bigtest" --src "<data>\Test_tool_v3" --n 10
python tools/bulk_build.py "<drafts-dir>\bigtest" --src "<data>\Test_tool_v3" --n 300
python scripts_v1/kb_apply.py "<drafts-dir>\bigtest"
```

`kb_apply.py` có `PLAN` cứng cho 8 shot nên nó **chỉ áp cho 8 shot đầu** — đủ để test tải project. Nếu muốn đủ 300 thì sửa `PLAN` thành vòng lặp modulo, nhưng không cần cho phép thử này.

Rồi mở CapCut và ghi lại: mất bao lâu để timeline hiển thị xong, kéo thanh thời gian có mượt không, preview có chạy được không, RAM chiếm bao nhiêu (Task Manager), và `draft_content.json` nặng bao nhiêu MB.

**Cảnh báo dung lượng:** 300 shot × khoảng 900 KB ảnh = 270 MB copy vào `assets\video\` của project, trên ổ chứa thư mục draft. Kiểm chỗ trống trước.

**Ghi lại mọi con số ngay khi đo được** — đó là output quan trọng nhất của phiên máy render, và nó sẽ đi vào `research-log.md`.

---