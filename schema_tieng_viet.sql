-- ============================================================================
-- schema_tieng_viet.sql (Chuẩn Microsoft SQL Server / T-SQL - SSMS)
-- Kịch bản khởi tạo Cơ sở dữ liệu & nạp dữ liệu mẫu (11 bảng tiếng Việt không dấu)
-- Đề tài: NLCNPM23CS-38 - Ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp CNTT
-- Hướng dẫn: Mở file này trong SQL Server Management Studio (SSMS) và nhấn F5 (Execute)
-- ============================================================================

USE master;
GO

IF DB_ID(N'CSDL_NIEN_LUAN') IS NULL
BEGIN
    CREATE DATABASE CSDL_NIEN_LUAN;
END
GO

USE CSDL_NIEN_LUAN;
GO

-- Xóa các bảng cũ (nếu có) theo thứ tự khóa ngoại để chạy lại không bị lỗi
IF OBJECT_ID(N'dbo.LICH_SU_DOI_SANH', N'U') IS NOT NULL DROP TABLE dbo.LICH_SU_DOI_SANH;
IF OBJECT_ID(N'dbo.GOI_Y_KHOA_HOC', N'U') IS NOT NULL DROP TABLE dbo.GOI_Y_KHOA_HOC;
IF OBJECT_ID(N'dbo.KE_HOACH_HOC_TAP', N'U') IS NOT NULL DROP TABLE dbo.KE_HOACH_HOC_TAP;
IF OBJECT_ID(N'dbo.TIN_TUYEN_DUNG', N'U') IS NOT NULL DROP TABLE dbo.TIN_TUYEN_DUNG;
IF OBJECT_ID(N'dbo.KINH_NGHIEM', N'U') IS NOT NULL DROP TABLE dbo.KINH_NGHIEM;
IF OBJECT_ID(N'dbo.CHUNG_CHI', N'U') IS NOT NULL DROP TABLE dbo.CHUNG_CHI;
IF OBJECT_ID(N'dbo.KY_NANG', N'U') IS NOT NULL DROP TABLE dbo.KY_NANG;
IF OBJECT_ID(N'dbo.HOC_PHAN', N'U') IS NOT NULL DROP TABLE dbo.HOC_PHAN;
IF OBJECT_ID(N'dbo.HO_SO_SINH_VIEN', N'U') IS NOT NULL DROP TABLE dbo.HO_SO_SINH_VIEN;
IF OBJECT_ID(N'dbo.VI_TRI_NGHE_NGHIEP', N'U') IS NOT NULL DROP TABLE dbo.VI_TRI_NGHE_NGHIEP;
IF OBJECT_ID(N'dbo.NGUOI_DUNG', N'U') IS NOT NULL DROP TABLE dbo.NGUOI_DUNG;
GO

-- 1. Bảng NGUOI_DUNG (Tài khoản người dùng)
CREATE TABLE dbo.NGUOI_DUNG (
    ma_nguoi_dung INT IDENTITY(1,1) PRIMARY KEY,
    ho_ten NVARCHAR(150) NOT NULL,
    email NVARCHAR(150) NOT NULL UNIQUE,
    mat_khau_bam NVARCHAR(255) NOT NULL,
    vai_tro NVARCHAR(50) DEFAULT N'student',
    ngay_tao DATETIME DEFAULT GETDATE()
);
GO

-- 2. Bảng VI_TRI_NGHE_NGHIEP (Danh mục vị trí nghề nghiệp CNTT)
CREATE TABLE dbo.VI_TRI_NGHE_NGHIEP (
    ma_vi_tri INT IDENTITY(1,1) PRIMARY KEY,
    ten_vi_tri NVARCHAR(200) NOT NULL,
    ma_dinh_danh NVARCHAR(100) DEFAULT N'',
    mo_ta_cong_viec NVARCHAR(MAX) DEFAULT N'',
    ky_nang_cot_loi_json NVARCHAR(MAX) DEFAULT N'[]',
    muc_do_nhu_cau NVARCHAR(100) DEFAULT N'Cao'
);
GO

-- 3. Bảng HO_SO_SINH_VIEN (Thông tin cá nhân & định hướng của sinh viên)
CREATE TABLE dbo.HO_SO_SINH_VIEN (
    ma_ho_so INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL UNIQUE,
    ho_ten NVARCHAR(150) NOT NULL,
    ma_so_sinh_vien NVARCHAR(50) DEFAULT N'',
    email NVARCHAR(150) NOT NULL,
    so_dien_thoai NVARCHAR(30) DEFAULT N'',
    truong_dai_hoc NVARCHAR(255) DEFAULT N'',
    khoa_vien NVARCHAR(255) DEFAULT N'',
    chuyen_nganh NVARCHAR(255) DEFAULT N'',
    nien_khoa NVARCHAR(100) DEFAULT N'',
    diem_gpa NVARCHAR(20) DEFAULT N'0.0',
    ma_vi_tri_muc_tieu INT NULL DEFAULT 1,
    gioi_thieu_ban_than NVARCHAR(MAX) DEFAULT N'',
    CONSTRAINT FK_HSSV_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE,
    CONSTRAINT FK_HSSV_VITRI FOREIGN KEY (ma_vi_tri_muc_tieu) REFERENCES dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri) ON DELETE SET NULL
);
GO

-- 4. Bảng HOC_PHAN (Danh sách học phần đại học đã học)
CREATE TABLE dbo.HOC_PHAN (
    ma_hoc_phan INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,
    ma_mon_hoc NVARCHAR(50) NOT NULL,
    ten_hoc_phan NVARCHAR(255) NOT NULL,
    so_tin_chi INT DEFAULT 3,
    diem_chu NVARCHAR(10) DEFAULT N'A',
    hoc_ky NVARCHAR(100) DEFAULT N'',
    CONSTRAINT FK_HOCPHAN_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);
GO

-- 5. Bảng KY_NANG (Kỹ năng chuyên môn & mức độ thành thạo 1-5)
CREATE TABLE dbo.KY_NANG (
    ma_ky_nang INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,
    ten_ky_nang NVARCHAR(150) NOT NULL,
    nhom_ky_nang NVARCHAR(150) DEFAULT N'Ngôn ngữ lập trình',
    muc_do_thanh_thao INT DEFAULT 3 CHECK (muc_do_thanh_thao >= 1 AND muc_do_thanh_thao <= 5),
    ghi_chu NVARCHAR(MAX) DEFAULT N'',
    CONSTRAINT FK_KYNANG_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);
GO

-- 6. Bảng CHUNG_CHI (Chứng chỉ chuyên môn & ngoại ngữ)
CREATE TABLE dbo.CHUNG_CHI (
    ma_chung_chi INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,
    ten_chung_chi NVARCHAR(255) NOT NULL,
    to_chuc_cap NVARCHAR(255) NOT NULL,
    ngay_cap NVARCHAR(50) DEFAULT N'',
    ngay_het_han NVARCHAR(50) DEFAULT N'',
    duong_dan_xac_thuc NVARCHAR(500) DEFAULT N'',
    CONSTRAINT FK_CHUNGCHI_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);
GO

-- 7. Bảng KINH_NGHIEM (Kinh nghiệm thực tập, làm việc & dự án thực tế)
CREATE TABLE dbo.KINH_NGHIEM (
    ma_kinh_nghiem INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,
    ten_cong_viec_du_an NVARCHAR(255) NOT NULL,
    ten_don_vi_cong_ty NVARCHAR(255) NOT NULL,
    loai_hinh_vai_tro NVARCHAR(100) DEFAULT N'Thực tập sinh',
    ngay_bat_dau NVARCHAR(50) DEFAULT N'',
    ngay_ket_thuc NVARCHAR(50) DEFAULT N'',
    mo_ta_chi_tiet NVARCHAR(MAX) DEFAULT N'',
    CONSTRAINT FK_KINHNGHIEM_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);
GO

-- 8. Bảng TIN_TUYEN_DUNG (Danh sách tin tuyển dụng từ doanh nghiệp)
CREATE TABLE dbo.TIN_TUYEN_DUNG (
    ma_tin_tuyen_dung INT IDENTITY(1,1) PRIMARY KEY,
    tieu_de_tin NVARCHAR(300) NOT NULL,
    ten_cong_ty NVARCHAR(255) NOT NULL,
    ma_vi_tri INT NOT NULL,
    dia_diem_lam_viec NVARCHAR(150) DEFAULT N'Toàn quốc',
    muc_luong NVARCHAR(150) DEFAULT N'Thỏa thuận',
    yeu_cau_kinh_nghiem NVARCHAR(150) DEFAULT N'Không yêu cầu',
    ky_nang_yeu_cau_json NVARCHAR(MAX) DEFAULT N'[]',
    cong_nghe_yeu_cau_json NVARCHAR(MAX) DEFAULT N'[]',
    chung_chi_uu_tien_json NVARCHAR(MAX) DEFAULT N'[]',
    han_nop_ho_so NVARCHAR(50) DEFAULT N'',
    mo_ta_chi_tiet NVARCHAR(MAX) DEFAULT N'',
    ngay_dang DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_TINTUYENDUNG_VITRI FOREIGN KEY (ma_vi_tri) REFERENCES dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri) ON DELETE CASCADE
);
GO

-- 9. Bảng KE_HOACH_HOC_TAP (Lộ trình phát triển năng lực cá nhân)
CREATE TABLE dbo.KE_HOACH_HOC_TAP (
    ma_ke_hoach INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,
    tieu_de_muc_tieu NVARCHAR(300) NOT NULL,
    danh_muc_bo_sung NVARCHAR(150) DEFAULT N'Kỹ năng bổ sung',
    loai_muc_tieu NVARCHAR(50) DEFAULT N'skill',
    trang_thai NVARCHAR(50) DEFAULT N'todo',
    ngay_hoan_thanh_du_kien NVARCHAR(50) DEFAULT N'',
    ghi_chu_hoc_tap NVARCHAR(MAX) DEFAULT N'',
    CONSTRAINT FK_KEHOACH_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);
GO

-- 10. Bảng GOI_Y_KHOA_HOC (Kho gợi ý khóa học & chứng chỉ theo kỹ năng thiếu)
CREATE TABLE dbo.GOI_Y_KHOA_HOC (
    ma_goi_y INT IDENTITY(1,1) PRIMARY KEY,
    ten_ky_nang NVARCHAR(150) NOT NULL,
    ten_khoa_hoc_chung_chi NVARCHAR(300) NOT NULL,
    don_vi_cung_cap NVARCHAR(200) DEFAULT N'Coursera / Udemy',
    loai_goi_y NVARCHAR(50) DEFAULT N'course',
    thoi_luong_hoc NVARCHAR(100) DEFAULT N'4 tuần',
    duong_dan_khoa_hoc NVARCHAR(500) DEFAULT N'',
    mo_ta_noi_dung NVARCHAR(MAX) DEFAULT N''
);
GO

-- 11. Bảng LICH_SU_DOI_SANH (Lịch sử đánh giá & đối sánh độ phù hợp hồ sơ)
CREATE TABLE dbo.LICH_SU_DOI_SANH (
    ma_lich_su INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,
    ma_vi_tri INT NOT NULL,
    ten_vi_tri NVARCHAR(200) NOT NULL,
    diem_phu_hop_phan_tram INT DEFAULT 0,
    ky_nang_da_co_json NVARCHAR(MAX) DEFAULT N'[]',
    ky_nang_con_thieu_json NVARCHAR(MAX) DEFAULT N'[]',
    ngay_danh_gia DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_LICHSU_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE,
    CONSTRAINT FK_LICHSU_VITRI FOREIGN KEY (ma_vi_tri) REFERENCES dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri) ON DELETE CASCADE
);
GO

-- ============================================================================
-- NẠP DỮ LIỆU MẪU CHO 11 BẢNG
-- ============================================================================

-- Dữ liệu bảng NGUOI_DUNG
SET IDENTITY_INSERT dbo.NGUOI_DUNG ON;
INSERT INTO dbo.NGUOI_DUNG (ma_nguoi_dung, ho_ten, email, mat_khau_bam, vai_tro, ngay_tao) VALUES (1, N'Nguyễn Văn An', N'an.nguyen20@sis.hust.edu.vn', N'pbkdf2:sha256:600000$nlcnpm23cs38$6bfcfe64747a64f4b4eb02ab917856466acb89e1b86dba3f1003a114aee7f474', N'student', N'2026-11-03 03:50:08');
INSERT INTO dbo.NGUOI_DUNG (ma_nguoi_dung, ho_ten, email, mat_khau_bam, vai_tro, ngay_tao) VALUES (2, N'Quản trị viên Hệ thống', N'admin@hust.edu.vn', N'scrypt:32768:8:1$ROptqPydseg6RrzJ$2fec4fa92aaede2bf119d7e69a9d0331c477e4ae21f8073e82b16995a3e77d30d9084d052b883e268cdc9fbec5c8d181a8a78fe83a3e846f202c26f4b86d79fe', N'admin', N'2026-11-06 14:13:04');
INSERT INTO dbo.NGUOI_DUNG (ma_nguoi_dung, ho_ten, email, mat_khau_bam, vai_tro, ngay_tao) VALUES (3, N'Nguyễn Phi Long (Admin)', N'long.admin@hust.edu.vn', N'scrypt:32768:8:1$mBPB6Cz6n371w99z$cfe03f8c986b3803f2eb56d7eaa763c7ecda6e408dc59e6637cb1862e6fed10cc3edd5af4cc559a5d13ac1be11447a757901d26f7ba75413931d94cb4d8643c2', N'admin', N'2026-11-06 15:32:10');
INSERT INTO dbo.NGUOI_DUNG (ma_nguoi_dung, ho_ten, email, mat_khau_bam, vai_tro, ngay_tao) VALUES (4, N'Trần Thị Bích Ngọc', N'ngoc.tran21@student.edu.vn', N'scrypt:32768:8:1$mBPB6Cz6n371w99z$cfe03f8c986b3803f2eb56d7eaa763c7ecda6e408dc59e6637cb1862e6fed10cc3edd5af4cc559a5d13ac1be11447a757901d26f7ba75413931d94cb4d8643c2', N'student', N'2026-11-06 15:32:10');
INSERT INTO dbo.NGUOI_DUNG (ma_nguoi_dung, ho_ten, email, mat_khau_bam, vai_tro, ngay_tao) VALUES (5, N'Lê Hoàng Nam', N'nam.le21@student.edu.vn', N'scrypt:32768:8:1$mBPB6Cz6n371w99z$cfe03f8c986b3803f2eb56d7eaa763c7ecda6e408dc59e6637cb1862e6fed10cc3edd5af4cc559a5d13ac1be11447a757901d26f7ba75413931d94cb4d8643c2', N'student', N'2026-11-06 15:32:10');
INSERT INTO dbo.NGUOI_DUNG (ma_nguoi_dung, ho_ten, email, mat_khau_bam, vai_tro, ngay_tao) VALUES (6, N'Phạm Minh Tuấn', N'tuan.pham22@student.edu.vn', N'scrypt:32768:8:1$mBPB6Cz6n371w99z$cfe03f8c986b3803f2eb56d7eaa763c7ecda6e408dc59e6637cb1862e6fed10cc3edd5af4cc559a5d13ac1be11447a757901d26f7ba75413931d94cb4d8643c2', N'student', N'2026-11-06 15:32:10');
SET IDENTITY_INSERT dbo.NGUOI_DUNG OFF;
GO

-- Dữ liệu bảng VI_TRI_NGHE_NGHIEP
SET IDENTITY_INSERT dbo.VI_TRI_NGHE_NGHIEP ON;
INSERT INTO dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri, ten_vi_tri, ma_dinh_danh, mo_ta_cong_viec, ky_nang_cot_loi_json, muc_do_nhu_cau) VALUES (1, N'Lập trình viên Backend (Backend Developer)', N'BACKEND_DEV', N'Xây dựng và tối ưu hệ thống xử lý phía máy chủ, thiết kế kiến trúc cơ sở dữ liệu và RESTful/GraphQL API.', N'["Python", "Java", "Node.js", "SQL", "Docker", "RESTful API", "Redis", "Git"]', N'Rất cao');
INSERT INTO dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri, ten_vi_tri, ma_dinh_danh, mo_ta_cong_viec, ky_nang_cot_loi_json, muc_do_nhu_cau) VALUES (2, N'Lập trình viên Frontend (Frontend Developer)', N'FRONTEND_DEV', N'Thiết kế, xây dựng giao diện ứng dụng web tối ưu trải nghiệm người dùng, responsive và tương tác mượt mà.', N'["HTML5/CSS3", "JavaScript", "TypeScript", "ReactJS", "VueJS", "Bootstrap", "Tailwind CSS", "Git"]', N'Cao');
INSERT INTO dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri, ten_vi_tri, ma_dinh_danh, mo_ta_cong_viec, ky_nang_cot_loi_json, muc_do_nhu_cau) VALUES (3, N'Lập trình viên Fullstack (Fullstack Developer)', N'FULLSTACK_DEV', N'Thành thạo cả tầng giao diện Frontend và logic Backend, triển khai và bảo trì toàn diện hệ thống web.', N'["JavaScript", "Node.js", "ReactJS", "PostgreSQL", "Docker", "RESTful API", "CI/CD", "Git"]', N'Rất cao');
INSERT INTO dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri, ten_vi_tri, ma_dinh_danh, mo_ta_cong_viec, ky_nang_cot_loi_json, muc_do_nhu_cau) VALUES (4, N'Chuyên viên Phân tích Dữ liệu (Data Analyst)', N'DATA_ANALYST', N'Khai phá, xử lý và trực quan hóa dữ liệu từ nhiều nguồn nhằm hỗ trợ doanh nghiệp ra quyết định chiến lược.', N'["Python", "SQL", "Power BI", "Tableau", "Excel nâng cao", "Xác suất thống kê", "Pandas", "Data Cleaning"]', N'Cao');
INSERT INTO dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri, ten_vi_tri, ma_dinh_danh, mo_ta_cong_viec, ky_nang_cot_loi_json, muc_do_nhu_cau) VALUES (5, N'Kỹ sư DevOps & Cloud (DevOps Engineer)', N'DEVOPS_ENG', N'Tự động hóa chu trình phát triển - triển khai CI/CD, vận hành hạ tầng đám mây và giám sát tính ổn định hệ thống.', N'["Linux", "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Shell Scripting", "Prometheus"]', N'Rất cao');
INSERT INTO dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri, ten_vi_tri, ma_dinh_danh, mo_ta_cong_viec, ky_nang_cot_loi_json, muc_do_nhu_cau) VALUES (6, N'Kỹ sư Kiểm thử Phần mềm (QA / QC Tester)', N'QA_TESTER', N'Đảm bảo chất lượng sản phẩm phần mềm qua việc lập kế hoạch kiểm thử, thiết kế test case thủ công và tự động.', N'["Kiểm thử phần mềm", "Thiết kế Test Case", "Postman", "Selenium", "SQL cơ bản", "Jira", "API Testing"]', N'Trung bình');
INSERT INTO dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri, ten_vi_tri, ma_dinh_danh, mo_ta_cong_viec, ky_nang_cot_loi_json, muc_do_nhu_cau) VALUES (7, N'Lập trình viên Ứng dụng Di động (Mobile App Developer)', N'MOBILE_DEV', N'Phát triển ứng dụng di động đa nền tảng hoặc native cho hệ điều hành iOS và Android.', N'["Flutter", "Dart", "React Native", "Swift", "Kotlin", "RESTful API", "Mobile UX", "Git"]', N'Cao');
INSERT INTO dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri, ten_vi_tri, ma_dinh_danh, mo_ta_cong_viec, ky_nang_cot_loi_json, muc_do_nhu_cau) VALUES (8, N'Kỹ sư Trí tuệ Nhân tạo & Học máy (AI / ML Engineer)', N'AI_ML_ENG', N'Nghiên cứu, huấn luyện và triển khai các mô hình học máy, thị giác máy tính và xử lý ngôn ngữ tự nhiên.', N'["Python", "PyTorch", "TensorFlow", "Toán rời rạc & Đại số tuyến tính", "Scikit-Learn", "Computer Vision", "NLP", "Docker"]', N'Rất cao');
SET IDENTITY_INSERT dbo.VI_TRI_NGHE_NGHIEP OFF;
GO

-- Dữ liệu bảng HO_SO_SINH_VIEN
SET IDENTITY_INSERT dbo.HO_SO_SINH_VIEN ON;
INSERT INTO dbo.HO_SO_SINH_VIEN (ma_ho_so, ma_nguoi_dung, ho_ten, ma_so_sinh_vien, email, so_dien_thoai, truong_dai_hoc, khoa_vien, chuyen_nganh, nien_khoa, diem_gpa, ma_vi_tri_muc_tieu, gioi_thieu_ban_than) VALUES (1, 1, N'Nguyễn Văn An', N'20205012', N'an.nguyen20@sis.hust.edu.vn', N'0987654321', N'Đại học Bách Khoa Hà Nội', N'Trường Công nghệ Thông tin & Truyền thông', N'Khoa học Máy tính', N'K65 (2020 - 2025)', N'3.42', 1, N'Sinh viên năm cuối đam mê phát triển hệ thống backend phân tán, có kiến thức vững chắc về Python, SQL, RESTful API và Docker.');
INSERT INTO dbo.HO_SO_SINH_VIEN (ma_ho_so, ma_nguoi_dung, ho_ten, ma_so_sinh_vien, email, so_dien_thoai, truong_dai_hoc, khoa_vien, chuyen_nganh, nien_khoa, diem_gpa, ma_vi_tri_muc_tieu, gioi_thieu_ban_than) VALUES (2, 2, N'Quản trị viên Hệ thống', N'', N'admin@hust.edu.vn', N'', N'', N'', N'', N'', N'0.0', 1, N'');
INSERT INTO dbo.HO_SO_SINH_VIEN (ma_ho_so, ma_nguoi_dung, ho_ten, ma_so_sinh_vien, email, so_dien_thoai, truong_dai_hoc, khoa_vien, chuyen_nganh, nien_khoa, diem_gpa, ma_vi_tri_muc_tieu, gioi_thieu_ban_than) VALUES (3, 4, N'Trần Thị Bích Ngọc', N'20216045', N'ngoc.tran21@student.edu.vn', N'0912345678', N'Đại học Công nghệ - ĐHQGHN', N'Khoa Công nghệ Thông tin', N'Kỹ thuật Phần mềm', N'K66 (2021 - 2025)', N'3.58', 2, N'Sinh viên năm cuối yêu thích thiết kế UI/UX và phát triển giao diện Frontend hiện đại với ReactJS, TypeScript và Tailwind CSS.');
INSERT INTO dbo.HO_SO_SINH_VIEN (ma_ho_so, ma_nguoi_dung, ho_ten, ma_so_sinh_vien, email, so_dien_thoai, truong_dai_hoc, khoa_vien, chuyen_nganh, nien_khoa, diem_gpa, ma_vi_tri_muc_tieu, gioi_thieu_ban_than) VALUES (4, 5, N'Lê Hoàng Nam', N'20218102', N'nam.le21@student.edu.vn', N'0934567890', N'Đại học Kinh tế Quốc dân', N'Viện Công nghệ Thông tin & Kinh tế số', N'Hệ thống Thông tin Quản lý', N'K63 (2021 - 2025)', N'3.35', 4, N'Định hướng trở thành Chuyên viên Phân tích Dữ liệu (Data Analyst) trong lĩnh vực Fintech & E-commerce.');
INSERT INTO dbo.HO_SO_SINH_VIEN (ma_ho_so, ma_nguoi_dung, ho_ten, ma_so_sinh_vien, email, so_dien_thoai, truong_dai_hoc, khoa_vien, chuyen_nganh, nien_khoa, diem_gpa, ma_vi_tri_muc_tieu, gioi_thieu_ban_than) VALUES (5, 6, N'Phạm Minh Tuấn', N'20225109', N'tuan.pham22@student.edu.vn', N'0978123456', N'Đại học Bách Khoa Hà Nội', N'Trường Công nghệ Thông tin & Truyền thông', N'Trí tuệ Nhân tạo (AI)', N'K67 (2022 - 2026)', N'3.65', 8, N'Đam mê nghiên cứu Học sâu (Deep Learning), Thị giác máy tính (Computer Vision) và xử lý ngôn ngữ tự nhiên (NLP).');
SET IDENTITY_INSERT dbo.HO_SO_SINH_VIEN OFF;
GO

-- Dữ liệu bảng HOC_PHAN
SET IDENTITY_INSERT dbo.HOC_PHAN ON;
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (1, 1, N'IT3011', N'Cấu trúc dữ liệu và giải thuật', 3, N'A', N'2022.1');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (2, 1, N'IT3080', N'Mạng máy tính', 3, N'B+', N'2022.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (3, 1, N'IT3090', N'Cơ sở dữ liệu', 3, N'A', N'2022.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (4, 1, N'IT4010', N'Lập trình Web', 3, N'A', N'2023.1');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (5, 1, N'IT4060', N'Lập trình mạng và hệ thống phân tán', 3, N'B+', N'2023.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (6, 1, N'IT4409', N'Kiểm thử và đảm bảo chất lượng phần mềm', 2, N'A', N'2023.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (7, 4, N'INT2204', N'Lập trình hướng đối tượng', 3, N'A', N'2022.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (8, 4, N'INT3306', N'Phát triển ứng dụng Web', 3, N'A+', N'2023.1');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (9, 4, N'INT3110', N'Giao diện người - máy (UI/UX)', 3, N'A', N'2023.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (10, 5, N'IT1102', N'Cơ sở dữ liệu & Quản trị dữ liệu', 3, N'A', N'2022.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (11, 5, N'DS2010', N'Xác suất thống kê ứng dụng', 3, N'A', N'2023.1');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (12, 5, N'DA3050', N'Trực quan hóa dữ liệu kinh doanh (BI)', 3, N'B+', N'2023.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (13, 6, N'MI2020', N'Toán rời rạc & Đại số tuyến tính', 4, N'A', N'2022.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (14, 6, N'IT3160', N'Nhập môn Trí tuệ nhân tạo', 3, N'A+', N'2023.2');
INSERT INTO dbo.HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky) VALUES (15, 6, N'IT4172', N'Xử lý ảnh và Thị giác máy tính', 3, N'A', N'2024.1');
SET IDENTITY_INSERT dbo.HOC_PHAN OFF;
GO

-- Dữ liệu bảng KY_NANG
SET IDENTITY_INSERT dbo.KY_NANG ON;
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (1, 1, N'Python', N'Ngôn ngữ lập trình', 4, N'Thành thạo lập trình OOP, xử lý cấu trúc dữ liệu');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (2, 1, N'SQL', N'Cơ sở dữ liệu', 4, N'Viết truy vấn phức tạp, tối ưu chỉ mục index');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (3, 1, N'Flask', N'Framework / Thư viện', 3, N'Xây dựng REST API, tích hợp SQLite/SQLAlchemy');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (4, 1, N'Git', N'Công cụ phát triển', 4, N'Sử dụng thành thạo Git branch, PR, merge rebase');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (5, 1, N'HTML5/CSS3', N'Frontend cơ bản', 3, N'Cắt giao diện chuẩn responsive, Bootstrap');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (6, 1, N'JavaScript', N'Ngôn ngữ lập trình', 3, N'ES6+, DOM, Async/Await');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (7, 1, N'Docker', N'DevOps & Môi trường', 2, N'Biết viết Dockerfile cơ bản, docker-compose');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (8, 4, N'HTML5/CSS3', N'Frontend cơ bản', 5, N'Responsive, Flexbox, CSS Grid');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (9, 4, N'JavaScript', N'Ngôn ngữ lập trình', 4, N'ES6+, Fetch API, DOM');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (10, 4, N'ReactJS', N'Framework / Thư viện', 4, N'React Hooks, Redux Toolkit, React Router');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (11, 4, N'Tailwind CSS', N'Framework / Thư viện', 4, N'Thiết kế giao diện nhanh chuẩn Design System');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (12, 4, N'Git', N'Công cụ phát triển', 3, N'Quản lý mã nguồn nhóm');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (13, 5, N'SQL', N'Cơ sở dữ liệu', 4, N'Truy vấn phức tạp, Window Functions, CTE');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (14, 5, N'Python', N'Ngôn ngữ lập trình', 4, N'Phân tích dữ liệu với Pandas, NumPy');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (15, 5, N'Excel nâng cao', N'Công cụ phân tích', 5, N'Pivot Table, Power Query, VBA cơ bản');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (16, 5, N'Power BI', N'Công cụ BI', 3, N'Xây dựng Dashboard báo cáo DAX');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (17, 5, N'Pandas', N'Thư viện dữ liệu', 4, N'Làm sạch và biến đổi dữ liệu');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (18, 6, N'Python', N'Ngôn ngữ lập trình', 5, N'Thành thạo lập trình AI/ML');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (19, 6, N'PyTorch', N'Framework / Thư viện', 4, N'Huấn luyện mô hình CNN, Transformer');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (20, 6, N'Scikit-Learn', N'Framework / Thư viện', 4, N'Các thuật toán Machine Learning cổ điển');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (21, 6, N'Computer Vision', N'Chuyên ngành AI', 3, N'Nhận diện vật thể YOLO, OpenCV');
INSERT INTO dbo.KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu) VALUES (22, 6, N'Toán rời rạc & Đại số tuyến tính', N'Nền tảng toán', 4, N'Ma trận, tối ưu hóa Gradient');
SET IDENTITY_INSERT dbo.KY_NANG OFF;
GO

-- Dữ liệu bảng CHUNG_CHI
SET IDENTITY_INSERT dbo.CHUNG_CHI ON;
INSERT INTO dbo.CHUNG_CHI (ma_chung_chi, ma_nguoi_dung, ten_chung_chi, to_chuc_cap, ngay_cap, ngay_het_han, duong_dan_xac_thuc) VALUES (1, 1, N'TOEIC 785', N'ETS', N'2023-08-15', N'2025-08-15', N'https://www.iigvietnam.com');
INSERT INTO dbo.CHUNG_CHI (ma_chung_chi, ma_nguoi_dung, ten_chung_chi, to_chuc_cap, ngay_cap, ngay_het_han, duong_dan_xac_thuc) VALUES (2, 1, N'Python PCEP Certified Entry-Level', N'Python Institute', N'2023-11-20', N'', N'https://pythoninstitute.org');
INSERT INTO dbo.CHUNG_CHI (ma_chung_chi, ma_nguoi_dung, ten_chung_chi, to_chuc_cap, ngay_cap, ngay_het_han, duong_dan_xac_thuc) VALUES (3, 1, N'SQL for Data Science', N'Coursera (UC Davis)', N'2024-02-10', N'', N'https://coursera.org');
INSERT INTO dbo.CHUNG_CHI (ma_chung_chi, ma_nguoi_dung, ten_chung_chi, to_chuc_cap, ngay_cap, ngay_het_han, duong_dan_xac_thuc) VALUES (4, 4, N'Meta Front-End Developer Professional', N'Coursera (Meta)', N'2024-01-15', N'', N'https://coursera.org');
INSERT INTO dbo.CHUNG_CHI (ma_chung_chi, ma_nguoi_dung, ten_chung_chi, to_chuc_cap, ngay_cap, ngay_het_han, duong_dan_xac_thuc) VALUES (5, 4, N'IELTS Academic 6.5', N'British Council', N'2023-09-10', N'2025-09-10', N'https://britishcouncil.vn');
INSERT INTO dbo.CHUNG_CHI (ma_chung_chi, ma_nguoi_dung, ten_chung_chi, to_chuc_cap, ngay_cap, ngay_het_han, duong_dan_xac_thuc) VALUES (6, 5, N'Google Data Analytics Professional Certificate', N'Coursera (Google)', N'2024-03-12', N'', N'https://coursera.org');
INSERT INTO dbo.CHUNG_CHI (ma_chung_chi, ma_nguoi_dung, ten_chung_chi, to_chuc_cap, ngay_cap, ngay_het_han, duong_dan_xac_thuc) VALUES (7, 5, N'TOEIC 750', N'IIG Việt Nam', N'2023-10-05', N'2025-10-05', N'https://iigvietnam.com');
INSERT INTO dbo.CHUNG_CHI (ma_chung_chi, ma_nguoi_dung, ten_chung_chi, to_chuc_cap, ngay_cap, ngay_het_han, duong_dan_xac_thuc) VALUES (8, 6, N'DeepLearning.AI TensorFlow Developer', N'Coursera', N'2024-04-20', N'', N'https://deeplearning.ai');
SET IDENTITY_INSERT dbo.CHUNG_CHI OFF;
GO

-- Dữ liệu bảng KINH_NGHIEM
SET IDENTITY_INSERT dbo.KINH_NGHIEM ON;
INSERT INTO dbo.KINH_NGHIEM (ma_kinh_nghiem, ma_nguoi_dung, ten_cong_viec_du_an, ten_don_vi_cong_ty, loai_hinh_vai_tro, ngay_bat_dau, ngay_ket_thuc, mo_ta_chi_tiet) VALUES (1, 1, N'Thực tập sinh Backend (Python Intern)', N'Công ty Cổ phần Công nghệ ABC', N'Thực tập sinh', N'2024-06-01', N'2024-09-30', N'Tham gia viết API xác thực người dùng bằng JWT, tối ưu hóa câu truy vấn SQL giảm 35% thời gian phản hồi.');
INSERT INTO dbo.KINH_NGHIEM (ma_kinh_nghiem, ma_nguoi_dung, ten_cong_viec_du_an, ten_don_vi_cong_ty, loai_hinh_vai_tro, ngay_bat_dau, ngay_ket_thuc, mo_ta_chi_tiet) VALUES (2, 1, N'Trưởng nhóm Đồ án môn học Web Bán hàng', N'Dự án cá nhân / Nhóm sinh viên', N'Đồ án', N'2023-09-01', N'2023-12-20', N'Thiết kế kiến trúc MVC bằng Flask, cơ sở dữ liệu PostgreSQL, tích hợp cổng thanh toán Sandbox VNPAY.');
INSERT INTO dbo.KINH_NGHIEM (ma_kinh_nghiem, ma_nguoi_dung, ten_cong_viec_du_an, ten_don_vi_cong_ty, loai_hinh_vai_tro, ngay_bat_dau, ngay_ket_thuc, mo_ta_chi_tiet) VALUES (3, 4, N'Frontend Developer Intern', N'VNG Corporation', N'Thực tập sinh', N'2024-06-01', N'2024-09-30', N'Xây dựng các component giao diện bằng ReactJS và tối ưu hiệu năng tải trang.');
INSERT INTO dbo.KINH_NGHIEM (ma_kinh_nghiem, ma_nguoi_dung, ten_cong_viec_du_an, ten_don_vi_cong_ty, loai_hinh_vai_tro, ngay_bat_dau, ngay_ket_thuc, mo_ta_chi_tiet) VALUES (4, 5, N'Data Analyst Collaborator', N'Shopee Việt Nam', N'Cộng tác viên', N'2024-04-01', N'2024-08-30', N'Xây dựng báo cáo theo dõi hành vi mua sắm và phân tích phễu chuyển đổi bằng SQL & Power BI.');
INSERT INTO dbo.KINH_NGHIEM (ma_kinh_nghiem, ma_nguoi_dung, ten_cong_viec_du_an, ten_don_vi_cong_ty, loai_hinh_vai_tro, ngay_bat_dau, ngay_ket_thuc, mo_ta_chi_tiet) VALUES (5, 6, N'Nghiên cứu viên Sinh viên (AI Lab)', N'BKAI Research Center', N'Dự án nghiên cứu', N'2023-10-01', N'2024-09-01', N'Nghiên cứu mô hình nhận diện văn bản tiếng Việt OCR bằng PyTorch.');
SET IDENTITY_INSERT dbo.KINH_NGHIEM OFF;
GO

-- Dữ liệu bảng TIN_TUYEN_DUNG
SET IDENTITY_INSERT dbo.TIN_TUYEN_DUNG ON;
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (1, N'Junior/Mid Backend Developer (Python/Flask/FastAPI)', N'FPT Software', 1, N'Hà Nội / Đà Nẵng', N'14 - 25 triệu VNĐ', N'1 - 2 năm', N'["Python", "Flask", "SQL", "Git", "RESTful API"]', N'["PostgreSQL", "Docker", "Redis", "FastAPI"]', N'["Python PCEP/PCAP", "AWS Certified Cloud Practitioner"]', N'2026-11-30', N'Tham gia phát triển các phân hệ dịch vụ tài chính vi mô, viết API hiệu năng cao và thiết kế CSDL.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (2, N'Java Backend Engineer (Spring Boot)', N'Viettel Telecom', 1, N'Hà Nội', N'18 - 35 triệu VNĐ', N'2+ năm', N'["Java", "Spring Boot", "SQL", "OOP", "Git"]', N'["Kafka", "Docker", "Oracle DB", "Microservices"]', N'["Oracle Certified Professional Java", "AWS Solutions Architect"]', N'2026-12-15', N'Xây dựng các hệ thống Core Billing, tích hợp cổng thanh toán viễn thông với lưu lượng hàng triệu giao dịch/ngày.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (3, N'Node.js Backend Developer', N'VNG Corporation', 1, N'TP. Hồ Chí Minh', N'16 - 28 triệu VNĐ', N'1 - 3 năm', N'["JavaScript", "Node.js", "ExpressJS", "SQL", "RESTful API"]', N'["MongoDB", "Redis", "Docker", "RabbitMQ"]', N'["Node.js Application Developer", "MongoDB Associate"]', N'2026-11-25', N'Phát triển hệ thống backend cho nền tảng mạng xã hội và giải trí trực tuyến.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (4, N'Golang Backend Developer', N'Momo (M-Service)', 1, N'TP. Hồ Chí Minh', N'20 - 40 triệu VNĐ', N'2+ năm', N'["Golang", "Microservices", "SQL", "Git", "Clean Architecture"]', N'["gRPC", "Redis", "Kafka", "Kubernetes"]', N'["AWS Certified Developer"]', N'2026-12-01', N'Nâng cấp và duy trì các dịch vụ thanh toán QR, ví điện tử với yêu cầu tính sẵn sàng cao (High Availability).', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (5, N'Frontend Developer (ReactJS / TypeScript)', N'Shopee Vietnam', 2, N'TP. Hồ Chí Minh', N'18 - 32 triệu VNĐ', N'1 - 3 năm', N'["HTML5/CSS3", "JavaScript", "TypeScript", "ReactJS", "Redux"]', N'["Webpack", "Tailwind CSS", "Next.js", "Jest"]', N'["Meta Front-End Developer"]', N'2026-12-10', N'Phát triển các tính năng giỏ hàng, thanh toán và chiến dịch khuyến mãi trên cổng thương mại điện tử Shopee.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (6, N'Web Frontend Developer (Vue.js / Bootstrap)', N'Tiki Corporation', 2, N'TP. Hồ Chí Minh', N'15 - 26 triệu VNĐ', N'1 - 2 năm', N'["HTML5/CSS3", "JavaScript", "VueJS", "Bootstrap", "Git"]', N'["Pinia", "Sass", "RESTful API", "Vite"]', N'[]', N'2026-11-20', N'Xây dựng dashboard quản trị cho người bán hàng và cổng tiếp nhận đơn hàng.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (7, N'Junior Frontend Developer (ReactJS/HTML/CSS)', N'NashTech Vietnam', 2, N'Hà Nội / TP.HCM', N'10 - 18 triệu VNĐ', N'Dưới 1 năm / Fresher', N'["HTML5/CSS3", "JavaScript", "ReactJS", "Bootstrap", "Git"]', N'["RESTful API", "CSS Modules", "NPM"]', N'[]', N'2026-12-05', N'Cơ hội cho sinh viên mới ra trường tham gia dự án phần mềm cho khách hàng châu Âu và Úc.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (8, N'Senior Frontend Engineer (Angular / TypeScript)', N'KMS Technology', 2, N'Đà Nẵng', N'25 - 45 triệu VNĐ', N'3+ năm', N'["TypeScript", "Angular", "RxJS", "HTML5/CSS3", "Unit Test"]', N'["NgRx", "SCSS", "CI/CD", "Karma"]', N'[]', N'2026-12-20', N'Chịu trách nhiệm kiến trúc frontend cho ứng dụng chăm sóc sức khỏe điện tử (Healthcare SaaS).', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (9, N'Fullstack Developer (Node.js & ReactJS)', N'ZaloPay', 3, N'TP. Hồ Chí Minh', N'22 - 38 triệu VNĐ', N'2+ năm', N'["JavaScript", "TypeScript", "ReactJS", "Node.js", "SQL"]', N'["PostgreSQL", "Docker", "Redis", "Next.js"]', N'["AWS Certified Developer"]', N'2026-11-30', N'Xây dựng các mini-app trên nền tảng Zalo, tích hợp ví thanh toán và quản trị merchant.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (10, N'Fullstack Software Engineer (.NET & Angular)', N'One Mount Group', 3, N'Hà Nội', N'20 - 36 triệu VNĐ', N'2+ năm', N'["C#", ".NET Core", "Angular", "SQL", "Git"]', N'["SQL Server", "Docker", "Azure", "Microservices"]', N'["Microsoft Certified: Azure Developer Associate"]', N'2026-12-18', N'Phát triển các giải pháp số hóa chuỗi cung ứng VinShop và bất động sản OneHousing.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (11, N'Fullstack Web Developer (Python & Vue.js)', N'VNPT Information Technology', 3, N'Hà Nội', N'15 - 25 triệu VNĐ', N'1 - 3 năm', N'["Python", "Django", "VueJS", "JavaScript", "SQL"]', N'["PostgreSQL", "Bootstrap", "Git", "Docker"]', N'[]', N'2026-12-12', N'Phát triển cổng thông tin hành chính công và các phần mềm dịch vụ giáo dục điện tử.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (12, N'Junior Data Analyst', N'Techcombank', 4, N'Hà Nội', N'14 - 22 triệu VNĐ', N'0 - 1 năm / Fresher', N'["SQL", "Python", "Power BI", "Excel nâng cao", "Phân tích dữ liệu"]', N'["Pandas", "Oracle DB", "Jupyter Notebook"]', N'["PL-300: Microsoft Power BI Data Analyst", "Google Data Analytics Certificate"]', N'2026-12-05', N'Phân tích hành vi chi tiêu thẻ tín dụng, xây dựng các dashboard theo dõi chỉ số rủi ro tín dụng hàng tuần.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (13, N'BI Data Analyst (Tableau & SQL)', N'VPBank', 4, N'Hà Nội', N'18 - 30 triệu VNĐ', N'1 - 3 năm', N'["SQL", "Tableau", "Data Modeling", "Xác suất thống kê", "Python"]', N'["PostgreSQL", "Snowflake", "Excel"]', N'["Tableau Desktop Specialist"]', N'2026-12-25', N'Xây dựng mô hình dữ liệu trực quan phục vụ khối Khách hàng Doanh nghiệp SME.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (14, N'Data Analyst - Product & Marketing', N'Chợ Tốt (Carousell Group)', 4, N'TP. Hồ Chí Minh', N'16 - 28 triệu VNĐ', N'1 - 2 năm', N'["SQL", "Python", "Google Analytics", "A/B Testing", "Trực quan hóa dữ liệu"]', N'["BigQuery", "Looker Studio", "Pandas"]', N'["Google Data Analytics Certificate"]', N'2026-11-28', N'Đo lường hiệu quả các chiến dịch Marketing, phân tích phễu chuyển đổi người dùng trên app Chợ Tốt.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (15, N'DevOps Engineer (AWS & Kubernetes)', N'FPT Software', 5, N'Hà Nội', N'22 - 40 triệu VNĐ', N'2+ năm', N'["Linux", "Docker", "Kubernetes", "AWS", "CI/CD"]', N'["Terraform", "GitLab CI", "Prometheus", "Helm"]', N'["AWS Certified Solutions Architect", "CKA (Certified Kubernetes Administrator)"]', N'2026-12-30', N'Vận hành hạ tầng Cloud cho các khách hàng tài chính quốc tế, đảm bảo uptime 99.9%.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (16, N'Cloud Infrastructure Engineer', N'MB Bank', 5, N'Hà Nội', N'20 - 38 triệu VNĐ', N'1 - 3 năm', N'["Linux", "Shell Scripting", "Docker", "CI/CD", "Mạng máy tính"]', N'["Jenkins", "Ansible", "Kubernetes", "Grafana"]', N'["Red Hat Certified System Administrator (RHCSA)", "AWS SysOps"]', N'2026-12-15', N'Tự động hóa triển khai ứng dụng ngân hàng số MBBank, cấu hình cảnh báo và giám sát hệ thống tự động.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (17, N'Site Reliability Engineer (SRE / DevOps)', N'VNG Corporation', 5, N'TP. Hồ Chí Minh', N'25 - 45 triệu VNĐ', N'2+ năm', N'["Linux", "Python", "Docker", "Kubernetes", "Troubleshooting"]', N'["ELK Stack", "Prometheus", "Kafka", "GitOps"]', N'["CKA (Certified Kubernetes Administrator)"]', N'2026-12-10', N'Duy trì tính sẵn sàng và khả năng chịu tải cho các game bom tấn và ứng dụng Zalo.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (18, N'Manual & Automation QA Tester', N'KMS Technology', 6, N'TP. Hồ Chí Minh', N'14 - 24 triệu VNĐ', N'1 - 2 năm', N'["Kiểm thử phần mềm", "Thiết kế Test Case", "Postman", "Selenium", "SQL"]', N'["Jira", "TestRail", "Java", "Git"]', N'["ISTQB Foundation Level (CTFL)"]', N'2026-12-05', N'Thực hiện kiểm thử chức năng và phi chức năng, viết script tự động hóa kiểm thử hồi quy cho ứng dụng web.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (19, N'QC Tester (Fresher / Junior)', N'FPT Information System', 6, N'Hà Nội', N'9 - 15 triệu VNĐ', N'0 - 1 năm', N'["Kiểm thử phần mềm", "Tạo Test Case", "SQL cơ bản", "Kỹ năng giao tiếp"]', N'["Jira", "Postman", "Excel"]', N'["ISTQB Foundation Level (CTFL)"]', N'2026-11-20', N'Hỗ trợ đội ngũ kiểm thử các phần mềm chính phủ điện tử, quản lý bệnh viện và giao thông thông minh.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (20, N'Senior Automation Test Engineer (Cypress / Playwright)', N'Shopee Vietnam', 6, N'TP. Hồ Chí Minh', N'25 - 40 triệu VNĐ', N'3+ năm', N'["Automation Testing", "JavaScript", "TypeScript", "CI/CD Integration", "API Testing"]', N'["Cypress", "Playwright", "Jenkins", "Docker"]', N'["ISTQB Advanced Level Test Automation Engineer"]', N'2026-12-28', N'Thiết kế và duy trì framework kiểm thử tự động quy mô lớn cho hệ sinh thái Shopee.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (21, N'Flutter Mobile Developer', N'Momo (M-Service)', 7, N'TP. Hồ Chí Minh', N'16 - 30 triệu VNĐ', N'1 - 3 năm', N'["Flutter", "Dart", "RESTful API", "Git", "State Management (Bloc/Provider)"]', N'["Firebase", "SQLite", "GraphQL"]', N'[]', N'2026-12-15', N'Phát triển các module tiện ích mới trên siêu ứng dụng MoMo phục vụ hơn 30 triệu người dùng.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (22, N'React Native Developer', N'Tiki Corporation', 7, N'TP. Hồ Chí Minh', N'15 - 28 triệu VNĐ', N'1 - 2 năm', N'["React Native", "JavaScript", "TypeScript", "Redux", "Mobile UI"]', N'["Xcode", "Android Studio", "Firebase"]', N'[]', N'2026-12-08', N'Tối ưu hóa hiệu năng ứng dụng Tiki trên iOS và Android, cải thiện tốc độ load trang danh mục sản phẩm.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (23, N'iOS Native Developer (Swift)', N'Viettel Digital', 7, N'Hà Nội', N'20 - 35 triệu VNĐ', N'2+ năm', N'["Swift", "iOS SDK", "AutoLayout", "OOP", "Git"]', N'["CoreData", "Combine", "CocoaPods", "Fastlane"]', N'["Apple Certified Developer"]', N'2026-12-31', N'Phát triển ứng dụng tài chính số Viettel Money phiên bản iOS native, bảo mật dữ liệu cấp độ ngân hàng.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (24, N'Android Native Developer (Kotlin)', N'VNPT Technology', 7, N'Hà Nội', N'16 - 28 triệu VNĐ', N'1 - 3 năm', N'["Kotlin", "Android SDK", "Jetpack Compose", "Coroutines", "MVVM"]', N'["Retrofit", "Room DB", "Dagger Hilt"]', N'["Google Associate Android Developer"]', N'2026-12-10', N'Xây dựng ứng dụng nhà thông minh (Smart Home IoT) kết nối thiết bị phần cứng của VNPT.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (25, N'AI / Machine Learning Engineer', N'VinAI Research', 8, N'Hà Nội', N'25 - 50 triệu VNĐ', N'1 - 3 năm', N'["Python", "PyTorch", "Toán giải tích & Đại số", "Machine Learning", "Git"]', N'["OpenCV", "CUDA", "Docker", "Linux"]', N'["DeepLearning.AI Machine Learning Specialization", "AWS Certified Machine Learning"]', N'2026-12-25', N'Nghiên cứu và huấn luyện các mô hình thị giác máy tính cho hệ thống lái xe tự hành VinFast.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (26, N'NLP Engineer (Natural Language Processing)', N'Zalo AI Lab', 8, N'TP. Hồ Chí Minh', N'22 - 42 triệu VNĐ', N'2+ năm', N'["Python", "NLP", "PyTorch", "Transformers", "Xử lý văn bản tiếng Việt"]', N'["HuggingFace", "BERT", "FastAPI", "ONNX"]', N'["DeepLearning.AI Deep Learning Specialization"]', N'2026-12-20', N'Phát triển trợ lý giọng nói Kiki, mô hình tóm tắt văn bản và chatbot thông minh trên hệ sinh thái Zalo.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (27, N'Computer Vision Engineer', N'FPT Software (FPT AI)', 8, N'Quy Nhơn / Hà Nội', N'20 - 38 triệu VNĐ', N'1 - 3 năm', N'["Python", "Computer Vision", "TensorFlow", "PyTorch", "OpenCV"]', N'["YOLO", "Docker", "Triton Server"]', N'[]', N'2026-12-15', N'Xây dựng giải pháp định danh khách hàng điện tử (eKYC) và nhận diện tài liệu OCR cho ngân hàng.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (28, N'Backend Developer (Node.js & AWS Serverless)', N'TymeX Vietnam', 1, N'TP. Hồ Chí Minh', N'20 - 35 triệu VNĐ', N'2+ năm', N'["JavaScript", "TypeScript", "Node.js", "RESTful API", "SQL"]', N'["AWS Lambda", "DynamoDB", "Docker", "Jest"]', N'["AWS Certified Cloud Practitioner"]', N'2026-11-30', N'Phát triển nền tảng ngân hàng số đa quốc gia (Digital Banking) phục vụ hàng triệu khách hàng Nam Phi & Philippines.', N'2026-11-03 03:50:08');
INSERT INTO dbo.TIN_TUYEN_DUNG (ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec, muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json, chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang) VALUES (29, N'Frontend Developer (ReactJS & WebSockets)', N'SSI Securities (Chứng khoán SSI)', 2, N'Hà Nội', N'18 - 32 triệu VNĐ', N'2+ năm', N'["HTML5/CSS3", "JavaScript", "ReactJS", "TypeScript", "WebSockets"]', N'["Chart.js", "Redux Toolkit", "Ant Design", "TradingView API"]', N'[]', N'2026-12-18', N'Xây dựng bảng giá chứng khoán thời gian thực tốc độ mili-giây, biểu đồ kỹ thuật chuyên sâu.', N'2026-11-03 03:50:08');
SET IDENTITY_INSERT dbo.TIN_TUYEN_DUNG OFF;
GO

-- Dữ liệu bảng KE_HOACH_HOC_TAP
SET IDENTITY_INSERT dbo.KE_HOACH_HOC_TAP ON;
INSERT INTO dbo.KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap) VALUES (1, 1, N'Học và thực hành chuyên sâu Docker & Containerization', N'Kỹ năng thiếu (Backend)', N'skill', N'done', N'2026-11-30', N'Làm chủ viết Multi-stage Dockerfile, Docker Compose và kết nối mạng giữa các container.');
INSERT INTO dbo.KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap) VALUES (2, 1, N'Ôn thi chứng chỉ AWS Certified Cloud Practitioner (CLF-C02)', N'Chứng chỉ nghề nghiệp', N'certificate', N'done', N'2026-12-25', N'Học qua khóa học Stephane Maarek trên Udemy, luyện 6 đề thi thử.');
INSERT INTO dbo.KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap) VALUES (3, 1, N'Nghiên cứu kiến trúc Microservices và gRPC với Go', N'Nâng cao kỹ năng', N'skill', N'done', N'2027-01-15', N'Đọc sách Designing Data-Intensive Applications của Martin Kleppmann.');
INSERT INTO dbo.KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap) VALUES (4, 1, N'Xây dựng đồ án cá nhân: RESTful API mạng xã hội thu nhỏ', N'Kinh nghiệm / Portfolio', N'project', N'done', N'2026-09-15', N'Hoàn thành API với Flask, Redis caching, Celery background worker và PostgreSQL.');
INSERT INTO dbo.KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap) VALUES (5, 1, N'Thực hành cấu hình CI/CD Pipeline bằng GitHub Actions', N'Kỹ năng thiếu (DevOps)', N'skill', N'done', N'2026-12-10', N'Tự động chạy pytest và deploy container lên AWS EC2 khi push code.');
INSERT INTO dbo.KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap) VALUES (6, 4, N'Hoàn thành khóa học TypeScript nâng cao', N'Kỹ năng Frontend', N'skill', N'in_progress', N'2026-12-01', N'Áp dụng TypeScript vào dự án tốt nghiệp');
INSERT INTO dbo.KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap) VALUES (7, 4, N'Tìm hiểu VueJS 3 & NuxtJS', N'Framework mở rộng', N'skill', N'todo', N'2026-12-20', N'Mở rộng cơ hội ứng tuyển Frontend');
INSERT INTO dbo.KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap) VALUES (8, 5, N'Luyện tập Tableau Desktop Specialist', N'Chứng chỉ BI', N'certificate', N'in_progress', N'2026-12-10', N'Bổ sung kỹ năng trực quan hóa dữ liệu');
INSERT INTO dbo.KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap) VALUES (9, 6, N'Triển khai mô hình AI với Docker & FastAPI', N'MLOps', N'skill', N'in_progress', N'2026-12-15', N'Đóng gói model phục vụ inference thực tế');
SET IDENTITY_INSERT dbo.KE_HOACH_HOC_TAP OFF;
GO

-- Dữ liệu bảng GOI_Y_KHOA_HOC
SET IDENTITY_INSERT dbo.GOI_Y_KHOA_HOC ON;
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (1, N'Java', N'Java Programming and Software Engineering Fundamentals', N'Coursera (Duke University)', N'course', N'6 tuần', N'https://www.coursera.org', N'Nắm vững lập trình hướng đối tượng OOP, cấu trúc dữ liệu và thiết kế phần mềm với Java.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (2, N'Spring Boot', N'Master Microservices with Spring Boot and Spring Cloud', N'Udemy', N'course', N'8 tuần', N'https://www.udemy.com', N'Xây dựng RESTful API, bảo mật Spring Security, JPA/Hibernate và kiến trúc Microservices.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (3, N'Node.js', N'The Complete Node.js Developer Course', N'Udemy', N'course', N'5 tuần', N'https://www.udemy.com', N'Phát triển ứng dụng Backend thời gian thực với Node.js, ExpressJS, MongoDB và Socket.io.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (4, N'RESTful API', N'Thiết kế và Bảo mật RESTful API chuẩn Doanh nghiệp', N'F8 / Coursera', N'course', N'3 tuần', N'https://www.coursera.org', N'Chuẩn hóa HTTP Methods, Status Codes, xác thực JWT/OAuth2 và tài liệu hóa bằng Swagger/OpenAPI.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (5, N'Redis', N'Redis University - RU101: Introduction to Redis Data Structures', N'Redis University', N'certificate', N'3 tuần', N'https://university.redis.com', N'Ứng dụng In-Memory Caching, Pub/Sub, Session Store và tối ưu độ trễ truy vấn Backend.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (6, N'Docker', N'Docker & Kubernetes: The Practical Guide', N'Udemy', N'course', N'4 tuần', N'https://www.udemy.com', N'Thực hành đóng gói ứng dụng với Multi-stage Dockerfile, Docker Compose và triển khai Container.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (7, N'Golang', N'Programming with Google Go Specialization', N'Coursera (UC Irvine)', N'course', N'6 tuần', N'https://www.coursera.org', N'Làm chủ Concurrency (Goroutines, Channels) và xây dựng dịch vụ hiệu năng cao với Golang.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (8, N'Microservices', N'Microservices Architecture & System Design', N'edX / Udemy', N'course', N'6 tuần', N'https://www.edx.org', N'Thiết kế hệ thống phân tán, API Gateway, Message Queue (Kafka/RabbitMQ) và Circuit Breaker.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (9, N'ReactJS', N'Meta Front-End Developer Professional Certificate', N'Coursera (Meta)', N'certificate', N'8 tuần', N'https://www.coursera.org', N'Xây dựng giao diện Single Page Application hiện đại với React Hooks, State Management và Testing.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (10, N'TypeScript', N'Understanding TypeScript - 2026 Edition', N'Udemy', N'course', N'4 tuần', N'https://www.udemy.com', N'Kiểm soát kiểu dữ liệu tĩnh, Generics, Decorators và tích hợp TypeScript vào dự án React/Node.js.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (11, N'VueJS', N'Vue - The Complete Guide (incl. Router & Composition API)', N'Udemy', N'course', N'5 tuần', N'https://www.udemy.com', N'Phát triển Frontend với Vue 3 Composition API, Pinia và Vite.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (12, N'Power BI', N'PL-300: Microsoft Power BI Data Analyst', N'Microsoft Learn', N'certificate', N'6 tuần', N'https://learn.microsoft.com', N'Xử lý dữ liệu với Power Query, ngôn ngữ DAX và thiết kế báo cáo BI trực quan.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (13, N'Tableau', N'Data Visualization with Tableau Specialization', N'Coursera (UC Davis)', N'certificate', N'5 tuần', N'https://www.coursera.org', N'Trực quan hóa dữ liệu chuyên nghiệp và xây dựng Interactive Storytelling Dashboard.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (14, N'Linux', N'Introduction to Linux (LFS101)', N'The Linux Foundation', N'certificate', N'4 tuần', N'https://training.linuxfoundation.org', N'Quản trị hệ điều hành Linux, phân quyền, tiến trình và viết kịch bản Bash Shell.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (15, N'Kubernetes', N'Certified Kubernetes Administrator (CKA) Prep Course', N'KodeKloud / Linux Foundation', N'certificate', N'8 tuần', N'https://kodekloud.com', N'Quản trị cụm Kubernetes, Pods, Deployments, Services, Ingress và Helm Charts.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (16, N'AWS', N'AWS Certified Cloud Practitioner (CLF-C02)', N'AWS Skill Builder', N'certificate', N'6 tuần', N'https://explore.skillbuilder.aws', N'Kiến thức nền tảng về điện toán đám mây AWS: EC2, S3, RDS, IAM, VPC và Lambda.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (17, N'CI/CD', N'CI/CD Pipelines with GitHub Actions & GitLab CI', N'Udemy', N'course', N'3 tuần', N'https://www.udemy.com', N'Tự động hóa kiểm thử, đóng gói Docker và triển khai liên tục lên máy chủ Cloud.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (18, N'Selenium', N'Selenium WebDriver with Java/Python - Automation Testing', N'Udemy', N'course', N'5 tuần', N'https://www.udemy.com', N'Xây dựng Page Object Model (POM) và kịch bản kiểm thử tự động cho ứng dụng Web.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (19, N'Postman', N'Postman API Fundamentals Student Expert', N'Postman Academy', N'certificate', N'2 tuần', N'https://academy.postman.com', N'Kiểm thử tự động RESTful API, viết test script và chạy Collection bằng Newman.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (20, N'Flutter', N'Flutter & Dart - The Complete Guide', N'Udemy', N'course', N'6 tuần', N'https://www.udemy.com', N'Phát triển ứng dụng di động đa nền tảng iOS & Android với Flutter và Bloc/Provider.');
INSERT INTO dbo.GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung) VALUES (21, N'PyTorch', N'Deep Learning Specialization', N'Coursera (DeepLearning.AI)', N'certificate', N'8 tuần', N'https://www.coursera.org', N'Huấn luyện mạng nơ-ron sâu CNN, RNN, Transformers với PyTorch và ứng dụng thực tế.');
SET IDENTITY_INSERT dbo.GOI_Y_KHOA_HOC OFF;
GO

-- Dữ liệu bảng LICH_SU_DOI_SANH
SET IDENTITY_INSERT dbo.LICH_SU_DOI_SANH ON;
INSERT INTO dbo.LICH_SU_DOI_SANH (ma_lich_su, ma_nguoi_dung, ma_vi_tri, ten_vi_tri, diem_phu_hop_phan_tram, ky_nang_da_co_json, ky_nang_con_thieu_json, ngay_danh_gia) VALUES (1, 1, 1, N'Lập trình viên Backend (Backend Developer)', 50, N'["Python", "SQL", "Docker", "Git", "Flask", "JavaScript"]', N'["Java", "Node.js", "RESTful API", "Redis", "Spring Boot", "Golang"]', N'2026-11-06 12:05:01');
INSERT INTO dbo.LICH_SU_DOI_SANH (ma_lich_su, ma_nguoi_dung, ma_vi_tri, ten_vi_tri, diem_phu_hop_phan_tram, ky_nang_da_co_json, ky_nang_con_thieu_json, ngay_danh_gia) VALUES (2, 1, 4, N'Chuyên viên Phân tích Dữ liệu (Data Analyst)', 38, N'["Python", "SQL", "Phân tích dữ liệu"]', N'["Power BI", "Tableau", "Excel nâng cao", "Xác suất thống kê", "Pandas"]', N'2026-11-06 12:05:01');
INSERT INTO dbo.LICH_SU_DOI_SANH (ma_lich_su, ma_nguoi_dung, ma_vi_tri, ten_vi_tri, diem_phu_hop_phan_tram, ky_nang_da_co_json, ky_nang_con_thieu_json, ngay_danh_gia) VALUES (3, 1, 1, N'Lập trình viên Backend (Backend Developer)', 41, N'["Python", "Java", "SQL", "Docker", "Git", "Flask", "JavaScript"]', N'["Node.js", "RESTful API", "Redis", "Spring Boot", "OOP", "ExpressJS", "Golang", "Microservices", "Clean Architecture", "TypeScript"]', N'2026-11-06 12:05:02');
INSERT INTO dbo.LICH_SU_DOI_SANH (ma_lich_su, ma_nguoi_dung, ma_vi_tri, ten_vi_tri, diem_phu_hop_phan_tram, ky_nang_da_co_json, ky_nang_con_thieu_json, ngay_danh_gia) VALUES (4, 2, 1, N'Lập trình viên Backend (Backend Developer)', 0, N'[]', N'["Python", "Java", "Node.js", "SQL", "Docker", "RESTful API", "Redis", "Git", "Flask", "Spring Boot", "OOP", "JavaScript", "ExpressJS", "Golang", "Microservices", "Clean Architecture", "TypeScript"]', N'2026-11-06 14:22:59');
SET IDENTITY_INSERT dbo.LICH_SU_DOI_SANH OFF;
GO
