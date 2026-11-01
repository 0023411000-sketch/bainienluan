"""
models.py - Thiết kế Cơ sở dữ liệu SQLite (Phân hệ Thành viên 2: Phân tích, Đối sánh & Kế hoạch)
Đề tài: NLCNPM23CS-38

Các bảng dữ liệu của Thành viên 2:
1. learning_plans         : Lộ trình học tập & chứng chỉ mục tiêu cá nhân
2. course_recommendations : Kho gợi ý nội dung học tập / chứng chỉ theo kỹ năng
3. comparison_history     : Lịch sử đánh giá mức độ phù hợp hồ sơ
"""

import os
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def parse_json_list(val):
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


def init_analytics_db():
    """Khởi tạo các bảng phân tích & kế hoạch học tập của Thành viên 2."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Bảng learning_plans (Kế hoạch phát triển năng lực)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            title TEXT NOT NULL,
            category TEXT DEFAULT 'Kỹ năng bổ sung',
            type TEXT DEFAULT 'skill',
            status TEXT DEFAULT 'todo',
            target_date TEXT DEFAULT '',
            note TEXT DEFAULT ''
        );
    """)

    # 2. Bảng course_recommendations (Kho gợi ý khóa học/chứng chỉ theo kỹ năng)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL,
            recommended_title TEXT NOT NULL,
            rec_type TEXT DEFAULT 'course',
            provider TEXT DEFAULT ''
        );
    """)

    # 3. Bảng comparison_history (Lịch sử đối sánh hồ sơ)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comparison_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            position_id INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            matched_skills TEXT DEFAULT '[]',
            missing_skills TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Nạp dữ liệu mẫu cho learning_plans nếu trống
    cursor.execute("SELECT COUNT(*) AS cnt FROM learning_plans")
    if cursor.fetchone()["cnt"] == 0:
        plans_data = [
            (1, "Học và thực hành chuyên sâu Docker & Containerization", "Kỹ năng thiếu (Backend)", "skill", "doing", "2026-11-30", "Làm chủ viết Multi-stage Dockerfile, Docker Compose và kết nối mạng giữa các container."),
            (1, "Ôn thi chứng chỉ AWS Certified Cloud Practitioner (CLF-C02)", "Chứng chỉ nghề nghiệp", "certificate", "doing", "2026-12-25", "Học qua khóa học Stephane Maarek trên Udemy, luyện 6 đề thi thử."),
            (1, "Nghiên cứu kiến trúc Microservices và gRPC với Go", "Nâng cao kỹ năng", "skill", "todo", "2027-01-15", "Đọc sách Designing Data-Intensive Applications của Martin Kleppmann."),
            (1, "Xây dựng đồ án cá nhân: RESTful API mạng xã hội thu nhỏ", "Kinh nghiệm / Portfolio", "project", "done", "2026-09-15", "Hoàn thành API với Flask, Redis caching, Celery background worker và PostgreSQL."),
            (1, "Thực hành cấu hình CI/CD Pipeline bằng GitHub Actions", "Kỹ năng thiếu (DevOps)", "skill", "todo", "2026-12-10", "Tự động chạy pytest và deploy container lên AWS EC2 khi push code."),
        ]
        cursor.executemany(
            """
            INSERT INTO learning_plans (user_id, title, category, type, status, target_date, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            plans_data,
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_analytics_db()
    print(f"Đã khởi tạo các bảng Phân tích & Kế hoạch (Thành viên 2) tại: {DB_PATH}")
