# KẾ HOẠCH THỰC HIỆN NIÊN LUẬN NGÀNH CÔNG NGHỆ THÔNG TIN

## 1. THÔNG TIN CHUNG VỀ ĐỀ TÀI
- **Tên đề tài:** Xây dựng ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp cho sinh viên CNTT dựa trên tin tuyển dụng (Mã đề tài: `NLCNPM23CS-38`).
- **Mục tiêu đề tài:** Xây dựng hệ thống web giúp sinh viên CNTT quản lý hồ sơ năng lực cá nhân (học phần, kỹ năng, chứng chỉ, kinh nghiệm), đối chiếu với dữ liệu yêu cầu thực tế từ các tin tuyển dụng theo từng vị trí nghề nghiệp, từ đó đánh giá mức độ phù hợp (%), chỉ ra các kỹ năng/chứng chỉ còn thiếu và lập kế hoạch phát triển năng lực.
- **Công nghệ sử dụng:**
  - **Backend:** Python 3.8+, Flask Framework, RESTful API, xác thực Session / JWT, xử lý dữ liệu CSV.
  - **Cơ sở dữ liệu:** SQLite (`database.db`) kết hợp SQLAlchemy / `sqlite3`.
  - **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Jinja2 Templates, Chart.js (vẽ biểu đồ thống kê & đối sánh).
- **Kho lưu trữ mã nguồn (GitHub Repository):** [https://github.com/0023411000-sketch/bainienluan](https://github.com/0023411000-sketch/bainienluan)
- **Số lượng thành viên:** 02 thành viên.

---

## 2. CẤU TRÚC NHÁNH GIT (GIT FLOW) & QUY TẮC QUẢN LÝ CODE

### 2.1. Danh sách các nhánh trên GitHub
Hệ thống quản lý mã nguồn tại kho `https://github.com/0023411000-sketch/bainienluan` được chia thành **4 nhánh chính**:

1. **`main` (Nhánh chính thức / Production):**
   - Chỉ chứa mã nguồn đã hoàn thiện, chạy ổn định và kiểm thử đầy đủ.
   - **QUY TẮC BẮT BUỘC:** Tuyệt đối **KHÔNG** tự ý push hoặc merge trực tiếp vào `main`. Nhánh `main` do **Trưởng nhóm (Chủ kho lưu trữ)** trực tiếp kiểm duyệt và đưa code lên thủ công khi sản phẩm đã hoàn thiện và được sự cho phép.
2. **`develop` (Nhánh tích hợp chung):**
   - Nhánh trung gian dùng để ghép nối (merge) code từ nhánh của Thành viên 1 và Thành viên 2.
   - Mọi tính năng sau khi hoàn thành ở nhánh cá nhân sẽ tạo Pull Request (hoặc merge) về `develop` để chạy thử nghiệm tích hợp (Frontend + Backend + SQLite).
3. **`thanh-vien-1` (Nhánh làm việc của Thành viên 1):**
   - Nhánh phát triển riêng của Thành viên 1 (tách ra từ `develop`).
4. **`thanh-vien-2` (Nhánh làm việc của Thành viên 2):**
   - Nhánh phát triển riêng của Thành viên 2 (tách ra từ `develop`).

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

### 2.2. Quy trình làm việc hàng ngày với Git
- **Bước 1: Lấy code mới nhất từ nhánh `develop` trước khi làm việc**
  ```bash
  git checkout thanh-vien-1   # (hoặc thanh-vien-2)
  git pull origin develop
  ```
- **Bước 2: Viết code, kiểm thử tại máy cá nhân và commit**
  ```bash
  git add .
  git commit -m "feat: mô tả ngắn gọn chức năng vừa làm"
  git push origin thanh-vien-1   # (hoặc thanh-vien-2)
  ```
- **Bước 3: Gộp code vào nhánh `develop`**
  - Tạo Pull Request từ `thanh-vien-1` (hoặc `thanh-vien-2`) vào `develop` trên GitHub để kiểm tra xung đột (conflict) trước khi merge.
- **Bước 4: Đưa code lên `main` (Dành riêng cho Chủ dự án)**
  - Chỉ khi toàn bộ tính năng trên `develop` đã hoàn thiện 100%, kiểm thử không còn lỗi, chủ dự án mới thực hiện đưa code lên `main`.

---

## 3. PHÂN CÔNG CÔNG VIỆC CHI TIẾT CHO 2 THÀNH VIÊN

Để tránh trùng lặp file gây xung đột (conflict) khi làm việc nhóm và đảm bảo khối lượng công việc cân bằng (50% - 50%), dự án được chia thành **2 mảng nghiệp vụ rõ ràng** từ Giao diện đến CSDL và API:

### 👤 THÀNH VIÊN 1 (Nhánh: `thanh-vien-1`)
**Vai trò:** Phụ trách **Phân hệ Người dùng, Hồ sơ sinh viên, Vị trí nghề nghiệp & Tin tuyển dụng (Core Data & CRUD)**.

| STT | Hạng mục công việc | Chi tiết chức năng cần thực hiện | File / Đường dẫn phụ trách |
| :-: | :--- | :--- | :--- |
| 1 | **Thiết kế CSDL nền tảng (SQLite)** | - Thiết kế bảng `users`, `student_profiles`, `courses` (học phần), `skills` (kỹ năng), `certificates` (chứng chỉ), `experiences` (kinh nghiệm).<br>- Thiết kế bảng `positions` (vị trí nghề nghiệp) và `jobs` (tin tuyển dụng).<br>- Viết script khởi tạo CSDL và dữ liệu mẫu (`init_db.py` / `models.py`). | `models.py`, `database.db`, `seed_data.py` |
| 2 | **Xác thực & Quản lý tài khoản** | - API Đăng ký (`/api/auth/register`), Đăng nhập (`/api/auth/login`), Đăng xuất (`/api/auth/logout`).<br>- Mã hóa mật khẩu (`werkzeug.security`), quản lý phiên đăng nhập / token.<br>- Kết nối giao diện `login.html`, `register.html` và `static/js/auth.js`. | `templates/login.html`, `templates/register.html`, `static/js/auth.js` |
| 3 | **Quản lý Hồ sơ sinh viên (4 danh mục)** | - Xem và cập nhật thông tin cá nhân (`GET/PUT /api/profile`).<br>- CRUD Học phần đã học (`/api/profile/courses`).<br>- CRUD Kỹ năng & mức độ thành thạo 1-5 (`/api/profile/skills`).<br>- CRUD Chứng chỉ (`/api/profile/certificates`).<br>- CRUD Kinh nghiệm thực tế / dự án (`/api/profile/experiences`). | `templates/profile.html`, `static/js/profile.js` |
| 4 | **Quản lý Vị trí nghề nghiệp & Tin tuyển dụng** | - CRUD Danh mục vị trí nghề nghiệp CNTT (`/api/positions`), tìm kiếm & phân trang.<br>- CRUD Tin tuyển dụng (`/api/jobs`), lọc theo vị trí & từ khóa.<br>- Chức năng nhập hàng loạt tin tuyển dụng từ file CSV (`POST /api/jobs/import-csv`). | `templates/positions.html`, `templates/jobs.html`, `static/js/positions.js`, `static/js/jobs.js` |

---

### 👤 THÀNH VIÊN 2 (Nhánh: `thanh-vien-2`)
**Vai trò:** Phụ trách **Phân hệ Phân tích dữ liệu, Đối sánh độ phù hợp, Gợi ý lộ trình học tập & Dashboard tổng quan (Analytics & Recommendation)**.

| STT | Hạng mục công việc | Chi tiết chức năng cần thực hiện | File / Đường dẫn phụ trách |
| :-: | :--- | :--- | :--- |
| 1 | **Thiết kế CSDL Phân tích & Kế hoạch** | - Thiết kế bảng `learning_plans` (lộ trình học tập/chứng chỉ mục tiêu), `course_recommendations` (kho gợi ý khóa học/chứng chỉ theo kỹ năng), `comparison_history` (lịch sử đánh giá). | `models.py` (phần bảng kế hoạch & gợi ý) |
| 2 | **Tổng hợp & Thống kê yêu cầu tuyển dụng** | - Xây dựng thuật toán thống kê tần suất xuất hiện của kỹ năng, công nghệ, chứng chỉ và kinh nghiệm từ các tin tuyển dụng theo từng vị trí (`GET /api/statistics/<position_id>`).<br>- Biểu diễn trực quan bằng biểu đồ cột ngang (Top kỹ năng) và biểu đồ tròn (Tỷ trọng công nghệ) với Chart.js. | `templates/statistics.html`, `static/js/statistics.js` |
| 3 | **Đánh giá & So sánh hồ sơ với vị trí nghề nghiệp** | - Xây dựng thuật toán tính điểm phù hợp (`POST /api/compare`) dựa trên trọng số: Kỹ năng (50%), Học phần liên quan (20%), Chứng chỉ (15%), Kinh nghiệm (15%).<br>- Tách biệt danh sách: Kỹ năng đã đáp ứng (Badge xanh) và Kỹ năng/Chứng chỉ còn thiếu (Badge đỏ).<br>- Gợi ý nội dung học tập / chứng chỉ cần bổ sung tương ứng với phần còn thiếu. | `templates/compare.html`, `static/js/compare.js` |
| 4 | **Quản lý Kế hoạch phát triển năng lực & Dashboard** | - Thêm kỹ năng/chứng chỉ còn thiếu từ trang So sánh vào Kế hoạch cá nhân (`GET/POST/PUT/DELETE /api/plan`).<br>- Theo dõi trạng thái (`Chưa bắt đầu`, `Đang học`, `Hoàn thành`) và tính % tiến độ hoàn thành.<br>- Xây dựng API & giao diện Dashboard tổng quan (`/api/dashboard`): hiển thị 4 chỉ số chính, biểu đồ độ phù hợp với các vị trí và danh sách việc cần làm. | `templates/dashboard.html`, `templates/plan.html`, `static/js/dashboard.js`, `static/js/plan.js` |

---

## 4. LỘ TRÌNH THỰC HIỆN THEO TUẦN (TIMELINE 6 TUẦN)

### 🗓️ Tuần 1: Khởi tạo dự án, Phân tích yêu cầu & Thiết kế CSDL
- **Cả 2 thành viên:**
  - Thống nhất yêu cầu đề tài, luồng nghiệp vụ và hợp đồng API JSON (theo `README_frontend.md`).
  - Thiết lập kho GitHub `bainienluan` và các nhánh `develop`, `thanh-vien-1`, `thanh-vien-2`.
- **Thành viên 1:** Thiết kế sơ đồ ERD cho nhóm bảng Người dùng, Hồ sơ 4 phần, Vị trí, Tin tuyển dụng.
- **Thành viên 2:** Thiết kế sơ đồ ERD cho nhóm bảng Kế hoạch học tập, Gợi ý kỹ năng; thiết kế công thức tính độ phù hợp (%).

### 🗓️ Tuần 2: Xây dựng Giao diện (Frontend) & Khung Backend Flask
- **Thành viên 1:** Hoàn thiện giao diện & logic JS cho trang Đăng nhập, Đăng ký, Hồ sơ cá nhân (`profile`), Vị trí nghề nghiệp (`positions`), Tin tuyển dụng (`jobs`).
- **Thành viên 2:** Hoàn thiện giao diện & logic JS cho trang Dashboard (`dashboard`), Thống kê (`statistics`), So sánh hồ sơ (`compare`), Lộ trình phát triển (`plan`).
- **Tích hợp lần 1:** Gộp giao diện của 2 thành viên vào nhánh `develop`, chạy thử với dữ liệu giả lập (`USE_MOCK: true`).

### 🗓️ Tuần 3: Phát triển Backend API & Cơ sở dữ liệu SQLite (Phần 1)
- **Thành viên 1:**
  - Khởi tạo SQLite Database và viết API xác thực (`/api/auth/*`).
  - Viết API CRUD Hồ sơ sinh viên (`/api/profile/*`).
- **Thành viên 2:**
  - Viết module tổng hợp dữ liệu tin tuyển dụng (`/api/statistics/<position_id>`).
  - Viết thuật toán đối sánh hồ sơ sinh viên với yêu cầu vị trí (`/api/compare`).

### 🗓️ Tuần 4: Phát triển Backend API & Tính năng nâng cao (Phần 2)
- **Thành viên 1:**
  - Viết API CRUD Vị trí nghề nghiệp (`/api/positions`) và Tin tuyển dụng (`/api/jobs`).
  - Viết API nhập dữ liệu tin tuyển dụng từ file CSV (`/api/jobs/import-csv`).
- **Thành viên 2:**
  - Viết API gợi ý nội dung học tập và quản lý Kế hoạch phát triển năng lực (`/api/plan`).
  - Viết API tổng hợp chỉ số Dashboard (`/api/dashboard`).

### 🗓️ Tuần 5: Kết nối Frontend - Backend & Kiểm thử tích hợp
- **Cả 2 thành viên:**
  - Chuyển cấu hình `USE_MOCK: false` trong `static/js/config.js` để kết nối giao diện với Backend Flask + SQLite thật.
  - Merge code từ `thanh-vien-1` và `thanh-vien-2` vào `develop`.
  - Kiểm thử chéo (Cross-testing): Thành viên 1 test chức năng của Thành viên 2 và ngược lại theo Checklist kiểm thử.

### 🗓️ Tuần 6: Hoàn thiện Báo cáo Niên luận, Đóng gói & Đưa lên nhánh `main`
- **Cả 2 thành viên:**
  - Viết báo cáo tổng kết niên luận (Chương 1: Tổng quan, Chương 2: Phân tích & Thiết kế, Chương 3: Cài đặt & Kết quả thực nghiệm, Chương 4: Kết luận).
  - Chuẩn bị slide thuyết trình và kịch bản demo.
- **Trưởng nhóm (Chủ kho Git):**
  - Kiểm tra toàn bộ mã nguồn lần cuối trên nhánh `develop`.
  - Đưa code hoàn chỉnh lên nhánh `main` thủ công.

---

## 5. TIÊU CHUẨN KỸ THUẬT & QUY ƯỚC CHUNG

1. **Chuẩn phản hồi API JSON:**
   - Thành công:
     ```json
     {
       "success": true,
       "data": { ... },
       "message": "Thao tác thành công"
     }
     ```
   - Thất bại:
     ```json
     {
       "success": false,
       "message": "Thông báo lỗi tiếng Việt rõ ràng"
     }
     ```
2. **Quy ước đặt tên Commit Git:**
   - `feat: ...` — Thêm tính năng mới (Ví dụ: `feat: them API nhap tin tuyen dung tu CSV`)
   - `fix: ...` — Sửa lỗi (Ví dụ: `fix: sua loi tinh phan tram do phu hop`)
   - `docs: ...` — Cập nhật tài liệu, báo cáo, kế hoạch
   - `refactor: ...` — Tối ưu hóa mã nguồn
3. **Bảo vệ nhánh `main`:**
   - Không thành viên nào được chạy lệnh `git push origin main` khi chưa có sự đồng ý của chủ dự án.
   - Mọi công việc phát triển và tích hợp chỉ diễn ra trên `thanh-vien-1`, `thanh-vien-2` và `develop`.

