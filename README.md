# HỆ THỐNG HỖ TRỢ ĐỊNH HƯỚNG KỸ NĂNG NGHỀ NGHIỆP CHO SINH VIÊN CNTT DỰA TRÊN TIN TUYỂN DỤNG
**Mã đề tài:** `NLCNPM23CS-38` — Học phần: Niên luận Công nghệ Phần mềm

---

## 1. Giới thiệu đề tài
Ứng dụng web hỗ trợ sinh viên ngành Công nghệ Thông tin quản lý hồ sơ năng lực học tập cá nhân, thu thập và thống kê yêu cầu thực tế từ các tin tuyển dụng CNTT, đối sánh mức độ phù hợp (`%` Matching Score), phát hiện kỹ năng còn thiếu (Skill Gap) và xây dựng lộ trình học tập cá nhân hóa.

## 2. Phân công thành viên (Nhóm 2 sinh viên)
- **Thành viên 1 (Nhánh `thanh-vien-1`):** Phụ trách **Core Data & CRUD** — Quản lý tài khoản xác thực, Hồ sơ sinh viên & 4 danh mục con (`Học phần`, `Kỹ năng`, `Chứng chỉ`, `Kinh nghiệm`), Quản lý Vị trí nghề nghiệp & Tin tuyển dụng (kèm nhập/xuất CSV).
- **Thành viên 2 (Nhánh `thanh-vien-2`):** Phụ trách **Analytics & Recommendation** — Thống kê yêu cầu tuyển dụng theo vị trí (Chart.js), Thuật toán đối sánh hồ sơ & Gợi ý khóa học/chứng chỉ + Lưu lịch sử đối sánh, Quản lý Lộ trình phát triển năng lực & Dashboard tổng quan.

---

## 3. Cấu trúc thư mục dự án
```text
bainienluana/
├── app.py                     # Ứng dụng Flask (Routes HTML & RESTful API)
├── models.py                  # Định nghĩa cấu trúc bảng SQLite & kết nối CSDL
├── seed_data.py               # Khởi tạo dữ liệu mẫu thực tế (8 vị trí, 30 tin tuyển dụng...)
├── init_db.py                 # Script khởi tạo nhanh database.db & csdl_nien_luan.db
├── tao_csdl_tieng_viet.py     # Script tạo CSDL 11 bảng tiếng Việt không dấu & xuất SQL Server
├── schema_tieng_viet.sql      # Kịch bản T-SQL chuẩn Microsoft SQL Server (SSMS) kèm dữ liệu mẫu
├── thiet_ke_csdl.md           # Tài liệu thiết kế CSDL 11 bảng & code vẽ sơ đồ ERD Mermaid (Draw.io)
├── kehoach.md                 # Đề cương chi tiết: Bài toán, Mục tiêu, Phạm vi, Khảo sát & Kế hoạch
├── database.db                # File CSDL SQLite chính của ứng dụng
├── csdl_nien_luan.db          # File CSDL SQLite độc lập 11 bảng tiếng Việt không dấu
├── requirements.txt           # Danh sách thư viện Python cần cài đặt
├── templates/                 # Giao diện HTML (Jinja2 + Bootstrap 5)
└── static/                    # Tài nguyên tĩnh (CSS, JavaScript, Chart.js)
```

---

## 4. Hướng dẫn cài đặt và chạy chương trình

### Bước 1: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 2: Khởi tạo Cơ sở dữ liệu (SQLite)
```bash
python init_db.py
```
*(Nếu dùng **Microsoft SQL Server Management Studio - SSMS**, mở file `schema_tieng_viet.sql` và nhấn **F5 / Execute** để tự động tạo Database `CSDL_NIEN_LUAN` cùng 11 bảng và dữ liệu mẫu).*

### Bước 3: Khởi chạy máy chủ Flask
```bash
python app.py
```
Truy cập ứng dụng tại địa chỉ: **http://127.0.0.1:5000**

### Tài khoản sinh viên mẫu để đăng nhập thử nghiệm:
- **Email:** `an.nguyen20@sis.hust.edu.vn`
- **Mật khẩu:** `123456`
