# Nhật ký phiên 02/08/2026 (3) — filter thả tay từ GUI, và cờ VIP của JianYing hoá ra không dùng được

**Tóm tắt:** Ba luật làm việc mới vào mục 8 của START-HERE: sinh file mới bằng script, ngưỡng 4 KB giữa fetch trọn và trích dòng, đặt tên `tmp_` cho file dùng một lần. Dựng `fxprobe01` từ scaffold rỗng cộng ba ảnh test rồi thả tay hai filter từ GUI, gỡ chặn khuôn filter. Đo được: filter trong GUI CapCut quốc tế là namespace khác hẳn 468 mục JianYing, `resource_id` không trùng và cờ `is_vip` không dự đoán được vương miện, nên mục kiểm khoá Pro mất đối chứng dương và chuyển sang trạng thái chặn vì phương pháp. Filter nằm ở bucket `materials.effects` chứ không phải `filters`. Bảy dương tính giả CRLF chứ không phải sáu
**Phiên:** 17:00 tối

Máy lab. Có mở CapCut, không export. Phiên trước là `2026-08-02-2-no-nho-va-filter.md`.

## Ba luật làm việc mới, đã vào mục 8 của START-HERE

Tạo file mới cũng phải bằng script sinh file chứ không dán tay, áp dụng cho cả file mã lẫn file tài liệu. Lý do không phải tiết kiệm công mà là mã hoá: `>` của PowerShell ghi UTF-16LE, Notepad có thể lưu cp1252, còn `docs_audit.py` đếm byte chứ không kiểm mã hoá nên một file hỏng mã hoá sẽ lọt qua.

Ngưỡng quyết định giữa fetch trọn file và trích dòng. File trong repo dưới 4 KB thì fetch trọn, vì một lượt trích tốn script cộng output dán về cộng một vòng đối đáp, cộng lại đắt hơn chính file đó; từ 4 KB trở lên mà chỉ cần dưới một phần ba thì trích; nằm ngoài repo thì luôn phải trích vì không fetch được.

File dùng một lần trong `data\tmp\` đặt tên theo khuôn `tmp_<YYYYMMDD>_<nhãn>` để dọn được theo tiền tố. Suýt mất `data\tmp\gen_cc_fixture.py` vì thoáng nghĩ `data\tmp\` là thư mục rác thuần; nó là nguyên mẫu của `../../tools/shots_dump.py` và nằm ngoài repo nên không có bản sao nào.

Kèm một quy ước nhỏ: script nào in ra nhiều thông tin thừa thì tự bọc phần cần copy giữa hai dòng đánh dấu và gom phần đó liền mạch, để người dùng không phải tự lọc.

Commit `4b398c0`.

## Dựng đối chứng: project fxprobe01

`testV3_CLEAN` là scaffold **rỗng**: `duration=0`, 0 track, không material nào, 107190 byte trên đĩa. Clone xong sẽ không có clip nào để thả filter lên. Phát hiện được trước khi mở CapCut nhờ đo scaffold thay vì giả định.

Nhân bản bằng `../../scripts_v1/clone_project.py <scaffold> <thư-mục-drafts> <tên-mới>` — ba tham số vị trí, không argparse; gõ `--help` thì chết bằng `IndexError` vì `--help` bị nhận làm tham số 1. Kết quả sạch: 4 GUID sinh mới, `main_timeline_id = 5be63baa-62ad-48fb-a0ee-eada3a7fcc11`, `draft_name` khớp tên thư mục, `draft_fold_path` khớp, 0 file sót tên cũ.

Ba clip thêm bằng `capcut add-video` từ `data\Test_tool_v3\`: `Shot_001_IE3_Launch.png` ở 0,0–5,0 s, `Shot_002_CSS_Revolution.png` ở 5,0–10,0 s, `Shot_003_IE_Acclaimed.png` ở 10,0–15,0 s. Clip 3 cố ý không nhận filter, làm đối chứng âm. `lint` sạch, `segments` in đúng ba mốc. Ghi nhận phụ: ffprobe đọc file PNG ra `videoCodec: "mjpeg"`, `fps: 25`, `durationUs: 40000` — vô hại vì `duration_source` là `argument`, nhưng đừng tin `media_probe.durationUs` với ảnh tĩnh.

Bảng ground truth được viết ra **trước** khi mở CapCut, theo quy tắc bốn của `../failures.md`.

## Khảo sát vương miện: 13 slug, chỉ 3 tìm thấy

Tra lần lượt 13 slug Latin trong ô tìm kiếm tab Filters của CapCut 9.1.0.3879 bản quốc tế, chỉ ghi chép, chưa thả gì.

| Slug JianYing | `is_vip` | Tìm thấy trong GUI | Vương miện |
|---|---|---|---|
| `vhs-iii` | false | có | không |
| `1980` | false | có, hai mục cùng tên | không, cả hai |
| `ditto` | false | không | — |
| `abg` | false | không | — |
| `ke1` | false | không, GUI trả "no content" | — |
| `kv5-d` | false | không | — |
| `2077` | true | có, hai mục cùng tên | **không**, cả hai |
| `90s` | true | không | — |
| `city-walk` | true | không | — |
| `160-c` | true | không | — |
| `400-h` | true | không | — |
| `800-z` | true | không | — |
| `fxn` | true | không | — |

Sáu trong bảy mục `is_vip: true` không tra được, mục còn lại là `2077` thì hiện ra không có vương miện. Riêng bảng này đã đủ để nghi ngờ cờ `is_vip`, nhưng phép đo tiếp theo cho biết lý do sâu hơn.

## Cú sốc: resource_id hai namespace không trùng nhau

Thả tay "VHS III" phủ 0–5 s và "2077" phủ 5–10 s, kéo xuống vùng trống dưới track video để tạo segment độc lập chứ không kéo lên clip. Đóng CapCut bằng nút X rồi đọc ngược JSON.

| Tên | `resource_id` GUI ghi ra | `resource_id` JianYing |
|---|---|---|
| VHS III | `6764669298095952396` | `7127669764905782542` |
| 2077 | `7145435245712511489` | `7131347316111314189` |

**Không trùng.** Hai filter trùng tên là hai tài nguyên khác nhau. Filter trong GUI CapCut quốc tế là **một namespace khác hẳn** 468 mục của `capcut enums --filters --jianying`, nên cờ `is_vip` của JianYing không nói gì về mục cùng tên trong GUI. Cùng chiều với `../failures.md` mục 2.5 nhưng mạnh hơn: trước đó chỉ biết filter "Film" không tìm thấy trong `enums.json`, bây giờ biết một mục **tìm thấy tên mà khác id**.

Hệ quả cho mục kiểm khoá Pro: **không tạo được đối chứng dương bằng filter**. Cả hai filter thả tay đều free. Muốn có một filter Pro trong project thì phải tìm được mục Pro trong chính GUI, mà catalogue thật của GUI hiện chưa có cách nào liệt kê. Nửa sau của mục kiểm khoá Pro chuyển từ "chưa làm" sang "chặn vì phương pháp".

Hệ quả cho đường dựng: 468 mục JianYing vẫn dùng được qua `../../scripts_v1/filter_apply.py` theo quy tắc cache-first vì chúng có md5 và có thư mục cache. Cái mất là khả năng biết trước mục nào khoá Pro.

## Hình dạng JSON của filter do GUI ghi

Filter **không** nằm ở bucket tên `filters`. Nó nằm ở `materials.effects` với `"type": "filter"`, trên một track riêng `"type": "filter"` có `name` rỗng. Mọi phép quét trước đây tìm bucket `filters` đều cho âm tính giả.

Trường đáng chú ý: `category_id: "123456"` và `category_name: "heycan_search_filter"` — dấu vết của việc thả từ kết quả tìm kiếm chứ không từ một mục trong danh mục, chưa rõ có khác gì không. `effect_id`, `resource_id` và `third_resource_id` bằng nhau. `value: 1.0` là cường độ. `path` trỏ vào `C:/Users/anhlt/AppData/Local/CapCut/User Data/Cache/effect/<resource_id>/<md5>`, dùng gạch chéo xuôi. `id` là GUID kiểu CapCut hoa lẫn thường, ví dụ `581160D0-CD36-42c1-B5AD-A07FAAFC3005`. `time_range: null`.

Segment trên track filter: mục thứ nhất `start=0 dur=5000000` khít clip 1; mục thứ hai `start=5033333 dur=4966667`, trễ đúng một frame so với 5 s nhưng vẫn kết thúc đúng 10000000. Đó là hệ quả kéo tay, không phải lỗi. Ghi lại vì phép so khuôn của `../../tools/v4_mold.py` sẽ gặp lại con số này.

Độ dài mặc định khi kéo một filter xuống timeline là khoảng **3 giây**, phải kéo tay cho khớp bề ngang clip.

CapCut ghi **cả** `draft_content.json` ở gốc lẫn bản trong `Timelines\<id>\`, cả hai cùng 27423 byte sau khi lưu, trong khi trước đó gốc 13099 và bản lồng 4329. Tức CapCut tự đồng bộ hai bản khi lưu; nghĩa vụ ghi cả bốn file chỉ đặt lên phía Python.

`../../scripts_v1/fx_audit.py` chạy sau khi đóng CapCut báo cả hai mục `OK`, `path` resolve được, thư mục cache 281 mục. Đúng như `../failures.md` mục 1 mô tả, `OK` ở đây chỉ chứng minh file có thật, không nói gì về khoá Pro.

## Đính chính số đo

Danh sách dương tính giả CRLF là **bảy** file chứ không phải sáu, và một con số sai. Danh sách đúng, đo bằng cách so `docs_audit.py` với blob GitHub ở commit `cf9c069`: `../STATE.md` **+40** chứ không phải +38, `../procedures.md` +198, `../model.md` +57, `../../_deprecated/README.md` +22, `2026-08-01-1-docs-headers.md` +50, `2026-08-01-4-readme-cua-vao.md` +32, và `../../molds/capcut-9.1.0/_README.md` **+18** vốn bị sót khỏi danh sách cũ.

Thư mục draft trên máy lab có 13 mục trước phiên này, gồm `.recycle_bin` và 12 project, chứ không phải 11 như `../STATE.md` ghi. Mục dôi ra là `fxlab01`, rỗng hoàn toàn ở cả bản gốc lẫn bản lồng, không tài liệu nào giải thích; nên xoá.

Câu "ổ C tụt dần vì snapshot của `docs_audit.py` dồn vào `data\perf\`" trong `../STATE.md` sai: `CAPCUT_LAB` trỏ vào `D:\IT\capcut-lab\data` nên snapshot ghi trên ổ D.

Ghi nhận công cụ cho AI phiên sau: git tree API dạng `?recursive=1` bị công cụ fetch cắt cứng ở 10000 byte, đứt giữa mảng JSON, rồi khi xin offset tiếp theo thì **báo sai** là đã hết body. Đường dùng được là tree không đệ quy cộng contents API theo từng thư mục; mỗi phản hồi đóng ngoặc đầy đủ và có `"truncated": false`.

## Chưa kiểm chứng

Hai mục cùng tên "2077" và hai mục cùng tên "1980" trong GUI là hai tài nguyên khác nhau hay một mục hiện hai lần; chỉ thả một trong hai.

Có cách nào liệt kê catalogue filter thật của CapCut bản quốc tế hay không, và có mục filter nào trong GUI mang vương miện hay không — phiên này chưa gặp mục nào.

Cờ VIP của scene-effect, image-intro, image-outro và image-combo; chưa đọc trong phiên này.

Áp filter thẳng vào một clip thay vì tạo segment trên track riêng: GUI cho phép cả hai kiểu, nhưng chưa thử bằng CLI hay bằng Python và chưa biết JSON sinh ra hình dạng gì.

Project `testB` có `materials.hsl` một mục, không project nào khác có, chưa tài liệu nào nhắc.

## Còn lại

Bốn việc của lộ trình phiên này chưa làm: vá `../../tools/v4_mold.py`, nửa sau của mục kiểm khoá Pro, viết `../../tools/shots_dump.py`, và nghiệm thu ba script blur. Tất cả còn nguyên trong `../TODO.md` kèm tiêu chí xong.
