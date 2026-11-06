import json
from app import app, get_db_connection

def test_evaluation_flow():
    client = app.test_client()

    print("[1] Logging in as student (an.nguyen20@sis.hust.edu.vn)...")
    login_res = client.post("/api/auth/login", json={
        "email": "an.nguyen20@sis.hust.edu.vn",
        "password": "123456"
    })
    login_data = login_res.get_json()
    print(f"Login status code: {login_res.status_code}, response: {login_data}")
    assert login_data.get("success"), f"Login failed: {login_data}"
    user_info = login_data["data"]
    print(f"Logged in user: {user_info['full_name']} (Role: {user_info['role']}, ID: {user_info['id']})")

    print("\n[2] Fetching Profile and Auto-Evaluation (GET /api/profile)...")
    prof_res = client.get("/api/profile")
    prof_data = prof_res.get_json()
    assert prof_data.get("success"), f"Get profile failed: {prof_data}"
    
    data = prof_data["data"]
    assert "evaluation" in data, "evaluation missing in profile response!"
    eval_data = data["evaluation"]
    
    print(f"Target Position: {eval_data.get('target_position')}")
    print(f"Current Fit Score: {eval_data.get('score')}%")
    print(f"Have Skills ({len(eval_data.get('have', []))}): {eval_data.get('have')}")
    print(f"Missing Skills ({len(eval_data.get('missing', []))}): {eval_data.get('missing')}")
    
    suggested_courses = eval_data.get("suggested_academic_courses", [])
    print(f"Suggested University IT Courses ({len(suggested_courses)}):")
    for sc in suggested_courses:
        print(f"  - [{sc['code']}] {sc['name']} ({sc['credits']} tín chỉ) -> Bổ trợ: {sc.get('matched_missing_skills')}")
    assert len(suggested_courses) > 0, "No academic courses suggested!"

    print("\n[3] Testing GET /api/profile/evaluation with different position (AI/ML id=8)...")
    ai_eval_res = client.get("/api/profile/evaluation?position_id=8")
    ai_eval = ai_eval_res.get_json()
    assert ai_eval.get("success"), f"AI eval failed: {ai_eval}"
    print(f"AI/ML Position Score: {ai_eval['data']['score']}%")
    print(f"AI/ML Suggested Courses ({len(ai_eval['data']['suggested_academic_courses'])}):")
    for sc in ai_eval["data"]["suggested_academic_courses"]:
        print(f"  - [{sc['code']}] {sc['name']} -> Bổ trợ: {sc.get('matched_missing_skills')}")

    print("\n[4] Testing Add to Learning Plan (POST /api/plan)...")
    first_course = suggested_courses[0]
    plan_res = client.post("/api/plan", json={
        "title": f"Học phần: {first_course['name']} ({first_course['code']})",
        "category": "Học phần đại học",
        "type": "course",
        "status": "todo",
        "note": first_course["description"]
    })
    plan_data = plan_res.get_json()
    print(f"Plan creation response: {plan_data}")
    assert plan_data.get("success"), f"Plan creation failed: {plan_data}"
    created_plan_id = plan_data["data"]["id"]

    print("\n[5] Testing Add Course to Completed Courses (POST /api/profile/courses)...")
    add_c_res = client.post("/api/profile/courses", json={
        "code": first_course["code"],
        "name": first_course["name"],
        "credits": first_course["credits"],
        "grade": "A",
        "term": "2024.1"
    })
    add_c_data = add_c_res.get_json()
    print(f"Add course response: {add_c_data}")
    assert add_c_data.get("success"), f"Add course failed: {add_c_data}"
    new_course_id = add_c_data["data"]["id"]

    print("\n[6] Re-fetching Profile to verify auto-recalculation and course removal...")
    new_prof_res = client.get("/api/profile")
    new_prof_data = new_prof_res.get_json()
    new_eval = new_prof_data["data"]["evaluation"]
    new_suggested_codes = [c["code"] for c in new_eval["suggested_academic_courses"]]
    print(f"New Fit Score: {new_eval['score']}% (Old: {eval_data['score']}%)")
    print(f"New Suggested Course Codes: {new_suggested_codes}")
    assert first_course["code"] not in new_suggested_codes, f"Course {first_course['code']} should have been removed from suggestions!"
    assert new_eval["score"] >= eval_data["score"], "Fit score should not decrease after completing a relevant course!"

    print("\n[7] Cleaning up test course and plan...")
    del_c = client.delete(f"/api/profile/courses/{new_course_id}")
    del_p = client.delete(f"/api/plan/{created_plan_id}")
    assert del_c.get_json().get("success")
    assert del_p.get_json().get("success")
    print("Cleanup successful.")

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! 100% OK! <<<")

if __name__ == "__main__":
    test_evaluation_flow()
