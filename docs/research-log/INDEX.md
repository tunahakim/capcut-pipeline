# Nhật ký nghiên cứu — mục lục

Mỗi phiên làm việc một file, tên theo quy ước `<ngày>-<số thứ tự phiên trong ngày>-<nhãn ngắn>.md`, mới nhất lên đầu. Nhật ký gộp chung trước đây đã được tách vào thư mục này ngày 01/08/2026 và không còn tồn tại; nội dung không mất chữ nào, chỉ đổi chỗ.

| Phiên | File | Nội dung chính |
|---|---|---|
| 02/08 tối | `2026-08-02-3-filter-gui-vip.md` | Ba luật làm việc mới vào mục 8 của START-HERE: sinh file mới bằng script, ngưỡng 4 KB giữa fetch trọn và trích dòng, đặt tên `tmp_` cho file dùng một lần. Dựng `fxprobe01` từ scaffold rỗng cộng ba ảnh test rồi thả tay hai filter từ GUI, gỡ chặn khuôn filter. Đo được: filter trong GUI CapCut quốc tế là namespace khác hẳn 468 mục JianYing, `resource_id` không trùng và cờ `is_vip` không dự đoán được vương miện, nên mục kiểm khoá Pro mất đối chứng dương và chuyển sang trạng thái chặn vì phương pháp. Filter nằm ở bucket `materials.effects` chứ không phải `filters`. Bảy dương tính giả CRLF chứ không phải sáu |
| 02/08 chiều | `2026-08-02-2-no-nho-va-filter.md` | Trả năm món nợ nhỏ thuần code: `oracle_read.py` bỏ mặc định `D:\Test_tool` và chỉ in cột delta khi có `--baseline`; `bgblur_diag.py` nhận nhiều project, `bgblur_frames.py` và `frame_audit.py` chuyển sang `--project` cùng `--mp4`, báo cáo gắn tên project; `docs_audit.py` bỏ điều kiện cứng loại trừ README; dời `scan_paths.py`. TODO từ 95 xuống 83,6 phần trăm trần. Đo cờ `is_vip` của 468 filter JianYing: 300 VIP, 168 free. Sáu dương tính giả CRLF chứ không phải ba. Chốt hai kỹ thuật làm việc: trích dòng thay vì đọc trọn file, và vá file bằng script kiểm-khớp-trước-ghi-sau |
| 02/08 khuya | `2026-08-02-1-data-manifest.md` | Viết `data_manifest.py` kiểm kê `data\` và `vendor\`, vendor chia hai khối canonical và extra; sinh `manifests/lab.json`; tự kiểm đủ ba mã thoát bằng đối chứng dương, đối chứng âm và ca thiếu file; đo lại thời gian hash khi cache lạnh và cache nóng; xoá Ưu tiên 1 khỏi `../TODO.md` |
| 01/08 khuya | `2026-08-01-4-readme-cua-vao.md` | README viết lại thành cửa vào, đưa vào bản đồ và thứ tự đọc của START-HERE, thêm luật khai báo lỗ hổng đọc; ghi nhận hai lớp cắt nội dung của công cụ fetch; đo quy mô `data\` và `vendor\` trên máy lab chuẩn bị cho `tools/data_manifest.py` |
| 01/08 tối | `2026-08-01-3-crosscheck-cli.md` | `shots_crosscheck.py` bắt buộc `--project` và `--csv`, bỏ tự dò, thêm đầu báo cáo và hợp đồng mã thoát, bịt lỗi im lặng cột `kb`; tự kiểm ba bộ trên `testV3` khớp dự đoán; gộp `fix_fold_path.py` vào `clone_project.py` |
| 01/08 chiều | `2026-08-01-2-kxky.md` | Tổng quát hoá hình học sang KX và KY theo từng ảnh; `prod_shots.py` ghi hai cột mới, `kb_apply.py` có `GEO`, `bench_kb.py` nạp từ CSV; tự kiểm 25600 điểm trên dữ liệu tổng hợp; nghiệm thu thị giác chờ máy render |
| 01/08 sáng | `2026-08-01-1-docs-headers.md` | Docstring cho 15 script còn thiếu, chốt luật mô tả sinh tự động từ docstring, `scripts.md` tự sinh bằng `tools/scripts_index.py --write`, dời `split_research_log.py` vào kho lưu trữ, viết `artifacts/README.md` |
| 31/07 đêm | `2026-07-31-5-prod60.md` | Bài sản xuất thật 60 phút có narration. 902 lệnh CLI trong 5,5 phút, lệch 0,0 ms trên 300 shot, export 4,07 GB trong 6 phút. Đính chính con số 20 phút. Phát hiện `shots_crosscheck.py` đối chiếu nhầm project. Hạn chế KY dùng chung cho mọi ảnh |
| 31/07 tối muộn | `2026-07-31-4-reh10-audio.md` | Tổng duyệt 10 shot có narration. Shot video lệch 0,0 ms, segment audio bị nới +8,5 ms ở mốc cuối, đuôi cố ý hấp thụ trọn |
| 31/07 tối | `2026-07-31-3-bgblur-timing.md` | Đóng ca lỗi im lặng thứ bảy: `bg-blur` không hỏng, quan sát ban đầu sai. Chốt luật bắt lưới 0,1 giây theo ranh giới tuyệt đối, mốc cuối dùng ceil, cộng đuôi cố ý |
| 31/07 chiều | `2026-07-31-2-benchmark-render.md` | Benchmark máy render: dựng 300 shot đủ hiệu ứng, lệch 0,0 ms, export 60 phút thành công |
| 31/07 sáng | `2026-07-31-1-parity-300shot.md` | Parity hai máy đạt 0,0 ms tuyệt đối, bài tải 300 shot, đóng Việc A về kiến trúc lớp ghi |
| 30/07 | `2026-07-30-1-refactor.md` | Di trú sang cây ba nhánh, tạo bộ tài liệu, đưa tài liệu nháp cũ ra khỏi repo |
| 29/07 (v7) | `2026-07-29-3-v7.md` | Chuẩn hoá `CAPCUT_LAB`, đóng vendor kit, chặn updater, dựng mốc vàng parity |
| 29/07 (v6) | `2026-07-29-2-v6.md` | Export MP4 thật lần đầu, chặn bởi khoá Pro, đo từng khung, `cube` ra cắt cứng |
| 29/07 (v5) | `2026-07-29-1-v5.md` | Lớp filter bằng Python, quy tắc cache-first, bỏ hẳn `add-filter` |
| 28/07 | `2026-07-28-1-mo-dau.md` | Quyết định giữ CapCut, hệ toạ độ NDC, công thức lề, ba lỗi im lặng đầu tiên |

Bốn file của ngày 28 và 29/07 vốn là phụ lục E1 tới E4 chép sang từ `../legacy/v0.8-full.md`, chưa được viết lại, nên văn phong khác các phiên sau.

Số liệu trong nhật ký là số **tại thời điểm phiên đó**. Khi một con số bị đính chính ở phiên sau, phiên cũ được thêm một đoạn "Đính chính" trỏ tới phiên đã sửa, chứ không sửa lặng lẽ. Nguồn số hiện hành luôn là `../reference.md` và `../STATE.md`.