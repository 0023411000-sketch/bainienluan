"""
app.py - Ứng dụng Flask Backend & Frontend tích hợp SQLite (Phân hệ Thành viên 1)
Đề tài: NLCNPM23CS-38 - Xây dựng ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp cho sinh viên CNTT dựa trên tin tuyển dụng

Chức năng Thành viên 1 phụ trách:
1. Thiết kế & khởi tạo CSDL SQLite (models.py, seed_data.py, database.db)
2. Xác thực & Quản lý tài khoản (/api/auth/register, /api/auth/login, /api/auth/logout)
3. Quản lý Hồ sơ sinh viên & 4 danh mục con (/api/profile, courses, skills, certificates, experiences)
4. Quản lý Vị trí nghề nghiệp & Tin tuyển dụng + Nhập file CSV (/api/positions, /api/jobs, /api/jobs/import-csv)
"""

import math
from flask import Flask, render_template, redirect, url_for, request, jsonify, session
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


def get_current_user_id():
    """Lấy user_id từ Bearer token, session hoặc mặc định là 1 (tài khoản mẫu)."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "").strip()
        if token.startswith("user_"):
            try:
                uid = int(token.split("_")[1])
                conn = get_db_connection()
                user = conn.execute("SELECT id FROM users WHERE id = ?", (uid,)).fetchone()
                conn.close()
                if user:
                    return uid
            except Exception:
                pass
    if "user_id" in session:
        return session["user_id"]
    return 1


# ==============================================================================
# CÁC ROUTE GIAO DIỆN CỦA THÀNH VIÊN 1 (HTML TEMPLATES)
# ==============================================================================

@app.route("/")
def index():
    return redirect(url_for("profile"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/positions")
def positions():
    return render_template("positions.html")


@app.route("/jobs")
def jobs():
    return render_template("jobs.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# ==============================================================================
# PHẦN 1 (THÀNH VIÊN 1): API XÁC THỰC & QUẢN LÝ TÀI KHOẢN (/api/auth/*)
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
# PHẦN 2 (THÀNH VIÊN 1): API QUẢN LÝ HỒ SƠ SINH VIÊN (4 DANH MỤC) (/api/profile/*)
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
            "target_position_id": prof["target_position_id"],
            "bio": prof["bio"],
        },
        "courses": [dict(r) for r in courses_rows],
        "skills": [dict(r) for r in skills_rows],
        "certificates": [dict(r) for r in certs_rows],
        "experiences": [dict(r) for r in exps_rows],
    }
    return api_response(True, data)


@app.route("/api/profile", methods=["PUT"])
def api_update_profile():
    user_id = get_current_user_id()
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
    user_id = get_current_user_id()
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
    user_id = get_current_user_id()
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
    user_id = get_current_user_id()
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
    user_id = get_current_user_id()
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
    user_id = get_current_user_id()
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
    user_id = get_current_user_id()
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
    user_id = get_current_user_id()
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
    user_id = get_current_user_id()
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
# PHẦN 3 (THÀNH VIÊN 1): API QUẢN LÝ VỊ TRÍ NGHỀ NGHIỆP (/api/positions/*)
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
    conn = get_db_connection()
    conn.execute("DELETE FROM positions WHERE id = ?", (pos_id,))
    conn.commit()
    conn.close()
    return api_response(True, None, "Xóa vị trí nghề nghiệp thành công!")


# ==============================================================================
# PHẦN 4 (THÀNH VIÊN 1): API QUẢN LÝ TIN TUYỂN DỤNG & NHẬP CSV (/api/jobs/*)
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
    conn = get_db_connection()
    conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    return api_response(True, None, "Xóa tin tuyển dụng thành công!")


@app.route("/api/jobs/import-csv", methods=["POST"])
def api_import_jobs_csv():
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


if __name__ == "__main__":
    print("=" * 68)
    print("  PHAN HE THANH VIEN 1: TAI KHOAN, HO SO, VI TRI & TIN TUYEN DUNG")
    print("  De tai: NLCNPM23CS-38 - Nhanh: thanh-vien-1")
    print("  May chu dang chay tai: http://127.0.0.1:5000")
    print("=" * 68)
    app.run(debug=True, host="0.0.0.0", port=5000)
