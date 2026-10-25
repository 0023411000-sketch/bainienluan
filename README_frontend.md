# TÀI LIỆU HƯỚNG DẪN VẬN HÀNH & NỐI GHÉP FRONTEND
## Đề tài: NLCNPM23CS-38 - Xây dựng ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp cho sinh viên CNTT dựa trên tin tuyển dụng

---

## 1. CẤU TRÚC THƯ MỤC DỰ ÁN
```text
bainienluana/
├── templates/
│   ├── base.html                 # Layout khung sườn dùng chung (Navbar, CDN, Toast, Loading)
│   ├── login.html                # Trang đăng nhập tài khoản
│   ├── register.html             # Trang đăng ký tài khoản sinh viên
│   ├── dashboard.html            # Dashboard tổng quan chỉ số và biểu đồ
│   ├── profile.html              # Hồ sơ sinh viên & 4 phần quản lý (học phần, kỹ năng, chứng chỉ, kinh nghiệm)
│   ├── positions.html            # Danh mục vị trí nghề nghiệp CNTT
│   ├── jobs.html                 # Danh sách tin tuyển dụng & nhập file CSV
│   ├── statistics.html           # Thống kê kỹ năng & công nghệ theo vị trí
│   ├── compare.html              # Đánh giá & so sánh mức độ phù hợp hồ sơ
│   ├── plan.html                 # Kế hoạch & lộ trình phát triển kỹ năng cá nhân
│   ├── 404.html                  # Trang lỗi 404 Not Found thân thiện
│   └── partials/
│       └── navbar.html           # Thanh điều hướng (Navbar) dùng chung
├── static/
│   ├── css/
│   │   └── style.css             # Định kiểu thiết kế đồng bộ, typography Inter, theme hiện đại
│   └── js/
│       ├── config.js             # File cấu hình trung tâm (CỜ USE_MOCK, BASE_URL)
│       ├── mock-data.js          # Dữ liệu giả lập thực tế: 8 vị trí, 30 tin tuyển dụng, hồ sơ mẫu
│       ├── utils.js              # Tiện ích chung: chống XSS, Toast, Loading, Confirm Modal, Pagination
│       ├── api.js                # Lớp giao tiếp API tập trung (Centralized Service)
│       ├── auth.js               # Logic trang Đăng nhập / Đăng ký (kiểm tra email, khớp mật khẩu)
│       ├── dashboard.js          # Logic bảng điều khiển tổng quan (Chart.js Bar)
│       ├── profile.js            # Logic quản lý hồ sơ & CRUD 4 phần qua Bootstrap Modal
│       ├── positions.js          # Logic tìm kiếm, phân trang và CRUD vị trí nghề nghiệp
│       ├── jobs.js               # Logic lọc, tìm kiếm, CRUD tin tuyển dụng & đọc/xem trước CSV
│       ├── statistics.js         # Logic thống kê: Horizontal Bar Chart + Doughnut Chart
│       ├── compare.js            # Logic so sánh độ phù hợp: Doughnut Chart + Badge + Thêm vào kế hoạch
│       └── plan.js               # Logic quản lý lộ trình học tập, thanh tiến độ và lọc trạng thái
├── app_frontend.py               # Ứng dụng Flask render giao diện độc lập
├── app.py                        # Entrypoint Flask chính (đồng bộ với app_frontend.py)
└── README_frontend.md            # Tài liệu này
```

---

## 2. HƯỚNG DẪN CÀI ĐẶT & CHẠY THỬ FRONTEND ĐỘC LẬP

### Bước 1: Chuẩn bị môi trường Python
Yêu cầu đã cài đặt **Python 3.8+**. Mở Terminal / PowerShell tại thư mục dự án:
```bash
pip install flask
```

### Bước 2: Khởi chạy máy chủ giao diện
Chạy một trong hai lệnh sau:
```bash
python app_frontend.py
# hoặc
python app.py
```

### Bước 3: Truy cập hệ thống trên trình duyệt
Mở trình duyệt web và truy cập địa chỉ:
**`http://127.0.0.1:5000`**

Hệ thống sẽ tự động chuyển hướng đến `/dashboard`.
- **Tài khoản dùng thử đăng nhập sẵn**: `an.nguyen20@sis.hust.edu.vn` / Mật khẩu: `123456`
- Có thể trải nghiệm đầy đủ 100% tính năng bằng dữ liệu giả lập chất lượng cao không cần backend.

---

## 3. CÁCH CHUYỂN ĐỔI TỪ MOCK DATA SANG BACKEND FLASK THẬT

Hệ thống được thiết kế theo mô hình **Adapter Pattern** tại tầng `static/js/api.js`. Để chuyển đổi sang Backend thật của nhóm backend:

1. Mở file **`static/js/config.js`**.
2. Tìm dòng `USE_MOCK: true` và sửa thành `false`:
```javascript
const CONFIG = {
    // ĐỔI THÀNH false ĐỂ KẾT NỐI BACKEND THẬT:
    USE_MOCK: false,

    // Cấu hình URL backend của bạn (mặc định /api):
    API_BASE_URL: '/api',
    ...
};
```
3. Lưu file và tải lại trang trên trình duyệt (`F5`). Toàn bộ các yêu cầu thêm/sửa/xóa/đọc dữ liệu sẽ tự động chuyển thành các lệnh `fetch` HTTP đến Backend thật theo đúng hợp đồng API JSON.

---

## 4. HỢP ĐỒNG API VỚI BACKEND FLASK
Mọi API trả về phản hồi JSON có cấu trúc thống nhất:
- Thành công: `{"success": true, "data": ..., "message": "..."}`
- Thất bại: `{"success": false, "message": "Nội dung thông báo lỗi tiếng Việt"}`

| Chức năng | Phương thức | Đường dẫn API | Tham số / Body |
| :--- | :---: | :--- | :--- |
| Đăng ký | `POST` | `/api/auth/register` | `{"full_name", "email", "password"}` |
| Đăng nhập | `POST` | `/api/auth/login` | `{"email", "password"}` |
| Đăng xuất | `POST` | `/api/auth/logout` | Header `Authorization: Bearer <token>` |
| Lấy dữ liệu Dashboard | `GET` | `/api/dashboard` | Thống kê số lượng, điểm cao nhất, tiến độ |
| Xem hồ sơ cá nhân | `GET` | `/api/profile` | Thông tin cá nhân, 4 danh sách con |
| Cập nhật thông tin cá nhân | `PUT` | `/api/profile` | Thông tin cá nhân mới |
| Thêm / Sửa / Xóa kỹ năng | `POST/PUT/DELETE` | `/api/profile/skills` (`/<id>`) | `{"name", "category", "level", "note"}` |
| Thêm / Sửa / Xóa học phần | `POST/PUT/DELETE` | `/api/profile/courses` (`/<id>`) | `{"code", "name", "credits", "grade", "term"}` |
| Thêm / Sửa / Xóa chứng chỉ | `POST/PUT/DELETE` | `/api/profile/certificates` (`/<id>`) | `{"name", "organization", "issue_date", "expiry_date", "credential_url"}` |
| Thêm / Sửa / Xóa kinh nghiệm | `POST/PUT/DELETE` | `/api/profile/experiences` (`/<id>`) | `{"title", "company", "role_type", "start_date", "end_date", "description"}` |
| Danh sách vị trí | `GET` | `/api/positions?q=&page=&limit=` | Danh sách vị trí phân trang |
| Thêm / Sửa / Xóa vị trí | `POST/PUT/DELETE` | `/api/positions` (`/<id>`) | `{"name", "code", "description", "core_skills", "demand_level"}` |
| Danh sách tin tuyển dụng | `GET` | `/api/jobs?q=&position_id=&page=&limit=` | Lọc theo vị trí & từ khóa |
| Thêm / Sửa / Xóa việc làm | `POST/PUT/DELETE` | `/api/jobs` (`/<id>`) | Tiêu đề, công ty, vị trí, kỹ năng, công nghệ... |
| Nhập dữ liệu CSV | `POST` | `/api/jobs/import-csv` | `{"records": [...]}` |
| Thống kê kỹ năng theo vị trí | `GET` | `/api/statistics/<position_id>` | `top_skills`, `technologies`, `certificates` |
| Đánh giá phù hợp hồ sơ | `POST` | `/api/compare` | `{"position_id": 1}` |
| Lộ trình học tập cá nhân | `GET/POST` | `/api/plan` | `{"title", "category", "type", "status", "target_date"}` |
| Cập nhật trạng thái kế hoạch | `PUT` | `/api/plan/<id>` | `{"status": "todo"|"doing"|"done"}` |
| Xóa mục kế hoạch | `DELETE` | `/api/plan/<id>` | Xóa mục khỏi kế hoạch |

---

## 5. DANH SÁCH KIỂM TRA (CHECKLIST) TỰ KIỂM THỬ TỪNG TRANG

| Trang | Hạng mục kiểm thử | Kết quả mong đợi |
| :--- | :--- | :--- |
| **Đăng nhập (`/login`)** | Bỏ trống email / sai định dạng | Báo đỏ viền ô nhập, hiện thông báo lỗi tiếng Việt cụ thể |
| | Mật khẩu dưới 6 ký tự | Báo lỗi mật khẩu không đủ độ dài |
| | Bấm icon con mắt | Chuyển đổi qua lại giữa hiển thị mật khẩu và dấu chấm ••• |
| | Bấm "Đăng nhập ngay" | Nút hiện spinner chống nhấn đúp; Toast báo thành công; chuyển sang `/dashboard` |
| **Đăng ký (`/register`)** | Mật khẩu xác nhận không trùng | Báo lỗi "Mật khẩu nhập lại không khớp" |
| | Chưa tick đồng ý điều khoản | Chặn submit và nhắc nhở người dùng |
| **Dashboard (`/dashboard`)** | Xem 4 thẻ chỉ số | Số kỹ năng, chứng chỉ, điểm cao nhất và thanh tiến độ hiển thị chính xác |
| | Biểu đồ cột điểm vị trí | Render bằng Chart.js, có màu sắc theo thang điểm, hover xem tooltip % |
| | Việc cần làm gần đây | Bấm icon tròn hoàn thành việc cần làm; danh sách và thanh tiến độ cập nhật ngay |
| **Hồ sơ (`/profile`)** | Sửa thông tin cá nhân | Mở modal, sửa thông tin, bấm lưu; sidebar và thông tin cập nhật tức thì |
| | Thao tác 4 tab | Chuyển mượt mà giữa: Kỹ năng (1-5 sao), Học phần, Chứng chỉ, Kinh nghiệm |
| | Thêm / Sửa / Xóa từng mục | Modal hiển thị đúng dữ liệu; xác nhận xóa bằng hộp thoại trước khi xóa |
| **Vị trí (`/positions`)** | Tìm kiếm từ khóa | Gõ từ khóa, hệ thống tự động lọc (debounce 300ms) không cần tải lại trang |
| | Phân trang | Bấm số trang, chuyển trang mượt mà |
| | Thêm / Sửa / Xóa vị trí | Thêm vị trí mới và danh sách cập nhật ngay |
| **Tuyển dụng (`/jobs`)** | Lọc theo vị trí & tìm kiếm | Kết hợp đồng thời lọc theo nhóm vị trí và từ khóa |
| | Nhập file CSV | Bấm nút CSV -> chọn file -> xem trước đúng 5 dòng đầu -> bấm xác nhận nhập |
| | Tải file mẫu CSV | Bấm tải về tập tin mẫu `tin_tuyen_dung_mau.csv` |
| **Thống kê (`/statistics`)** | Đổi vị trí trong dropdown | Biểu đồ cột ngang (top kỹ năng) và biểu đồ tròn (công nghệ) tự hủy và vẽ lại |
| **So sánh (`/compare`)** | Bấm "Bắt đầu so sánh" | Biểu đồ Doughnut quay sinh động; hiện badges xanh (đã có), đỏ (còn thiếu) |
| | Nút "Thêm vào Kế hoạch" | Tự động tạo các mục tiêu cho kỹ năng còn thiếu vào trang Lộ trình |
| **Kế hoạch (`/plan`)** | Bộ lọc trạng thái | Lọc theo Tất cả / Chưa bắt đầu / Đang học / Hoàn thành |
| | Đổi trạng thái nhanh | Bấm dropdown trên thẻ, chuyển đổi trạng thái tức thì; thanh % tiến độ tăng/giảm |
| **Trang 404 (`/404`)** | Gõ URL không hợp lệ | Hiển thị giao diện 404 đẹp mắt kèm các nút quay về trang chính |

---

## 6. CÁC ĐIỂM CẦN LƯU Ý KHI NỐI VỚI BACKEND FLASK THẬT
1. **CORS (Cross-Origin Resource Sharing)**: Nếu Backend chạy ở cổng khác (ví dụ Backend `:8000`, Frontend `:5000`), cần cài đặt `flask-cors` ở Backend:
   ```python
   from flask_cors import CORS
   CORS(app)
   ```
2. **Session / JWT Authentication**: File `api.js` đã tự động gắn `Authorization: Bearer <token>` từ `localStorage`. Khi Backend trả token tại endpoint `/auth/login`, frontend sẽ tự động lưu và gửi đi trong mọi request sau đó.
3. **Mã hóa và chống tấn công XSS**: Toàn bộ dữ liệu hiển thị từ API đều được xử lý qua hàm `Utils.escapeHtml()` trước khi render vào DOM, bảo vệ an toàn trước các cuộc tấn công tiêm mã độc.
4. **Quản lý biểu đồ Chart.js**: Các file JS đã tự động kiểm tra và gọi `chartInstance.destroy()` trước khi khởi tạo lại canvas, đảm bảo không bị lỗi đè biểu đồ hoặc rò rỉ bộ nhớ.
