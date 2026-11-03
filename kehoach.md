# ĐỀ CƯƠNG & KẾ HOẠCH THỰC HIỆN NIÊN LUẬN NGÀNH CÔNG NGHỆ THÔNG TIN

**Tên đề tài:** Xây dựng ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp cho sinh viên CNTT dựa trên tin tuyển dụng (Mã đề tài: `NLCNPM23CS-38`)  
**Kho lưu trữ mã nguồn (GitHub):** [https://github.com/0023411000-sketch/bainienluan](https://github.com/0023411000-sketch/bainienluan)  
**Số lượng thực hiện:** 02 thành viên  

---

## 1. ĐẶT VẤN ĐỀ & PHÁT BIỂU BÀI TOÁN (BÀI TOÁN)

### 1.1. Bối cảnh thực tế
Thị trường lao động ngành Công nghệ Thông tin (CNTT) luôn biến động nhanh chóng với sự xuất hiện liên tục của các ngôn ngữ lập trình, framework, công cụ và tiêu chuẩn chứng chỉ mới. Trong khi đó, sinh viên CNTT khi còn ngồi trên ghế nhà trường thường gặp phải khoảng cách lớn giữa **kiến thức tích lũy trong chương trình đào tạo** (học phần, đồ án môn học) và **yêu cầu thực tế từ doanh nghiệp** được đăng tải trên các bản tin tuyển dụng.

Những khó khăn phổ biến mà sinh viên CNTT đang gặp phải:
- Chưa có cái nhìn định lượng rõ ràng về việc hồ sơ năng lực hiện tại của bản thân đáp ứng được **bao nhiêu phần trăm (%)** so với vị trí nghề nghiệp mong muốn (như *Backend Developer, Frontend Developer, Data Analyst, DevOps Engineer, QA/QC Tester, AI/ML Engineer...*).
- Khó tổng hợp được đâu là các kỹ năng cốt lõi, công nghệ phổ biến và chứng chỉ thường được doanh nghiệp yêu cầu nhiều nhất cho từng vị trí.
- Thiếu công cụ tự động chỉ ra **kỹ năng/chứng chỉ còn thiếu (Skill Gap)** và chưa biết lập lộ trình học tập bổ sung như thế nào cho hiệu quả trước khi ra trường.

### 1.2. Phát biểu bài toán
Xây dựng một ứng dụng web hỗ trợ sinh viên CNTT định hướng kỹ năng nghề nghiệp với bài toán trọng tâm:
- **Đầu vào (Input):**
  1. **Hồ sơ năng lực cá nhân của sinh viên:** Thông tin cá nhân, các học phần đã học (mã môn, số tín chỉ, điểm), kỹ năng chuyên môn (mức độ 1–5), chứng chỉ đã đạt và kinh nghiệm/dự án thực tế.
  2. **Dữ liệu vị trí nghề nghiệp & tin tuyển dụng:** Danh mục các vị trí CNTT và tập hợp các tin tuyển dụng thực tế (nhập trực tiếp hoặc nhập hàng loạt từ file CSV), chứa yêu cầu về kỹ năng, công nghệ, chứng chỉ, kinh nghiệm.
- **Quá trình xử lý (Process):**
  1. Tổng hợp, thống kê tần suất xuất hiện của từng kỹ năng, công nghệ, chứng chỉ theo từng vị trí nghề nghiệp từ tập tin tuyển dụng.
  2. Đối sánh (Matching) hồ sơ sinh viên với yêu cầu của vị trí nghề nghiệp mục tiêu để tính **điểm số phù hợp (%)** và phân loại danh sách **Kỹ năng đã đáp ứng** – **Kỹ năng/Chứng chỉ còn thiếu**.
  3. Đề xuất nội dung học tập/chứng chỉ cần bổ sung và chuyển hóa thành các mục tiêu trong kế hoạch phát triển năng lực.
- **Đầu ra (Output):**
  1. Biểu đồ thống kê trực quan nhu cầu kỹ năng & công nghệ của thị trường theo từng vị trí.
  2. Báo cáo đánh giá mức độ phù hợp (%), danh sách kỹ năng đã có (Badge xanh), kỹ năng còn thiếu (Badge đỏ) và chứng chỉ khuyến nghị.
  3. Lộ trình phát triển năng lực cá nhân theo trạng thái (*Chưa bắt đầu*, *Đang học*, *Hoàn thành*) kèm tỷ lệ hoàn thành trên Dashboard.

---

## 2. MỤC TIÊU CỦA ĐỀ TÀI

### 2.1. Mục tiêu chung
Xây dựng hoàn chỉnh ứng dụng web hỗ trợ sinh viên CNTT tự đánh giá năng lực bản thân so với nhu cầu tuyển dụng thực tế của doanh nghiệp, từ đó xác định khoảng trống kỹ năng (Skill Gap) và chủ động lập kế hoạch học tập, rèn luyện phù hợp với định hướng nghề nghiệp.

### 2.2. Mục tiêu cụ thể
1. **Về mặt nghiệp vụ & chức năng:**
   - Quản lý tập trung hồ sơ sinh viên CNTT theo 4 nhóm: *Học phần đã học, Kỹ năng chuyên môn, Chứng chỉ, Kinh nghiệm & Dự án*.
   - Quản lý danh mục vị trí nghề nghiệp CNTT và kho dữ liệu tin tuyển dụng (hỗ trợ tìm kiếm, lọc và nhập dữ liệu hàng loạt qua file CSV).
   - Tự động tổng hợp và trực quan hóa bằng biểu đồ các kỹ năng, công nghệ, chứng chỉ được yêu cầu nhiều nhất cho từng vị trí.
   - Xây dựng thuật toán so sánh hồ sơ sinh viên với yêu cầu vị trí tuyển dụng, tính điểm phù hợp (%) và liệt kê chính xác các kỹ năng/chứng chỉ còn thiếu.
   - Gợi ý nội dung học tập và cung cấp công cụ theo dõi tiến độ kế hoạch phát triển năng lực cá nhân.
2. **Về mặt kỹ thuật & công nghệ:**
   - Áp dụng kiến trúc Web hiện đại với **Python Flask** (RESTful API), cơ sở dữ liệu **SQLite** và giao diện **HTML5/CSS3/JavaScript (Bootstrap 5 + Chart.js)** thân thiện, phản hồi nhanh và bảo mật (mã hóa mật khẩu, chống XSS).

---

## 3. PHẠM VI CỦA ĐỀ TÀI

### 3.1. Phạm vi chức năng
Hệ thống tập trung vào 6 nhóm chức năng cốt lõi theo đúng yêu cầu đề tài:
1. **Quản lý tài khoản & Hồ sơ sinh viên:** Đăng ký, đăng nhập, cập nhật thông tin cá nhân và CRUD 4 danh mục (Học phần, Kỹ năng, Chứng chỉ, Kinh nghiệm).
2. **Quản lý Vị trí nghề nghiệp & Tin tuyển dụng:** CRUD vị trí nghề nghiệp, CRUD tin tuyển dụng, tìm kiếm, lọc theo vị trí và nhập file CSV.
3. **Thống kê & Tổng hợp yêu cầu theo vị trí:** Phân tích tần suất kỹ năng, công nghệ, chứng chỉ từ các tin tuyển dụng và vẽ biểu đồ cột ngang (Horizontal Bar) + biểu đồ tròn (Doughnut).
4. **Đánh giá & So sánh hồ sơ:** Tính % độ phù hợp giữa hồ sơ sinh viên với vị trí mong muốn, tách biệt kỹ năng đã có và kỹ năng còn thiếu.
5. **Gợi ý & Quản lý Kế hoạch phát triển năng lực:** Thêm trực tiếp kỹ năng/chứng chỉ còn thiếu vào lộ trình học tập, cập nhật trạng thái (*Chưa bắt đầu / Đang học / Hoàn thành*) và theo dõi % tiến độ.
6. **Dashboard tổng quan:** Tổng hợp 4 chỉ số quan trọng (Tổng kỹ năng, Tổng chứng chỉ, Vị trí phù hợp nhất, Tiến độ kế hoạch) và biểu đồ so sánh điểm phù hợp giữa các vị trí.

### 3.2. Phạm vi dữ liệu & đối tượng sử dụng
- **Đối tượng sử dụng chính:** Sinh viên ngành Công nghệ Thông tin, Khoa học Máy tính, Kỹ thuật Phần mềm.
- **Phạm vi dữ liệu:** Tập trung vào 8 nhóm vị trí nghề nghiệp CNTT phổ biến tại Việt Nam (*Backend, Frontend, Fullstack, Data Analyst, DevOps, QA/QC Tester, Mobile App, AI/ML*) cùng bộ dữ liệu tin tuyển dụng thu thập từ các doanh nghiệp CNTT.

### 3.3. Giới hạn của đề tài
- Hệ thống thu thập tin tuyển dụng thông qua chức năng quản trị và nhập dữ liệu chuẩn hóa từ file CSV (chưa thực hiện cào dữ liệu tự động thời gian thực từ các trang web bên thứ ba để tránh vi phạm chính sách bảo mật của các cổng tuyển dụng).
- Việc đối sánh dựa trên chuẩn hóa từ khóa kỹ năng, công nghệ và chứng chỉ trong ngành CNTT.

---

## 4. KHẢO SÁT HIỆN TRẠNG & CÁC HỆ THỐNG LIÊN QUAN

### 4.1. Khảo sát các hệ thống hiện có
| Hệ thống khảo sát | Ưu điểm nổi bật | Hạn chế đối với sinh viên CNTT |
| :--- | :--- | :--- |
| **Các cổng tuyển dụng (TopCV, ITviec, VietnamWorks)** | Kho tin tuyển dụng lớn, cập nhật liên tục, hỗ trợ tạo CV đẹp mắt. | Hướng tới người đi làm tìm việc ngay; không quản lý bảng điểm học phần đại học, không thống kê tỷ lệ kỹ năng theo vị trí và không có công cụ lập kế hoạch học tập dài hạn cho sinh viên. |
| **Mạng xã hội nghề nghiệp (LinkedIn)** | Kết nối nhà tuyển dụng tốt, có hiển thị số lượng kỹ năng trùng khớp với tin đăng. | Giao diện phức tạp, chủ yếu bằng tiếng Anh, thiếu sự gắn kết với chương trình học đại học (học phần, tín chỉ) và lộ trình tự học của sinh viên Việt Nam. |
| **Hệ thống quản lý đào tạo của trường đại học** | Lưu trữ chính xác điểm số các học phần, tín chỉ và GPA của sinh viên. | Chỉ quản lý kết quả học tập nội bộ; hoàn toàn tách biệt với dữ liệu thị trường tuyển dụng, không đánh giá được sinh viên đang thiếu kỹ năng thực tế nào để làm việc tại doanh nghiệp. |

### 4.2. Điểm khác biệt & Giá trị của ứng dụng đề xuất
Ứng dụng của đề tài đóng vai trò là **cầu nối giữa Nhà trường và Doanh nghiệp**:
- Kết hợp cả **Học phần đại học + Kỹ năng + Chứng chỉ + Kinh nghiệm dự án** trong cùng một hồ sơ.
- Cung cấp góc nhìn **Thống kê định lượng** từ dữ liệu tin tuyển dụng thực tế cho từng vị trí nghề nghiệp.
- Không chỉ dừng ở việc chấm điểm độ phù hợp (%) mà còn **chuyển hóa các kỹ năng còn thiếu thành Kế hoạch học tập cá nhân** có theo dõi tiến độ hoàn thành.

---

## 5. CẤU TRÚC NHÁNH GIT (GIT FLOW) & QUY TẮC QUẢN LÝ CODE

### 5.1. Danh sách các nhánh trên GitHub
Hệ thống quản lý mã nguồn tại kho `https://github.com/0023411000-sketch/bainienluan` được chia thành **4 nhánh chính**:

1. **`main` (Nhánh chính thức / Production):**
   - Chứa toàn bộ mã nguồn hoàn chỉnh sau khi tích hợp và kiểm thử.
   - **QUY TẮC BẮT BUỘC:** Tuyệt đối **KHÔNG** tự ý push hoặc merge trực tiếp vào `main`. Nhánh `main` do **Trưởng nhóm (Chủ kho lưu trữ)** trực tiếp kiểm duyệt và đưa code lên thủ công khi sản phẩm đã hoàn thiện và được sự cho phép.
2. **`develop` (Nhánh tích hợp chung):**
   - Nhánh trung gian dùng để ghép nối (merge) code từ nhánh của Thành viên 1 và Thành viên 2.
3. **`thanh-vien-1` (Nhánh làm việc của Thành viên 1):**
   - Chỉ chứa các file thuộc phân hệ của Thành viên 1.
4. **`thanh-vien-2` (Nhánh làm việc của Thành viên 2):**
   - Chỉ chứa các file thuộc phân hệ của Thành viên 2.

```
main (Khoá bảo vệ - Chỉ đưa code lên thủ công khi hoàn thiện & được phép)
  ▲
  └── (Đưa code thủ công khi hoàn tất toàn bộ dự án)
        │
     develop (Nhánh tích hợp & kiểm thử chung)
      ▲   ▲
      │   └──── Merge / Pull Request ──── thanh-vien-2 (Nhánh Thành viên 2)
      └──────── Merge / Pull Request ──── thanh-vien-1 (Nhánh Thành viên 1)
```

---

## 6. KẾ HOẠCH THỰC HIỆN & PHÂN CÔNG NHIỆM VỤ CHI TIẾT

### 6.1. Bảng phân công công việc cho 2 thành viên (50% - 50%)

#### 👤 THÀNH VIÊN 1 (Nhánh: `thanh-vien-1`)
**Vai trò:** Phụ trách **Phân hệ Người dùng, Hồ sơ sinh viên, Vị trí nghề nghiệp & Tin tuyển dụng (Core Data & CRUD)**.

| STT | Hạng mục công việc | Chi tiết chức năng cần thực hiện | File / Đường dẫn phụ trách |
| :-: | :--- | :--- | :--- |
| 1 | **Thiết kế CSDL nền tảng (SQLite)** | - Thiết kế bảng `users`, `student_profiles`, `courses` (học phần), `skills` (kỹ năng), `certificates` (chứng chỉ), `experiences` (kinh nghiệm).<br>- Thiết kế bảng `positions` (vị trí nghề nghiệp) và `jobs` (tin tuyển dụng).<br>- Viết script khởi tạo CSDL và dữ liệu mẫu (`models.py`, `seed_data.py`). | `models.py`, `database.db`, `seed_data.py` |
| 2 | **Xác thực & Quản lý tài khoản** | - API Đăng ký (`/api/auth/register`), Đăng nhập (`/api/auth/login`), Đăng xuất (`/api/auth/logout`).<br>- Mã hóa mật khẩu (`werkzeug.security`), quản lý phiên đăng nhập / token.<br>- Kết nối giao diện `login.html`, `register.html` và `static/js/auth.js`. | `templates/login.html`, `templates/register.html`, `static/js/auth.js` |
| 3 | **Quản lý Hồ sơ sinh viên (4 danh mục)** | - Xem và cập nhật thông tin cá nhân (`GET/PUT /api/profile`).<br>- CRUD Học phần đã học (`/api/profile/courses`).<br>- CRUD Kỹ năng & mức độ thành thạo 1-5 (`/api/profile/skills`).<br>- CRUD Chứng chỉ (`/api/profile/certificates`).<br>- CRUD Kinh nghiệm thực tế / dự án (`/api/profile/experiences`). | `templates/profile.html`, `static/js/profile.js` |
| 4 | **Quản lý Vị trí nghề nghiệp & Tin tuyển dụng** | - CRUD Danh mục vị trí nghề nghiệp CNTT (`/api/positions`), tìm kiếm & phân trang.<br>- CRUD Tin tuyển dụng (`/api/jobs`), lọc theo vị trí & từ khóa.<br>- Chức năng nhập hàng loạt tin tuyển dụng từ file CSV (`POST /api/jobs/import-csv`). | `templates/positions.html`, `templates/jobs.html`, `static/js/positions.js`, `static/js/jobs.js` |

#### 👤 THÀNH VIÊN 2 (Nhánh: `thanh-vien-2`)
**Vai trò:** Phụ trách **Phân hệ Phân tích dữ liệu, Đối sánh độ phù hợp, Gợi ý lộ trình học tập & Dashboard tổng quan (Analytics & Recommendation)**.

| STT | Hạng mục công việc | Chi tiết chức năng cần thực hiện | File / Đường dẫn phụ trách |
| :-: | :--- | :--- | :--- |
| 1 | **Thiết kế CSDL Phân tích & Kế hoạch** | - Thiết kế bảng `learning_plans` (lộ trình học tập/chứng chỉ mục tiêu), `course_recommendations` (kho gợi ý khóa học/chứng chỉ theo kỹ năng), `comparison_history` (lịch sử đánh giá). | `models.py` (phần bảng kế hoạch & gợi ý) |
| 2 | **Tổng hợp & Thống kê yêu cầu tuyển dụng** | - Xây dựng thuật toán thống kê tần suất xuất hiện của kỹ năng, công nghệ, chứng chỉ và kinh nghiệm từ các tin tuyển dụng theo từng vị trí (`GET /api/statistics/<position_id>`).<br>- Biểu diễn trực quan bằng biểu đồ cột ngang (Top kỹ năng) và biểu đồ tròn (Tỷ trọng công nghệ) với Chart.js. | `templates/statistics.html`, `static/js/statistics.js` |
| 3 | **Đánh giá & So sánh hồ sơ với vị trí nghề nghiệp** | - Xây dựng thuật toán tính điểm phù hợp (`POST /api/compare`) đối chiếu hồ sơ sinh viên với yêu cầu vị trí.<br>- Tách biệt danh sách: Kỹ năng đã đáp ứng (Badge xanh) và Kỹ năng/Chứng chỉ còn thiếu (Badge đỏ).<br>- Gợi ý nội dung học tập / chứng chỉ cần bổ sung tương ứng với phần còn thiếu. | `templates/compare.html`, `static/js/compare.js` |
| 4 | **Quản lý Kế hoạch phát triển năng lực & Dashboard** | - Thêm kỹ năng/chứng chỉ còn thiếu từ trang So sánh vào Kế hoạch cá nhân (`GET/POST/PUT/DELETE /api/plan`).<br>- Theo dõi trạng thái (`Chưa bắt đầu`, `Đang học`, `Hoàn thành`) và tính % tiến độ hoàn thành.<br>- Xây dựng API & giao diện Dashboard tổng quan (`/api/dashboard`): hiển thị 4 chỉ số chính, biểu đồ độ phù hợp với các vị trí và danh sách việc cần làm. | `templates/dashboard.html`, `templates/plan.html`, `static/js/dashboard.js`, `static/js/plan.js` |

---

### 6.2. Lộ trình thực hiện theo tuần (Timeline 6 tuần)

| Tuần | Nội dung công việc chính | Kết quả đạt được (Deliverables) |
| :-: | :--- | :--- |
| **Tuần 1** | **Khởi tạo dự án, Khảo sát & Thiết kế CSDL**<br>- Phân tích bài toán, xác định mục tiêu, phạm vi và thống nhất hợp đồng API.<br>- Thiết lập kho GitHub `bainienluan` và các nhánh `develop`, `thanh-vien-1`, `thanh-vien-2`.<br>- Thiết kế sơ đồ ERD và cấu trúc bảng SQLite. | File kế hoạch `kehoach.md`, sơ đồ CSDL, cấu trúc nhánh Git. |
| **Tuần 2** | **Xây dựng Giao diện (Frontend) & Khung ứng dụng**<br>- Thành viên 1: Giao diện Đăng nhập, Đăng ký, Hồ sơ 4 mục, Vị trí, Tin tuyển dụng.<br>- Thành viên 2: Giao diện Dashboard, Thống kê, So sánh, Kế hoạch học tập. | Bộ giao diện HTML/CSS/JS hoàn chỉnh, chạy thử nghiệm mượt mà. |
| **Tuần 3** | **Phát triển Backend API & CSDL SQLite (Giai đoạn 1)**<br>- Thành viên 1: Khởi tạo `database.db`, API Xác thực (`/api/auth/*`) và API Hồ sơ (`/api/profile/*`).<br>- Thành viên 2: API Thống kê kỹ năng theo vị trí (`/api/statistics/*`) và thuật toán So sánh (`/api/compare`). | CSDL SQLite có dữ liệu mẫu, hoàn thành 50% RESTful API. |
| **Tuần 4** | **Phát triển Backend API & Tính năng nâng cao (Giai đoạn 2)**<br>- Thành viên 1: API Vị trí (`/api/positions`), Tin tuyển dụng (`/api/jobs`) và Nhập CSV (`/api/jobs/import-csv`).<br>- Thành viên 2: API Kế hoạch học tập (`/api/plan`) và Tổng hợp Dashboard (`/api/dashboard`). | Hoàn thành 100% các API của cả 2 phân hệ. |
| **Tuần 5** | **Tích hợp hệ thống & Kiểm thử chéo (Integration & Testing)**<br>- Kết nối Frontend với Backend thật (`USE_MOCK: false`).<br>- Gộp code từ 2 nhánh thành viên vào `develop` và kiểm thử toàn bộ chức năng theo Checklist. | Hệ thống tích hợp hoàn chỉnh trên nhánh `develop`, không còn lỗi. |
| **Tuần 6** | **Hoàn thiện Báo cáo Niên luận & Đưa code lên `main`**<br>- Viết báo cáo tổng kết niên luận và chuẩn bị slide bảo vệ.<br>- Chủ dự án kiểm duyệt lần cuối và đưa code hoàn chỉnh lên nhánh `main`. | Báo cáo niên luận hoàn chỉnh, mã nguồn chính thức trên nhánh `main`. |
