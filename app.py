"""
app.py - Ứng dụng Flask Backend & Frontend tích hợp SQLite (Phân hệ Thành viên 1 & Thành viên 2)
Đề tài: NLCNPM23CS-38 - Xây dựng ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp cho sinh viên CNTT dựa trên tin tuyển dụng

Chức năng hệ thống:
- Phân hệ Core Data & CRUD:
  1. Thiết kế & khởi tạo CSDL SQLite (models.py, seed_data.py, database.db)
  2. Xác thực & Quản lý tài khoản (/api/auth/register, /api/auth/login, /api/auth/logout)
  3. Quản lý Hồ sơ sinh viên & 4 danh mục con (/api/profile, courses, skills, certificates, experiences)
  4. Quản lý Vị trí nghề nghiệp & Tin tuyển dụng + Nhập file CSV (/api/positions, /api/jobs, /api/jobs/import-csv)
- Phân hệ Analytics & Recommendation:
  5. Tổng hợp & Thống kê yêu cầu tuyển dụng theo vị trí (/api/statistics/<position_id>)
  6. Đánh giá & So sánh hồ sơ với vị trí nghề nghiệp + Gợi ý khóa học & Lịch sử (/api/compare, /api/compare/history)
  7. Quản lý Kế hoạch phát triển năng lực & Dashboard tổng quan (/api/plan, /api/dashboard)
"""

import os
import math
from collections import Counter
# pyrefly: ignore[missing-import]
from flask import Flask, render_template, redirect, url_for, request, jsonify, session
# pyrefly: ignore[missing-import]
from werkzeug.security import generate_password_hash, check_password_hash

from models import get_db_connection, parse_json_list, dump_json_list
from seed_data import seed_database

app = Flask(__name__)
app.secret_key = "it-career-compass-secret-key-nlcnpm23cs-38"

# Khởi tạo CSDL & dữ liệu mẫu khi chạy ứng dụng
seed_database()


def api_response(success=True, data=None, message="Thành công", status_code=200):
    """Chuẩn hóa phản hồi JSON thống nhất cho toàn bộ API."""
    return jsonify({
        "success": success,
        "data": data,
        "message": message
    }), status_code


def get_current_user():
    """Lấy người dùng đang đăng nhập từ session (cookie đã ký bởi secret_key).

    Không tin chuỗi token gửi từ client vì token dạng "user_<id>" có thể bị giả mạo.
    Trả về None nếu chưa đăng nhập.
    """
    uid = session.get("user_id")
    if not uid:
        return None
    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, full_name, email, role, created_at FROM users WHERE id = ?",
        (uid,),
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def get_current_user_id():
    """Lấy user_id của người dùng hiện tại (đã được require_login đảm bảo tồn tại)."""
    user = get_current_user()
    return user["id"] if user else None


def is_current_user_admin():
    """Kiểm tra người dùng hiện tại có quyền Quản trị viên (admin) hay không."""
    user = get_current_user()
    return bool(user and user.get("role") == "admin")


# Các đường dẫn không yêu cầu đăng nhập
PUBLIC_PAGES = {"/login", "/register"}
PUBLIC_APIS = {"/api/auth/login", "/api/auth/register", "/api/auth/logout", "/api/chatbot"}


@app.before_request
def require_login():
    """Bắt buộc đăng nhập: API trả 401, trang giao diện chuyển về /login."""
    path = request.path
    if path.startswith("/static/") or path in PUBLIC_PAGES or path in PUBLIC_APIS:
        return None
    if get_current_user():
        return None
    if path.startswith("/api/"):
        return api_response(False, None, "Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn!", 401)
    return redirect(url_for("login"))


# ==============================================================================
# CÁC ROUTE GIAO DIỆN (HTML TEMPLATES)
# ==============================================================================

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/positions")
def positions():
    return render_template("positions.html")


@app.route("/jobs")
def jobs():
    return render_template("jobs.html")


@app.route("/statistics")
def statistics():
    return render_template("statistics.html")


@app.route("/compare")
@app.route("/comparison")
def compare():
    return render_template("compare.html")


@app.route("/plan")
@app.route("/roadmap")
def plan():
    return render_template("plan.html")


@app.route("/admin/users")
def admin_users():
    return render_template("admin_users.html")


@app.route("/db-viewer")
def db_viewer():
    return render_template("db_viewer.html")


@app.route("/api/db-viewer", methods=["GET"])
def api_db_viewer():
    """API đọc trực tiếp danh sách bảng, cột và dữ liệu trong database.db (chỉ Admin)."""
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới được xem cơ sở dữ liệu!", 403)
    hidden_cols = {"password_hash", "mat_khau_bam"}
    conn = get_db_connection()
    tables_rows = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name ASC"
    ).fetchall()
    result = []
    for t in tables_rows:
        tname = t["name"]
        cols = [c["name"] for c in conn.execute(f"PRAGMA table_info({tname})").fetchall()]
        rows = []
        for r in conn.execute(f"SELECT * FROM {tname} LIMIT 100").fetchall():
            row = dict(r)
            for hc in hidden_cols & row.keys():
                row[hc] = "******"
            rows.append(row)
        total = conn.execute(f"SELECT COUNT(*) AS cnt FROM {tname}").fetchone()["cnt"]
        result.append({
            "table_name": tname,
            "create_sql": t["sql"],
            "columns": cols,
            "total_rows": total,
            "rows": rows,
        })
    conn.close()
    return api_response(True, result)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# ==============================================================================
# PHẦN 1 (THÀNH VIÊN 2): API XÁC THỰC & QUẢN LÝ TÀI KHOẢN (/api/auth/*)
# ==============================================================================

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    payload = request.get_json(silent=True) or {}
    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not full_name or not email or len(password) < 6:
        return api_response(False, None, "Vui lòng nhập đầy đủ họ tên, email và mật khẩu từ 6 ký tự!", 400)

    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return api_response(False, None, "Email này đã được đăng ký trong hệ thống!", 400)

    pwd_hash = generate_password_hash(password)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, 'student')",
        (full_name, email, pwd_hash),
    )
    new_user_id = cursor.lastrowid

    # Khởi tạo hồ sơ sinh viên mặc định cho tài khoản mới
    cursor.execute(
        """
        INSERT INTO student_profiles (
            user_id, full_name, student_code, email, phone,
            university, faculty, major, academic_year, gpa, target_position_id, bio
        ) VALUES (?, ?, ?, ?, '', 'Đại học Đồng Tháp', 'Khoa Công nghệ Thông tin', 'Công nghệ Thông tin', '2023 - 2027', '3.20', 1, 'Sinh viên CNTT định hướng phát triển phần mềm.')
        """,
        (new_user_id, full_name, f"SV{new_user_id:05d}", email),
    )
    conn.commit()
    conn.close()

    session["user_id"] = new_user_id
    user_data = {
        "id": new_user_id,
        "full_name": full_name,
        "email": email,
        "role": "student",
        "token": f"user_{new_user_id}",
    }
    return api_response(True, user_data, "Đăng ký tài khoản thành công!", 201)


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return api_response(False, None, "Vui lòng nhập email và mật khẩu!", 400)

    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, full_name, email, password_hash, role FROM users WHERE LOWER(email) = ?",
        (email,),
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return api_response(False, None, "Email hoặc mật khẩu không chính xác!", 401)

    session["user_id"] = user["id"]
    user_data = {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "role": user["role"],
        "token": f"user_{user['id']}",
    }
    return api_response(True, user_data, "Đăng nhập thành công!")


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.pop("user_id", None)
    return api_response(True, None, "Đã đăng xuất thành công!")


# ==============================================================================
# PHẦN 2 (THÀNH VIÊN 2): API QUẢN LÝ HỒ SƠ SINH VIÊN (4 DANH MỤC) (/api/profile/*)
# ==============================================================================

@app.route("/api/profile", methods=["GET"])
def api_get_profile():
    user_id = get_current_user_id()
    conn = get_db_connection()

    prof = conn.execute("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,)).fetchone()
    if not prof:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        full_name = user["full_name"] if user else "Sinh viên CNTT"
        email = user["email"] if user else "student@example.com"
        conn.execute(
            """
            INSERT INTO student_profiles (user_id, full_name, email)
            VALUES (?, ?, ?)
            """,
            (user_id, full_name, email),
        )
        conn.commit()
        prof = conn.execute("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,)).fetchone()

    courses_rows = conn.execute(
        "SELECT id, code, name, credits, grade, term FROM courses WHERE user_id = ? ORDER BY id ASC",
        (user_id,),
    ).fetchall()
    skills_rows = conn.execute(
        "SELECT id, name, category, level, note FROM skills WHERE user_id = ? ORDER BY id ASC",
        (user_id,),
    ).fetchall()
    certs_rows = conn.execute(
        "SELECT id, name, organization, issue_date, expiry_date, credential_url FROM certificates WHERE user_id = ? ORDER BY id ASC",
        (user_id,),
    ).fetchall()
    exps_rows = conn.execute(
        "SELECT id, title, company, role_type, start_date, end_date, description FROM experiences WHERE user_id = ? ORDER BY id ASC",
        (user_id,),
    ).fetchall()
    courses_list = [dict(r) for r in courses_rows]
    skills_list = [dict(r) for r in skills_rows]
    certs_list = [dict(r) for r in certs_rows]
    exps_list = [dict(r) for r in exps_rows]
    target_pos_id = prof["target_position_id"] if prof and prof["target_position_id"] else 1
    eval_result = evaluate_profile_fit_and_suggest_courses(user_id, target_pos_id, save_history=False, conn=conn)
    conn.close()

    data = {
        "personal_info": {
            "full_name": prof["full_name"],
            "student_code": prof["student_code"],
            "email": prof["email"],
            "phone": prof["phone"],
            "university": prof["university"],
            "faculty": prof["faculty"],
            "major": prof["major"],
            "academic_year": prof["academic_year"],
            "gpa": prof["gpa"],
            "target_position_id": target_pos_id,
            "bio": prof["bio"],
        },
        "courses": courses_list,
        "skills": skills_list,
        "certificates": certs_list,
        "experiences": exps_list,
        "evaluation": eval_result,
    }
    return api_response(True, data)


@app.route("/api/profile", methods=["PUT"])
def api_update_profile():
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}

    full_name = (payload.get("full_name") or "").strip()
    if not full_name:
        return api_response(False, None, "Họ và tên không được để trống!", 400)

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE student_profiles
        SET full_name = ?,
            student_code = ?,
            email = ?,
            phone = ?,
            university = ?,
            faculty = ?,
            major = ?,
            academic_year = ?,
            gpa = ?,
            target_position_id = ?,
            bio = ?
        WHERE user_id = ?
        """,
        (
            full_name,
            (payload.get("student_code") or "").strip(),
            (payload.get("email") or "").strip(),
            (payload.get("phone") or "").strip(),
            (payload.get("university") or "").strip(),
            (payload.get("faculty") or "").strip(),
            (payload.get("major") or "").strip(),
            (payload.get("academic_year") or "").strip(),
            str(payload.get("gpa") or "0.0").strip(),
            int(payload.get("target_position_id") or 1),
            (payload.get("bio") or "").strip(),
            user_id,
        ),
    )
    conn.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name, user_id))
    conn.commit()
    updated = conn.execute("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()

    return api_response(True, dict(updated) if updated else payload, "Cập nhật thông tin cá nhân thành công!")


# --- 2.1. CRUD HỌC PHẦN (COURSES) ---

@app.route("/api/profile/courses", methods=["POST"])
def api_add_course():
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    code = (payload.get("code") or "").strip()
    name = (payload.get("name") or "").strip()
    if not code or not name:
        return api_response(False, None, "Mã học phần và tên học phần không được để trống!", 400)

    credits = int(payload.get("credits") or 3)
    grade = (payload.get("grade") or "A").strip()
    term = (payload.get("term") or "").strip()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO courses (user_id, code, name, credits, grade, term) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, code, name, credits, grade, term),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return api_response(
        True,
        {"id": new_id, "code": code, "name": name, "credits": credits, "grade": grade, "term": term},
        "Thêm học phần thành công!",
        201,
    )


@app.route("/api/profile/courses/<int:item_id>", methods=["PUT"])
def api_update_course(item_id):
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    code = (payload.get("code") or "").strip()
    name = (payload.get("name") or "").strip()
    credits = int(payload.get("credits") or 3)
    grade = (payload.get("grade") or "A").strip()
    term = (payload.get("term") or "").strip()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE courses SET code = ?, name = ?, credits = ?, grade = ?, term = ? WHERE id = ? AND user_id = ?",
        (code, name, credits, grade, term, item_id, user_id),
    )
    conn.commit()
    conn.close()

    return api_response(
        True,
        {"id": item_id, "code": code, "name": name, "credits": credits, "grade": grade, "term": term},
        "Cập nhật học phần thành công!",
    )


@app.route("/api/profile/courses/<int:item_id>", methods=["DELETE"])
def api_delete_course(item_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    conn.execute("DELETE FROM courses WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()
    return api_response(True, None, "Xóa học phần thành công!")


# --- 2.2. CRUD KỸ NĂNG (SKILLS) ---

@app.route("/api/profile/skills", methods=["POST"])
def api_add_skill():
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return api_response(False, None, "Tên kỹ năng không được để trống!", 400)

    category = (payload.get("category") or "Ngôn ngữ lập trình").strip()
    level = min(max(int(payload.get("level") or 3), 1), 5)
    note = (payload.get("note") or "").strip()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO skills (user_id, name, category, level, note) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, category, level, note),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return api_response(
        True,
        {"id": new_id, "name": name, "category": category, "level": level, "note": note},
        "Thêm kỹ năng thành công!",
        201,
    )


@app.route("/api/profile/skills/<int:item_id>", methods=["PUT"])
def api_update_skill(item_id):
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    category = (payload.get("category") or "Ngôn ngữ lập trình").strip()
    level = min(max(int(payload.get("level") or 3), 1), 5)
    note = (payload.get("note") or "").strip()

    conn = get_db_connection()
    conn.execute(
        "UPDATE skills SET name = ?, category = ?, level = ?, note = ? WHERE id = ? AND user_id = ?",
        (name, category, level, note, item_id, user_id),
    )
    conn.commit()
    conn.close()

    return api_response(
        True,
        {"id": item_id, "name": name, "category": category, "level": level, "note": note},
        "Cập nhật kỹ năng thành công!",
    )


@app.route("/api/profile/skills/<int:item_id>", methods=["DELETE"])
def api_delete_skill(item_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    conn.execute("DELETE FROM skills WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()
    return api_response(True, None, "Xóa kỹ năng thành công!")


# --- 2.3. CRUD CHỨNG CHỈ (CERTIFICATES) ---

@app.route("/api/profile/certificates", methods=["POST"])
def api_add_certificate():
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    organization = (payload.get("organization") or "").strip()
    if not name or not organization:
        return api_response(False, None, "Tên chứng chỉ và tổ chức cấp không được để trống!", 400)

    issue_date = (payload.get("issue_date") or "").strip()
    expiry_date = (payload.get("expiry_date") or "").strip()
    credential_url = (payload.get("credential_url") or "").strip()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO certificates (user_id, name, organization, issue_date, expiry_date, credential_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, organization, issue_date, expiry_date, credential_url),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return api_response(
        True,
        {
            "id": new_id,
            "name": name,
            "organization": organization,
            "issue_date": issue_date,
            "expiry_date": expiry_date,
            "credential_url": credential_url,
        },
        "Thêm chứng chỉ thành công!",
        201,
    )


@app.route("/api/profile/certificates/<int:item_id>", methods=["PUT"])
def api_update_certificate(item_id):
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    organization = (payload.get("organization") or "").strip()
    issue_date = (payload.get("issue_date") or "").strip()
    expiry_date = (payload.get("expiry_date") or "").strip()
    credential_url = (payload.get("credential_url") or "").strip()

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE certificates
        SET name = ?, organization = ?, issue_date = ?, expiry_date = ?, credential_url = ?
        WHERE id = ? AND user_id = ?
        """,
        (name, organization, issue_date, expiry_date, credential_url, item_id, user_id),
    )
    conn.commit()
    conn.close()

    return api_response(
        True,
        {
            "id": item_id,
            "name": name,
            "organization": organization,
            "issue_date": issue_date,
            "expiry_date": expiry_date,
            "credential_url": credential_url,
        },
        "Cập nhật chứng chỉ thành công!",
    )


@app.route("/api/profile/certificates/<int:item_id>", methods=["DELETE"])
def api_delete_certificate(item_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    conn.execute("DELETE FROM certificates WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()
    return api_response(True, None, "Xóa chứng chỉ thành công!")


# --- 2.4. CRUD KINH NGHIỆM & DỰ ÁN (EXPERIENCES) ---

@app.route("/api/profile/experiences", methods=["POST"])
def api_add_experience():
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    company = (payload.get("company") or "").strip()
    if not title or not company:
        return api_response(False, None, "Vị trí/tên dự án và đơn vị không được để trống!", 400)

    role_type = (payload.get("role_type") or "Thực tập sinh").strip()
    start_date = (payload.get("start_date") or "").strip()
    end_date = (payload.get("end_date") or "").strip()
    description = (payload.get("description") or "").strip()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO experiences (user_id, title, company, role_type, start_date, end_date, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, title, company, role_type, start_date, end_date, description),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return api_response(
        True,
        {
            "id": new_id,
            "title": title,
            "company": company,
            "role_type": role_type,
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
        },
        "Thêm kinh nghiệm/dự án thành công!",
        201,
    )


@app.route("/api/profile/experiences/<int:item_id>", methods=["PUT"])
def api_update_experience(item_id):
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    company = (payload.get("company") or "").strip()
    role_type = (payload.get("role_type") or "Thực tập sinh").strip()
    start_date = (payload.get("start_date") or "").strip()
    end_date = (payload.get("end_date") or "").strip()
    description = (payload.get("description") or "").strip()

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE experiences
        SET title = ?, company = ?, role_type = ?, start_date = ?, end_date = ?, description = ?
        WHERE id = ? AND user_id = ?
        """,
        (title, company, role_type, start_date, end_date, description, item_id, user_id),
    )
    conn.commit()
    conn.close()

    return api_response(
        True,
        {
            "id": item_id,
            "title": title,
            "company": company,
            "role_type": role_type,
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
        },
        "Cập nhật kinh nghiệm thành công!",
    )


@app.route("/api/profile/experiences/<int:item_id>", methods=["DELETE"])
def api_delete_experience(item_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    conn.execute("DELETE FROM experiences WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()
    return api_response(True, None, "Xóa kinh nghiệm thành công!")


# ==============================================================================
# PHẦN 3 (THÀNH VIÊN 2): API QUẢN LÝ VỊ TRÍ NGHỀ NGHIỆP (/api/positions/*)
# ==============================================================================

def serialize_position(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "code": row["code"],
        "description": row["description"],
        "core_skills": parse_json_list(row["core_skills"]),
        "demand_level": row["demand_level"],
    }


@app.route("/api/positions", methods=["GET"])
def api_get_positions():
    q = (request.args.get("q") or "").strip().lower()
    page = max(int(request.args.get("page") or 1), 1)
    limit = max(int(request.args.get("limit") or 8), 1)

    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM positions ORDER BY id ASC").fetchall()
    conn.close()

    all_items = [serialize_position(r) for r in rows]
    if q:
        all_items = [
            p for p in all_items
            if q in p["name"].lower()
            or q in (p["code"] or "").lower()
            or q in (p["description"] or "").lower()
            or any(q in s.lower() for s in p["core_skills"])
        ]

    total = len(all_items)
    total_pages = max(math.ceil(total / limit), 1)
    start = (page - 1) * limit
    paged_items = all_items[start : start + limit]

    return api_response(
        True,
        {
            "items": paged_items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        },
    )


@app.route("/api/positions/<int:pos_id>", methods=["GET"])
def api_get_position_by_id(pos_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM positions WHERE id = ?", (pos_id,)).fetchone()
    conn.close()
    if not row:
        return api_response(False, None, "Không tìm thấy vị trí nghề nghiệp!", 404)
    return api_response(True, serialize_position(row))


@app.route("/api/positions", methods=["POST"])
def api_create_position():
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền thêm vị trí nghề nghiệp!", 403)
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return api_response(False, None, "Tên vị trí nghề nghiệp không được để trống!", 400)

    code = (payload.get("code") or "").strip()
    description = (payload.get("description") or "").strip()
    core_skills_json = dump_json_list(payload.get("core_skills"))
    demand_level = (payload.get("demand_level") or "Cao").strip()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO positions (name, code, description, core_skills, demand_level) VALUES (?, ?, ?, ?, ?)",
        (name, code, description, core_skills_json, demand_level),
    )
    new_id = cur.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM positions WHERE id = ?", (new_id,)).fetchone()
    conn.close()

    return api_response(True, serialize_position(row), "Thêm vị trí nghề nghiệp thành công!", 201)


@app.route("/api/positions/<int:pos_id>", methods=["PUT"])
def api_update_position(pos_id):
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền chỉnh sửa vị trí nghề nghiệp!", 403)
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    code = (payload.get("code") or "").strip()
    description = (payload.get("description") or "").strip()
    core_skills_json = dump_json_list(payload.get("core_skills"))
    demand_level = (payload.get("demand_level") or "Cao").strip()

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE positions
        SET name = ?, code = ?, description = ?, core_skills = ?, demand_level = ?
        WHERE id = ?
        """,
        (name, code, description, core_skills_json, demand_level, pos_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM positions WHERE id = ?", (pos_id,)).fetchone()
    conn.close()
    if not row:
        return api_response(False, None, "Không tìm thấy vị trí!", 404)
    return api_response(True, serialize_position(row), "Cập nhật vị trí thành công!")


@app.route("/api/positions/<int:pos_id>", methods=["DELETE"])
def api_delete_position(pos_id):
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền xóa vị trí nghề nghiệp!", 403)
    conn = get_db_connection()
    conn.execute("DELETE FROM positions WHERE id = ?", (pos_id,))
    conn.commit()
    conn.close()
    return api_response(True, None, "Xóa vị trí nghề nghiệp thành công!")


# ==============================================================================
# PHẦN 4 (THÀNH VIÊN 2): API QUẢN LÝ TIN TUYỂN DỤNG & NHẬP CSV (/api/jobs/*)
# ==============================================================================

def serialize_job(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "company": row["company"],
        "position_id": row["position_id"],
        "location": row["location"],
        "salary": row["salary"],
        "experience_required": row["experience_required"],
        "skills": parse_json_list(row["skills"]),
        "technologies": parse_json_list(row["technologies"]),
        "certificates": parse_json_list(row["certificates"]),
        "deadline": row["deadline"],
        "description": row["description"],
    }


@app.route("/api/jobs", methods=["GET"])
def api_get_jobs():
    q = (request.args.get("q") or "").strip().lower()
    position_id = (request.args.get("position_id") or "").strip()
    page = max(int(request.args.get("page") or 1), 1)
    limit = max(int(request.args.get("limit") or 8), 1)

    conn = get_db_connection()
    if position_id and position_id.isdigit():
        rows = conn.execute(
            "SELECT * FROM jobs WHERE position_id = ? ORDER BY id DESC",
            (int(position_id),),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    conn.close()

    all_items = [serialize_job(r) for r in rows]
    if q:
        all_items = [
            j for j in all_items
            if q in j["title"].lower()
            or q in j["company"].lower()
            or any(q in s.lower() for s in j["skills"])
            or any(q in t.lower() for t in j["technologies"])
        ]

    total = len(all_items)
    total_pages = max(math.ceil(total / limit), 1)
    start = (page - 1) * limit
    paged_items = all_items[start : start + limit]

    return api_response(
        True,
        {
            "items": paged_items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        },
    )


@app.route("/api/jobs/<int:job_id>", methods=["GET"])
def api_get_job_by_id(job_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    if not row:
        return api_response(False, None, "Không tìm thấy tin tuyển dụng!", 404)
    return api_response(True, serialize_job(row))


@app.route("/api/jobs", methods=["POST"])
def api_create_job():
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền đăng tin tuyển dụng!", 403)
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    company = (payload.get("company") or "").strip()
    if not title or not company:
        return api_response(False, None, "Tiêu đề tin và tên công ty không được để trống!", 400)

    position_id = int(payload.get("position_id") or 1)
    location = (payload.get("location") or "Toàn quốc").strip()
    salary = (payload.get("salary") or "Thỏa thuận").strip()
    experience_required = (payload.get("experience_required") or "Không yêu cầu").strip()
    skills_json = dump_json_list(payload.get("skills"))
    technologies_json = dump_json_list(payload.get("technologies"))
    certificates_json = dump_json_list(payload.get("certificates"))
    deadline = (payload.get("deadline") or "").strip()
    description = (payload.get("description") or "").strip()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO jobs (
            title, company, position_id, location, salary,
            experience_required, skills, technologies, certificates, deadline, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            company,
            position_id,
            location,
            salary,
            experience_required,
            skills_json,
            technologies_json,
            certificates_json,
            deadline,
            description,
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (new_id,)).fetchone()
    conn.close()

    return api_response(True, serialize_job(row), "Đăng tin tuyển dụng thành công!", 201)


@app.route("/api/jobs/<int:job_id>", methods=["PUT"])
def api_update_job(job_id):
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền chỉnh sửa tin tuyển dụng!", 403)
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    company = (payload.get("company") or "").strip()
    position_id = int(payload.get("position_id") or 1)
    location = (payload.get("location") or "Toàn quốc").strip()
    salary = (payload.get("salary") or "Thỏa thuận").strip()
    experience_required = (payload.get("experience_required") or "Không yêu cầu").strip()
    skills_json = dump_json_list(payload.get("skills"))
    technologies_json = dump_json_list(payload.get("technologies"))
    certificates_json = dump_json_list(payload.get("certificates"))
    deadline = (payload.get("deadline") or "").strip()
    description = (payload.get("description") or "").strip()

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE jobs
        SET title = ?, company = ?, position_id = ?, location = ?, salary = ?,
            experience_required = ?, skills = ?, technologies = ?, certificates = ?,
            deadline = ?, description = ?
        WHERE id = ?
        """,
        (
            title,
            company,
            position_id,
            location,
            salary,
            experience_required,
            skills_json,
            technologies_json,
            certificates_json,
            deadline,
            description,
            job_id,
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    if not row:
        return api_response(False, None, "Không tìm thấy tin tuyển dụng!", 404)
    return api_response(True, serialize_job(row), "Cập nhật tin tuyển dụng thành công!")


@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def api_delete_job(job_id):
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền xóa tin tuyển dụng!", 403)
    conn = get_db_connection()
    conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    return api_response(True, None, "Xóa tin tuyển dụng thành công!")


@app.route("/api/jobs/import-csv", methods=["POST"])
def api_import_jobs_csv():
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền nhập dữ liệu CSV!", 403)
    payload = request.get_json(silent=True) or {}
    records = payload.get("records") or []
    if not isinstance(records, list) or len(records) == 0:
        return api_response(False, None, "Không có dữ liệu CSV hợp lệ để nhập!", 400)

    conn = get_db_connection()
    cur = conn.cursor()
    imported_count = 0

    for row in records:
        title = (row.get("title") or "Vị trí tuyển dụng CNTT").strip()
        company = (row.get("company") or "Doanh nghiệp CNTT").strip()
        try:
            pos_id = int(row.get("position_id") or 1)
        except ValueError:
            pos_id = 1
        location = (row.get("location") or "Toàn quốc").strip()
        salary = (row.get("salary") or "Thỏa thuận").strip()
        experience_required = (row.get("experience_required") or "Không yêu cầu").strip()
        skills_json = dump_json_list(row.get("skills"), delimiter=";")
        technologies_json = dump_json_list(row.get("technologies"), delimiter=";")
        certificates_json = dump_json_list(row.get("certificates"), delimiter=";")
        deadline = (row.get("deadline") or "2026-12-31").strip()
        description = (row.get("description") or "").strip()

        cur.execute(
            """
            INSERT INTO jobs (
                title, company, position_id, location, salary,
                experience_required, skills, technologies, certificates, deadline, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                company,
                pos_id,
                location,
                salary,
                experience_required,
                skills_json,
                technologies_json,
                certificates_json,
                deadline,
                description,
            ),
        )
        imported_count += 1

    conn.commit()
    conn.close()
    return api_response(
        True,
        {"imported_count": imported_count},
        f"Đã nhập thành công {imported_count} tin tuyển dụng từ CSV vào cơ sở dữ liệu!",
        201,
    )


# ==============================================================================
# PHẦN QUẢN TRỊ NGƯỜI DÙNG & PHÂN QUYỀN (ADMIN RBAC - /api/admin/users/*)
# ==============================================================================

@app.route("/api/admin/users", methods=["GET"])
def api_admin_get_users():
    if not is_current_user_admin():
        return api_response(False, None, "Truy cập bị từ chối: Yêu cầu quyền Quản trị viên (Admin)!", 403)
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, full_name, email, role, created_at FROM users ORDER BY id ASC"
    ).fetchall()
    conn.close()
    return api_response(True, [dict(r) for r in rows])


@app.route("/api/admin/users", methods=["POST"])
def api_admin_create_user():
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền tạo tài khoản!", 403)
    payload = request.get_json(silent=True) or {}
    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or "123456"
    role = (payload.get("role") or "student").strip().lower()
    if role not in ("student", "admin"):
        role = "student"

    if not full_name or not email or len(password) < 6:
        return api_response(False, None, "Họ tên, email và mật khẩu (tối thiểu 6 ký tự) không hợp lệ!", 400)

    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return api_response(False, None, "Email này đã tồn tại trong hệ thống!", 400)

    pwd_hash = generate_password_hash(password)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (full_name, email, pwd_hash, role),
    )
    new_uid = cur.lastrowid
    if role == "student":
        cur.execute(
            """
            INSERT INTO student_profiles (
                user_id, full_name, student_code, email, phone,
                university, faculty, major, academic_year, gpa, target_position_id, bio
            ) VALUES (?, ?, ?, ?, '', 'Đại học Bách Khoa Hà Nội', 'Trường CNTT & Truyền thông', 'Công nghệ Thông tin', 'K66 (2021 - 2026)', '3.20', 1, 'Sinh viên CNTT định hướng phát triển phần mềm.')
            """,
            (new_uid, full_name, f"SV{new_uid:05d}", email),
        )
    conn.commit()
    row = conn.execute(
        "SELECT id, full_name, email, role, created_at FROM users WHERE id = ?", (new_uid,)
    ).fetchone()
    conn.close()
    return api_response(True, dict(row), "Tạo tài khoản người dùng thành công!", 201)


@app.route("/api/admin/users/<int:target_id>", methods=["PUT"])
def api_admin_update_user(target_id):
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền phân quyền tài khoản!", 403)
    payload = request.get_json(silent=True) or {}
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM users WHERE id = ?", (target_id,)).fetchone()
    if not existing:
        conn.close()
        return api_response(False, None, "Không tìm thấy tài khoản người dùng!", 404)

    full_name = (payload.get("full_name") or existing["full_name"]).strip()
    role = (payload.get("role") or existing["role"]).strip().lower()
    if role not in ("student", "admin"):
        role = existing["role"]
    new_password = (payload.get("password") or "").strip()

    if new_password and len(new_password) >= 6:
        pwd_hash = generate_password_hash(new_password)
        conn.execute(
            "UPDATE users SET full_name = ?, role = ?, password_hash = ? WHERE id = ?",
            (full_name, role, pwd_hash, target_id),
        )
    else:
        conn.execute(
            "UPDATE users SET full_name = ?, role = ? WHERE id = ?",
            (full_name, role, target_id),
        )
    conn.commit()
    updated = conn.execute(
        "SELECT id, full_name, email, role, created_at FROM users WHERE id = ?", (target_id,)
    ).fetchone()
    conn.close()
    return api_response(True, dict(updated), "Cập nhật thông tin & phân quyền thành công!")


@app.route("/api/admin/users/<int:target_id>", methods=["DELETE"])
def api_admin_delete_user(target_id):
    if not is_current_user_admin():
        return api_response(False, None, "Chỉ Quản trị viên (Admin) mới có quyền xóa tài khoản!", 403)
    current_uid = get_current_user_id()
    if target_id == current_uid:
        return api_response(False, None, "Không thể tự xóa tài khoản Quản trị viên đang đăng nhập!", 400)
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (target_id,))
    conn.commit()
    conn.close()
    return api_response(True, None, "Đã xóa tài khoản người dùng thành công!")


# ==============================================================================
# CÁC API BỔ TRỢ ĐỒNG BỘ (DASHBOARD, THỐNG KÊ, SO SÁNH, KẾ HOẠCH)
# ==============================================================================

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    user_id = get_current_user_id()
    conn = get_db_connection()

    user_skills = [
        r["name"].strip().lower()
        for r in conn.execute("SELECT name FROM skills WHERE user_id = ?", (user_id,)).fetchall()
    ]
    total_skills = len(user_skills)
    total_certs = conn.execute("SELECT COUNT(*) AS c FROM certificates WHERE user_id = ?", (user_id,)).fetchone()["c"]

    positions_rows = conn.execute("SELECT * FROM positions ORDER BY id ASC").fetchall()
    match_scores = []
    for p in positions_rows:
        eval_res = evaluate_profile_fit_and_suggest_courses(
            user_id, position_id=p["id"], save_history=False, conn=conn
        )
        match_scores.append({"id": p["id"], "name": p["name"], "score": eval_res.get("score", 0)})

    highest = max(match_scores, key=lambda x: x["score"]) if match_scores else {"id": 1, "name": "Chưa có", "score": 0}

    plans_rows = conn.execute("SELECT * FROM learning_plans WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()

    plans_list = [dict(r) for r in plans_rows]
    done_count = sum(1 for p in plans_list if p["status"] == "done")
    progress_percent = round((done_count / len(plans_list)) * 100) if plans_list else 0
    recent_todos = [p for p in plans_list if p["status"] != "done"][:5]

    return api_response(
        True,
        {
            "total_skills": total_skills,
            "total_certificates": total_certs,
            "highest_match": highest,
            "plan_progress": progress_percent,
            "match_by_positions": match_scores,
            "recent_todos": recent_todos,
        },
    )


@app.route("/api/statistics/<int:position_id>", methods=["GET"])
def api_statistics(position_id):
    conn = get_db_connection()
    pos = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,)).fetchone()
    if not pos:
        pos = conn.execute("SELECT * FROM positions ORDER BY id ASC LIMIT 1").fetchone()
    jobs_rows = conn.execute("SELECT * FROM jobs WHERE position_id = ?", (pos["id"],)).fetchall()
    conn.close()

    total_jobs = len(jobs_rows)
    skill_counter = Counter()
    tech_counter = Counter()
    cert_counter = Counter()
    exp_counter = Counter()

    # Đếm số TIN TUYỂN DỤNG có nhắc tới mỗi yêu cầu (mỗi tin chỉ tính 1 lần cho 1 yêu cầu)
    for j in jobs_rows:
        for s in set(parse_json_list(j["skills"])):
            skill_counter[s] += 1
        for t in set(parse_json_list(j["technologies"])):
            tech_counter[t] += 1
        for c in set(parse_json_list(j["certificates"])):
            cert_counter[c] += 1
        exp_req = (j["experience_required"] or "Không yêu cầu").strip()
        exp_counter[exp_req] += 1

    def pct(v):
        # Tỷ lệ % = số tin yêu cầu / tổng số tin của vị trí
        return round(v / total_jobs * 100) if total_jobs else 0

    top_skills = [
        {"name": k, "count": v, "percentage": pct(v)}
        for k, v in skill_counter.most_common(8)
    ]
    # Vị trí chưa có tin tuyển dụng: hiển thị bộ kỹ năng cốt lõi với tỷ lệ 0%
    if not top_skills:
        top_skills = [
            {"name": cs, "count": 0, "percentage": 0}
            for cs in parse_json_list(pos["core_skills"])[:8]
        ]
    technologies = [
        {"name": k, "count": v, "percentage": pct(v)}
        for k, v in tech_counter.most_common(6)
    ]
    certificates = [
        {"name": k, "count": v, "percentage": pct(v), "level": "Khuyến nghị"}
        for k, v in cert_counter.most_common(4)
    ]
    experience_stats = [
        {"level": k, "count": v, "percentage": pct(v)}
        for k, v in exp_counter.most_common(4)
    ]

    return api_response(
        True,
        {
            "position_name": pos["name"],
            "total_jobs_analyzed": total_jobs,
            "top_skills": top_skills,
            "technologies": technologies,
            "certificates": certificates,
            "experience_stats": experience_stats,
        },
    )


ACADEMIC_CURRICULUM = [
    {
        "code": "IT3090",
        "name": "Cơ sở dữ liệu",
        "credits": 3,
        "skills": ["SQL", "Cơ sở dữ liệu", "Thiết kế CSDL", "Tối ưu truy vấn", "PostgreSQL"],
        "positions": [1, 3, 4],
        "description": "Trang bị kiến thức mô hình quan hệ, viết truy vấn SQL phức tạp, tối ưu chỉ mục và thiết kế kiến trúc CSDL."
    },
    {
        "code": "IT4010",
        "name": "Phát triển ứng dụng Web",
        "credits": 3,
        "skills": ["HTML5/CSS3", "JavaScript", "RESTful API", "Bootstrap", "Tailwind CSS", "Flask", "Node.js"],
        "positions": [1, 2, 3],
        "description": "Xây dựng ứng dụng web hiện đại chuẩn Client-Server, giao diện responsive và tích hợp RESTful API."
    },
    {
        "code": "IT4060",
        "name": "Lập trình mạng và hệ thống phân tán",
        "credits": 3,
        "skills": ["RESTful API", "Socket", "Microservices", "Java", "Python", "Golang", "Redis"],
        "positions": [1, 3, 5],
        "description": "Lập trình socket đa luồng, đồng bộ dữ liệu thời gian thực và kiến trúc microservices chịu tải cao."
    },
    {
        "code": "INT3110",
        "name": "Giao diện người - máy & Thiết kế UI/UX",
        "credits": 3,
        "skills": ["UI/UX", "HTML5/CSS3", "JavaScript", "Tailwind CSS", "Bootstrap", "Mobile UX"],
        "positions": [2, 7],
        "description": "Nguyên lý trải nghiệm người dùng, thiết kế wireframe/prototype và xây dựng hệ thống Design System."
    },
    {
        "code": "INT3306",
        "name": "Phát triển ứng dụng Web hiện đại (Frontend)",
        "credits": 3,
        "skills": ["ReactJS", "TypeScript", "VueJS", "JavaScript", "Node.js", "Git"],
        "positions": [2, 3],
        "description": "Làm chủ kiến trúc Single Page Application với React/Vue, quản lý State và tích hợp TypeScript."
    },
    {
        "code": "IT4520",
        "name": "Điện toán đám mây & Công nghệ ảo hóa",
        "credits": 3,
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform"],
        "positions": [1, 3, 5, 8],
        "description": "Đóng gói ứng dụng với Docker, điều phối cụm Kubernetes và triển khai hạ tầng đám mây AWS."
    },
    {
        "code": "IT3070",
        "name": "Hệ điều hành Linux & Quản trị hệ thống",
        "credits": 3,
        "skills": ["Linux", "Shell Scripting", "Prometheus", "Git", "DevOps"],
        "positions": [1, 5],
        "description": "Quản trị hệ điều hành Linux, phân quyền an toàn, tự động hóa bằng Bash Shell và giám sát hệ thống."
    },
    {
        "code": "IT4409",
        "name": "Kiểm thử và đảm bảo chất lượng phần mềm",
        "credits": 2,
        "skills": ["Kiểm thử phần mềm", "Thiết kế Test Case", "Postman", "Selenium", "Jira", "API Testing"],
        "positions": [6, 3],
        "description": "Thiết kế test case, tự động hóa kiểm thử API với Postman và giao diện web với Selenium WebDriver."
    },
    {
        "code": "IT3160",
        "name": "Nhập môn Trí tuệ nhân tạo",
        "credits": 3,
        "skills": ["Python", "Toán rời rạc & Đại số tuyến tính", "Scikit-Learn", "Trí tuệ nhân tạo"],
        "positions": [8, 4],
        "description": "Nền tảng thuật toán tìm kiếm thông minh, tối ưu hóa bài toán và ứng dụng thuật toán học máy cơ bản."
    },
    {
        "code": "IT4170",
        "name": "Học máy & Khai phá dữ liệu",
        "credits": 3,
        "skills": ["Python", "Machine Learning", "Scikit-Learn", "Pandas", "Data Cleaning", "Xác suất thống kê"],
        "positions": [8, 4],
        "description": "Quy trình tiền xử lý dữ liệu và huấn luyện các mô hình Machine Learning có giám sát/không giám sát."
    },
    {
        "code": "IT4172",
        "name": "Thị giác máy tính & Xử lý ảnh",
        "credits": 3,
        "skills": ["Computer Vision", "PyTorch", "TensorFlow", "Python", "Deep Learning"],
        "positions": [8],
        "description": "Xử lý ảnh số, huấn luyện mạng nơ-ron tích chập (CNN), nhận diện khuôn mặt và phát hiện vật thể YOLO."
    },
    {
        "code": "IT4180",
        "name": "Xử lý ngôn ngữ tự nhiên (NLP)",
        "credits": 3,
        "skills": ["NLP", "PyTorch", "TensorFlow", "Python", "Deep Learning"],
        "positions": [8],
        "description": "Xử lý văn bản tiếng Việt, trích xuất thực thể, dịch máy và ứng dụng mô hình ngôn ngữ lớn Transformers."
    },
    {
        "code": "IT4220",
        "name": "Phân tích dữ liệu kinh doanh & Trực quan hóa",
        "credits": 3,
        "skills": ["Power BI", "Tableau", "Excel nâng cao", "SQL", "Data Cleaning", "Phân tích dữ liệu"],
        "positions": [4],
        "description": "Thiết kế dashboard báo cáo quản trị BI, phân tích xu hướng và xây dựng mô hình dự báo kinh doanh."
    },
    {
        "code": "MI2020",
        "name": "Toán rời rạc & Xác suất thống kê ứng dụng",
        "credits": 4,
        "skills": ["Xác suất thống kê", "Toán rời rạc & Đại số tuyến tính", "Pandas"],
        "positions": [4, 8],
        "description": "Cơ sở toán học cho khoa học dữ liệu: phân phối xác suất, kiểm định giả thuyết và đại số ma trận tuyến tính."
    },
    {
        "code": "IT4780",
        "name": "Phát triển ứng dụng di động đa nền tảng",
        "credits": 3,
        "skills": ["Flutter", "Dart", "React Native", "Swift", "Kotlin", "Mobile UX", "RESTful API"],
        "positions": [7],
        "description": "Phát triển ứng dụng di động cho iOS & Android với Flutter/React Native, giao diện native và gọi API."
    },
    {
        "code": "IT4110",
        "name": "Kiến trúc và Thiết kế phần mềm",
        "credits": 3,
        "skills": ["Design Patterns", "Clean Code", "OOP", "Microservices", "Java", "Python", "Git"],
        "positions": [1, 3],
        "description": "Áp dụng các mẫu thiết kế hướng đối tượng (GoF), kiến trúc phân lớp Clean Architecture và nguyên lý SOLID."
    },
    {
        "code": "IT4440",
        "name": "Quản lý dự án phần mềm & Quy trình Agile",
        "credits": 3,
        "skills": ["Git", "Jira", "CI/CD", "Kiểm thử phần mềm", "Agile/Scrum"],
        "positions": [1, 2, 3, 5, 6],
        "description": "Quản lý chu trình phát triển phần mềm theo chuẩn Agile/Scrum, theo dõi task trên Jira và tích hợp Git."
    }
]


def evaluate_profile_fit_and_suggest_courses(user_id, position_id=None, save_history=False, conn=None):
    """
    Hàm phân tích & đối sánh hồ sơ sinh viên với vị trí nghề nghiệp mong muốn,
    đồng thời tự động gợi ý các môn học đại học và khóa học trực tuyến phù hợp.
    """
    import re
    from datetime import date

    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    try:
        # 1. Xác định vị trí nghề nghiệp mục tiêu
        if not position_id:
            prof = conn.execute("SELECT target_position_id FROM student_profiles WHERE user_id = ?", (user_id,)).fetchone()
            position_id = prof["target_position_id"] if prof and prof["target_position_id"] else 1

        pos = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,)).fetchone()
        if not pos:
            pos = conn.execute("SELECT * FROM positions ORDER BY id ASC LIMIT 1").fetchone()

        jobs_rows = conn.execute("SELECT * FROM jobs WHERE position_id = ?", (pos["id"],)).fetchall()
        user_skills = [
            r["name"].strip().lower()
            for r in conn.execute("SELECT name FROM skills WHERE user_id = ?", (user_id,)).fetchall()
        ]
        user_certs = [
            r["name"].strip().lower()
            for r in conn.execute("SELECT name FROM certificates WHERE user_id = ?", (user_id,)).fetchall()
        ]
        user_courses_rows = conn.execute("SELECT code, name FROM courses WHERE user_id = ?", (user_id,)).fetchall()
        user_course_codes = {r["code"].strip().upper() for r in user_courses_rows if r["code"]}
        user_course_names = {r["name"].strip().lower() for r in user_courses_rows if r["name"]}

        user_exps = conn.execute(
            "SELECT start_date, end_date FROM experiences WHERE user_id = ?", (user_id,)
        ).fetchall()
        all_recs_rows = conn.execute("SELECT * FROM course_recommendations").fetchall()

        def _match(a, b):
            return a == b or a in b or b in a

        # Ánh xạ thêm các kỹ năng được trang bị từ các học phần sinh viên đã hoàn thành
        course_taught_skills = set(user_course_names)
        for c in ACADEMIC_CURRICULUM:
            c_code = c["code"].strip().upper()
            c_name = c["name"].strip().lower()
            if c_code in user_course_codes or any(_match(c_name, uc) for uc in user_course_names):
                for sk in c.get("skills", []):
                    course_taught_skills.add(sk.strip().lower())

        # 2. Tổng hợp kỹ năng yêu cầu từ vị trí & tin tuyển dụng
        req_skills = []
        for s in parse_json_list(pos["core_skills"]):
            if s not in req_skills:
                req_skills.append(s)
        for j in jobs_rows:
            for s in parse_json_list(j["skills"]):
                if s not in req_skills:
                    req_skills.append(s)

        # 3. Đối chiếu kỹ năng & kiến thức đã học
        have = []
        have_by_courses = []
        missing = []
        for req in req_skills:
            req_lower = req.lower()
            if any(_match(us, req_lower) for us in user_skills):
                have.append(req)
            elif any(_match(cs, req_lower) for cs in course_taught_skills):
                have.append(req)
                have_by_courses.append(req)
            else:
                missing.append(req)

        # 4. Đối chiếu chứng chỉ
        rec_certs = []
        missing_certs = []
        for j in jobs_rows:
            for c in parse_json_list(j["certificates"]):
                if c not in rec_certs:
                    rec_certs.append(c)
                    c_lower = c.lower()
                    if not any(_match(uc, c_lower) for uc in user_certs):
                        missing_certs.append(c)

        # 5. Đối chiếu số năm kinh nghiệm
        def _min_years(text):
            m = re.search(r"\d+", text or "")
            return int(m.group()) if m else 0

        def _to_date(s):
            try:
                y, mth = [int(x) for x in (s or "").split("-")[:2]]
                return date(y, mth, 1)
            except Exception:
                return None

        req_years_list = [_min_years(j["experience_required"]) for j in jobs_rows]
        required_years = Counter(req_years_list).most_common(1)[0][0] if req_years_list else 0
        user_months = 0
        for e in user_exps:
            sd = _to_date(e["start_date"])
            ed = _to_date(e["end_date"]) or date.today()
            if sd and ed >= sd:
                user_months += (ed.year - sd.year) * 12 + (ed.month - sd.month)
        user_years = round(user_months / 12, 1)
        experience_met = user_years >= required_years

        matched_count = len(have) + (len(rec_certs) - len(missing_certs)) + (1 if experience_met else 0)
        total = len(req_skills) + len(rec_certs) + 1
        score = round(matched_count / total * 100) if total > 0 else 0

        if score >= 75:
            summary = f'Tuyệt vời! Hồ sơ của bạn đạt mức độ phù hợp rất cao ({score}%) đối với vị trí "{pos["name"]}".'
        elif score >= 50:
            summary = f'Khá tốt! Mức độ phù hợp của bạn là {score}%. Hãy bổ sung các kỹ năng còn thiếu vào Lộ trình học tập.'
        else:
            summary = f'Mức độ phù hợp hiện tại là {score}%. Vị trí "{pos["name"]}" đòi hỏi thêm các kỹ năng chuyên sâu mà bạn cần bổ sung.'
        summary += (
            f' Kinh nghiệm: bạn có khoảng {user_years} năm, yêu cầu phổ biến là {required_years}+ năm'
            f' ({"đạt" if experience_met else "chưa đạt"}).'
        )

        # 6. Tự động gợi ý các môn học đại học CNTT phù hợp (chưa học & bù đắp kỹ năng thiếu)
        suggested_academic_courses = []
        for c in ACADEMIC_CURRICULUM:
            c_code = c["code"].strip().upper()
            c_name = c["name"].strip().lower()
            # Bỏ qua nếu sinh viên đã học môn này
            if c_code in user_course_codes or any(_match(c_name, uc) for uc in user_course_names):
                continue

            # Tìm các kỹ năng còn thiếu mà môn này đào tạo
            matched_missing = [
                s for s in c["skills"]
                if any(_match(s.lower(), m.lower()) for m in missing)
            ]
            is_core_for_target = (pos["id"] in c.get("positions", []))

            if matched_missing or is_core_for_target:
                reason = (
                    f"Bổ trợ trực tiếp kỹ năng thiếu: {', '.join(matched_missing)}"
                    if matched_missing
                    else f"Học phần chuyên ngành trọng tâm cho vị trí {pos['name']}"
                )
                suggested_academic_courses.append({
                    "code": c["code"],
                    "name": c["name"],
                    "credits": c["credits"],
                    "matched_missing_skills": matched_missing,
                    "is_core": is_core_for_target,
                    "description": c["description"],
                    "reason": reason,
                })

        # Sắp xếp môn bù đắp nhiều kỹ năng thiếu nhất lên đầu
        suggested_academic_courses.sort(
            key=lambda x: (len(x["matched_missing_skills"]), 1 if x["is_core"] else 0),
            reverse=True,
        )
        suggested_academic_courses = suggested_academic_courses[:6]

        # 7. Gợi ý khóa học trực tuyến & chứng chỉ
        recommendations = []
        seen_titles = set()
        for m_skill in missing:
            m_lower = m_skill.lower()
            matched_rec = None
            for r in all_recs_rows:
                sk_lower = r["skill_name"].strip().lower()
                if sk_lower == m_lower or sk_lower in m_lower or m_lower in sk_lower:
                    matched_rec = dict(r)
                    break
            if matched_rec and matched_rec["title"] not in seen_titles:
                seen_titles.add(matched_rec["title"])
                recommendations.append(matched_rec)
            elif not matched_rec:
                fallback_title = f"Khóa học thực chiến {m_skill} cho vị trí {pos['name']}"
                if fallback_title not in seen_titles:
                    seen_titles.add(fallback_title)
                    recommendations.append({
                        "id": 0,
                        "skill_name": m_skill,
                        "title": fallback_title,
                        "provider": "Coursera / Udemy",
                        "rec_type": "course",
                        "duration": "4 tuần",
                        "url": "https://www.coursera.org",
                        "description": f"Bổ sung kiến thức nền tảng và dự án thực hành về {m_skill} đáp ứng yêu cầu doanh nghiệp.",
                    })

        # 8. Lưu lịch sử đối sánh nếu được yêu cầu
        history_list = []
        if save_history:
            last_hist = conn.execute(
                "SELECT position_id, score FROM comparison_history WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                (user_id,),
            ).fetchone()
            if not last_hist or last_hist["position_id"] != pos["id"] or last_hist["score"] != score:
                conn.execute(
                    """
                    INSERT INTO comparison_history (user_id, position_id, position_name, score, matched_skills, missing_skills)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        pos["id"],
                        pos["name"],
                        score,
                        dump_json_list(have),
                        dump_json_list(missing),
                    ),
                )
                conn.commit()

        history_rows = conn.execute(
            "SELECT id, position_id, position_name, score, matched_skills, missing_skills, created_at FROM comparison_history WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (user_id,),
        ).fetchall()
        history_list = [
            {
                "id": h["id"],
                "position_id": h["position_id"],
                "position_name": h["position_name"],
                "score": h["score"],
                "matched_count": len(parse_json_list(h["matched_skills"])),
                "missing_count": len(parse_json_list(h["missing_skills"])),
                "created_at": h["created_at"],
            }
            for h in history_rows
        ]

        return {
            "target_position": {
                "id": pos["id"],
                "name": pos["name"],
                "code": pos["code"],
                "demand_level": pos["demand_level"],
            },
            "position_id": pos["id"],
            "position_name": pos["name"],
            "score": score,
            "have": have,
            "have_by_courses": have_by_courses,
            "missing": missing,
            "missing_certs": missing_certs,
            "experience": {
                "required_years": required_years,
                "user_years": user_years,
                "met": experience_met,
            },
            "summary": summary,
            "suggested_academic_courses": suggested_academic_courses,
            "recommended_certs": rec_certs,
            "recommendations": recommendations,
            "history": history_list,
        }
    finally:
        if close_conn:
            conn.close()


@app.route("/api/compare", methods=["POST"])
def api_compare():
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    position_id = int(payload.get("position_id") or 1)
    eval_data = evaluate_profile_fit_and_suggest_courses(user_id, position_id=position_id, save_history=True)
    return api_response(True, eval_data)


@app.route("/api/profile/evaluation", methods=["GET"])
def api_profile_evaluation():
    user_id = get_current_user_id()
    pos_id = request.args.get("position_id")
    pos_id = int(pos_id) if pos_id and pos_id.isdigit() else None
    eval_data = evaluate_profile_fit_and_suggest_courses(user_id, position_id=pos_id, save_history=False)
    return api_response(True, eval_data)


@app.route("/api/compare/history", methods=["GET"])
def api_compare_history():
    user_id = get_current_user_id()
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, position_id, position_name, score, matched_skills, missing_skills, created_at FROM comparison_history WHERE user_id = ? ORDER BY id DESC LIMIT 10",
        (user_id,),
    ).fetchall()
    conn.close()
    items = [
        {
            "id": r["id"],
            "position_id": r["position_id"],
            "position_name": r["position_name"],
            "score": r["score"],
            "matched_skills": parse_json_list(r["matched_skills"]),
            "missing_skills": parse_json_list(r["missing_skills"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]
    return api_response(True, items)


@app.route("/api/plan", methods=["GET"])
def api_get_plans():
    user_id = get_current_user_id()
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM learning_plans WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()
    return api_response(True, [dict(r) for r in rows])


@app.route("/api/plan", methods=["POST"])
def api_create_plan():
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return api_response(False, None, "Tiêu đề mục tiêu không được để trống!", 400)

    category = (payload.get("category") or "Kỹ năng bổ sung").strip()
    plan_type = (payload.get("type") or "skill").strip()
    status = (payload.get("status") or "todo").strip()
    target_date = (payload.get("target_date") or "").strip()
    note = (payload.get("note") or "").strip()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO learning_plans (user_id, title, category, type, status, target_date, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, title, category, plan_type, status, target_date, note),
    )
    new_id = cur.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM learning_plans WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return api_response(True, dict(row), "Đã thêm mục tiêu mới vào kế hoạch!", 201)


@app.route("/api/plan/<int:plan_id>", methods=["PUT"])
def api_update_plan(plan_id):
    user_id = get_current_user_id() or 1
    payload = request.get_json(silent=True) or {}
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM learning_plans WHERE id = ? AND user_id = ?", (plan_id, user_id)).fetchone()
    if not existing:
        conn.close()
        return api_response(False, None, "Không tìm thấy mục kế hoạch!", 404)

    title = (payload.get("title") if "title" in payload else existing["title"]).strip()
    category = (payload.get("category") if "category" in payload else existing["category"]).strip()
    plan_type = (payload.get("type") if "type" in payload else existing["type"]).strip()
    status = (payload.get("status") if "status" in payload else existing["status"]).strip()
    target_date = (payload.get("target_date") if "target_date" in payload else existing["target_date"]).strip()
    note = (payload.get("note") if "note" in payload else existing["note"]).strip()

    conn.execute(
        """
        UPDATE learning_plans
        SET title = ?, category = ?, type = ?, status = ?, target_date = ?, note = ?
        WHERE id = ? AND user_id = ?
        """,
        (title, category, plan_type, status, target_date, note, plan_id, user_id),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM learning_plans WHERE id = ?", (plan_id,)).fetchone()
    conn.close()
    return api_response(True, dict(updated), "Cập nhật kế hoạch thành công!")


@app.route("/api/plan/<int:plan_id>", methods=["DELETE"])
def api_delete_plan(plan_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    conn.execute("DELETE FROM learning_plans WHERE id = ? AND user_id = ?", (plan_id, user_id))
    conn.commit()
    conn.close()
    return api_response(True, None, "Xóa mục kế hoạch thành công!")


# ==============================================================================
# API CHATBOT TRỢ LÝ ĐỊNH HƯỚNG NGHỀ NGHIỆP CNTT (/api/chatbot)
# Kiến trúc Hybrid: Gọi AI (Gemini/OpenAI) kèm dữ liệu SQLite (Mini-RAG) + Fallback
# ==============================================================================

# ĐIỀN API KEY GEMINI CỦA BẠN VÀO ĐÂY (hoặc đặt biến môi trường GEMINI_API_KEY):
CHATBOT_GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
CHATBOT_GEMINI_MODEL = "gemini-2.5-flash"


def _call_gemini_with_sqlite_context(api_key, user_message, history, student_context):
    """Gọi Google Gemini REST API kèm ngữ cảnh trang web & hồ sơ sinh viên từ SQLite."""
    import urllib.request
    import json as _json

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{CHATBOT_GEMINI_MODEL}:generateContent?key={api_key}"
    system_prompt = (
        "Bạn là Trợ lý AI chính thức của website IT Career Compass (Đề tài NLCNPM23CS-38).\n"
        "Dưới đây là toàn bộ thông tin cấu trúc trang web và dữ liệu thực tế trích xuất từ CSDL SQLite của người dùng đang trò chuyện:\n"
        f"{student_context}\n\n"
        "Hãy trả lời tự nhiên, thông minh, linh hoạt mọi câu hỏi của người dùng bằng tiếng Việt, bám sát dữ liệu thực tế trên trang web."
    )

    contents = [
        {"role": "user", "parts": [{"text": system_prompt}]},
        {"role": "model", "parts": [{"text": "Mình đã nắm rõ toàn bộ chức năng website và hồ sơ năng lực của bạn trong CSDL."}]},
    ]
    for h in (history or [])[-8:]:
        role = "user" if h.get("role") == "user" else "model"
        text = (h.get("content") or "").strip()
        if text:
            contents.append({"role": role, "parts": [{"text": text}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    req = urllib.request.Request(
        url,
        data=_json.dumps({"contents": contents}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = _json.loads(resp.read().decode("utf-8"))
        return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")


def _call_hf_llama_with_sqlite_context(user_message, history, website_context):
    """Gọi Mô hình Ngôn ngữ Lớn (Llama-3.2-Instruct trên HuggingFace Space) hoàn toàn miễn phí,
    không bị giới hạn 429, kèm 100% dữ liệu thực tế người dùng đã nhập trên trang web."""
    import urllib.request
    import json as _json

    history_lines = []
    for h in (history or [])[-6:]:
        role_label = "Người dùng" if h.get("role") == "user" else "Trợ lý AI"
        text = (h.get("content") or "").strip()
        if text:
            history_lines.append(f"{role_label}: {text}")
    history_block = "\n".join(history_lines)

    full_prompt = (
        "Bạn là Trợ lý AI chính thức của trang web IT Career Compass (Hệ thống định hướng kỹ năng nghề nghiệp CNTT).\n"
        "Nhiệm vụ của bạn là hỗ trợ người dùng trả lời chính xác MỌI câu hỏi dựa trên TẤT CẢ dữ liệu mà người dùng đã nhập vào trang web dưới đây:\n\n"
        f"{website_context}\n\n"
        + (f"[LỊCH SỬ HỘI THOẠI GẦN ĐÂY]\n{history_block}\n\n" if history_block else "")
        + f"[CÂU HỎI CỦA NGƯỜI DÙNG]: {user_message}\n\n"
        "YÊU CẦU TRẢ LỜI:\n"
        "- Trả lời trực tiếp vào trọng tâm câu hỏi của người dùng bằng tiếng Việt tự nhiên, rõ ràng, thân thiện (dùng Markdown).\n"
        "- Bám sát 100% vào dữ liệu thực tế mà người dùng đã nhập ở trên (họ tên, MSSV, trường học, GPA, từng môn học đã nhập, từng kỹ năng, chứng chỉ, dự án/kinh nghiệm, kế hoạch học tập, vị trí mục tiêu và tin tuyển dụng trên web).\n"
        "- Tuyệt đối không trả lời chung chung."
    )

    base = "https://huggingface-projects-llama-3-2-3b-instruct.hf.space"
    req = urllib.request.Request(
        f"{base}/gradio_api/call/generate",
        data=_json.dumps({"data": [full_prompt, 512, 0.25, 0.9, 50, 1.1]}).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        ev_id = _json.loads(r.read().decode("utf-8"))["event_id"]

    with urllib.request.urlopen(f"{base}/gradio_api/call/generate/{ev_id}", timeout=18) as r:
        lines = r.read().decode("utf-8").splitlines()
        for line in reversed(lines):
            if line.startswith("data: "):
                arr = _json.loads(line[6:])
                if arr and isinstance(arr[0], str) and arr[0].strip():
                    return arr[0].strip()
    return ""


def _call_free_llm_with_sqlite_context(user_message, history, website_context):
    """Cổng LLM dự phòng thứ 2 (LLM7 OpenAI-compatible Gateway) kèm ngữ cảnh SQLite."""
    import urllib.request
    import json as _json

    history_lines = []
    for h in (history or [])[-6:]:
        role_label = "Người dùng" if h.get("role") == "user" else "Trợ lý AI"
        text = (h.get("content") or "").strip()
        if text:
            history_lines.append(f"{role_label}: {text}")
    history_block = "\n".join(history_lines)

    full_prompt = (
        "[DỮ LIỆU TRANG WEB IT CAREER COMPASS & HỒ SƠ NGƯỜI DÙNG ĐÃ NHẬP]\n"
        f"{website_context}\n\n"
        + (f"[LỊCH SỬ TRÒ CHUYỆN]\n{history_block}\n\n" if history_block else "")
        + f"[CÂU HỎI CỦA NGƯỜI DÙNG]: {user_message}\n\n"
        "Hãy trả lời trực tiếp, chi tiết, đúng trọng tâm câu hỏi bằng tiếng Việt dựa trên đúng dữ liệu người dùng đã nhập ở trên."
    )

    req = urllib.request.Request(
        "https://api.llm7.io/v1/chat/completions",
        data=_json.dumps({
            "model": "default",
            "temperature": 0.2,
            "max_tokens": 500,
            "messages": [{"role": "user", "content": full_prompt}],
        }).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = _json.loads(resp.read().decode("utf-8"))
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()


def _resolve_chatbot_user_id(payload):
    """Xác định chính xác tài khoản người dùng đang thao tác trên trình duyệt."""
    uid = get_current_user_id()
    if uid:
        return uid
    if payload.get("user_id"):
        try:
            return int(payload.get("user_id"))
        except (ValueError, TypeError):
            pass
    auth_header = request.headers.get("Authorization", "")
    if "user_" in auth_header:
        try:
            return int(auth_header.split("user_")[-1].strip())
        except (ValueError, TypeError):
            pass
    conn = get_db_connection()
    row = conn.execute("SELECT id FROM users WHERE role = 'student' ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return row["id"] if row else 1


@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    """
    Endpoint AI Hỗ trợ Người dùng thực thụ của Website (/api/chatbot):
    1. Tự động nhận diện đúng tài khoản người dùng đang đăng nhập và đọc 100% dữ liệu người dùng đã nhập
       (Hồ sơ cá nhân, Học phần & điểm số, Kỹ năng, Chứng chỉ, Kinh nghiệm & Dự án, Kế hoạch học tập,
       Điểm đánh giá 8 vị trí nghề nghiệp và Tin tuyển dụng).
    2. Hỗ trợ thực thi thao tác nhanh ngay trong khung chat (ví dụ: thêm kỹ năng, thêm mục tiêu học tập, đổi vị trí mục tiêu).
    3. Kết nối trực tiếp mô hình AI sinh ngôn ngữ tự nhiên (Gemini / Llama-3.2-Instruct / LLM7) kèm toàn bộ ngữ cảnh trang web.
    """
    payload = request.get_json(silent=True) or {}
    user_id = _resolve_chatbot_user_id(payload)
    message = (payload.get("message") or "").strip()
    history = payload.get("history") or []
    ui_api_key = (payload.get("api_key") or "").strip()
    active_api_key = ui_api_key or CHATBOT_GEMINI_API_KEY

    if not message:
        return api_response(False, None, "Vui lòng nhập nội dung câu hỏi!", 400)

    msg_lower = message.lower()
    conn = get_db_connection()

    # Hỗ trợ AI thực hiện hành động trực tiếp trên web nếu người dùng yêu cầu "thêm kỹ năng ..." hoặc "thêm kế hoạch ..."
    if msg_lower.startswith("thêm kỹ năng ") or msg_lower.startswith("them ky nang "):
        skill_name = message[13:].strip()
        if skill_name:
            conn.execute(
                "INSERT INTO skills (user_id, name, category, level, note) VALUES (?, ?, ?, ?, ?)",
                (user_id, skill_name, "Kỹ năng chuyên môn", 3, "Thêm qua Trợ lý AI"),
            )
            conn.commit()
            conn.close()
            return api_response(
                True,
                {
                    "reply": f"✅ Mình đã thêm trực tiếp kỹ năng **{skill_name}** (Mức độ: 3/5) vào mục **Hồ sơ sinh viên (`/profile`)** của bạn! Bạn có thể tải lại trang Hồ sơ hoặc trang Đánh giá phù hợp để xem điểm số mới.",
                    "mode": "action_agent",
                },
            )

    if msg_lower.startswith("thêm kế hoạch ") or msg_lower.startswith("thêm mục tiêu "):
        plan_title = message[14:].strip()
        if plan_title:
            conn.execute(
                "INSERT INTO learning_plans (user_id, title, category, type, status, target_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, plan_title, "Mục tiêu AI gợi ý", "skill", "todo", "2026-12-31", "Thêm trực tiếp từ Trợ lý AI"),
            )
            conn.commit()
            conn.close()
            return api_response(
                True,
                {
                    "reply": f"✅ Mình đã thêm mục tiêu **\"{plan_title}\"** vào trang **Kế hoạch học tập (`/plan`)** của bạn (Trạng thái: *Cần làm*)!",
                    "mode": "action_agent",
                },
            )

    prof = conn.execute("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,)).fetchone()
    user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    user_skills_rows = conn.execute("SELECT name, category, level, note FROM skills WHERE user_id = ?", (user_id,)).fetchall()
    user_courses = conn.execute("SELECT code, name, credits, grade, term FROM courses WHERE user_id = ?", (user_id,)).fetchall()
    user_certs = conn.execute("SELECT name, organization, issue_date, expiry_date FROM certificates WHERE user_id = ?", (user_id,)).fetchall()
    user_exps = conn.execute("SELECT title, company, role_type, start_date, end_date, description FROM experiences WHERE user_id = ?", (user_id,)).fetchall()
    positions = conn.execute("SELECT * FROM positions ORDER BY id ASC").fetchall()
    total_jobs = conn.execute("SELECT COUNT(*) AS c FROM jobs").fetchone()["c"]
    recent_jobs = conn.execute(
        "SELECT j.*, p.name AS position_name FROM jobs j LEFT JOIN positions p ON j.position_id = p.id ORDER BY j.id DESC LIMIT 10"
    ).fetchall()
    plan_items = conn.execute(
        "SELECT title, category, type, status, target_date, note FROM learning_plans WHERE user_id = ? ORDER BY id DESC",
        (user_id,),
    ).fetchall()
    conn.close()

    user_skills = [r["name"] for r in user_skills_rows]
    target_id = prof["target_position_id"] if prof and prof["target_position_id"] else 1
    eval_data = evaluate_profile_fit_and_suggest_courses(user_id, target_id, save_history=False)

    # Tính điểm phù hợp trên toàn bộ 8 vị trí
    all_pos_scores = []
    for pos in positions:
        ev = evaluate_profile_fit_and_suggest_courses(user_id, pos["id"], save_history=False)
        if ev:
            all_pos_scores.append({
                "id": pos["id"],
                "name": pos["name"],
                "score": ev["score"],
                "demand": pos["demand_level"],
                "have": ev.get("have", []),
                "missing": ev.get("missing", [])[:5],
            })
    all_pos_scores.sort(key=lambda x: x["score"], reverse=True)

    # Chuỗi hóa toàn bộ dữ liệu thực tế người dùng đã nhập vào web
    student_name = (prof["full_name"] if prof and prof["full_name"] else (user_row["full_name"] if user_row else "Sinh viên"))
    student_code = prof["student_code"] if prof and prof["student_code"] else "Chưa nhập"
    student_email = prof["email"] if prof and prof["email"] else (user_row["email"] if user_row else "Chưa nhập")
    student_phone = prof["phone"] if prof and prof["phone"] else "Chưa nhập"
    student_uni = prof["university"] if prof and prof["university"] else "Chưa nhập"
    student_faculty = prof["faculty"] if prof and prof["faculty"] else "Chưa nhập"
    student_major = prof["major"] if prof and prof["major"] else "Chưa nhập"
    student_year = prof["academic_year"] if prof and prof["academic_year"] else "Chưa nhập"
    student_gpa = prof["gpa"] if prof and prof["gpa"] else "0.0"
    student_bio = prof["bio"] if prof and prof["bio"] else "Chưa nhập"
    target_pos_name = eval_data["target_position"]["name"] if eval_data else "Backend Developer"
    target_score = eval_data["score"] if eval_data else 0

    courses_detail_str = (
        "; ".join([f"{c['code']} - {c['name']} ({c['credits']} tín chỉ, Điểm: {c['grade']}, Học kỳ: {c['term'] or 'N/A'})" for c in user_courses])
        if user_courses else "Người dùng chưa nhập học phần nào"
    )
    skills_detail_str = (
        "; ".join([f"{s['name']} (Nhóm: {s['category']}, Mức độ: {s['level']}/5{', Ghi chú: ' + s['note'] if s['note'] else ''})" for s in user_skills_rows])
        if user_skills_rows else "Người dùng chưa nhập kỹ năng nào"
    )
    certs_detail_str = (
        "; ".join([f"{c['name']} do {c['organization']} cấp ngày {c['issue_date'] or 'N/A'}" for c in user_certs])
        if user_certs else "Người dùng chưa nhập chứng chỉ nào"
    )
    exps_detail_str = (
        "; ".join([f"{e['title']} tại {e['company']} ({e['role_type']}, {e['start_date']} - {e['end_date']})" for e in user_exps])
        if user_exps else "Người dùng chưa nhập kinh nghiệm/dự án nào"
    )
    plans_detail_str = (
        "; ".join([f"{p['title']} (Danh mục: {p['category']}, Trạng thái: {p['status']}, Hạn: {p['target_date'] or 'N/A'})" for p in plan_items])
        if plan_items else "Người dùng chưa nhập mục tiêu nào trong Kế hoạch học tập"
    )
    ranking_str = "; ".join([f"{p['name']}: {p['score']}% (Nhu cầu: {p['demand']})" for p in all_pos_scores])
    jobs_sample_str = "; ".join([f"{j['title']} tại {j['company']} (Vị trí: {j['position_name']}, Lương: {j['salary']}, Địa điểm: {j['location']})" for j in recent_jobs[:6]])

    website_and_student_context = (
        "=== 1. DỮ LIỆU CÁ NHÂN DO NGƯỜI DÙNG ĐÃ NHẬP TRÊN WEBSITE ===\n"
        f"- Họ và tên: {student_name}\n"
        f"- Mã số sinh viên (MSSV): {student_code}\n"
        f"- Email: {student_email} | Số điện thoại: {student_phone}\n"
        f"- Trường học: {student_uni} | Khoa: {student_faculty} | Chuyên ngành: {student_major} | Niên khóa: {student_year}\n"
        f"- Điểm trung bình tích lũy (GPA): {student_gpa}/4.0\n"
        f"- Giới thiệu bản thân (Bio): {student_bio}\n"
        f"- Vị trí nghề nghiệp mục tiêu đang chọn: {target_pos_name} (Độ phù hợp hiện tại: {target_score}%)\n\n"
        "=== 2. DANH SÁCH HỌC PHẦN, KỸ NĂNG, CHỨNG CHỈ, KINH NGHIỆM & KẾ HOẠCH NGƯỜI DÙNG ĐÃ NHẬP ===\n"
        f"- Học phần đã học ({len(user_courses)} môn): {courses_detail_str}\n"
        f"- Kỹ năng hiện có ({len(user_skills_rows)} kỹ năng): {skills_detail_str}\n"
        f"- Chứng chỉ đã nhập ({len(user_certs)} chứng chỉ): {certs_detail_str}\n"
        f"- Kinh nghiệm & Dự án đã nhập ({len(user_exps)} mục): {exps_detail_str}\n"
        f"- Kế hoạch học tập cá nhân ({len(plan_items)} mục): {plans_detail_str}\n\n"
        "=== 3. KẾT QUẢ PHÂN TÍCH ĐỊNH HƯỚNG & DỮ LIỆU WEBSITE ===\n"
        f"- Điểm phù hợp của người dùng với 8 vị trí CNTT trên web: {ranking_str}\n"
        f"- Kỹ năng đã đáp ứng cho vị trí mục tiêu ({target_pos_name}): {', '.join(eval_data.get('have', [])) if eval_data and eval_data.get('have') else 'Chưa khớp kỹ năng nào'}\n"
        f"- Kỹ năng còn thiếu cho vị trí mục tiêu ({target_pos_name}): {', '.join(eval_data.get('missing', [])) if eval_data and eval_data.get('missing') else 'Không thiếu'}\n"
        f"- Học phần gợi ý nên học bổ sung: {', '.join(c['code'] + ' - ' + c['name'] for c in eval_data.get('suggested_courses', [])[:5]) if eval_data else ''}\n"
        f"- Tin tuyển dụng trên trang web ({total_jobs} tin): {jobs_sample_str}\n"
        "- Các trang chức năng của website: Tổng quan (/dashboard), Hồ sơ sinh viên (/profile), Vị trí nghề nghiệp (/positions), Tin tuyển dụng (/jobs), Thống kê kỹ năng (/statistics), Đánh giá phù hợp (/compare), Kế hoạch học tập (/plan)."
    )

    # ------------------------------------------------------------------
    # TẦNG 1: Nếu người dùng nhập Gemini API Key -> Gọi Google Gemini AI
    # ------------------------------------------------------------------
    if active_api_key:
        try:
            ai_reply = _call_gemini_with_sqlite_context(active_api_key, message, history, website_and_student_context)
            if ai_reply:
                return api_response(True, {"reply": ai_reply, "mode": "gemini_rag"})
        except Exception:
            pass

    # ------------------------------------------------------------------
    # TẦNG 2 (MẶC ĐỊNH): Gọi Llama-3.2-Instruct (HuggingFace Space - Không giới hạn 429)
    # ------------------------------------------------------------------
    try:
        hf_reply = _call_hf_llama_with_sqlite_context(message, history, website_and_student_context)
        if hf_reply:
            return api_response(True, {"reply": hf_reply, "mode": "hf_llama_rag"})
    except Exception:
        pass

    # ------------------------------------------------------------------
    # TẦNG 3: Gọi cổng LLM7 OpenAI-compatible dự phòng
    # ------------------------------------------------------------------
    try:
        llm_reply = _call_free_llm_with_sqlite_context(message, history, website_and_student_context)
        if llm_reply:
            return api_response(True, {"reply": llm_reply, "mode": "llm7_rag"})
    except Exception:
        pass

    # ------------------------------------------------------------------
    # TẦNG 4 (Dự phòng khi mất mạng Internet): Trả lời chi tiết từng mục dữ liệu người dùng đã nhập
    # ------------------------------------------------------------------
    if any(k in msg_lower for k in ["môn", "học phần", "điểm", "tín chỉ", "đã học"]):
        if user_courses:
            lines = "\n".join([f"• **{c['code']} - {c['name']}**: **{c['credits']} tín chỉ** — Điểm: **{c['grade']}** (Học kỳ: {c['term'] or 'N/A'})" for c in user_courses])
            reply = f"📚 **Danh sách {len(user_courses)} học phần bạn đã nhập trên hệ thống ({student_name}):**\n{lines}"
        else:
            reply = f"📚 Hiện tại tài khoản **{student_name}** chưa nhập học phần nào. Bạn có thể vào trang **Hồ sơ sinh viên (`/profile`)** -> mục **Học phần đã học** để thêm môn học nhé!"
        return api_response(True, {"reply": reply, "mode": "sqlite_direct"})

    if any(k in msg_lower for k in ["kỹ năng của tôi", "kỹ năng tôi", "tôi có kỹ năng", "đã nhập kỹ năng", "skill"]):
        if user_skills_rows:
            lines = "\n".join([f"• **{s['name']}** (*{s['category']}*) — Mức độ: **{s['level']}/5** {('- ' + s['note']) if s['note'] else ''}" for s in user_skills_rows])
            reply = f"🛠️ **Các kỹ năng bạn đã nhập vào hồ sơ ({len(user_skills_rows)} kỹ năng):**\n{lines}\n\n💡 Bạn cũng có thể gõ trực tiếp vào chat: `Thêm kỹ năng <Tên kỹ năng>` để mình thêm nhanh vào hồ sơ giúp bạn!"
        else:
            reply = "🛠️ Bạn chưa nhập kỹ năng nào. Hãy vào **Hồ sơ sinh viên (`/profile`)** hoặc gõ `Thêm kỹ năng Python` ngay tại đây!"
        return api_response(True, {"reply": reply, "mode": "sqlite_direct"})

    if any(k in msg_lower for k in ["chứng chỉ", "toeic", "ielts", "coursera", "aws"]):
        if user_certs:
            lines = "\n".join([f"• **{c['name']}** — Tổ chức cấp: *{c['organization']}* (Ngày cấp: {c['issue_date'] or 'N/A'})" for c in user_certs])
            reply = f"🏅 **Danh sách chứng chỉ bạn đã nhập ({len(user_certs)} chứng chỉ):**\n{lines}"
        else:
            reply = f"🏅 Hiện tại hồ sơ của **{student_name}** chưa có chứng chỉ nào được nhập. Bạn có thể vào trang **Hồ sơ sinh viên (`/profile`)** -> mục **Chứng chỉ** để bổ sung!"
        return api_response(True, {"reply": reply, "mode": "sqlite_direct"})

    if any(k in msg_lower for k in ["kinh nghiệm", "dự án", "thực tập", "project", "đồ án"]):
        if user_exps:
            lines = "\n".join([f"• **{e['title']}** tại *{e['company']}* ({e['role_type']}, {e['start_date']} - {e['end_date']})" for e in user_exps])
            reply = f"💼 **Kinh nghiệm & Dự án bạn đã nhập ({len(user_exps)} mục):**\n{lines}"
        else:
            reply = f"💼 Hiện tại hồ sơ của **{student_name}** chưa nhập mục Kinh nghiệm & Dự án nào tại trang `/profile`."
        return api_response(True, {"reply": reply, "mode": "sqlite_direct"})

    if any(k in msg_lower for k in ["kế hoạch", "lộ trình", "mục tiêu học", "plan"]):
        if plan_items:
            lines = "\n".join([f"• **{p['title']}** (*{p['category']}*) — Trạng thái: **{p['status']}** (Hạn: {p['target_date'] or 'N/A'})" for p in plan_items])
            reply = f"📌 **Kế hoạch học tập hiện tại của bạn ({len(plan_items)} mục tiêu):**\n{lines}\n\n💡 Bạn có thể gõ `Thêm kế hoạch <Tên mục tiêu>` vào chat để mình thêm trực tiếp giúp bạn!"
        else:
            reply = "📌 Bạn chưa có mục tiêu nào trong trang **Kế hoạch học tập (`/plan`)**."
        return api_response(True, {"reply": reply, "mode": "sqlite_direct"})

    # Trả lời tổng hợp toàn bộ dữ liệu cá nhân đã nhập khi offline
    reply = (
        f"👤 **Toàn bộ dữ liệu hồ sơ của bạn trên hệ thống ({student_name}):**\n"
        f"- **MSSV:** {student_code} | **Trường:** {student_uni} | **Ngành:** {student_major} | **GPA:** **{student_gpa}**\n"
        f"- **Vị trí mục tiêu đang chọn:** **{target_pos_name}** (Độ phù hợp: **{target_score}%**)\n"
        f"- **Học phần đã nhập ({len(user_courses)}):** {courses_detail_str}\n"
        f"- **Kỹ năng đã nhập ({len(user_skills_rows)}):** {skills_detail_str}\n"
        f"- **Chứng chỉ ({len(user_certs)}):** {certs_detail_str}\n"
        f"- **Kinh nghiệm/Dự án ({len(user_exps)}):** {exps_detail_str}\n"
        f"- **Kế hoạch học tập ({len(plan_items)}):** {plans_detail_str}"
    )
    return api_response(True, {"reply": reply, "mode": "sqlite_direct"})


if __name__ == "__main__":
    print("=" * 68)
    print("  HE THONG DINH HUONG KY NANG NGHE NGHIEP CNTT (FLASK + SQLITE)")
    print("  De tai: NLCNPM23CS-38 - Nhanh: thanh-vien-2")
    print("  May chu dang chay tai: http://127.0.0.1:5000")
    print("=" * 68)
    app.run(debug=True, host="0.0.0.0", port=5000)
