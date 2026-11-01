"""
seed_data.py - Khởi tạo cơ sở dữ liệu SQLite và nạp dữ liệu mẫu (Phân hệ Thành viên 1)
Đề tài: NLCNPM23CS-38
"""

from werkzeug.security import generate_password_hash
from models import init_db, get_db_connection, dump_json_list, DB_PATH


def seed_database():
    """Khởi tạo các bảng của Thành viên 1 và nạp dữ liệu mẫu nếu CSDL đang trống."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS cnt FROM users")
    if cursor.fetchone()["cnt"] > 0:
        conn.close()
        return

    # 1. Tạo tài khoản sinh viên mẫu
    pwd_hash = generate_password_hash("123456")
    cursor.execute(
        """
        INSERT INTO users (id, full_name, email, password_hash, role)
        VALUES (1, ?, ?, ?, 'student')
        """,
        ("Nguyễn Văn An", "an.nguyen20@sis.hust.edu.vn", pwd_hash),
    )

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

    conn.commit()
    conn.close()
    print(f"Đã nạp dữ liệu mẫu (Thành viên 1) thành công vào: {DB_PATH}")


if __name__ == "__main__":
    seed_database()
