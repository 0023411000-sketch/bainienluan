"""
models.py - Thiết kế Cơ sở dữ liệu SQLite (Phân hệ Thành viên 1)
Đề tài: NLCNPM23CS-38 - Xây dựng ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp cho sinh viên CNTT dựa trên tin tuyển dụng

Các bảng dữ liệu của Thành viên 1:
1. users              : Tài khoản người dùng (sinh viên)
2. student_profiles   : Thông tin cá nhân của sinh viên
3. courses            : Học phần đã học (mục 1 hồ sơ)
4. skills             : Kỹ năng chuyên môn & mức độ 1-5 (mục 2 hồ sơ)
5. certificates       : Chứng chỉ nghề nghiệp/ngoại ngữ (mục 3 hồ sơ)
6. experiences        : Kinh nghiệm thực tế & dự án (mục 4 hồ sơ)
7. positions          : Danh mục vị trí nghề nghiệp CNTT
8. jobs               : Danh sách tin tuyển dụng liên quan
"""

import os
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_db_connection():
    """Tạo kết nối đến SQLite database với row_factory trả về kiểu dict-like."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def parse_json_list(val):
    """Chuyển chuỗi JSON hoặc chuỗi phân tách dấu phẩy từ DB thành list Python."""
    if not val:
        return []
    if isinstance(val, list):
        return val
    try:
        parsed = json.loads(val)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass
    return [s.strip() for s in str(val).split(",") if s.strip()]


def dump_json_list(val, delimiter=","):
    """Chuẩn hóa list hoặc chuỗi phân tách thành chuỗi JSON lưu vào SQLite."""
    if val is None:
        return json.dumps([], ensure_ascii=False)
    if isinstance(val, list):
        cleaned = [str(x).strip() for x in val if str(x).strip()]
        return json.dumps(cleaned, ensure_ascii=False)
    text = str(val).strip()
    if not text:
        return json.dumps([], ensure_ascii=False)
    if ";" in text and delimiter == ";":
        cleaned = [s.strip() for s in text.split(";") if s.strip()]
    else:
        cleaned = [s.strip() for s in text.replace(";", ",").split(",") if s.strip()]
    return json.dumps(cleaned, ensure_ascii=False)


def init_db():
    """Khởi tạo cấu trúc các bảng của Thành viên 1 trong cơ sở dữ liệu SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Bảng users (Xác thực & Quản lý tài khoản)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Bảng student_profiles (Thông tin cá nhân sinh viên)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            student_code TEXT DEFAULT '',
            email TEXT NOT NULL,
            phone TEXT DEFAULT '',
            university TEXT DEFAULT '',
            faculty TEXT DEFAULT '',
            major TEXT DEFAULT '',
            academic_year TEXT DEFAULT '',
            gpa TEXT DEFAULT '0.0',
            target_position_id INTEGER DEFAULT 1,
            bio TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 3. Bảng courses (Học phần đã học)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            credits INTEGER DEFAULT 3,
            grade TEXT DEFAULT 'A',
            term TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 4. Bảng skills (Kỹ năng cá nhân)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'Ngôn ngữ lập trình',
            level INTEGER DEFAULT 3,
            note TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 5. Bảng certificates (Chứng chỉ)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            organization TEXT NOT NULL,
            issue_date TEXT DEFAULT '',
            expiry_date TEXT DEFAULT '',
            credential_url TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 6. Bảng experiences (Kinh nghiệm thực tế & Dự án)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            role_type TEXT DEFAULT 'Thực tập sinh',
            start_date TEXT DEFAULT '',
            end_date TEXT DEFAULT '',
            description TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 7. Bảng positions (Danh mục vị trí nghề nghiệp CNTT)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT DEFAULT '',
            description TEXT DEFAULT '',
            core_skills TEXT DEFAULT '[]',
            demand_level TEXT DEFAULT 'Cao'
        );
    """)

    # 8. Bảng jobs (Danh sách tin tuyển dụng)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            position_id INTEGER NOT NULL,
            location TEXT DEFAULT 'Toàn quốc',
            salary TEXT DEFAULT 'Thỏa thuận',
            experience_required TEXT DEFAULT 'Không yêu cầu',
            skills TEXT DEFAULT '[]',
            technologies TEXT DEFAULT '[]',
            certificates TEXT DEFAULT '[]',
            deadline TEXT DEFAULT '',
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (position_id) REFERENCES positions (id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Đã khởi tạo cơ sở dữ liệu SQLite (Thành viên 1) tại: {DB_PATH}")
