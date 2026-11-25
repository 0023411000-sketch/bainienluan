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
PUBLIC_APIS = {"/api/auth/login", "/api/auth/register", "/api/auth/logout", "/api/chatbot", "/api/chatbot/history"}


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
        "SELECT id, full_name, email, password_hash, role, avatar_url FROM users WHERE LOWER(email) = ?",
        (email,),
    ).fetchone()
    avatar_url = ""
    if user:
        if "avatar_url" in user.keys() and user["avatar_url"]:
            avatar_url = user["avatar_url"]
        else:
            sp = conn.execute("SELECT avatar_url FROM student_profiles WHERE user_id = ?", (user["id"],)).fetchone()
            if sp and "avatar_url" in sp.keys() and sp["avatar_url"]:
                avatar_url = sp["avatar_url"]
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return api_response(False, None, "Email hoặc mật khẩu không chính xác!", 401)

    session["user_id"] = user["id"]
    session.pop("guest_chat_count", None)
    session.pop("guest_chat_history", None)
    user_data = {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "role": user["role"],
        "avatar_url": avatar_url,
        "token": f"user_{user['id']}",
    }
    return api_response(True, user_data, "Đăng nhập thành công!")


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.pop("user_id", None)
    session.pop("guest_chat_count", None)
    session.pop("guest_chat_history", None)
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
            "avatar_url": prof["avatar_url"] if "avatar_url" in prof.keys() and prof["avatar_url"] else "",
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

    avatar_url = (payload.get("avatar_url") or "").strip()

    conn = get_db_connection()
    if avatar_url:
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
                bio = ?,
                avatar_url = ?
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
                avatar_url,
                user_id,
            ),
        )
        conn.execute("UPDATE users SET full_name = ?, avatar_url = ? WHERE id = ?", (full_name, avatar_url, user_id))
    else:
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


@app.route("/api/profile/avatar", methods=["POST"])
def api_upload_avatar():
    user_id = get_current_user_id() or 1
    avatar_url = ""

    # 1. Trường hợp gửi tệp tải lên (Multipart form-data)
    if "avatar" in request.files:
        file = request.files["avatar"]
        if file and file.filename:
            filename = file.filename.lower()
            allowed_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
            ext = os.path.splitext(filename)[1]
            if ext not in allowed_exts:
                return api_response(False, None, "Định dạng ảnh không hợp lệ (hỗ trợ JPG, PNG, WEBP, GIF, SVG)!", 400)

            upload_dir = os.path.join(app.root_path, "static", "uploads", "avatars")
            os.makedirs(upload_dir, exist_ok=True)

            import time
            saved_name = f"avatar_{user_id}_{int(time.time())}{ext}"
            saved_path = os.path.join(upload_dir, saved_name)
            file.save(saved_path)
            avatar_url = f"/static/uploads/avatars/{saved_name}"

    # 2. Trường hợp gửi JSON chứa avatar_url (chọn từ mẫu hoặc dán link)
    if not avatar_url:
        payload = request.get_json(silent=True) or {}
        raw_url = (payload.get("avatar_url") or "").strip()
        if raw_url:
            avatar_url = raw_url

    if not avatar_url:
        return api_response(False, None, "Vui lòng chọn tệp ảnh đại diện hoặc chọn ảnh mẫu hợp lệ!", 400)

    conn = get_db_connection()
    conn.execute("UPDATE student_profiles SET avatar_url = ? WHERE user_id = ?", (avatar_url, user_id))
    conn.execute("UPDATE users SET avatar_url = ? WHERE id = ?", (avatar_url, user_id))
    conn.commit()
    conn.close()

    return api_response(True, {"avatar_url": avatar_url}, "Cập nhật ảnh đại diện thành công!")


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
        seen_cert_keys = set()
        for j in jobs_rows:
            for c in parse_json_list(j["certificates"]):
                c_clean = str(c).strip()
                if not c_clean:
                    continue
                # Chuẩn hóa để tránh trùng lặp
                c_key = re.sub(r'[\s\-_]+', ' ', c_clean.lower())
                if c_key not in seen_cert_keys:
                    seen_cert_keys.add(c_key)
                    rec_certs.append(c_clean)
                    if not any(_match(uc, c_key) for uc in user_certs):
                        missing_certs.append(c_clean)

        # Lọc bớt chứng chỉ cùng nhóm nhà cung cấp (VD: nhiều chứng chỉ AWS chỉ giữ 1-2 chứng chỉ tiêu biểu)
        deduped_missing_certs = []
        seen_cert_families = set()
        for c in missing_certs:
            c_low = c.lower()
            family = None
            if "aws" in c_low:
                family = "aws"
            elif "istqb" in c_low:
                family = "istqb"
            elif "deeplearning" in c_low:
                family = "deeplearning"
            elif "google" in c_low:
                family = "google"
            elif "microsoft" in c_low or "pl-300" in c_low or "azure" in c_low:
                family = "microsoft"

            if family:
                if family not in seen_cert_families:
                    seen_cert_families.add(family)
                    deduped_missing_certs.append(c)
            else:
                deduped_missing_certs.append(c)
        missing_certs = deduped_missing_certs

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

        # 7. Gợi ý khóa học trực tuyến & chứng chỉ (lọc trùng lặp & ưu tiên khóa học chất lượng)
        recommendations = []
        seen_titles = set()
        seen_skills = set()

        # Bước 7.1: Nạp các khóa học chuẩn từ bảng course_recommendations
        for m_skill in missing:
            m_lower = m_skill.lower()
            matched_rec = None
            for r in all_recs_rows:
                sk_lower = r["skill_name"].strip().lower()
                if sk_lower == m_lower or sk_lower in m_lower or m_lower in sk_lower:
                    matched_rec = dict(r)
                    break
            if matched_rec:
                t_key = matched_rec["title"].strip().lower()
                if t_key not in seen_titles:
                    seen_titles.add(t_key)
                    seen_skills.add(matched_rec["skill_name"].lower())
                    recommendations.append(matched_rec)

        # Bước 7.2: Bổ sung khóa học thực hành cho các kỹ năng thiếu còn lại (tối đa 6 gợi ý tổng cộng)
        for m_skill in missing:
            if len(recommendations) >= 6:
                break
            m_lower = m_skill.lower()
            # Bỏ qua nếu kỹ năng này đã được bao hàm trong một khóa học ở trên
            if any(m_lower in s or s in m_lower for s in seen_skills) or any(m_lower in t for t in seen_titles):
                continue

            fallback_title = f"Khóa học thực chiến {m_skill} cho vị trí {pos['name']}"
            t_key = fallback_title.lower()
            if t_key not in seen_titles:
                seen_titles.add(t_key)
                seen_skills.add(m_lower)
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
            "recommended_certs": missing_certs,
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
CHATBOT_MAX_SAVED_MESSAGES = 60


def _ensure_chat_messages_table(conn):
    """Đảm bảo bảng chat_messages luôn tồn tại ngay cả trên file database.db cũ."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)


def _load_user_chat_history(user_id, limit=40):
    """Đọc lịch sử hội thoại của người dùng đã đăng nhập từ SQLite."""
    if not user_id:
        return []
    conn = get_db_connection()
    try:
        _ensure_chat_messages_table(conn)
        rows = conn.execute(
            """
            SELECT role, content FROM (
                SELECT id, role, content FROM chat_messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            ) ORDER BY id ASC
            """,
            (user_id, limit),
        ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    finally:
        conn.close()


def _save_user_chat_turn(user_id, user_message, bot_reply):
    """Lưu cặp câu hỏi - câu trả lời vào SQLite để giữ nguyên hội thoại khi chuyển tab/trang."""
    if not user_id or not user_message or not bot_reply:
        return
    conn = get_db_connection()
    try:
        _ensure_chat_messages_table(conn)
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)",
            (user_id, user_message),
        )
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'assistant', ?)",
            (user_id, bot_reply),
        )
        conn.execute(
            """
            DELETE FROM chat_messages
            WHERE user_id = ? AND id NOT IN (
                SELECT id FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?
            )
            """,
            (user_id, user_id, CHATBOT_MAX_SAVED_MESSAGES),
        )
        conn.commit()
    finally:
        conn.close()


def _normalize_history(history, max_items=8):
    """Chuẩn hóa danh sách lịch sử hội thoại theo thứ tự luân phiên user/assistant sạch sẽ."""
    cleaned = []
    for h in (history or []):
        if not isinstance(h, dict):
            continue
        raw_role = str(h.get("role") or "").strip().lower()
        role = "user" if raw_role == "user" else "assistant"
        content = (h.get("content") or "").strip()
        if not content:
            continue
        if cleaned and cleaned[-1]["role"] == role:
            if cleaned[-1]["content"] != content:
                cleaned[-1]["content"] += "\n" + content
        else:
            cleaned.append({"role": role, "content": content})
    return cleaned[-max_items:]


def _build_chatbot_system_prompt(website_context, is_guest=False):
    """Xây dựng System Prompt tự nhiên, mạch lạc, nghiêm cấm lặp từ và lặp lại câu trả lời cũ."""
    if is_guest:
        return (
            "Bạn là Trợ lý AI của website IT Career Compass.\n"
            f"{website_context}\n\n"
            "QUY TẮC TRẢ LỜI:\n"
            "- Xưng 'mình' và gọi người dùng là 'bạn', giọng điệu tự nhiên, thân thiện.\n"
            "- Trả lời thật ngắn gọn trong 1-2 câu (dưới 50 từ) bằng tiếng Việt, không lặp từ, không liệt kê dài dòng."
        )
    return (
        "Bạn là Trợ lý AI Định hướng Nghề nghiệp CNTT của website IT Career Compass (Đề tài NLCNPM23CS-38).\n"
        "Hãy đóng vai một cố vấn nghề nghiệp (Career Mentor) gần gũi, thông minh và thực tế; xưng 'mình' và gọi người dùng là 'bạn'.\n\n"
        "QUY TẮC DIỄN ĐẠT TỰ NHIÊN & CHỐNG LẶP TỪ (BẮT BUỘC TUÂN THỦ):\n"
        "1. Đi thẳng vào trọng tâm câu hỏi ngay từ câu đầu tiên. KHÔNG mở bài rập khuôn hay nhắc lại nguyên văn câu hỏi của người dùng (tránh kiểu 'Để đánh giá hồ sơ hiện tại của bạn..., chúng ta cần xem xét...').\n"
        "2. Viết tiếng Việt tự nhiên, trôi chảy, đa dạng từ ngữ: KHÔNG lặp lại cùng một kỹ năng nhiều lần trong một câu, KHÔNG lặp đi lặp lại các từ nối hoặc cụm từ (như 'Tuy nhiên...', 'Ngoài ra...', 'nền tảng vững chắc...', 'cần phải...').\n"
        "3. Trong hội thoại nhiều lượt, TUYỆT ĐỐI KHÔNG chép lại hoặc tóm tắt lại nội dung mình vừa trả lời ở lượt trước; chỉ trả lời trực tiếp ý mới mà người dùng đang hỏi.\n"
        "4. Bám sát 100% dữ liệu thực tế bên dưới. Nếu người dùng hỏi hồ sơ phù hợp vị trí nào, hãy nêu rõ Top vị trí đạt tỷ lệ phù hợp cao nhất trong 8 vị trí, đồng thời nhận xét ngắn gọn về vị trí mục tiêu hiện tại của bạn ấy.\n"
        "5. Trình bày gọn gàng bằng Markdown (in đậm từ khóa chính, gạch đầu dòng ngắn gọn dễ đọc), độ dài vừa phải (khoảng 100 - 250 từ), luôn kết thúc câu trọn vẹn.\n\n"
        f"{website_context}"
    )


def _polish_bot_reply(reply, history=None):
    """Hậu xử lý câu trả lời AI: loại bỏ tiền tố thừa, cắt bỏ đoạn lặp từ lượt trước, khử câu trùng lặp và tránh cụt câu."""
    import re

    if not reply:
        return ""

    text = str(reply).strip()
    # 1. Xóa tiền tố vai trò nếu mô hình vô tình sinh ra
    text = re.sub(r"^(Trợ lý AI|Assistant|Bot|AI)\s*:\s*", "", text, flags=re.IGNORECASE).strip()

    # 2. Nếu mô hình vô tình chép lại đoạn đầu câu trả lời của lượt trước (lỗi phổ biến ở model nhỏ), tự động gỡ bỏ
    prev_assistant_msgs = [
        (h.get("content") or "").strip()
        for h in (history or [])
        if isinstance(h, dict) and h.get("role") in ("assistant", "bot", "model") and (h.get("content") or "").strip()
    ]
    if prev_assistant_msgs:
        last_bot = prev_assistant_msgs[-1]
        if len(text) > len(last_bot) + 25 and text.startswith(last_bot):
            text = text[len(last_bot):].lstrip(" \n\r\t—-")
        else:
            last_paras = [p.strip() for p in last_bot.split("\n\n") if len(p.strip()) >= 40]
            cur_paras = [p.strip() for p in text.split("\n\n") if p.strip()]
            removed = False
            while last_paras and len(cur_paras) > 1 and cur_paras[0] == last_paras[0]:
                cur_paras.pop(0)
                last_paras.pop(0)
                removed = True
            if removed and cur_paras:
                text = "\n\n".join(cur_paras).strip()

    # 3. Loại bỏ các dòng/đoạn trùng lặp liên tiếp hoặc câu bị lặp nguyên văn trong cùng đoạn
    raw_lines = text.splitlines()
    deduped_lines = []
    prev_norm_line = None
    for line in raw_lines:
        stripped = line.strip()
        norm_line = re.sub(r"\s+", " ", stripped.lower())
        if norm_line and norm_line == prev_norm_line:
            continue
        deduped_lines.append(line)
        if norm_line:
            prev_norm_line = norm_line
    text = "\n".join(deduped_lines)

    # Khử lặp cụm từ lắp bắp sát nhau (ví dụ: "và Docker ... và Docker" hoặc câu lặp liền kề)
    cleaned_paragraphs = []
    seen_long_sentences = set()
    for para in text.split("\n\n"):
        p_strip = para.strip()
        if not p_strip:
            continue
        # Nếu là đoạn văn xuôi bình thường (không phải danh sách bullet)
        if not re.match(r"^[-*•\d#]", p_strip):
            parts = re.split(r"(?<=[.!?])\s+", p_strip)
            unique_parts = []
            for s in parts:
                s_norm = re.sub(r"[^\w\s]", "", s.lower()).strip()
                s_norm = re.sub(r"\s+", " ", s_norm)
                if len(s_norm) >= 35 and s_norm in seen_long_sentences:
                    continue
                if len(s_norm) >= 35:
                    seen_long_sentences.add(s_norm)
                unique_parts.append(s)
            p_strip = " ".join(unique_parts).strip()
        if p_strip:
            cleaned_paragraphs.append(p_strip)

    text = "\n\n".join(cleaned_paragraphs).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 4. Nếu câu trả lời dài bị cắt cụt giữa chừng do giới hạn token, cắt gọn về câu hoàn chỉnh gần nhất
    if len(text) > 220 and text[-1] not in ".!?:)`*\"'”’]%":
        last_punct = max(text.rfind(". "), text.rfind(".\n"), text.rfind("!"), text.rfind("?"))
        if last_punct > len(text) * 0.55:
            text = text[: last_punct + 1].strip()

    return text


def _build_natural_local_advisor_reply(
    message,
    msg_lower,
    student_name,
    student_code,
    student_uni,
    student_major,
    student_gpa,
    best_pos,
    target_pos_name,
    target_score,
    eval_data,
    all_pos_scores,
    positions,
    user_courses,
    unique_skill_items,
    user_certs,
    user_exps,
    plan_items,
    recent_jobs,
    total_jobs,
    suggested_courses_list,
):
    """Cố vấn nghề nghiệp thông minh nội bộ dựa trên SQLite: diễn đạt tiếng Việt tự nhiên,
    hiểu ngữ cảnh câu hỏi tiếp nối (follow-up), không lặp từ và không trả lời rập khuôn."""
    missing_skills = list(dict.fromkeys((eval_data or {}).get("missing", [])))
    matched_skills = list(dict.fromkeys((eval_data or {}).get("have", [])))

    # 1. Hỏi chào hỏi / cảm ơn xã giao
    if any(msg_lower == g or msg_lower.startswith(g + " ") for g in ["xin chào", "chào bạn", "chào ai", "hello", "hi", "hey"]):
        return (
            f"Chào **{student_name}**! 👋 Mình đã kết nối trực tiếp với hồ sơ của bạn rồi "
            f"(hiện bạn đang khớp cao nhất với **{best_pos['name']} - {best_pos['score']}%**). "
            "Hôm nay bạn muốn mình tư vấn chọn hướng nghề nghiệp, gợi ý kỹ năng cần học tiếp theo hay lọc việc làm phù hợp?"
        )

    if any(k in msg_lower for k in ["cảm ơn", "cam on", "thank", "tuyệt vời", "ok nhé"]):
        return (
            f"Rất vui được đồng hành cùng **{student_name}**! 😊 Khi nào cần kiểm tra lại độ phù hợp, "
            "tìm học phần bổ trợ hay cập nhật [Kế hoạch học tập](/plan), bạn cứ nhắn mình bất cứ lúc nào nhé!"
        )

    # 2. Hỏi chi tiết về một vị trí nghề nghiệp cụ thể (Backend, Frontend, Fullstack, DevOps, Data, AI, Mobile, QA...)
    pos_aliases = [
        (["backend"], "backend"),
        (["frontend", "front-end", "ui/ux"], "frontend"),
        (["fullstack", "full-stack"], "fullstack"),
        (["devops", "cloud"], "devops"),
        (["data analyst", "phân tích dữ liệu", "data"], "data"),
        (["ai engineer", "trí tuệ nhân tạo", "machine learning", "ai/ml"], "ai"),
        (["mobile", "di động", "flutter", "react native"], "mobile"),
        (["qa", "qc", "tester", "kiểm thử"], "kiểm thử"),
    ]
    if any(k in msg_lower for k in ["cần những kỹ năng", "cần kỹ năng", "yêu cầu gì", "cần học gì", "vị trí "]):
        for aliases, key_hint in pos_aliases:
            if any(a in msg_lower for a in aliases):
                matched_pos = None
                for p in positions:
                    if key_hint in p["name"].lower() or key_hint in (p["code"] or "").lower():
                        matched_pos = p
                        break
                if matched_pos:
                    core_sk = parse_json_list(matched_pos["core_skills"])
                    pos_score_item = next((x for x in all_pos_scores if x["id"] == matched_pos["id"]), None)
                    p_score = pos_score_item["score"] if pos_score_item else 0
                    p_have = pos_score_item.get("have", []) if pos_score_item else []
                    p_miss = pos_score_item.get("missing", []) if pos_score_item else []
                    have_note = f"Bạn đã có sẵn: **{', '.join(p_have[:5])}**." if p_have else "Hiện hồ sơ của bạn chưa có nhiều kỹ năng trùng khớp với nhóm này."
                    miss_note = f"Nên trau dồi thêm: **{', '.join(p_miss[:5])}**." if p_miss else "Bạn đã đáp ứng hầu hết kỹ năng nền tảng!"
                    return (
                        f"Đối với vị trí **{matched_pos['name']}** *(nhu cầu tuyển dụng: {matched_pos['demand_level']})*, "
                        f"các doanh nghiệp thường yêu cầu nhóm kỹ năng cốt lõi gồm: **{', '.join(core_sk)}**.\n\n"
                        f"So với hồ sơ hiện tại của bạn (đạt **{p_score}%** độ phù hợp):\n"
                        f"- {have_note}\n"
                        f"- {miss_note}\n\n"
                        f"Bạn có thể đối sánh chi tiết hơn tại trang [Đánh giá phù hợp](/compare) nhé!"
                    )

    # 3. Hỏi lộ trình / nên học thêm kỹ năng hay môn học nào tiếp theo (bao gồm câu hỏi tiếp nối!)
    if any(k in msg_lower for k in ["học thêm", "tiếp theo", "ưu tiên học", "nên học", "lộ trình", "bổ sung"]):
        top_missing = missing_skills[:4]
        skill_advice = (
            f"- **Kỹ năng chuyên môn cần ưu tiên:** {', '.join(f'**{s}**' for s in top_missing)} (để bứt phá điểm phù hợp ở vị trí *{target_pos_name}*)."
            if top_missing
            else f"- **Kỹ năng chuyên môn:** Bạn đã nắm khá vững nền tảng cho *{target_pos_name}*, hãy tập trung làm dự án thực tế chuyên sâu hơn."
        )
        if suggested_courses_list:
            course_items = ", ".join([f"**{c['code']} - {c['name']}**" for c in suggested_courses_list[:3]])
            course_advice = f"- **Học phần đại học gợi ý đăng ký:** {course_items}."
        else:
            course_advice = "- **Học phần đại học:** Bạn đã hoàn thành tốt các môn cốt lõi hiện có trong khung chương trình."

        recs = (eval_data or {}).get("recommendations", [])[:2]
        rec_advice = (
            "- **Khóa học thực chiến nên tham khảo:** " + "; ".join([f"*{r['title']}* ({r['provider']})" for r in recs]) + "."
            if recs else ""
        )
        parts = [
            f"Để nâng cao năng lực cạnh tranh cho hướng **{target_pos_name}** (hiện đạt **{target_score}%**), mình gợi ý lộ trình ngắn hạn cho bạn như sau:",
            skill_advice,
            course_advice,
        ]
        if rec_advice:
            parts.append(rec_advice)
        parts.append("💡 Bạn có thể nhắn `Thêm kế hoạch <Tên mục tiêu>` để mình lưu trực tiếp vào trang [Kế hoạch học tập](/plan) giúp bạn theo dõi tiến độ nhé!")
        return "\n".join(parts)

    # 4. So sánh toàn bộ 8 vị trí CNTT
    if any(k in msg_lower for k in ["so sánh", "8 vị trí", "tất cả vị trí", "xếp hạng"]):
        lines = "\n".join([
            f"- **{idx + 1}. {p['name']}**: **{p['score']}%** *(Nhu cầu: {p['demand']})*"
            for idx, p in enumerate(all_pos_scores)
        ])
        return (
            f"Dưới đây là mức độ tương thích của hồ sơ **{student_name}** trên toàn bộ **{len(all_pos_scores)} vị trí CNTT** trong hệ thống:\n"
            f"{lines}\n\n"
            f"👉 Nhìn chung, thế mạnh hiện tại của bạn nghiêng rõ nhất về **{best_pos['name']} ({best_pos['score']}%)**. "
            f"Nếu bạn vẫn muốn theo đuổi mục tiêu **{target_pos_name} ({target_score}%)**, hãy ưu tiên bù đắp sớm **{', '.join(missing_skills[:3]) or 'kinh nghiệm dự án'}**."
        )

    # 5. Đánh giá hồ sơ phù hợp vị trí nào
    if any(k in msg_lower for k in ["đánh giá", "phù hợp", "vị trí nào", "hồ sơ của tôi", "hồ sơ hiện tại"]):
        top3 = all_pos_scores[:3]
        top_lines = "\n".join([f"- **{p['name']}**: đạt **{p['score']}%** *(Nhu cầu: {p['demand']})*" for p in top3])
        gap_note = (
            f"Hiện bạn đang đặt mục tiêu là **{target_pos_name}** (**{target_score}%**). Để thu hẹp khoảng cách với yêu cầu doanh nghiệp, bạn nên bổ sung thêm **{', '.join(missing_skills[:4])}**."
            if target_pos_name != best_pos["name"] and missing_skills
            else f"Bạn đang đi rất đúng hướng với mục tiêu **{target_pos_name}**! Chỉ cần trau dồi thêm **{', '.join(missing_skills[:3]) or 'dự án thực tế'}** là hồ sơ sẽ rất ấn tượng."
        )
        return (
            f"Qua phân tích kỹ năng, học phần và kinh nghiệm của **{student_name}** (GPA **{student_gpa}/4.0**), 3 vị trí phù hợp nhất với bạn hiện nay là:\n"
            f"{top_lines}\n\n"
            f"{gap_note}"
        )

    # 6. Tin tuyển dụng & mức lương
    if any(k in msg_lower for k in ["tuyển dụng", "việc làm", "lương", "công ty", "job"]):
        if recent_jobs:
            job_lines = "\n".join([
                f"- **{j['title']}** tại *{j['company']}* — Lương: **{j['salary']}** ({j['location']})"
                for j in recent_jobs[:5]
            ])
            return (
                f"Hệ thống đang cập nhật **{total_jobs} tin tuyển dụng** thực tế từ doanh nghiệp, nổi bật có:\n"
                f"{job_lines}\n\n"
                f"Với nền tảng hiện tại, bạn có thể xem thêm các tin thuộc nhóm **{best_pos['name']}** tại trang [Tin tuyển dụng](/jobs) để chuẩn bị CV ứng tuyển nhé!"
            )
        return "Hiện hệ thống chưa ghi nhận tin tuyển dụng mới. Bạn có thể kiểm tra tại trang [Tin tuyển dụng](/jobs) nhé!"

    # 7. Học phần đã học
    if any(k in msg_lower for k in ["môn", "học phần", "điểm", "tín chỉ", "đã học"]):
        if user_courses:
            lines = "\n".join([f"- **{c['code']} - {c['name']}** ({c['credits']} tín chỉ) — Điểm: **{c['grade']}**" for c in user_courses])
            sug_str = ", ".join([f"**{c['code']} - {c['name']}**" for c in suggested_courses_list[:3]])
            sug = f"\n\n💡 Để bổ trợ cho hướng **{target_pos_name}**, bạn nên đăng ký thêm: {sug_str}." if sug_str else ""
            return f"Bạn đã tích lũy **{len(user_courses)} học phần** trong hồ sơ (GPA **{student_gpa}/4.0**):\n{lines}{sug}"
        return f"Hồ sơ của **{student_name}** chưa có học phần nào. Bạn hãy cập nhật bảng điểm tại [Hồ sơ sinh viên](/profile) để mình tư vấn sát hơn nhé!"

    # 8. Kỹ năng cá nhân
    if any(k in msg_lower for k in ["kỹ năng", "skill"]):
        if unique_skill_items:
            lines = "\n".join([f"- {item}" for item in unique_skill_items])
            return (
                f"Bạn đã cập nhật **{len(unique_skill_items)} kỹ năng** chuyên môn:\n{lines}\n\n"
                f"So với yêu cầu của **{target_pos_name}**, bạn đã khớp **{len(matched_skills)} kỹ năng** và có thể trau dồi thêm **{', '.join(missing_skills[:4]) or 'kỹ năng chuyên sâu'}**."
            )
        return "Hồ sơ của bạn hiện chưa có kỹ năng nào. Nhắn `Thêm kỹ năng Python` ngay tại đây hoặc vào [Hồ sơ sinh viên](/profile) để bổ sung nhé!"

    # 9. Chứng chỉ
    if any(k in msg_lower for k in ["chứng chỉ", "toeic", "ielts", "coursera", "aws"]):
        if user_certs:
            lines = "\n".join([f"- **{c['name']}** — *{c['organization']}* (cấp: {c['issue_date'] or 'N/A'})" for c in user_certs])
            rec_certs = (eval_data or {}).get("missing_certs", [])[:2]
            extra = f"\n\n💡 Chứng chỉ nên cân nhắc thi thêm cho vị trí **{target_pos_name}**: **{', '.join(rec_certs)}**." if rec_certs else ""
            return f"Bạn hiện sở hữu **{len(user_certs)} chứng chỉ** trong hồ sơ:\n{lines}{extra}"
        return f"Hiện bạn chưa thêm chứng chỉ nào vào [Hồ sơ sinh viên](/profile)."

    # 10. Kinh nghiệm & dự án
    if any(k in msg_lower for k in ["kinh nghiệm", "dự án", "thực tập", "project", "đồ án"]):
        if user_exps:
            lines = "\n".join([f"- **{e['title']}** tại *{e['company']}* ({e['role_type']}, {e['start_date']} - {e['end_date']})" for e in user_exps])
            return f"Bạn đã có **{len(user_exps)} mục kinh nghiệm & dự án thực tế**:\n{lines}"
        return f"Hồ sơ của **{student_name}** hiện chưa có mục kinh nghiệm hay dự án nào tại [Hồ sơ sinh viên](/profile)."

    # 11. Kế hoạch học tập
    if any(k in msg_lower for k in ["kế hoạch", "mục tiêu", "plan"]):
        if plan_items:
            lines = "\n".join([f"- **{p['title']}** (*{p['category']}*) — Trạng thái: **{p['status']}** (Hạn: {p['target_date'] or 'N/A'})" for p in plan_items])
            return f"Kế hoạch cá nhân của bạn hiện có **{len(plan_items)} mục tiêu**:\n{lines}\n\n💡 Gõ `Thêm kế hoạch <Tên mục tiêu>` nếu bạn muốn bổ sung nhanh nhé!"
        return "Bạn chưa có mục tiêu nào trong [Kế hoạch học tập](/plan). Hãy nhắn `Thêm kế hoạch Học Docker` để bắt đầu nhé!"

    # 12. Tổng quan mặc định tự nhiên
    return (
        f"Chào **{student_name}** ({student_major} — {student_uni}, GPA **{student_gpa}/4.0**)! 👋\n"
        f"- **Hướng phù hợp nhất hiện tại:** **{best_pos['name']}** (**{best_pos['score']}%**)\n"
        f"- **Mục tiêu bạn đang theo đuổi:** **{target_pos_name}** (**{target_score}%**)\n"
        f"- **Hồ sơ đã ghi nhận:** {len(user_courses)} học phần, {len(unique_skill_items)} kỹ năng, {len(user_certs)} chứng chỉ và {len(user_exps)} kinh nghiệm/dự án.\n\n"
        "Bạn muốn mình đi sâu vào phân tích kỹ năng còn thiếu, gợi ý môn học tiếp theo hay chọn tin tuyển dụng phù hợp?"
    )


def _call_gemini_with_sqlite_context(api_key, user_message, history, student_context, is_guest=False):
    """Gọi Google Gemini REST API kèm systemInstruction chuẩn và lịch sử đa lượt."""
    import urllib.request
    import json as _json

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{CHATBOT_GEMINI_MODEL}:generateContent?key={api_key}"
    system_prompt = _build_chatbot_system_prompt(student_context, is_guest=is_guest)

    clean_hist = _normalize_history(history, max_items=8)
    contents = []
    for h in clean_hist:
        g_role = "user" if h["role"] == "user" else "model"
        contents.append({"role": g_role, "parts": [{"text": h["content"]}]})

    if contents and contents[-1]["role"] == "user":
        contents[-1]["parts"][0]["text"] += "\n" + user_message
    else:
        contents.append({"role": "user", "parts": [{"text": user_message}]})

    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 150 if is_guest else 900,
            "temperature": 0.35 if is_guest else 0.55,
            "topP": 0.9,
        },
    }

    req = urllib.request.Request(
        url,
        data=_json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = _json.loads(resp.read().decode("utf-8"))
        raw = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return _polish_bot_reply(raw, clean_hist)


def _call_pollinations_openai_with_sqlite_context(user_message, history, website_context, is_guest=False):
    """Cổng AI tích hợp sẵn chính (OpenAI-compatible qua Pollinations Text API):
    Miễn phí, không cần API Key, hỗ trợ hội thoại đa lượt tự nhiên bằng tiếng Việt và không lặp từ."""
    import urllib.request
    import json as _json

    system_prompt = _build_chatbot_system_prompt(website_context, is_guest=is_guest)
    clean_hist = _normalize_history(history, max_items=8)

    messages = [{"role": "system", "content": system_prompt}]
    for h in clean_hist:
        messages.append({
            "role": "user" if h["role"] == "user" else "assistant",
            "content": h["content"],
        })
    messages.append({"role": "user", "content": user_message})

    req = urllib.request.Request(
        "https://text.pollinations.ai/openai",
        data=_json.dumps({
            "model": "openai",
            "temperature": 0.4 if is_guest else 0.55,
            "max_tokens": 160 if is_guest else 900,
            "messages": messages,
        }).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=18) as resp:
        data = _json.loads(resp.read().decode("utf-8"))
        raw = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return _polish_bot_reply(raw, clean_hist)


def _call_free_llm_with_sqlite_context(user_message, history, website_context, is_guest=False):
    """Gọi cổng OpenAI-compatible dự phòng (LLM7) với mảng messages đa lượt chuẩn xác
    và frequency_penalty chống lặp từ tự nhiên."""
    import urllib.request
    import json as _json

    system_prompt = _build_chatbot_system_prompt(website_context, is_guest=is_guest)
    clean_hist = _normalize_history(history, max_items=8)

    messages = [{"role": "system", "content": system_prompt}]
    for h in clean_hist:
        messages.append({
            "role": "user" if h["role"] == "user" else "assistant",
            "content": h["content"],
        })
    messages.append({"role": "user", "content": user_message})

    req = urllib.request.Request(
        "https://api.llm7.io/v1/chat/completions",
        data=_json.dumps({
            "model": "default",
            "temperature": 0.35 if is_guest else 0.45,
            "top_p": 0.9,
            "frequency_penalty": 0.35,
            "presence_penalty": 0.2,
            "max_tokens": 160 if is_guest else 900,
            "messages": messages,
        }).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=14) as resp:
        data = _json.loads(resp.read().decode("utf-8"))
        raw = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return _polish_bot_reply(raw, clean_hist)


def _call_hf_llama_with_sqlite_context(user_message, history, website_context, is_guest=False):
    """Cổng AI dự phòng (Llama-3.2-Instruct trên HuggingFace Space):
    Chỉ truyền tóm tắt ngữ cảnh câu hỏi trước (không dán nguyên văn bài trả lời cũ để tránh nhại lại)
    và tăng repetition_penalty = 1.22 chống lặp từ."""
    import urllib.request
    import json as _json

    clean_hist = _normalize_history(history, max_items=6)
    prior_user_questions = [h["content"] for h in clean_hist if h["role"] == "user"][-3:]
    context_note = ""
    if prior_user_questions:
        joined_q = " -> ".join(prior_user_questions)
        context_note = f"[Các ý người dùng đã hỏi trước đó để hiểu mạch chuyện: {joined_q}]\n\n"

    system_rules = _build_chatbot_system_prompt(website_context, is_guest=is_guest)
    full_prompt = (
        f"{system_rules}\n\n"
        f"{context_note}"
        f"[CÂU HỎI MỚI CẦN TRẢ LỜI NGAY]: {user_message}\n"
        "(Lưu ý: Chỉ trả lời trực tiếp câu hỏi mới này một cách tự nhiên, ngắn gọn, không lặp từ.)"
    )

    max_tok = 150 if is_guest else 800
    base = "https://huggingface-projects-llama-3-2-3b-instruct.hf.space"
    req = urllib.request.Request(
        f"{base}/gradio_api/call/generate",
        data=_json.dumps({"data": [full_prompt, max_tok, 0.45, 0.9, 40, 1.22]}).encode("utf-8"),
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
                if isinstance(arr, list) and arr and isinstance(arr[0], str) and arr[0].strip():
                    return _polish_bot_reply(arr[0].strip(), clean_hist)
    return ""


GUEST_CHAT_MAX_QUESTIONS = 4

SPECIALIZED_CHATBOT_KEYWORDS = (
    "thêm kỹ năng", "them ky nang", "thêm kế hoạch", "them ke hoach", "thêm mục tiêu", "them muc tieu",
    "hồ sơ", "ho so", "của tôi", "cua toi", "mssv", "gpa", "điểm trung bình", "diem trung binh",
    "học phần", "hoc phan", "môn học", "mon hoc", "tín chỉ", "tin chi", "kỹ năng", "ky nang",
    "chứng chỉ", "chung chi", "kinh nghiệm", "kinh nghiem", "kế hoạch", "ke hoach", "mục tiêu", "muc tieu",
    "lộ trình", "lo trinh", "đánh giá", "danh gia", "độ phù hợp", "do phu hop", "so sánh", "so sanh",
    "vị trí", "vi tri", "tuyển dụng", "tuyen dung", "việc làm", "viec lam", "mức lương", "muc luong",
    "lương cao", "luong cao", "backend", "frontend", "fullstack", "devops", "data analyst", "ai engineer",
    "mobile developer", "qa", "tester", "phỏng vấn", "phong van", "thực tập", "thuc tap",
    "đồ án", "do an", "dự án", "du an", "skill", "roadmap", "chuyên sâu", "chuyen sau",
    "chuyên môn", "chuyen mon", "csdl", "sqlite", "database", "toeic", "ielts", "coursera", "aws",
)


def _is_specialized_chatbot_query(message):
    """Kiểm tra câu hỏi có thuộc phạm vi chuyên môn/chuyên sâu của website hay không."""
    msg_lower = (message or "").lower()
    return any(kw in msg_lower for kw in SPECIALIZED_CHATBOT_KEYWORDS)


def _build_guest_chatbot_context():
    """Ngữ cảnh giới hạn cho người dùng chưa đăng nhập (không chứa dữ liệu SQLite hay nghiệp vụ chuyên sâu)."""
    return (
        "Người dùng hiện tại CHƯA ĐĂNG NHẬP tài khoản (đang ở chế độ khách).\n"
        "Bạn KHÔNG có quyền truy cập hồ sơ cá nhân, điểm số, kỹ năng, việc làm hay dữ liệu chuyên môn trên hệ thống.\n"
        "Quy tắc bắt buộc:\n"
        "1. Chỉ trả lời các câu hỏi chung chung, cơ bản, mang tính giới thiệu tổng quan hoặc giao tiếp thông thường.\n"
        "2. Tuyệt đối KHÔNG phân tích chuyên sâu, KHÔNG tư vấn lộ trình/kỹ năng/việc làm chi tiết.\n"
        "3. Nếu người dùng hỏi sâu hơn, nhắc họ đăng nhập tại /login."
    )


def _shorten_guest_reply(text, max_chars=180, max_sentences=2):
    """Rút gọn câu trả lời chế độ khách tối đa 2 câu ngắn gọn."""
    import re
    cleaned = " ".join((text or "").split())
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    short = ""
    for s in sentences[:max_sentences]:
        if len(short) + len(s) + 1 <= max_chars:
            short = f"{short} {s}".strip()
        else:
            break
    if short:
        return short
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rsplit(" ", 1)[0] + "..."


def _append_guest_chat_turn(user_message, bot_reply):
    """Lưu lịch sử chat chế độ khách trong Flask session để không bị mất khi chuyển trang."""
    guest_hist = list(session.get("guest_chat_history") or [])
    guest_hist.append({"role": "user", "content": user_message})
    guest_hist.append({"role": "assistant", "content": bot_reply})
    session["guest_chat_history"] = guest_hist[-16:]
    session.modified = True


def _handle_guest_chatbot(message, history, active_api_key):
    """Xử lý yêu cầu Chatbot cho khách chưa đăng nhập: chỉ trả lời ngắn gọn, chung chung và giới hạn tối đa 4 lượt."""
    guest_count = int(session.get("guest_chat_count", 0))
    if guest_count >= GUEST_CHAT_MAX_QUESTIONS:
        return api_response(
            True,
            {
                "reply": (
                    f"🔒 Bạn đã dùng hết **{GUEST_CHAT_MAX_QUESTIONS}/{GUEST_CHAT_MAX_QUESTIONS}** lượt hỏi thử. "
                    "Vui lòng [Đăng nhập ngay](/login) để tiếp tục sử dụng AI chuyên sâu!"
                ),
                "mode": "guest_limit_reached",
                "is_guest": True,
                "require_login": True,
                "guest_count": guest_count,
                "guest_limit": GUEST_CHAT_MAX_QUESTIONS,
                "guest_remaining": 0,
            },
        )

    guest_count += 1
    session["guest_chat_count"] = guest_count
    guest_remaining = max(0, GUEST_CHAT_MAX_QUESTIONS - guest_count)

    if _is_specialized_chatbot_query(message):
        reply = (
            "🔒 Câu hỏi này cần **đăng nhập tài khoản** để AI tư vấn chuyên sâu. "
            f"Vui lòng [Đăng nhập](/login)! *(Còn **{guest_remaining}/{GUEST_CHAT_MAX_QUESTIONS}** lượt)*"
        )
        _append_guest_chat_turn(message, reply)
        return api_response(
            True,
            {
                "reply": reply,
                "mode": "guest_specialized_blocked",
                "is_guest": True,
                "require_login": guest_remaining == 0,
                "guest_count": guest_count,
                "guest_limit": GUEST_CHAT_MAX_QUESTIONS,
                "guest_remaining": guest_remaining,
            },
        )

    guest_context = _build_guest_chatbot_context()
    ai_reply = ""
    mode = "guest_general_fallback"

    if active_api_key:
        try:
            ai_reply = _call_gemini_with_sqlite_context(active_api_key, message, history, guest_context, is_guest=True)
            if ai_reply:
                mode = "guest_gemini"
        except Exception:
            ai_reply = ""

    if not ai_reply:
        try:
            ai_reply = _call_pollinations_openai_with_sqlite_context(message, history, guest_context, is_guest=True)
            if ai_reply:
                mode = "guest_pollinations_openai"
        except Exception:
            ai_reply = ""

    if not ai_reply:
        try:
            ai_reply = _call_free_llm_with_sqlite_context(message, history, guest_context, is_guest=True)
            if ai_reply:
                mode = "guest_llm7"
        except Exception:
            ai_reply = ""

    if not ai_reply:
        try:
            ai_reply = _call_hf_llama_with_sqlite_context(message, history, guest_context, is_guest=True)
            if ai_reply:
                mode = "guest_hf_llama"
        except Exception:
            ai_reply = ""

    if not ai_reply:
        ai_reply = (
            "👋 Mình là **Trợ lý AI IT Career Compass**. "
            "Hiện bạn chưa đăng nhập nên mình chỉ trả lời ngắn gọn các câu hỏi chung; hãy [Đăng nhập](/login) để dùng tư vấn chuyên sâu!"
        )
    else:
        ai_reply = _shorten_guest_reply(ai_reply)

    if guest_remaining == 0:
        ai_reply += f"\n\n⚠️ *Đã hết lượt khách ({guest_count}/{GUEST_CHAT_MAX_QUESTIONS}). Hãy [Đăng nhập](/login) để hỏi tiếp!*"
    else:
        ai_reply += f"\n\n*(Còn **{guest_remaining}/{GUEST_CHAT_MAX_QUESTIONS}** lượt khách)*"

    _append_guest_chat_turn(message, ai_reply)
    return api_response(
        True,
        {
            "reply": ai_reply,
            "mode": mode,
            "is_guest": True,
            "require_login": guest_remaining == 0,
            "guest_count": guest_count,
            "guest_limit": GUEST_CHAT_MAX_QUESTIONS,
            "guest_remaining": guest_remaining,
        },
    )


@app.route("/api/chatbot/history", methods=["GET", "DELETE"])
def api_chatbot_history():
    """Đọc hoặc xóa lịch sử hội thoại Chatbot để đồng bộ xuyên suốt các tab/trang."""
    user_id = get_current_user_id()

    if request.method == "DELETE":
        if user_id:
            conn = get_db_connection()
            try:
                _ensure_chat_messages_table(conn)
                conn.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
                conn.commit()
            finally:
                conn.close()
        else:
            session.pop("guest_chat_history", None)
        return api_response(True, None, "Đã làm mới cuộc trò chuyện!")

    if user_id:
        messages = _load_user_chat_history(user_id, limit=40)
        return api_response(
            True,
            {
                "messages": messages,
                "is_guest": False,
                "require_login": False,
            },
        )

    guest_count = int(session.get("guest_chat_count", 0))
    guest_remaining = max(0, GUEST_CHAT_MAX_QUESTIONS - guest_count)
    return api_response(
        True,
        {
            "messages": list(session.get("guest_chat_history") or []),
            "is_guest": True,
            "guest_count": guest_count,
            "guest_limit": GUEST_CHAT_MAX_QUESTIONS,
            "guest_remaining": guest_remaining,
            "require_login": guest_count >= GUEST_CHAT_MAX_QUESTIONS,
        },
    )


@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    """
    Endpoint AI Hỗ trợ Người dùng thực thụ của Website (/api/chatbot):
    - Nếu đã đăng nhập (session hợp lệ): mở toàn bộ tính năng chuyên sâu + dữ liệu SQLite cá nhân.
    - Nếu chưa đăng nhập (khách): chỉ trả lời câu hỏi chung chung, chặn câu hỏi chuyên môn sâu và giới hạn tối đa 4 lượt hỏi.
    """
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    history = payload.get("history") or []
    ui_api_key = (payload.get("api_key") or "").strip()
    active_api_key = ui_api_key or CHATBOT_GEMINI_API_KEY

    if not message:
        return api_response(False, None, "Vui lòng nhập nội dung câu hỏi!", 400)

    user_id = get_current_user_id()
    if not user_id:
        return _handle_guest_chatbot(message, history, active_api_key)

    msg_lower = message.lower()
    if not history:
        history = _load_user_chat_history(user_id, limit=8)
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
            reply_text = f"✅ Mình đã thêm trực tiếp kỹ năng **{skill_name}** (Mức độ: 3/5) vào mục **Hồ sơ sinh viên** ([Xem hồ sơ](/profile)) của bạn! Bạn có thể mở trang [Đánh giá phù hợp](/compare) để xem điểm số mới nhé."
            _save_user_chat_turn(user_id, message, reply_text)
            return api_response(
                True,
                {
                    "reply": reply_text,
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
            reply_text = f"✅ Mình đã thêm mục tiêu **\"{plan_title}\"** vào trang [Kế hoạch học tập](/plan) của bạn (Trạng thái: *Cần làm*)!"
            _save_user_chat_turn(user_id, message, reply_text)
            return api_response(
                True,
                {
                    "reply": reply_text,
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

    # Khử trùng lặp tên kỹ năng khi xây dựng ngữ cảnh cho AI để tránh model lặp từ
    seen_skill_names = set()
    unique_skill_items = []
    for s in user_skills_rows:
        sk_key = s["name"].strip().lower()
        if sk_key not in seen_skill_names:
            seen_skill_names.add(sk_key)
            unique_skill_items.append(
                f"{s['name']} ({s['category']}, mức {s['level']}/5{', ' + s['note'] if s['note'] else ''})"
            )

    courses_detail_str = (
        "; ".join([f"{c['code']} - {c['name']} ({c['credits']} tín chỉ, Điểm: {c['grade']}, Học kỳ: {c['term'] or 'N/A'})" for c in user_courses])
        if user_courses else "Người dùng chưa nhập học phần nào"
    )
    skills_detail_str = (
        "; ".join(unique_skill_items)
        if unique_skill_items else "Người dùng chưa nhập kỹ năng nào"
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
    best_pos = all_pos_scores[0] if all_pos_scores else {"name": target_pos_name, "score": target_score}
    suggested_courses_list = eval_data.get("suggested_academic_courses", []) if eval_data else []
    suggested_courses_str = (
        "; ".join([f"{c['code']} - {c['name']} ({c['credits']} tín chỉ)" for c in suggested_courses_list[:5]])
        if suggested_courses_list else "Chưa có gợi ý học phần bổ sung"
    )
    jobs_sample_str = "; ".join([f"{j['title']} tại {j['company']} (Vị trí: {j['position_name']}, Lương: {j['salary']}, Địa điểm: {j['location']})" for j in recent_jobs[:6]])

    website_and_student_context = (
        "=== 1. DỮ LIỆU CÁ NHÂN TRONG HỒ SƠ ===\n"
        f"- Họ và tên: {student_name} | MSSV: {student_code}\n"
        f"- Email: {student_email} | Số điện thoại: {student_phone}\n"
        f"- Trường: {student_uni} | Khoa: {student_faculty} | Chuyên ngành: {student_major} | Niên khóa: {student_year}\n"
        f"- GPA tích lũy: {student_gpa}/4.0 | Giới thiệu: {student_bio}\n"
        f"- Vị trí phù hợp nhất hiện tại theo năng lực thực tế: {best_pos['name']} ({best_pos['score']}%)\n"
        f"- Vị trí mục tiêu người dùng đang đặt trên hồ sơ: {target_pos_name} (Độ phù hợp: {target_score}%)\n\n"
        "=== 2. HỌC PHẦN, KỸ NĂNG, CHỨNG CHỈ, KINH NGHIỆM & KẾ HOẠCH ===\n"
        f"- Học phần đã học ({len(user_courses)} môn): {courses_detail_str}\n"
        f"- Kỹ năng hiện có ({len(unique_skill_items)} kỹ năng): {skills_detail_str}\n"
        f"- Chứng chỉ ({len(user_certs)}): {certs_detail_str}\n"
        f"- Kinh nghiệm & Dự án ({len(user_exps)}): {exps_detail_str}\n"
        f"- Kế hoạch học tập ({len(plan_items)}): {plans_detail_str}\n\n"
        "=== 3. PHÂN TÍCH ĐỊNH HƯỚNG & TIN TUYỂN DỤNG ===\n"
        f"- Bảng xếp hạng độ phù hợp 8 vị trí CNTT (từ cao xuống thấp): {ranking_str}\n"
        f"- Kỹ năng đã đáp ứng cho vị trí mục tiêu ({target_pos_name}): {', '.join(dict.fromkeys(eval_data.get('have', []))) if eval_data and eval_data.get('have') else 'Chưa khớp kỹ năng nào'}\n"
        f"- Kỹ năng cần bổ sung cho vị trí mục tiêu ({target_pos_name}): {', '.join(dict.fromkeys(eval_data.get('missing', []))) if eval_data and eval_data.get('missing') else 'Không thiếu'}\n"
        f"- Học phần đại học gợi ý nên đăng ký thêm: {suggested_courses_str}\n"
        f"- Tin tuyển dụng tiêu biểu trên hệ thống ({total_jobs} tin): {jobs_sample_str}\n"
        "- Đường dẫn nhanh trên web: [Tổng quan](/dashboard), [Hồ sơ sinh viên](/profile), [Vị trí nghề nghiệp](/positions), [Tin tuyển dụng](/jobs), [Thống kê kỹ năng](/statistics), [Đánh giá phù hợp](/compare), [Kế hoạch học tập](/plan)."
    )

    # ------------------------------------------------------------------
    # TẦNG 1: Nếu có Gemini API Key -> Gọi Google Gemini AI
    # ------------------------------------------------------------------
    if active_api_key:
        try:
            ai_reply = _call_gemini_with_sqlite_context(active_api_key, message, history, website_and_student_context)
            if ai_reply:
                _save_user_chat_turn(user_id, message, ai_reply)
                return api_response(True, {"reply": ai_reply, "mode": "gemini_rag"})
        except Exception:
            pass

    # ------------------------------------------------------------------
    # TẦNG 2 (MẶC ĐỊNH): Gọi cổng OpenAI đa lượt tích hợp sẵn (Pollinations OpenAI)
    # Tiếng Việt tự nhiên, mạch lạc, hỗ trợ lịch sử đa lượt không lặp từ
    # ------------------------------------------------------------------
    try:
        polli_reply = _call_pollinations_openai_with_sqlite_context(message, history, website_and_student_context)
        if polli_reply:
            _save_user_chat_turn(user_id, message, polli_reply)
            return api_response(True, {"reply": polli_reply, "mode": "pollinations_openai_rag"})
    except Exception:
        pass

    # ------------------------------------------------------------------
    # TẦNG 3 (DỰ PHÒNG 1): Gọi cổng OpenAI-compatible đa lượt chuẩn (LLM7)
    # ------------------------------------------------------------------
    try:
        llm_reply = _call_free_llm_with_sqlite_context(message, history, website_and_student_context)
        if llm_reply:
            _save_user_chat_turn(user_id, message, llm_reply)
            return api_response(True, {"reply": llm_reply, "mode": "llm7_rag"})
    except Exception:
        pass

    # ------------------------------------------------------------------
    # TẦNG 4 (DỰ PHÒNG 2): Gọi Llama-3.2-Instruct (HuggingFace Space)
    # ------------------------------------------------------------------
    try:
        hf_reply = _call_hf_llama_with_sqlite_context(message, history, website_and_student_context)
        if hf_reply:
            _save_user_chat_turn(user_id, message, hf_reply)
            return api_response(True, {"reply": hf_reply, "mode": "hf_llama_rag"})
    except Exception:
        pass

    # ------------------------------------------------------------------
    # TẦNG 5 (Trợ lý Cố vấn Nội bộ thông minh từ CSDL SQLite - Phản hồi tức thì
    # ngay cả khi hết hạn mức API miễn phí hoặc ngoại tuyến)
    # ------------------------------------------------------------------
    reply = _build_natural_local_advisor_reply(
        message=message,
        msg_lower=msg_lower,
        student_name=student_name,
        student_code=student_code,
        student_uni=student_uni,
        student_major=student_major,
        student_gpa=student_gpa,
        best_pos=best_pos,
        target_pos_name=target_pos_name,
        target_score=target_score,
        eval_data=eval_data,
        all_pos_scores=all_pos_scores,
        positions=positions,
        user_courses=user_courses,
        unique_skill_items=unique_skill_items,
        user_certs=user_certs,
        user_exps=user_exps,
        plan_items=plan_items,
        recent_jobs=recent_jobs,
        total_jobs=total_jobs,
        suggested_courses_list=suggested_courses_list,
    )
    _save_user_chat_turn(user_id, message, reply)
    return api_response(True, {"reply": reply, "mode": "sqlite_direct"})


if __name__ == "__main__":
    print("=" * 68)
    print("  HE THONG DINH HUONG KY NANG NGHE NGHIEP CNTT (FLASK + SQLITE)")
    print("  De tai: NLCNPM23CS-38 - Nhanh: thanh-vien-2")
    print("  May chu dang chay tai: http://127.0.0.1:5000")
    print("=" * 68)
    app.run(debug=True, host="0.0.0.0", port=5000)
