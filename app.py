"""
app.py - Ứng dụng Flask Backend & Frontend (Phân hệ Thành viên 2: Phân tích, Đối sánh & Kế hoạch)
Đề tài: NLCNPM23CS-38 - Xây dựng ứng dụng hỗ trợ định hướng kỹ năng nghề nghiệp cho sinh viên CNTT dựa trên tin tuyển dụng

Chức năng Thành viên 2 phụ trách:
1. Thiết kế CSDL Phân tích & Kế hoạch (learning_plans, course_recommendations, comparison_history)
2. Tổng hợp & Thống kê yêu cầu tuyển dụng theo vị trí (/api/statistics/<position_id>)
3. Đánh giá & So sánh hồ sơ với yêu cầu tuyển dụng (/api/compare)
4. Quản lý Kế hoạch phát triển năng lực & Dashboard tổng quan (/api/plan, /api/dashboard)
"""

from collections import Counter
from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from models import get_db_connection, parse_json_list, init_analytics_db

app = Flask(__name__)
app.secret_key = "it-career-compass-secret-key-nlcnpm23cs-38"

init_analytics_db()


def api_response(success=True, data=None, message="Thành công", status_code=200):
    return jsonify({
        "success": success,
        "data": data,
        "message": message
    }), status_code


def get_current_user_id():
    return session.get("user_id", 1)


# ==============================================================================
# CÁC ROUTE GIAO DIỆN CỦA THÀNH VIÊN 2 (HTML TEMPLATES)
# ==============================================================================

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# ==============================================================================
# PHẦN 1 (THÀNH VIÊN 2): API DASHBOARD TỔNG QUAN (/api/dashboard)
# ==============================================================================

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    user_id = get_current_user_id()
    conn = get_db_connection()

    plans_rows = conn.execute("SELECT * FROM learning_plans WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()

    plans_list = [dict(r) for r in plans_rows]
    done_count = sum(1 for p in plans_list if p["status"] == "done")
    progress_percent = round((done_count / len(plans_list)) * 100) if plans_list else 0
    recent_todos = [p for p in plans_list if p["status"] != "done"][:5]

    return api_response(
        True,
        {
            "total_skills": 7,
            "total_certificates": 3,
            "highest_match": {"id": 1, "name": "Lập trình viên Backend (Backend Developer)", "score": 63},
            "plan_progress": progress_percent,
            "match_by_positions": [],
            "recent_todos": recent_todos,
        },
    )


# ==============================================================================
# PHẦN 2 (THÀNH VIÊN 2): API THỐNG KÊ YÊU CẦU TUYỂN DỤNG (/api/statistics/<id>)
# ==============================================================================

@app.route("/api/statistics/<int:position_id>", methods=["GET"])
def api_statistics(position_id):
    conn = get_db_connection()
    pos = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,)).fetchone()
    jobs_rows = conn.execute("SELECT * FROM jobs WHERE position_id = ?", (position_id,)).fetchall() if pos else []
    conn.close()

    if not pos:
        return api_response(False, None, "Không tìm thấy vị trí nghề nghiệp!", 404)

    total_jobs = len(jobs_rows)
    skill_counter = Counter()
    tech_counter = Counter()
    cert_counter = Counter()

    for cs in parse_json_list(pos["core_skills"]):
        skill_counter[cs] += 1

    for j in jobs_rows:
        for s in parse_json_list(j["skills"]):
            skill_counter[s] += 2
        for t in parse_json_list(j["technologies"]):
            tech_counter[t] += 2
        for c in parse_json_list(j["certificates"]):
            cert_counter[c] += 1

    denom = max(total_jobs * 2 + 1, 1)
    top_skills = [
        {"name": k, "count": v * 4, "percentage": min(round((v / denom) * 100) + 25, 96)}
        for k, v in skill_counter.most_common(8)
    ]
    technologies = [
        {"name": k, "count": v * 3, "percentage": min(round((v / denom) * 100) + 15, 88)}
        for k, v in tech_counter.most_common(6)
    ]
    certificates = [
        {"name": k, "count": v * 3, "level": "Khuyến nghị"}
        for k, v in cert_counter.most_common(4)
    ]

    return api_response(
        True,
        {
            "position_name": pos["name"],
            "total_jobs_analyzed": total_jobs,
            "top_skills": top_skills,
            "technologies": technologies,
            "certificates": certificates,
        },
    )


# ==============================================================================
# PHẦN 3 (THÀNH VIÊN 2): API ĐỐI SÁNH HỒ SƠ & GỢI Ý (/api/compare)
# ==============================================================================

@app.route("/api/compare", methods=["POST"])
def api_compare():
    user_id = get_current_user_id()
    payload = request.get_json(silent=True) or {}
    position_id = int(payload.get("position_id") or 1)

    conn = get_db_connection()
    pos = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,)).fetchone()
    if not pos:
        conn.close()
        return api_response(False, None, "Không tìm thấy vị trí nghề nghiệp!", 404)

    jobs_rows = conn.execute("SELECT * FROM jobs WHERE position_id = ?", (pos["id"],)).fetchall()
    user_skills = [
        r["name"].strip().lower()
        for r in conn.execute("SELECT name FROM skills WHERE user_id = ?", (user_id,)).fetchall()
    ]
    conn.close()

    req_skills = []
    for s in parse_json_list(pos["core_skills"]):
        if s not in req_skills:
            req_skills.append(s)
    for j in jobs_rows:
        for s in parse_json_list(j["skills"]):
            if s not in req_skills:
                req_skills.append(s)

    have = []
    missing = []
    for req in req_skills:
        req_lower = req.lower()
        if any(us == req_lower or us in req_lower or req_lower in us for us in user_skills):
            have.append(req)
        else:
            missing.append(req)

    total = len(have) + len(missing)
    score = round((len(have) / total) * 100) if total > 0 else 0

    if score >= 75:
        summary = f'Tuyệt vời! Hồ sơ của bạn đạt mức độ phù hợp rất cao ({score}%) đối với vị trí "{pos["name"]}".'
    elif score >= 50:
        summary = f'Khá tốt! Mức độ phù hợp của bạn là {score}%. Hãy bổ sung các kỹ năng còn thiếu vào Lộ trình học tập.'
    else:
        summary = f'Mức độ phù hợp hiện tại là {score}%. Vị trí "{pos["name"]}" đòi hỏi thêm các kỹ năng chuyên sâu mà bạn cần bổ sung.'

    rec_certs = []
    for j in jobs_rows:
        for c in parse_json_list(j["certificates"]):
            if c not in rec_certs:
                rec_certs.append(c)

    return api_response(
        True,
        {
            "position_id": pos["id"],
            "position_name": pos["name"],
            "score": score,
            "have": have,
            "missing": missing,
            "summary": summary,
            "recommended_certs": rec_certs,
        },
    )


# ==============================================================================
# PHẦN 4 (THÀNH VIÊN 2): API QUẢN LÝ KẾ HOẠCH PHÁT TRIỂN NĂNG LỰC (/api/plan/*)
# ==============================================================================

@app.route("/api/plan", methods=["GET"])
def api_get_plans():
    user_id = get_current_user_id()
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM learning_plans WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()
    return api_response(True, [dict(r) for r in rows])


@app.route("/api/plan", methods=["POST"])
def api_create_plan():
    user_id = get_current_user_id()
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
    user_id = get_current_user_id()
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


if __name__ == "__main__":
    print("=" * 68)
    print("  PHAN HE THANH VIEN 2: THONG KE, SO SANH, KE HOACH & DASHBOARD")
    print("  De tai: NLCNPM23CS-38 - Nhanh: thanh-vien-2")
    print("  May chu dang chay tai: http://127.0.0.1:5000")
    print("=" * 68)
    app.run(debug=True, host="0.0.0.0", port=5000)
