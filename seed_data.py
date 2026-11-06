"""
seed_data.py - Khởi tạo cơ sở dữ liệu SQLite và nạp dữ liệu mẫu thực tế (Thành viên 1 & Thành viên 2)
Đề tài: NLCNPM23CS-38
"""

try:
    # pyrefly: ignore[missing-import]
    from werkzeug.security import generate_password_hash
except ImportError:
    import hashlib
    def generate_password_hash(password):
        salt = "nlcnpm23cs38"
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 600000)
        return f"pbkdf2:sha256:600000${salt}${dk.hex()}"
from models import init_db, get_db_connection, dump_json_list, DB_PATH


def _ensure_admin_account(cursor):
    """Đảm bảo các tài khoản Quản trị viên và các tài khoản Sinh viên test luôn tồn tại."""
    pwd_hash = generate_password_hash("123456")

    # 1. Danh sách tài khoản bổ sung để test (Admin & Sinh viên các chuyên ngành)
    extra_users = [
        ("Quản trị viên Hệ thống", "admin@hust.edu.vn", "admin"),
        ("Nguyễn Phi Long (Admin)", "long.admin@hust.edu.vn", "admin"),
        ("Trần Thị Bích Ngọc", "ngoc.tran21@student.edu.vn", "student"),
        ("Lê Hoàng Nam", "nam.le21@student.edu.vn", "student"),
        ("Phạm Minh Tuấn", "tuan.pham22@student.edu.vn", "student"),
    ]

    for full_name, email, role in extra_users:
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email.lower(),))
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                """
                INSERT INTO users (full_name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                """,
                (full_name, email, pwd_hash, role),
            )

    # 2. Bổ sung hồ sơ chi tiết cho 3 sinh viên test nếu chưa có
    extra_profiles = [
        {
            "email": "ngoc.tran21@student.edu.vn",
            "full_name": "Trần Thị Bích Ngọc",
            "student_code": "20216045",
            "phone": "0912345678",
            "university": "Đại học Công nghệ - ĐHQGHN",
            "faculty": "Khoa Công nghệ Thông tin",
            "major": "Kỹ thuật Phần mềm",
            "academic_year": "K66 (2021 - 2025)",
            "gpa": "3.58",
            "target_position_id": 2,
            "bio": "Sinh viên năm cuối yêu thích thiết kế UI/UX và phát triển giao diện Frontend hiện đại với ReactJS, TypeScript và Tailwind CSS.",
            "courses": [
                ("INT2204", "Lập trình hướng đối tượng", 3, "A", "2022.2"),
                ("INT3306", "Phát triển ứng dụng Web", 3, "A+", "2023.1"),
                ("INT3110", "Giao diện người - máy (UI/UX)", 3, "A", "2023.2"),
            ],
            "skills": [
                ("HTML5/CSS3", "Frontend cơ bản", 5, "Responsive, Flexbox, CSS Grid"),
                ("JavaScript", "Ngôn ngữ lập trình", 4, "ES6+, Fetch API, DOM"),
                ("ReactJS", "Framework / Thư viện", 4, "React Hooks, Redux Toolkit, React Router"),
                ("Tailwind CSS", "Framework / Thư viện", 4, "Thiết kế giao diện nhanh chuẩn Design System"),
                ("Git", "Công cụ phát triển", 3, "Quản lý mã nguồn nhóm"),
            ],
            "certs": [
                ("Meta Front-End Developer Professional", "Coursera (Meta)", "2024-01-15", "", "https://coursera.org"),
                ("IELTS Academic 6.5", "British Council", "2023-09-10", "2025-09-10", "https://britishcouncil.vn"),
            ],
            "exps": [
                ("Frontend Developer Intern", "VNG Corporation", "Thực tập sinh", "2024-06-01", "2024-09-30", "Xây dựng các component giao diện bằng ReactJS và tối ưu hiệu năng tải trang."),
            ],
            "plans": [
                ("Hoàn thành khóa học TypeScript nâng cao", "Kỹ năng Frontend", "skill", "in_progress", "2026-12-01", "Áp dụng TypeScript vào dự án tốt nghiệp"),
                ("Tìm hiểu VueJS 3 & NuxtJS", "Framework mở rộng", "skill", "todo", "2026-12-20", "Mở rộng cơ hội ứng tuyển Frontend"),
            ],
        },
        {
            "email": "nam.le21@student.edu.vn",
            "full_name": "Lê Hoàng Nam",
            "student_code": "20218102",
            "phone": "0934567890",
            "university": "Đại học Kinh tế Quốc dân",
            "faculty": "Viện Công nghệ Thông tin & Kinh tế số",
            "major": "Hệ thống Thông tin Quản lý",
            "academic_year": "K63 (2021 - 2025)",
            "gpa": "3.35",
            "target_position_id": 4,
            "bio": "Định hướng trở thành Chuyên viên Phân tích Dữ liệu (Data Analyst) trong lĩnh vực Fintech & E-commerce.",
            "courses": [
                ("IT1102", "Cơ sở dữ liệu & Quản trị dữ liệu", 3, "A", "2022.2"),
                ("DS2010", "Xác suất thống kê ứng dụng", 3, "A", "2023.1"),
                ("DA3050", "Trực quan hóa dữ liệu kinh doanh (BI)", 3, "B+", "2023.2"),
            ],
            "skills": [
                ("SQL", "Cơ sở dữ liệu", 4, "Truy vấn phức tạp, Window Functions, CTE"),
                ("Python", "Ngôn ngữ lập trình", 4, "Phân tích dữ liệu với Pandas, NumPy"),
                ("Excel nâng cao", "Công cụ phân tích", 5, "Pivot Table, Power Query, VBA cơ bản"),
                ("Power BI", "Công cụ BI", 3, "Xây dựng Dashboard báo cáo DAX"),
                ("Pandas", "Thư viện dữ liệu", 4, "Làm sạch và biến đổi dữ liệu"),
            ],
            "certs": [
                ("Google Data Analytics Professional Certificate", "Coursera (Google)", "2024-03-12", "", "https://coursera.org"),
                ("TOEIC 750", "IIG Việt Nam", "2023-10-05", "2025-10-05", "https://iigvietnam.com"),
            ],
            "exps": [
                ("Data Analyst Collaborator", "Shopee Việt Nam", "Cộng tác viên", "2024-04-01", "2024-08-30", "Xây dựng báo cáo theo dõi hành vi mua sắm và phân tích phễu chuyển đổi bằng SQL & Power BI."),
            ],
            "plans": [
                ("Luyện tập Tableau Desktop Specialist", "Chứng chỉ BI", "certificate", "in_progress", "2026-12-10", "Bổ sung kỹ năng trực quan hóa dữ liệu"),
            ],
        },
        {
            "email": "tuan.pham22@student.edu.vn",
            "full_name": "Phạm Minh Tuấn",
            "student_code": "20225109",
            "phone": "0978123456",
            "university": "Đại học Bách Khoa Hà Nội",
            "faculty": "Trường Công nghệ Thông tin & Truyền thông",
            "major": "Trí tuệ Nhân tạo (AI)",
            "academic_year": "K67 (2022 - 2026)",
            "gpa": "3.65",
            "target_position_id": 8,
            "bio": "Đam mê nghiên cứu Học sâu (Deep Learning), Thị giác máy tính (Computer Vision) và xử lý ngôn ngữ tự nhiên (NLP).",
            "courses": [
                ("MI2020", "Toán rời rạc & Đại số tuyến tính", 4, "A", "2022.2"),
                ("IT3160", "Nhập môn Trí tuệ nhân tạo", 3, "A+", "2023.2"),
                ("IT4172", "Xử lý ảnh và Thị giác máy tính", 3, "A", "2024.1"),
            ],
            "skills": [
                ("Python", "Ngôn ngữ lập trình", 5, "Thành thạo lập trình AI/ML"),
                ("PyTorch", "Framework / Thư viện", 4, "Huấn luyện mô hình CNN, Transformer"),
                ("Scikit-Learn", "Framework / Thư viện", 4, "Các thuật toán Machine Learning cổ điển"),
                ("Computer Vision", "Chuyên ngành AI", 3, "Nhận diện vật thể YOLO, OpenCV"),
                ("Toán rời rạc & Đại số tuyến tính", "Nền tảng toán", 4, "Ma trận, tối ưu hóa Gradient"),
            ],
            "certs": [
                ("DeepLearning.AI TensorFlow Developer", "Coursera", "2024-04-20", "", "https://deeplearning.ai"),
            ],
            "exps": [
                ("Nghiên cứu viên Sinh viên (AI Lab)", "BKAI Research Center", "Dự án nghiên cứu", "2023-10-01", "2024-09-01", "Nghiên cứu mô hình nhận diện văn bản tiếng Việt OCR bằng PyTorch."),
            ],
            "plans": [
                ("Triển khai mô hình AI với Docker & FastAPI", "MLOps", "skill", "in_progress", "2026-12-15", "Đóng gói model phục vụ inference thực tế"),
            ],
        },
    ]

    for p in extra_profiles:
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (p["email"].lower(),))
        u_row = cursor.fetchone()
        if not u_row:
            continue
        uid = u_row["id"]

        cursor.execute("SELECT id FROM student_profiles WHERE user_id = ?", (uid,))
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO student_profiles (
                    user_id, full_name, student_code, email, phone,
                    university, faculty, major, academic_year, gpa, target_position_id, bio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uid,
                    p["full_name"],
                    p["student_code"],
                    p["email"],
                    p["phone"],
                    p["university"],
                    p["faculty"],
                    p["major"],
                    p["academic_year"],
                    p["gpa"],
                    p["target_position_id"],
                    p["bio"],
                ),
            )
            for code, name, credits, grade, term in p["courses"]:
                cursor.execute(
                    "INSERT INTO courses (user_id, code, name, credits, grade, term) VALUES (?, ?, ?, ?, ?, ?)",
                    (uid, code, name, credits, grade, term),
                )
            for name, category, level, note in p["skills"]:
                cursor.execute(
                    "INSERT INTO skills (user_id, name, category, level, note) VALUES (?, ?, ?, ?, ?)",
                    (uid, name, category, level, note),
                )
            for name, org, issue_date, exp_date, url in p["certs"]:
                cursor.execute(
                    "INSERT INTO certificates (user_id, name, organization, issue_date, expiry_date, credential_url) VALUES (?, ?, ?, ?, ?, ?)",
                    (uid, name, org, issue_date, exp_date, url),
                )
            for title, comp, rtype, sdate, edate, desc in p["exps"]:
                cursor.execute(
                    "INSERT INTO experiences (user_id, title, company, role_type, start_date, end_date, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (uid, title, comp, rtype, sdate, edate, desc),
                )
            for title, cat, ptype, status, tdate, note in p["plans"]:
                cursor.execute(
                    "INSERT INTO learning_plans (user_id, title, category, type, status, target_date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (uid, title, cat, ptype, status, tdate, note),
                )


def seed_database():
    """Khởi tạo các bảng và nạp dữ liệu mẫu nếu CSDL đang trống."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Kiểm tra nếu đã có user thì bổ sung tài khoản admin & bảng mới (nếu trống) rồi thoát
    cursor.execute("SELECT COUNT(*) AS cnt FROM users")
    if cursor.fetchone()["cnt"] > 0:
        _ensure_admin_account(cursor)
        _seed_analytics_tables_if_empty(cursor)
        conn.commit()
        conn.close()
        return

    # 1. Tạo tài khoản sinh viên mẫu & tài khoản Quản trị viên (Admin)
    pwd_hash = generate_password_hash("123456")
    cursor.execute(
        """
        INSERT INTO users (id, full_name, email, password_hash, role)
        VALUES (1, ?, ?, ?, 'student')
        """,
        ("Nguyễn Văn An", "an.nguyen20@sis.hust.edu.vn", pwd_hash),
    )
    _ensure_admin_account(cursor)

    # 2. Tạo thông tin cá nhân (student_profiles)
    cursor.execute(
        """
        INSERT INTO student_profiles (
            user_id, full_name, student_code, email, phone,
            university, faculty, major, academic_year, gpa, target_position_id, bio
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1,
            "Nguyễn Văn An",
            "20205012",
            "an.nguyen20@sis.hust.edu.vn",
            "0987654321",
            "Đại học Bách Khoa Hà Nội",
            "Trường Công nghệ Thông tin & Truyền thông",
            "Khoa học Máy tính",
            "K65 (2020 - 2025)",
            "3.42",
            1,
            "Sinh viên năm cuối đam mê phát triển hệ thống backend phân tán, có kiến thức vững chắc về Python, SQL, RESTful API và Docker.",
        ),
    )

    # 3. Nạp danh sách Học phần đã học (courses)
    sample_courses = [
        (1, "IT3011", "Cấu trúc dữ liệu và giải thuật", 3, "A", "2022.1"),
        (1, "IT3080", "Mạng máy tính", 3, "B+", "2022.2"),
        (1, "IT3090", "Cơ sở dữ liệu", 3, "A", "2022.2"),
        (1, "IT4010", "Lập trình Web", 3, "A", "2023.1"),
        (1, "IT4060", "Lập trình mạng và hệ thống phân tán", 3, "B+", "2023.2"),
        (1, "IT4409", "Kiểm thử và đảm bảo chất lượng phần mềm", 2, "A", "2023.2"),
    ]
    cursor.executemany(
        """
        INSERT INTO courses (user_id, code, name, credits, grade, term)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        sample_courses,
    )

    # 4. Nạp danh sách Kỹ năng cá nhân (skills)
    sample_skills = [
        (1, "Python", "Ngôn ngữ lập trình", 4, "Thành thạo lập trình OOP, xử lý cấu trúc dữ liệu"),
        (1, "SQL", "Cơ sở dữ liệu", 4, "Viết truy vấn phức tạp, tối ưu chỉ mục index"),
        (1, "Flask", "Framework / Thư viện", 3, "Xây dựng REST API, tích hợp SQLite/SQLAlchemy"),
        (1, "Git", "Công cụ phát triển", 4, "Sử dụng thành thạo Git branch, PR, merge rebase"),
        (1, "HTML5/CSS3", "Frontend cơ bản", 3, "Cắt giao diện chuẩn responsive, Bootstrap"),
        (1, "JavaScript", "Ngôn ngữ lập trình", 3, "ES6+, DOM, Async/Await"),
        (1, "Docker", "DevOps & Môi trường", 2, "Biết viết Dockerfile cơ bản, docker-compose"),
    ]
    cursor.executemany(
        """
        INSERT INTO skills (user_id, name, category, level, note)
        VALUES (?, ?, ?, ?, ?)
        """,
        sample_skills,
    )

    # 5. Nạp danh sách Chứng chỉ (certificates)
    sample_certs = [
        (1, "TOEIC 785", "ETS", "2023-08-15", "2025-08-15", "https://www.iigvietnam.com"),
        (1, "Python PCEP Certified Entry-Level", "Python Institute", "2023-11-20", "", "https://pythoninstitute.org"),
        (1, "SQL for Data Science", "Coursera (UC Davis)", "2024-02-10", "", "https://coursera.org"),
    ]
    cursor.executemany(
        """
        INSERT INTO certificates (user_id, name, organization, issue_date, expiry_date, credential_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        sample_certs,
    )

    # 6. Nạp danh sách Kinh nghiệm thực tế & Dự án (experiences)
    sample_exps = [
        (
            1,
            "Thực tập sinh Backend (Python Intern)",
            "Công ty Cổ phần Công nghệ ABC",
            "Thực tập sinh",
            "2024-06-01",
            "2024-09-30",
            "Tham gia viết API xác thực người dùng bằng JWT, tối ưu hóa câu truy vấn SQL giảm 35% thời gian phản hồi.",
        ),
        (
            1,
            "Trưởng nhóm Đồ án môn học Web Bán hàng",
            "Dự án cá nhân / Nhóm sinh viên",
            "Đồ án",
            "2023-09-01",
            "2023-12-20",
            "Thiết kế kiến trúc MVC bằng Flask, cơ sở dữ liệu PostgreSQL, tích hợp cổng thanh toán Sandbox VNPAY.",
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO experiences (user_id, title, company, role_type, start_date, end_date, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        sample_exps,
    )

    # 7. Nạp 8 Vị trí nghề nghiệp CNTT (positions)
    positions_data = [
        (
            1,
            "Lập trình viên Backend (Backend Developer)",
            "BACKEND_DEV",
            "Xây dựng và tối ưu hệ thống xử lý phía máy chủ, thiết kế kiến trúc cơ sở dữ liệu và RESTful/GraphQL API.",
            dump_json_list(["Python", "Java", "Node.js", "SQL", "Docker", "RESTful API", "Redis", "Git"]),
            "Rất cao",
        ),
        (
            2,
            "Lập trình viên Frontend (Frontend Developer)",
            "FRONTEND_DEV",
            "Thiết kế, xây dựng giao diện ứng dụng web tối ưu trải nghiệm người dùng, responsive và tương tác mượt mà.",
            dump_json_list(["HTML5/CSS3", "JavaScript", "TypeScript", "ReactJS", "VueJS", "Bootstrap", "Tailwind CSS", "Git"]),
            "Cao",
        ),
        (
            3,
            "Lập trình viên Fullstack (Fullstack Developer)",
            "FULLSTACK_DEV",
            "Thành thạo cả tầng giao diện Frontend và logic Backend, triển khai và bảo trì toàn diện hệ thống web.",
            dump_json_list(["JavaScript", "Node.js", "ReactJS", "PostgreSQL", "Docker", "RESTful API", "CI/CD", "Git"]),
            "Rất cao",
        ),
        (
            4,
            "Chuyên viên Phân tích Dữ liệu (Data Analyst)",
            "DATA_ANALYST",
            "Khai phá, xử lý và trực quan hóa dữ liệu từ nhiều nguồn nhằm hỗ trợ doanh nghiệp ra quyết định chiến lược.",
            dump_json_list(["Python", "SQL", "Power BI", "Tableau", "Excel nâng cao", "Xác suất thống kê", "Pandas", "Data Cleaning"]),
            "Cao",
        ),
        (
            5,
            "Kỹ sư DevOps & Cloud (DevOps Engineer)",
            "DEVOPS_ENG",
            "Tự động hóa chu trình phát triển - triển khai CI/CD, vận hành hạ tầng đám mây và giám sát tính ổn định hệ thống.",
            dump_json_list(["Linux", "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Shell Scripting", "Prometheus"]),
            "Rất cao",
        ),
        (
            6,
            "Kỹ sư Kiểm thử Phần mềm (QA / QC Tester)",
            "QA_TESTER",
            "Đảm bảo chất lượng sản phẩm phần mềm qua việc lập kế hoạch kiểm thử, thiết kế test case thủ công và tự động.",
            dump_json_list(["Kiểm thử phần mềm", "Thiết kế Test Case", "Postman", "Selenium", "SQL cơ bản", "Jira", "API Testing"]),
            "Trung bình",
        ),
        (
            7,
            "Lập trình viên Ứng dụng Di động (Mobile App Developer)",
            "MOBILE_DEV",
            "Phát triển ứng dụng di động đa nền tảng hoặc native cho hệ điều hành iOS và Android.",
            dump_json_list(["Flutter", "Dart", "React Native", "Swift", "Kotlin", "RESTful API", "Mobile UX", "Git"]),
            "Cao",
        ),
        (
            8,
            "Kỹ sư Trí tuệ Nhân tạo & Học máy (AI / ML Engineer)",
            "AI_ML_ENG",
            "Nghiên cứu, huấn luyện và triển khai các mô hình học máy, thị giác máy tính và xử lý ngôn ngữ tự nhiên.",
            dump_json_list(["Python", "PyTorch", "TensorFlow", "Toán rời rạc & Đại số tuyến tính", "Scikit-Learn", "Computer Vision", "NLP", "Docker"]),
            "Rất cao",
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO positions (id, name, code, description, core_skills, demand_level)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        positions_data,
    )

    # 8. Nạp 30 Tin tuyển dụng thực tế (jobs)
    jobs_data = [
        ("Junior/Mid Backend Developer (Python/Flask/FastAPI)", "FPT Software", 1, "Hà Nội / Đà Nẵng", "14 - 25 triệu VNĐ", "1 - 2 năm", ["Python", "Flask", "SQL", "Git", "RESTful API"], ["PostgreSQL", "Docker", "Redis", "FastAPI"], ["Python PCEP/PCAP", "AWS Certified Cloud Practitioner"], "2026-11-30", "Tham gia phát triển các phân hệ dịch vụ tài chính vi mô, viết API hiệu năng cao và thiết kế CSDL."),
        ("Java Backend Engineer (Spring Boot)", "Viettel Telecom", 1, "Hà Nội", "18 - 35 triệu VNĐ", "2+ năm", ["Java", "Spring Boot", "SQL", "OOP", "Git"], ["Kafka", "Docker", "Oracle DB", "Microservices"], ["Oracle Certified Professional Java", "AWS Solutions Architect"], "2026-12-15", "Xây dựng các hệ thống Core Billing, tích hợp cổng thanh toán viễn thông với lưu lượng hàng triệu giao dịch/ngày."),
        ("Node.js Backend Developer", "VNG Corporation", 1, "TP. Hồ Chí Minh", "16 - 28 triệu VNĐ", "1 - 3 năm", ["JavaScript", "Node.js", "ExpressJS", "SQL", "RESTful API"], ["MongoDB", "Redis", "Docker", "RabbitMQ"], ["Node.js Application Developer", "MongoDB Associate"], "2026-11-25", "Phát triển hệ thống backend cho nền tảng mạng xã hội và giải trí trực tuyến."),
        ("Golang Backend Developer", "Momo (M-Service)", 1, "TP. Hồ Chí Minh", "20 - 40 triệu VNĐ", "2+ năm", ["Golang", "Microservices", "SQL", "Git", "Clean Architecture"], ["gRPC", "Redis", "Kafka", "Kubernetes"], ["AWS Certified Developer"], "2026-12-01", "Nâng cấp và duy trì các dịch vụ thanh toán QR, ví điện tử với yêu cầu tính sẵn sàng cao (High Availability)."),
        ("Frontend Developer (ReactJS / TypeScript)", "Shopee Vietnam", 2, "TP. Hồ Chí Minh", "18 - 32 triệu VNĐ", "1 - 3 năm", ["HTML5/CSS3", "JavaScript", "TypeScript", "ReactJS", "Redux"], ["Webpack", "Tailwind CSS", "Next.js", "Jest"], ["Meta Front-End Developer"], "2026-12-10", "Phát triển các tính năng giỏ hàng, thanh toán và chiến dịch khuyến mãi trên cổng thương mại điện tử Shopee."),
        ("Web Frontend Developer (Vue.js / Bootstrap)", "Tiki Corporation", 2, "TP. Hồ Chí Minh", "15 - 26 triệu VNĐ", "1 - 2 năm", ["HTML5/CSS3", "JavaScript", "VueJS", "Bootstrap", "Git"], ["Pinia", "Sass", "RESTful API", "Vite"], [], "2026-11-20", "Xây dựng dashboard quản trị cho người bán hàng và cổng tiếp nhận đơn hàng."),
        ("Junior Frontend Developer (ReactJS/HTML/CSS)", "NashTech Vietnam", 2, "Hà Nội / TP.HCM", "10 - 18 triệu VNĐ", "Dưới 1 năm / Fresher", ["HTML5/CSS3", "JavaScript", "ReactJS", "Bootstrap", "Git"], ["RESTful API", "CSS Modules", "NPM"], [], "2026-12-05", "Cơ hội cho sinh viên mới ra trường tham gia dự án phần mềm cho khách hàng châu Âu và Úc."),
        ("Senior Frontend Engineer (Angular / TypeScript)", "KMS Technology", 2, "Đà Nẵng", "25 - 45 triệu VNĐ", "3+ năm", ["TypeScript", "Angular", "RxJS", "HTML5/CSS3", "Unit Test"], ["NgRx", "SCSS", "CI/CD", "Karma"], [], "2026-12-20", "Chịu trách nhiệm kiến trúc frontend cho ứng dụng chăm sóc sức khỏe điện tử (Healthcare SaaS)."),
        ("Fullstack Developer (Node.js & ReactJS)", "ZaloPay", 3, "TP. Hồ Chí Minh", "22 - 38 triệu VNĐ", "2+ năm", ["JavaScript", "TypeScript", "ReactJS", "Node.js", "SQL"], ["PostgreSQL", "Docker", "Redis", "Next.js"], ["AWS Certified Developer"], "2026-11-30", "Xây dựng các mini-app trên nền tảng Zalo, tích hợp ví thanh toán và quản trị merchant."),
        ("Fullstack Software Engineer (.NET & Angular)", "One Mount Group", 3, "Hà Nội", "20 - 36 triệu VNĐ", "2+ năm", ["C#", ".NET Core", "Angular", "SQL", "Git"], ["SQL Server", "Docker", "Azure", "Microservices"], ["Microsoft Certified: Azure Developer Associate"], "2026-12-18", "Phát triển các giải pháp số hóa chuỗi cung ứng VinShop và bất động sản OneHousing."),
        ("Fullstack Web Developer (Python & Vue.js)", "VNPT Information Technology", 3, "Hà Nội", "15 - 25 triệu VNĐ", "1 - 3 năm", ["Python", "Django", "VueJS", "JavaScript", "SQL"], ["PostgreSQL", "Bootstrap", "Git", "Docker"], [], "2026-12-12", "Phát triển cổng thông tin hành chính công và các phần mềm dịch vụ giáo dục điện tử."),
        ("Junior Data Analyst", "Techcombank", 4, "Hà Nội", "14 - 22 triệu VNĐ", "0 - 1 năm / Fresher", ["SQL", "Python", "Power BI", "Excel nâng cao", "Phân tích dữ liệu"], ["Pandas", "Oracle DB", "Jupyter Notebook"], ["PL-300: Microsoft Power BI Data Analyst", "Google Data Analytics Certificate"], "2026-12-05", "Phân tích hành vi chi tiêu thẻ tín dụng, xây dựng các dashboard theo dõi chỉ số rủi ro tín dụng hàng tuần."),
        ("BI Data Analyst (Tableau & SQL)", "VPBank", 4, "Hà Nội", "18 - 30 triệu VNĐ", "1 - 3 năm", ["SQL", "Tableau", "Data Modeling", "Xác suất thống kê", "Python"], ["PostgreSQL", "Snowflake", "Excel"], ["Tableau Desktop Specialist"], "2026-12-25", "Xây dựng mô hình dữ liệu trực quan phục vụ khối Khách hàng Doanh nghiệp SME."),
        ("Data Analyst - Product & Marketing", "Chợ Tốt (Carousell Group)", 4, "TP. Hồ Chí Minh", "16 - 28 triệu VNĐ", "1 - 2 năm", ["SQL", "Python", "Google Analytics", "A/B Testing", "Trực quan hóa dữ liệu"], ["BigQuery", "Looker Studio", "Pandas"], ["Google Data Analytics Certificate"], "2026-11-28", "Đo lường hiệu quả các chiến dịch Marketing, phân tích phễu chuyển đổi người dùng trên app Chợ Tốt."),
        ("DevOps Engineer (AWS & Kubernetes)", "FPT Software", 5, "Hà Nội", "22 - 40 triệu VNĐ", "2+ năm", ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD"], ["Terraform", "GitLab CI", "Prometheus", "Helm"], ["AWS Certified Solutions Architect", "CKA (Certified Kubernetes Administrator)"], "2026-12-30", "Vận hành hạ tầng Cloud cho các khách hàng tài chính quốc tế, đảm bảo uptime 99.9%."),
        ("Cloud Infrastructure Engineer", "MB Bank", 5, "Hà Nội", "20 - 38 triệu VNĐ", "1 - 3 năm", ["Linux", "Shell Scripting", "Docker", "CI/CD", "Mạng máy tính"], ["Jenkins", "Ansible", "Kubernetes", "Grafana"], ["Red Hat Certified System Administrator (RHCSA)", "AWS SysOps"], "2026-12-15", "Tự động hóa triển khai ứng dụng ngân hàng số MBBank, cấu hình cảnh báo và giám sát hệ thống tự động."),
        ("Site Reliability Engineer (SRE / DevOps)", "VNG Corporation", 5, "TP. Hồ Chí Minh", "25 - 45 triệu VNĐ", "2+ năm", ["Linux", "Python", "Docker", "Kubernetes", "Troubleshooting"], ["ELK Stack", "Prometheus", "Kafka", "GitOps"], ["CKA (Certified Kubernetes Administrator)"], "2026-12-10", "Duy trì tính sẵn sàng và khả năng chịu tải cho các game bom tấn và ứng dụng Zalo."),
        ("Manual & Automation QA Tester", "KMS Technology", 6, "TP. Hồ Chí Minh", "14 - 24 triệu VNĐ", "1 - 2 năm", ["Kiểm thử phần mềm", "Thiết kế Test Case", "Postman", "Selenium", "SQL"], ["Jira", "TestRail", "Java", "Git"], ["ISTQB Foundation Level (CTFL)"], "2026-12-05", "Thực hiện kiểm thử chức năng và phi chức năng, viết script tự động hóa kiểm thử hồi quy cho ứng dụng web."),
        ("QC Tester (Fresher / Junior)", "FPT Information System", 6, "Hà Nội", "9 - 15 triệu VNĐ", "0 - 1 năm", ["Kiểm thử phần mềm", "Tạo Test Case", "SQL cơ bản", "Kỹ năng giao tiếp"], ["Jira", "Postman", "Excel"], ["ISTQB Foundation Level (CTFL)"], "2026-11-20", "Hỗ trợ đội ngũ kiểm thử các phần mềm chính phủ điện tử, quản lý bệnh viện và giao thông thông minh."),
        ("Senior Automation Test Engineer (Cypress / Playwright)", "Shopee Vietnam", 6, "TP. Hồ Chí Minh", "25 - 40 triệu VNĐ", "3+ năm", ["Automation Testing", "JavaScript", "TypeScript", "CI/CD Integration", "API Testing"], ["Cypress", "Playwright", "Jenkins", "Docker"], ["ISTQB Advanced Level Test Automation Engineer"], "2026-12-28", "Thiết kế và duy trì framework kiểm thử tự động quy mô lớn cho hệ sinh thái Shopee."),
        ("Flutter Mobile Developer", "Momo (M-Service)", 7, "TP. Hồ Chí Minh", "16 - 30 triệu VNĐ", "1 - 3 năm", ["Flutter", "Dart", "RESTful API", "Git", "State Management (Bloc/Provider)"], ["Firebase", "SQLite", "GraphQL"], [], "2026-12-15", "Phát triển các module tiện ích mới trên siêu ứng dụng MoMo phục vụ hơn 30 triệu người dùng."),
        ("React Native Developer", "Tiki Corporation", 7, "TP. Hồ Chí Minh", "15 - 28 triệu VNĐ", "1 - 2 năm", ["React Native", "JavaScript", "TypeScript", "Redux", "Mobile UI"], ["Xcode", "Android Studio", "Firebase"], [], "2026-12-08", "Tối ưu hóa hiệu năng ứng dụng Tiki trên iOS và Android, cải thiện tốc độ load trang danh mục sản phẩm."),
        ("iOS Native Developer (Swift)", "Viettel Digital", 7, "Hà Nội", "20 - 35 triệu VNĐ", "2+ năm", ["Swift", "iOS SDK", "AutoLayout", "OOP", "Git"], ["CoreData", "Combine", "CocoaPods", "Fastlane"], ["Apple Certified Developer"], "2026-12-31", "Phát triển ứng dụng tài chính số Viettel Money phiên bản iOS native, bảo mật dữ liệu cấp độ ngân hàng."),
        ("Android Native Developer (Kotlin)", "VNPT Technology", 7, "Hà Nội", "16 - 28 triệu VNĐ", "1 - 3 năm", ["Kotlin", "Android SDK", "Jetpack Compose", "Coroutines", "MVVM"], ["Retrofit", "Room DB", "Dagger Hilt"], ["Google Associate Android Developer"], "2026-12-10", "Xây dựng ứng dụng nhà thông minh (Smart Home IoT) kết nối thiết bị phần cứng của VNPT."),
        ("AI / Machine Learning Engineer", "VinAI Research", 8, "Hà Nội", "25 - 50 triệu VNĐ", "1 - 3 năm", ["Python", "PyTorch", "Toán giải tích & Đại số", "Machine Learning", "Git"], ["OpenCV", "CUDA", "Docker", "Linux"], ["DeepLearning.AI Machine Learning Specialization", "AWS Certified Machine Learning"], "2026-12-25", "Nghiên cứu và huấn luyện các mô hình thị giác máy tính cho hệ thống lái xe tự hành VinFast."),
        ("NLP Engineer (Natural Language Processing)", "Zalo AI Lab", 8, "TP. Hồ Chí Minh", "22 - 42 triệu VNĐ", "2+ năm", ["Python", "NLP", "PyTorch", "Transformers", "Xử lý văn bản tiếng Việt"], ["HuggingFace", "BERT", "FastAPI", "ONNX"], ["DeepLearning.AI Deep Learning Specialization"], "2026-12-20", "Phát triển trợ lý giọng nói Kiki, mô hình tóm tắt văn bản và chatbot thông minh trên hệ sinh thái Zalo."),
        ("Computer Vision Engineer", "FPT Software (FPT AI)", 8, "Quy Nhơn / Hà Nội", "20 - 38 triệu VNĐ", "1 - 3 năm", ["Python", "Computer Vision", "TensorFlow", "PyTorch", "OpenCV"], ["YOLO", "Docker", "Triton Server"], [], "2026-12-15", "Xây dựng giải pháp định danh khách hàng điện tử (eKYC) và nhận diện tài liệu OCR cho ngân hàng."),
        ("Backend Developer (Node.js & AWS Serverless)", "TymeX Vietnam", 1, "TP. Hồ Chí Minh", "20 - 35 triệu VNĐ", "2+ năm", ["JavaScript", "TypeScript", "Node.js", "RESTful API", "SQL"], ["AWS Lambda", "DynamoDB", "Docker", "Jest"], ["AWS Certified Cloud Practitioner"], "2026-11-30", "Phát triển nền tảng ngân hàng số đa quốc gia (Digital Banking) phục vụ hàng triệu khách hàng Nam Phi & Philippines."),
        ("Frontend Developer (ReactJS & WebSockets)", "SSI Securities (Chứng khoán SSI)", 2, "Hà Nội", "18 - 32 triệu VNĐ", "2+ năm", ["HTML5/CSS3", "JavaScript", "ReactJS", "TypeScript", "WebSockets"], ["Chart.js", "Redux Toolkit", "Ant Design", "TradingView API"], [], "2026-12-18", "Xây dựng bảng giá chứng khoán thời gian thực tốc độ mili-giây, biểu đồ kỹ thuật chuyên sâu."),
        ("Junior Data Analyst - Operations", "Giao Hàng Nhanh (GHN)", 4, "TP. Hồ Chí Minh", "12 - 18 triệu VNĐ", "0 - 1 năm", ["SQL", "Excel nâng cao", "Power BI", "Phân tích dữ liệu", "Python"], ["Google Sheets", "PostgreSQL", "Pandas"], ["Google Data Analytics Certificate"], "2026-12-05", "Phân tích thời gian giao hàng, tối ưu hóa cung đường bưu tá và năng suất các kho bãi toàn quốc."),
    ]
    for j in jobs_data:
        cursor.execute(
            """
            INSERT INTO jobs (
                title, company, position_id, location, salary,
                experience_required, skills, technologies, certificates, deadline, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                j[0],
                j[1],
                j[2],
                j[3],
                j[4],
                j[5],
                dump_json_list(j[6]),
                dump_json_list(j[7]),
                dump_json_list(j[8]),
                j[9],
                j[10],
            ),
        )

    # 9. Nạp dữ liệu mẫu cho bảng learning_plans
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

    # 10 & 11. Nạp dữ liệu mẫu cho course_recommendations và comparison_history
    _seed_analytics_tables_if_empty(cursor)

    conn.commit()
    conn.close()
    print(f"Da nap du lieu mau thanh cong vao: {DB_PATH}")


def _seed_analytics_tables_if_empty(cursor):
    """Nạp dữ liệu mẫu cho bảng course_recommendations và comparison_history nếu đang trống."""
    cursor.execute("SELECT COUNT(*) AS cnt FROM course_recommendations")
    if cursor.fetchone()["cnt"] == 0:
        recs_data = [
            ("Java", "Java Programming and Software Engineering Fundamentals", "Coursera (Duke University)", "course", "6 tuần", "https://www.coursera.org", "Nắm vững lập trình hướng đối tượng OOP, cấu trúc dữ liệu và thiết kế phần mềm với Java."),
            ("Spring Boot", "Master Microservices with Spring Boot and Spring Cloud", "Udemy", "course", "8 tuần", "https://www.udemy.com", "Xây dựng RESTful API, bảo mật Spring Security, JPA/Hibernate và kiến trúc Microservices."),
            ("Node.js", "The Complete Node.js Developer Course", "Udemy", "course", "5 tuần", "https://www.udemy.com", "Phát triển ứng dụng Backend thời gian thực với Node.js, ExpressJS, MongoDB và Socket.io."),
            ("RESTful API", "Thiết kế và Bảo mật RESTful API chuẩn Doanh nghiệp", "F8 / Coursera", "course", "3 tuần", "https://www.coursera.org", "Chuẩn hóa HTTP Methods, Status Codes, xác thực JWT/OAuth2 và tài liệu hóa bằng Swagger/OpenAPI."),
            ("Redis", "Redis University - RU101: Introduction to Redis Data Structures", "Redis University", "certificate", "3 tuần", "https://university.redis.com", "Ứng dụng In-Memory Caching, Pub/Sub, Session Store và tối ưu độ trễ truy vấn Backend."),
            ("Docker", "Docker & Kubernetes: The Practical Guide", "Udemy", "course", "4 tuần", "https://www.udemy.com", "Thực hành đóng gói ứng dụng với Multi-stage Dockerfile, Docker Compose và triển khai Container."),
            ("Golang", "Programming with Google Go Specialization", "Coursera (UC Irvine)", "course", "6 tuần", "https://www.coursera.org", "Làm chủ Concurrency (Goroutines, Channels) và xây dựng dịch vụ hiệu năng cao với Golang."),
            ("Microservices", "Microservices Architecture & System Design", "edX / Udemy", "course", "6 tuần", "https://www.edx.org", "Thiết kế hệ thống phân tán, API Gateway, Message Queue (Kafka/RabbitMQ) và Circuit Breaker."),
            ("ReactJS", "Meta Front-End Developer Professional Certificate", "Coursera (Meta)", "certificate", "8 tuần", "https://www.coursera.org", "Xây dựng giao diện Single Page Application hiện đại với React Hooks, State Management và Testing."),
            ("TypeScript", "Understanding TypeScript - 2026 Edition", "Udemy", "course", "4 tuần", "https://www.udemy.com", "Kiểm soát kiểu dữ liệu tĩnh, Generics, Decorators và tích hợp TypeScript vào dự án React/Node.js."),
            ("VueJS", "Vue - The Complete Guide (incl. Router & Composition API)", "Udemy", "course", "5 tuần", "https://www.udemy.com", "Phát triển Frontend với Vue 3 Composition API, Pinia và Vite."),
            ("Power BI", "PL-300: Microsoft Power BI Data Analyst", "Microsoft Learn", "certificate", "6 tuần", "https://learn.microsoft.com", "Xử lý dữ liệu với Power Query, ngôn ngữ DAX và thiết kế báo cáo BI trực quan."),
            ("Tableau", "Data Visualization with Tableau Specialization", "Coursera (UC Davis)", "certificate", "5 tuần", "https://www.coursera.org", "Trực quan hóa dữ liệu chuyên nghiệp và xây dựng Interactive Storytelling Dashboard."),
            ("Linux", "Introduction to Linux (LFS101)", "The Linux Foundation", "certificate", "4 tuần", "https://training.linuxfoundation.org", "Quản trị hệ điều hành Linux, phân quyền, tiến trình và viết kịch bản Bash Shell."),
            ("Kubernetes", "Certified Kubernetes Administrator (CKA) Prep Course", "KodeKloud / Linux Foundation", "certificate", "8 tuần", "https://kodekloud.com", "Quản trị cụm Kubernetes, Pods, Deployments, Services, Ingress và Helm Charts."),
            ("AWS", "AWS Certified Cloud Practitioner (CLF-C02)", "AWS Skill Builder", "certificate", "6 tuần", "https://explore.skillbuilder.aws", "Kiến thức nền tảng về điện toán đám mây AWS: EC2, S3, RDS, IAM, VPC và Lambda."),
            ("CI/CD", "CI/CD Pipelines with GitHub Actions & GitLab CI", "Udemy", "course", "3 tuần", "https://www.udemy.com", "Tự động hóa kiểm thử, đóng gói Docker và triển khai liên tục lên máy chủ Cloud."),
            ("Selenium", "Selenium WebDriver with Java/Python - Automation Testing", "Udemy", "course", "5 tuần", "https://www.udemy.com", "Xây dựng Page Object Model (POM) và kịch bản kiểm thử tự động cho ứng dụng Web."),
            ("Postman", "Postman API Fundamentals Student Expert", "Postman Academy", "certificate", "2 tuần", "https://academy.postman.com", "Kiểm thử tự động RESTful API, viết test script và chạy Collection bằng Newman."),
            ("Flutter", "Flutter & Dart - The Complete Guide", "Udemy", "course", "6 tuần", "https://www.udemy.com", "Phát triển ứng dụng di động đa nền tảng iOS & Android với Flutter và Bloc/Provider."),
            ("PyTorch", "Deep Learning Specialization", "Coursera (DeepLearning.AI)", "certificate", "8 tuần", "https://www.coursera.org", "Huấn luyện mạng nơ-ron sâu CNN, RNN, Transformers với PyTorch và ứng dụng thực tế."),
        ]
        cursor.executemany(
            """
            INSERT INTO course_recommendations (skill_name, title, provider, rec_type, duration, url, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            recs_data,
        )

    cursor.execute("SELECT COUNT(*) AS cnt FROM comparison_history")
    if cursor.fetchone()["cnt"] == 0:
        history_data = [
            (
                1,
                1,
                "Lập trình viên Backend (Backend Developer)",
                50,
                dump_json_list(["Python", "SQL", "Docker", "Git", "Flask", "JavaScript"]),
                dump_json_list(["Java", "Node.js", "RESTful API", "Redis", "Spring Boot", "Golang"]),
            ),
            (
                1,
                4,
                "Chuyên viên Phân tích Dữ liệu (Data Analyst)",
                38,
                dump_json_list(["Python", "SQL", "Phân tích dữ liệu"]),
                dump_json_list(["Power BI", "Tableau", "Excel nâng cao", "Xác suất thống kê", "Pandas"]),
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO comparison_history (user_id, position_id, position_name, score, matched_skills, missing_skills)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            history_data,
        )


if __name__ == "__main__":
    seed_database()
