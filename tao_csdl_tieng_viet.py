"""
tao_csdl_tieng_viet.py - Khởi tạo và nạp dữ liệu cho 11 bảng CSDL tiếng Việt không dấu
Đề tài: NLCNPM23CS-38

Tạo ra:
1. csdl_nien_luan.db : File SQLite chứa đúng 11 bảng tiếng Việt không dấu.
2. database.db       : Đồng bộ 11 bảng tiếng Việt không dấu vào CSDL chính của ứng dụng.
3. schema_tieng_viet.sql : Script chuẩn SQL Server (T-SQL / SSMS) tạo Database, 11 bảng và nạp dữ liệu mẫu.
"""

import os
import sqlite3
from seed_data import seed_database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_SQL_PATH = os.path.join(BASE_DIR, "schema_tieng_viet.sql")
DB_MAIN_PATH = os.path.join(BASE_DIR, "database.db")
DB_VN_PATH = os.path.join(BASE_DIR, "csdl_nien_luan.db")

SQLITE_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS NGUOI_DUNG (
    ma_nguoi_dung INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    mat_khau_bam TEXT NOT NULL,
    vai_tro TEXT DEFAULT 'student',
    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS VI_TRI_NGHE_NGHIEP (
    ma_vi_tri INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_vi_tri TEXT NOT NULL,
    ma_dinh_danh TEXT DEFAULT '',
    mo_ta_cong_viec TEXT DEFAULT '',
    ky_nang_cot_loi_json TEXT DEFAULT '[]',
    muc_do_nhu_cau TEXT DEFAULT 'Cao'
);

CREATE TABLE IF NOT EXISTS HO_SO_SINH_VIEN (
    ma_ho_so INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL UNIQUE,
    ho_ten TEXT NOT NULL,
    ma_so_sinh_vien TEXT DEFAULT '',
    email TEXT NOT NULL,
    so_dien_thoai TEXT DEFAULT '',
    truong_dai_hoc TEXT DEFAULT '',
    khoa_vien TEXT DEFAULT '',
    chuyen_nganh TEXT DEFAULT '',
    nien_khoa TEXT DEFAULT '',
    diem_gpa TEXT DEFAULT '0.0',
    ma_vi_tri_muc_tieu INTEGER DEFAULT 1,
    gioi_thieu_ban_than TEXT DEFAULT '',
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE,
    FOREIGN KEY (ma_vi_tri_muc_tieu) REFERENCES VI_TRI_NGHE_NGHIEP (ma_vi_tri) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS HOC_PHAN (
    ma_hoc_phan INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL,
    ma_mon_hoc TEXT NOT NULL,
    ten_hoc_phan TEXT NOT NULL,
    so_tin_chi INTEGER DEFAULT 3,
    diem_chu TEXT DEFAULT 'A',
    hoc_ky TEXT DEFAULT '',
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS KY_NANG (
    ma_ky_nang INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL,
    ten_ky_nang TEXT NOT NULL,
    nhom_ky_nang TEXT DEFAULT 'Ngôn ngữ lập trình',
    muc_do_thanh_thao INTEGER DEFAULT 3 CHECK (muc_do_thanh_thao >= 1 AND muc_do_thanh_thao <= 5),
    ghi_chu TEXT DEFAULT '',
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CHUNG_CHI (
    ma_chung_chi INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL,
    ten_chung_chi TEXT NOT NULL,
    to_chuc_cap TEXT NOT NULL,
    ngay_cap TEXT DEFAULT '',
    ngay_het_han TEXT DEFAULT '',
    duong_dan_xac_thuc TEXT DEFAULT '',
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS KINH_NGHIEM (
    ma_kinh_nghiem INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL,
    ten_cong_viec_du_an TEXT NOT NULL,
    ten_don_vi_cong_ty TEXT NOT NULL,
    loai_hinh_vai_tro TEXT DEFAULT 'Thực tập sinh',
    ngay_bat_dau TEXT DEFAULT '',
    ngay_ket_thuc TEXT DEFAULT '',
    mo_ta_chi_tiet TEXT DEFAULT '',
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS TIN_TUYEN_DUNG (
    ma_tin_tuyen_dung INTEGER PRIMARY KEY AUTOINCREMENT,
    tieu_de_tin TEXT NOT NULL,
    ten_cong_ty TEXT NOT NULL,
    ma_vi_tri INTEGER NOT NULL,
    dia_diem_lam_viec TEXT DEFAULT 'Toàn quốc',
    muc_luong TEXT DEFAULT 'Thỏa thuận',
    yeu_cau_kinh_nghiem TEXT DEFAULT 'Không yêu cầu',
    ky_nang_yeu_cau_json TEXT DEFAULT '[]',
    cong_nghe_yeu_cau_json TEXT DEFAULT '[]',
    chung_chi_uu_tien_json TEXT DEFAULT '[]',
    han_nop_ho_so TEXT DEFAULT '',
    mo_ta_chi_tiet TEXT DEFAULT '',
    ngay_dang DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_vi_tri) REFERENCES VI_TRI_NGHE_NGHIEP (ma_vi_tri) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS KE_HOACH_HOC_TAP (
    ma_ke_hoach INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL,
    tieu_de_muc_tieu TEXT NOT NULL,
    danh_muc_bo_sung TEXT DEFAULT 'Kỹ năng bổ sung',
    loai_muc_tieu TEXT DEFAULT 'skill',
    trang_thai TEXT DEFAULT 'todo',
    ngay_hoan_thanh_du_kien TEXT DEFAULT '',
    ghi_chu_hoc_tap TEXT DEFAULT '',
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS GOI_Y_KHOA_HOC (
    ma_goi_y INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_ky_nang TEXT NOT NULL,
    ten_khoa_hoc_chung_chi TEXT NOT NULL,
    don_vi_cung_cap TEXT DEFAULT 'Coursera / Udemy',
    loai_goi_y TEXT DEFAULT 'course',
    thoi_luong_hoc TEXT DEFAULT '4 tuần',
    duong_dan_khoa_hoc TEXT DEFAULT '',
    mo_ta_noi_dung TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS LICH_SU_DOI_SANH (
    ma_lich_su INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL,
    ma_vi_tri INTEGER NOT NULL,
    ten_vi_tri TEXT NOT NULL,
    diem_phu_hop_phan_tram INTEGER DEFAULT 0,
    ky_nang_da_co_json TEXT DEFAULT '[]',
    ky_nang_con_thieu_json TEXT DEFAULT '[]',
    ngay_danh_gia DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE,
    FOREIGN KEY (ma_vi_tri) REFERENCES VI_TRI_NGHE_NGHIEP (ma_vi_tri) ON DELETE CASCADE
);
"""


def build_vietnamese_database():
    # Đảm bảo database.db gốc đã có đầy đủ dữ liệu mẫu
    seed_database()

    if os.path.exists(DB_VN_PATH):
        os.remove(DB_VN_PATH)

    src_conn = sqlite3.connect(DB_MAIN_PATH)
    src_conn.row_factory = sqlite3.Row
    src_conn.executescript(SQLITE_SCHEMA)

    vn_conn = sqlite3.connect(DB_VN_PATH)
    vn_conn.executescript(SQLITE_SCHEMA)

    for target_conn in (src_conn, vn_conn):
        cur = target_conn.cursor()

        for tbl in [
            "LICH_SU_DOI_SANH",
            "GOI_Y_KHOA_HOC",
            "KE_HOACH_HOC_TAP",
            "TIN_TUYEN_DUNG",
            "KINH_NGHIEM",
            "CHUNG_CHI",
            "KY_NANG",
            "HOC_PHAN",
            "HO_SO_SINH_VIEN",
            "VI_TRI_NGHE_NGHIEP",
            "NGUOI_DUNG",
        ]:
            cur.execute(f"DELETE FROM {tbl};")

        # 1. NGUOI_DUNG <- users
        for r in src_conn.execute("SELECT * FROM users"):
            cur.execute(
                """
                INSERT INTO NGUOI_DUNG (ma_nguoi_dung, ho_ten, email, mat_khau_bam, vai_tro, ngay_tao)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (r["id"], r["full_name"], r["email"], r["password_hash"], r["role"], r["created_at"]),
            )

        # 2. VI_TRI_NGHE_NGHIEP <- positions
        for r in src_conn.execute("SELECT * FROM positions"):
            cur.execute(
                """
                INSERT INTO VI_TRI_NGHE_NGHIEP (ma_vi_tri, ten_vi_tri, ma_dinh_danh, mo_ta_cong_viec, ky_nang_cot_loi_json, muc_do_nhu_cau)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (r["id"], r["name"], r["code"], r["description"], r["core_skills"], r["demand_level"]),
            )

        # 3. HO_SO_SINH_VIEN <- student_profiles
        for r in src_conn.execute("SELECT * FROM student_profiles"):
            cur.execute(
                """
                INSERT INTO HO_SO_SINH_VIEN (
                    ma_ho_so, ma_nguoi_dung, ho_ten, ma_so_sinh_vien, email, so_dien_thoai,
                    truong_dai_hoc, khoa_vien, chuyen_nganh, nien_khoa, diem_gpa, ma_vi_tri_muc_tieu, gioi_thieu_ban_than
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r["id"],
                    r["user_id"],
                    r["full_name"],
                    r["student_code"],
                    r["email"],
                    r["phone"],
                    r["university"],
                    r["faculty"],
                    r["major"],
                    r["academic_year"],
                    r["gpa"],
                    r["target_position_id"],
                    r["bio"],
                ),
            )

        # 4. HOC_PHAN <- courses
        for r in src_conn.execute("SELECT * FROM courses"):
            cur.execute(
                """
                INSERT INTO HOC_PHAN (ma_hoc_phan, ma_nguoi_dung, ma_mon_hoc, ten_hoc_phan, so_tin_chi, diem_chu, hoc_ky)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (r["id"], r["user_id"], r["code"], r["name"], r["credits"], r["grade"], r["term"]),
            )

        # 5. KY_NANG <- skills
        for r in src_conn.execute("SELECT * FROM skills"):
            cur.execute(
                """
                INSERT INTO KY_NANG (ma_ky_nang, ma_nguoi_dung, ten_ky_nang, nhom_ky_nang, muc_do_thanh_thao, ghi_chu)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (r["id"], r["user_id"], r["name"], r["category"], r["level"], r["note"]),
            )

        # 6. CHUNG_CHI <- certificates
        for r in src_conn.execute("SELECT * FROM certificates"):
            cur.execute(
                """
                INSERT INTO CHUNG_CHI (ma_chung_chi, ma_nguoi_dung, ten_chung_chi, to_chuc_cap, ngay_cap, ngay_het_han, duong_dan_xac_thuc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (r["id"], r["user_id"], r["name"], r["organization"], r["issue_date"], r["expiry_date"], r["credential_url"]),
            )

        # 7. KINH_NGHIEM <- experiences
        for r in src_conn.execute("SELECT * FROM experiences"):
            cur.execute(
                """
                INSERT INTO KINH_NGHIEM (ma_kinh_nghiem, ma_nguoi_dung, ten_cong_viec_du_an, ten_don_vi_cong_ty, loai_hinh_vai_tro, ngay_bat_dau, ngay_ket_thuc, mo_ta_chi_tiet)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (r["id"], r["user_id"], r["title"], r["company"], r["role_type"], r["start_date"], r["end_date"], r["description"]),
            )

        # 8. TIN_TUYEN_DUNG <- jobs
        for r in src_conn.execute("SELECT * FROM jobs"):
            cur.execute(
                """
                INSERT INTO TIN_TUYEN_DUNG (
                    ma_tin_tuyen_dung, tieu_de_tin, ten_cong_ty, ma_vi_tri, dia_diem_lam_viec,
                    muc_luong, yeu_cau_kinh_nghiem, ky_nang_yeu_cau_json, cong_nghe_yeu_cau_json,
                    chung_chi_uu_tien_json, han_nop_ho_so, mo_ta_chi_tiet, ngay_dang
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r["id"],
                    r["title"],
                    r["company"],
                    r["position_id"],
                    r["location"],
                    r["salary"],
                    r["experience_required"],
                    r["skills"],
                    r["technologies"],
                    r["certificates"],
                    r["deadline"],
                    r["description"],
                    r["created_at"],
                ),
            )

        # 9. KE_HOACH_HOC_TAP <- learning_plans
        for r in src_conn.execute("SELECT * FROM learning_plans"):
            cur.execute(
                """
                INSERT INTO KE_HOACH_HOC_TAP (ma_ke_hoach, ma_nguoi_dung, tieu_de_muc_tieu, danh_muc_bo_sung, loai_muc_tieu, trang_thai, ngay_hoan_thanh_du_kien, ghi_chu_hoc_tap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (r["id"], r["user_id"], r["title"], r["category"], r["type"], r["status"], r["target_date"], r["note"]),
            )

        # 10. GOI_Y_KHOA_HOC <- course_recommendations
        for r in src_conn.execute("SELECT * FROM course_recommendations"):
            cur.execute(
                """
                INSERT INTO GOI_Y_KHOA_HOC (ma_goi_y, ten_ky_nang, ten_khoa_hoc_chung_chi, don_vi_cung_cap, loai_goi_y, thoi_luong_hoc, duong_dan_khoa_hoc, mo_ta_noi_dung)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (r["id"], r["skill_name"], r["title"], r["provider"], r["rec_type"], r["duration"], r["url"], r["description"]),
            )

        # 11. LICH_SU_DOI_SANH <- comparison_history
        for r in src_conn.execute("SELECT * FROM comparison_history"):
            cur.execute(
                """
                INSERT INTO LICH_SU_DOI_SANH (ma_lich_su, ma_nguoi_dung, ma_vi_tri, ten_vi_tri, diem_phu_hop_phan_tram, ky_nang_da_co_json, ky_nang_con_thieu_json, ngay_danh_gia)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (r["id"], r["user_id"], r["position_id"], r["position_name"], r["score"], r["matched_skills"], r["missing_skills"], r["created_at"]),
            )

        target_conn.commit()

    print("Da tao thanh cong CSDL 11 bang tieng Viet khong dau:")
    for tbl in [
        "NGUOI_DUNG",
        "HO_SO_SINH_VIEN",
        "HOC_PHAN",
        "KY_NANG",
        "CHUNG_CHI",
        "KINH_NGHIEM",
        "VI_TRI_NGHE_NGHIEP",
        "TIN_TUYEN_DUNG",
        "KE_HOACH_HOC_TAP",
        "GOI_Y_KHOA_HOC",
        "LICH_SU_DOI_SANH",
    ]:
        cnt = vn_conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  - {tbl:<20}: {cnt} ban ghi")

    generate_sql_server_script(vn_conn)

    src_conn.close()
    vn_conn.close()


def _tsql_val(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("'", "''")
    return f"N'{s}'"


def generate_sql_server_script(conn):
    """Xuất file schema_tieng_viet.sql chuẩn Microsoft SQL Server (T-SQL / SSMS) kèm dữ liệu mẫu."""
    lines = [
        "-- ============================================================================",
        "-- schema_tieng_viet.sql (Chuẩn Microsoft SQL Server / T-SQL - SSMS)",
        "-- Kịch bản khởi tạo Cơ sở dữ liệu & nạp dữ liệu mẫu (11 bảng tiếng Việt không dấu)",
        "-- Đề tài: NLCNPM23CS-38 - Ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp CNTT",
        "-- Hướng dẫn: Mở file này trong SQL Server Management Studio (SSMS) và nhấn F5 (Execute)",
        "-- ============================================================================",
        "",
        "USE master;",
        "GO",
        "",
        "IF DB_ID(N'CSDL_NIEN_LUAN') IS NULL",
        "BEGIN",
        "    CREATE DATABASE CSDL_NIEN_LUAN;",
        "END",
        "GO",
        "",
        "USE CSDL_NIEN_LUAN;",
        "GO",
        "",
        "-- Xóa các bảng cũ (nếu có) theo thứ tự khóa ngoại để chạy lại không bị lỗi",
        "IF OBJECT_ID(N'dbo.LICH_SU_DOI_SANH', N'U') IS NOT NULL DROP TABLE dbo.LICH_SU_DOI_SANH;",
        "IF OBJECT_ID(N'dbo.GOI_Y_KHOA_HOC', N'U') IS NOT NULL DROP TABLE dbo.GOI_Y_KHOA_HOC;",
        "IF OBJECT_ID(N'dbo.KE_HOACH_HOC_TAP', N'U') IS NOT NULL DROP TABLE dbo.KE_HOACH_HOC_TAP;",
        "IF OBJECT_ID(N'dbo.TIN_TUYEN_DUNG', N'U') IS NOT NULL DROP TABLE dbo.TIN_TUYEN_DUNG;",
        "IF OBJECT_ID(N'dbo.KINH_NGHIEM', N'U') IS NOT NULL DROP TABLE dbo.KINH_NGHIEM;",
        "IF OBJECT_ID(N'dbo.CHUNG_CHI', N'U') IS NOT NULL DROP TABLE dbo.CHUNG_CHI;",
        "IF OBJECT_ID(N'dbo.KY_NANG', N'U') IS NOT NULL DROP TABLE dbo.KY_NANG;",
        "IF OBJECT_ID(N'dbo.HOC_PHAN', N'U') IS NOT NULL DROP TABLE dbo.HOC_PHAN;",
        "IF OBJECT_ID(N'dbo.HO_SO_SINH_VIEN', N'U') IS NOT NULL DROP TABLE dbo.HO_SO_SINH_VIEN;",
        "IF OBJECT_ID(N'dbo.VI_TRI_NGHE_NGHIEP', N'U') IS NOT NULL DROP TABLE dbo.VI_TRI_NGHE_NGHIEP;",
        "IF OBJECT_ID(N'dbo.NGUOI_DUNG', N'U') IS NOT NULL DROP TABLE dbo.NGUOI_DUNG;",
        "GO",
        "",
        "-- 1. Bảng NGUOI_DUNG (Tài khoản người dùng)",
        "CREATE TABLE dbo.NGUOI_DUNG (",
        "    ma_nguoi_dung INT IDENTITY(1,1) PRIMARY KEY,",
        "    ho_ten NVARCHAR(150) NOT NULL,",
        "    email NVARCHAR(150) NOT NULL UNIQUE,",
        "    mat_khau_bam NVARCHAR(255) NOT NULL,",
        "    vai_tro NVARCHAR(50) DEFAULT N'student',",
        "    ngay_tao DATETIME DEFAULT GETDATE()",
        ");",
        "GO",
        "",
        "-- 2. Bảng VI_TRI_NGHE_NGHIEP (Danh mục vị trí nghề nghiệp CNTT)",
        "CREATE TABLE dbo.VI_TRI_NGHE_NGHIEP (",
        "    ma_vi_tri INT IDENTITY(1,1) PRIMARY KEY,",
        "    ten_vi_tri NVARCHAR(200) NOT NULL,",
        "    ma_dinh_danh NVARCHAR(100) DEFAULT N'',",
        "    mo_ta_cong_viec NVARCHAR(MAX) DEFAULT N'',",
        "    ky_nang_cot_loi_json NVARCHAR(MAX) DEFAULT N'[]',",
        "    muc_do_nhu_cau NVARCHAR(100) DEFAULT N'Cao'",
        ");",
        "GO",
        "",
        "-- 3. Bảng HO_SO_SINH_VIEN (Thông tin cá nhân & định hướng của sinh viên)",
        "CREATE TABLE dbo.HO_SO_SINH_VIEN (",
        "    ma_ho_so INT IDENTITY(1,1) PRIMARY KEY,",
        "    ma_nguoi_dung INT NOT NULL UNIQUE,",
        "    ho_ten NVARCHAR(150) NOT NULL,",
        "    ma_so_sinh_vien NVARCHAR(50) DEFAULT N'',",
        "    email NVARCHAR(150) NOT NULL,",
        "    so_dien_thoai NVARCHAR(30) DEFAULT N'',",
        "    truong_dai_hoc NVARCHAR(255) DEFAULT N'',",
        "    khoa_vien NVARCHAR(255) DEFAULT N'',",
        "    chuyen_nganh NVARCHAR(255) DEFAULT N'',",
        "    nien_khoa NVARCHAR(100) DEFAULT N'',",
        "    diem_gpa NVARCHAR(20) DEFAULT N'0.0',",
        "    ma_vi_tri_muc_tieu INT NULL DEFAULT 1,",
        "    gioi_thieu_ban_than NVARCHAR(MAX) DEFAULT N'',",
        "    CONSTRAINT FK_HSSV_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE,",
        "    CONSTRAINT FK_HSSV_VITRI FOREIGN KEY (ma_vi_tri_muc_tieu) REFERENCES dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri) ON DELETE SET NULL",
        ");",
        "GO",
        "",
        "-- 4. Bảng HOC_PHAN (Danh sách học phần đại học đã học)",
        "CREATE TABLE dbo.HOC_PHAN (",
        "    ma_hoc_phan INT IDENTITY(1,1) PRIMARY KEY,",
        "    ma_nguoi_dung INT NOT NULL,",
        "    ma_mon_hoc NVARCHAR(50) NOT NULL,",
        "    ten_hoc_phan NVARCHAR(255) NOT NULL,",
        "    so_tin_chi INT DEFAULT 3,",
        "    diem_chu NVARCHAR(10) DEFAULT N'A',",
        "    hoc_ky NVARCHAR(100) DEFAULT N'',",
        "    CONSTRAINT FK_HOCPHAN_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE",
        ");",
        "GO",
        "",
        "-- 5. Bảng KY_NANG (Kỹ năng chuyên môn & mức độ thành thạo 1-5)",
        "CREATE TABLE dbo.KY_NANG (",
        "    ma_ky_nang INT IDENTITY(1,1) PRIMARY KEY,",
        "    ma_nguoi_dung INT NOT NULL,",
        "    ten_ky_nang NVARCHAR(150) NOT NULL,",
        "    nhom_ky_nang NVARCHAR(150) DEFAULT N'Ngôn ngữ lập trình',",
        "    muc_do_thanh_thao INT DEFAULT 3 CHECK (muc_do_thanh_thao >= 1 AND muc_do_thanh_thao <= 5),",
        "    ghi_chu NVARCHAR(MAX) DEFAULT N'',",
        "    CONSTRAINT FK_KYNANG_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE",
        ");",
        "GO",
        "",
        "-- 6. Bảng CHUNG_CHI (Chứng chỉ chuyên môn & ngoại ngữ)",
        "CREATE TABLE dbo.CHUNG_CHI (",
        "    ma_chung_chi INT IDENTITY(1,1) PRIMARY KEY,",
        "    ma_nguoi_dung INT NOT NULL,",
        "    ten_chung_chi NVARCHAR(255) NOT NULL,",
        "    to_chuc_cap NVARCHAR(255) NOT NULL,",
        "    ngay_cap NVARCHAR(50) DEFAULT N'',",
        "    ngay_het_han NVARCHAR(50) DEFAULT N'',",
        "    duong_dan_xac_thuc NVARCHAR(500) DEFAULT N'',",
        "    CONSTRAINT FK_CHUNGCHI_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE",
        ");",
        "GO",
        "",
        "-- 7. Bảng KINH_NGHIEM (Kinh nghiệm thực tập, làm việc & dự án thực tế)",
        "CREATE TABLE dbo.KINH_NGHIEM (",
        "    ma_kinh_nghiem INT IDENTITY(1,1) PRIMARY KEY,",
        "    ma_nguoi_dung INT NOT NULL,",
        "    ten_cong_viec_du_an NVARCHAR(255) NOT NULL,",
        "    ten_don_vi_cong_ty NVARCHAR(255) NOT NULL,",
        "    loai_hinh_vai_tro NVARCHAR(100) DEFAULT N'Thực tập sinh',",
        "    ngay_bat_dau NVARCHAR(50) DEFAULT N'',",
        "    ngay_ket_thuc NVARCHAR(50) DEFAULT N'',",
        "    mo_ta_chi_tiet NVARCHAR(MAX) DEFAULT N'',",
        "    CONSTRAINT FK_KINHNGHIEM_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE",
        ");",
        "GO",
        "",
        "-- 8. Bảng TIN_TUYEN_DUNG (Danh sách tin tuyển dụng từ doanh nghiệp)",
        "CREATE TABLE dbo.TIN_TUYEN_DUNG (",
        "    ma_tin_tuyen_dung INT IDENTITY(1,1) PRIMARY KEY,",
        "    tieu_de_tin NVARCHAR(300) NOT NULL,",
        "    ten_cong_ty NVARCHAR(255) NOT NULL,",
        "    ma_vi_tri INT NOT NULL,",
        "    dia_diem_lam_viec NVARCHAR(150) DEFAULT N'Toàn quốc',",
        "    muc_luong NVARCHAR(150) DEFAULT N'Thỏa thuận',",
        "    yeu_cau_kinh_nghiem NVARCHAR(150) DEFAULT N'Không yêu cầu',",
        "    ky_nang_yeu_cau_json NVARCHAR(MAX) DEFAULT N'[]',",
        "    cong_nghe_yeu_cau_json NVARCHAR(MAX) DEFAULT N'[]',",
        "    chung_chi_uu_tien_json NVARCHAR(MAX) DEFAULT N'[]',",
        "    han_nop_ho_so NVARCHAR(50) DEFAULT N'',",
        "    mo_ta_chi_tiet NVARCHAR(MAX) DEFAULT N'',",
        "    ngay_dang DATETIME DEFAULT GETDATE(),",
        "    CONSTRAINT FK_TINTUYENDUNG_VITRI FOREIGN KEY (ma_vi_tri) REFERENCES dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri) ON DELETE CASCADE",
        ");",
        "GO",
        "",
        "-- 9. Bảng KE_HOACH_HOC_TAP (Lộ trình phát triển năng lực cá nhân)",
        "CREATE TABLE dbo.KE_HOACH_HOC_TAP (",
        "    ma_ke_hoach INT IDENTITY(1,1) PRIMARY KEY,",
        "    ma_nguoi_dung INT NOT NULL,",
        "    tieu_de_muc_tieu NVARCHAR(300) NOT NULL,",
        "    danh_muc_bo_sung NVARCHAR(150) DEFAULT N'Kỹ năng bổ sung',",
        "    loai_muc_tieu NVARCHAR(50) DEFAULT N'skill',",
        "    trang_thai NVARCHAR(50) DEFAULT N'todo',",
        "    ngay_hoan_thanh_du_kien NVARCHAR(50) DEFAULT N'',",
        "    ghi_chu_hoc_tap NVARCHAR(MAX) DEFAULT N'',",
        "    CONSTRAINT FK_KEHOACH_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE",
        ");",
        "GO",
        "",
        "-- 10. Bảng GOI_Y_KHOA_HOC (Kho gợi ý khóa học & chứng chỉ theo kỹ năng thiếu)",
        "CREATE TABLE dbo.GOI_Y_KHOA_HOC (",
        "    ma_goi_y INT IDENTITY(1,1) PRIMARY KEY,",
        "    ten_ky_nang NVARCHAR(150) NOT NULL,",
        "    ten_khoa_hoc_chung_chi NVARCHAR(300) NOT NULL,",
        "    don_vi_cung_cap NVARCHAR(200) DEFAULT N'Coursera / Udemy',",
        "    loai_goi_y NVARCHAR(50) DEFAULT N'course',",
        "    thoi_luong_hoc NVARCHAR(100) DEFAULT N'4 tuần',",
        "    duong_dan_khoa_hoc NVARCHAR(500) DEFAULT N'',",
        "    mo_ta_noi_dung NVARCHAR(MAX) DEFAULT N''",
        ");",
        "GO",
        "",
        "-- 11. Bảng LICH_SU_DOI_SANH (Lịch sử đánh giá & đối sánh độ phù hợp hồ sơ)",
        "CREATE TABLE dbo.LICH_SU_DOI_SANH (",
        "    ma_lich_su INT IDENTITY(1,1) PRIMARY KEY,",
        "    ma_nguoi_dung INT NOT NULL,",
        "    ma_vi_tri INT NOT NULL,",
        "    ten_vi_tri NVARCHAR(200) NOT NULL,",
        "    diem_phu_hop_phan_tram INT DEFAULT 0,",
        "    ky_nang_da_co_json NVARCHAR(MAX) DEFAULT N'[]',",
        "    ky_nang_con_thieu_json NVARCHAR(MAX) DEFAULT N'[]',",
        "    ngay_danh_gia DATETIME DEFAULT GETDATE(),",
        "    CONSTRAINT FK_LICHSU_NGUOIDUNG FOREIGN KEY (ma_nguoi_dung) REFERENCES dbo.NGUOI_DUNG (ma_nguoi_dung) ON DELETE CASCADE,",
        "    CONSTRAINT FK_LICHSU_VITRI FOREIGN KEY (ma_vi_tri) REFERENCES dbo.VI_TRI_NGHE_NGHIEP (ma_vi_tri) ON DELETE CASCADE",
        ");",
        "GO",
        "",
        "-- ============================================================================",
        "-- NẠP DỮ LIỆU MẪU CHO 11 BẢNG",
        "-- ============================================================================",
        "",
    ]

    tables_ordered = [
        ("NGUOI_DUNG", ["ma_nguoi_dung", "ho_ten", "email", "mat_khau_bam", "vai_tro", "ngay_tao"]),
        ("VI_TRI_NGHE_NGHIEP", ["ma_vi_tri", "ten_vi_tri", "ma_dinh_danh", "mo_ta_cong_viec", "ky_nang_cot_loi_json", "muc_do_nhu_cau"]),
        ("HO_SO_SINH_VIEN", ["ma_ho_so", "ma_nguoi_dung", "ho_ten", "ma_so_sinh_vien", "email", "so_dien_thoai", "truong_dai_hoc", "khoa_vien", "chuyen_nganh", "nien_khoa", "diem_gpa", "ma_vi_tri_muc_tieu", "gioi_thieu_ban_than"]),
        ("HOC_PHAN", ["ma_hoc_phan", "ma_nguoi_dung", "ma_mon_hoc", "ten_hoc_phan", "so_tin_chi", "diem_chu", "hoc_ky"]),
        ("KY_NANG", ["ma_ky_nang", "ma_nguoi_dung", "ten_ky_nang", "nhom_ky_nang", "muc_do_thanh_thao", "ghi_chu"]),
        ("CHUNG_CHI", ["ma_chung_chi", "ma_nguoi_dung", "ten_chung_chi", "to_chuc_cap", "ngay_cap", "ngay_het_han", "duong_dan_xac_thuc"]),
        ("KINH_NGHIEM", ["ma_kinh_nghiem", "ma_nguoi_dung", "ten_cong_viec_du_an", "ten_don_vi_cong_ty", "loai_hinh_vai_tro", "ngay_bat_dau", "ngay_ket_thuc", "mo_ta_chi_tiet"]),
        ("TIN_TUYEN_DUNG", ["ma_tin_tuyen_dung", "tieu_de_tin", "ten_cong_ty", "ma_vi_tri", "dia_diem_lam_viec", "muc_luong", "yeu_cau_kinh_nghiem", "ky_nang_yeu_cau_json", "cong_nghe_yeu_cau_json", "chung_chi_uu_tien_json", "han_nop_ho_so", "mo_ta_chi_tiet", "ngay_dang"]),
        ("KE_HOACH_HOC_TAP", ["ma_ke_hoach", "ma_nguoi_dung", "tieu_de_muc_tieu", "danh_muc_bo_sung", "loai_muc_tieu", "trang_thai", "ngay_hoan_thanh_du_kien", "ghi_chu_hoc_tap"]),
        ("GOI_Y_KHOA_HOC", ["ma_goi_y", "ten_ky_nang", "ten_khoa_hoc_chung_chi", "don_vi_cung_cap", "loai_goi_y", "thoi_luong_hoc", "duong_dan_khoa_hoc", "mo_ta_noi_dung"]),
        ("LICH_SU_DOI_SANH", ["ma_lich_su", "ma_nguoi_dung", "ma_vi_tri", "ten_vi_tri", "diem_phu_hop_phan_tram", "ky_nang_da_co_json", "ky_nang_con_thieu_json", "ngay_danh_gia"]),
    ]

    for tbl_name, cols in tables_ordered:
        col_list = ", ".join(cols)
        rows = conn.execute(f"SELECT {col_list} FROM {tbl_name}").fetchall()
        if not rows:
            continue
        lines.append(f"-- Dữ liệu bảng {tbl_name}")
        lines.append(f"SET IDENTITY_INSERT dbo.{tbl_name} ON;")
        for row in rows:
            vals = ", ".join(_tsql_val(v) for v in row)
            lines.append(f"INSERT INTO dbo.{tbl_name} ({col_list}) VALUES ({vals});")
        lines.append(f"SET IDENTITY_INSERT dbo.{tbl_name} OFF;")
        lines.append("GO")
        lines.append("")

    with open(SCHEMA_SQL_PATH, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    build_vietnamese_database()
