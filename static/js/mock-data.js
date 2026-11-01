/**
 * mock-data.js - Dữ liệu giả lập thực tế phục vụ chạy Frontend độc lập
 * Đề tài: NLCNPM23CS-38
 * Bao gồm: 8 vị trí CNTT, 30 tin tuyển dụng từ các công ty công nghệ tại VN,
 * hồ sơ sinh viên đầy đủ 4 phần, kế hoạch học tập và dữ liệu thống kê.
 */

const MockData = {
    // 1. DANH MỤC 8 VỊ TRÍ NGHỀ NGHIỆP CNTT PHỔ BIẾN
    positions: [
        {
            id: 1,
            name: "Lập trình viên Backend (Backend Developer)",
            code: "BACKEND_DEV",
            description: "Xây dựng và tối ưu hệ thống xử lý phía máy chủ, thiết kế kiến trúc cơ sở dữ liệu và RESTful/GraphQL API.",
            core_skills: ["Python", "Java", "Node.js", "SQL", "Docker", "RESTful API", "Redis", "Git"],
            demand_level: "Rất cao"
        },
        {
            id: 2,
            name: "Lập trình viên Frontend (Frontend Developer)",
            code: "FRONTEND_DEV",
            description: "Thiết kế, xây dựng giao diện ứng dụng web tối ưu trải nghiệm người dùng, responsive và tương tác mượt mà.",
            core_skills: ["HTML5/CSS3", "JavaScript", "TypeScript", "ReactJS", "VueJS", "Bootstrap", "Tailwind CSS", "Git"],
            demand_level: "Cao"
        },
        {
            id: 3,
            name: "Lập trình viên Fullstack (Fullstack Developer)",
            code: "FULLSTACK_DEV",
            description: "Thành thạo cả tầng giao diện Frontend và logic Backend, triển khai và bảo trì toàn diện hệ thống web.",
            core_skills: ["JavaScript", "Node.js", "ReactJS", "PostgreSQL", "Docker", "RESTful API", "CI/CD", "Git"],
            demand_level: "Rất cao"
        },
        {
            id: 4,
            name: "Chuyên viên Phân tích Dữ liệu (Data Analyst)",
            code: "DATA_ANALYST",
            description: "Khai phá, xử lý và trực quan hóa dữ liệu từ nhiều nguồn nhằm hỗ trợ doanh nghiệp ra quyết định chiến lược.",
            core_skills: ["Python", "SQL", "Power BI", "Tableau", "Excel nâng cao", "Xác suất thống kê", "Pandas", "Data Cleaning"],
            demand_level: "Cao"
        },
        {
            id: 5,
            name: "Kỹ sư DevOps & Cloud (DevOps Engineer)",
            code: "DEVOPS_ENG",
            description: "Tự động hóa chu trình phát triển - triển khai CI/CD, vận hành hạ tầng đám mây và giám sát tính ổn định hệ thống.",
            core_skills: ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Shell Scripting", "Prometheus"],
            demand_level: "Rất cao"
        },
        {
            id: 6,
            name: "Kỹ sư Kiểm thử Phần mềm (QA / QC Tester)",
            code: "QA_TESTER",
            description: "Đảm bảo chất lượng sản phẩm phần mềm qua việc lập kế hoạch kiểm thử, thiết kế test case thủ công và tự động.",
            core_skills: ["Kiểm thử phần mềm", "Thiết kế Test Case", "Postman", "Selenium", "SQL cơ bản", "Jira", "API Testing"],
            demand_level: "Trung bình"
        },
        {
            id: 7,
            name: "Lập trình viên Ứng dụng Di động (Mobile App Developer)",
            code: "MOBILE_DEV",
            description: "Phát triển ứng dụng di động đa nền tảng hoặc native cho hệ điều hành iOS và Android.",
            core_skills: ["Flutter", "Dart", "React Native", "Swift", "Kotlin", "RESTful API", "Mobile UX", "Git"],
            demand_level: "Cao"
        },
        {
            id: 8,
            name: "Kỹ sư Trí tuệ Nhân tạo & Học máy (AI / ML Engineer)",
            code: "AI_ML_ENG",
            description: "Nghiên cứu, huấn luyện và triển khai các mô hình học máy, thị giác máy tính và xử lý ngôn ngữ tự nhiên.",
            core_skills: ["Python", "PyTorch", "TensorFlow", "Toán rời rạc & Đại số tuyến tính", "Scikit-Learn", "Computer Vision", "NLP", "Docker"],
            demand_level: "Rất cao"
        }
    ],

    // 2. DANH SÁCH 30 TIN TUYỂN DỤNG THỰC TẾ
    jobs: [
        {
            id: 1,
            title: "Junior/Mid Backend Developer (Python/Flask/FastAPI)",
            company: "FPT Software",
            position_id: 1,
            location: "Hà Nội / Đà Nẵng",
            salary: "14 - 25 triệu VNĐ",
            experience_required: "1 - 2 năm",
            skills: ["Python", "Flask", "SQL", "Git", "RESTful API"],
            technologies: ["PostgreSQL", "Docker", "Redis", "FastAPI"],
            certificates: ["Python PCEP/PCAP", "AWS Certified Cloud Practitioner"],
            deadline: "2026-11-30",
            description: "Tham gia phát triển các phân hệ dịch vụ tài chính vi mô, viết API hiệu năng cao và thiết kế CSDL."
        },
        {
            id: 2,
            title: "Java Backend Engineer (Spring Boot)",
            company: "Viettel Telecom",
            position_id: 1,
            location: "Hà Nội",
            salary: "18 - 35 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["Java", "Spring Boot", "SQL", "OOP", "Git"],
            technologies: ["Kafka", "Docker", "Oracle DB", "Microservices"],
            certificates: ["Oracle Certified Professional Java", "AWS Solutions Architect"],
            deadline: "2026-12-15",
            description: "Xây dựng các hệ thống Core Billing, tích hợp cổng thanh toán viễn thông với lưu lượng hàng triệu giao dịch/ngày."
        },
        {
            id: 3,
            title: "Node.js Backend Developer",
            company: "VNG Corporation",
            position_id: 1,
            location: "TP. Hồ Chí Minh",
            salary: "16 - 28 triệu VNĐ",
            experience_required: "1 - 3 năm",
            skills: ["JavaScript", "Node.js", "ExpressJS", "SQL", "RESTful API"],
            technologies: ["MongoDB", "Redis", "Docker", "RabbitMQ"],
            certificates: ["Node.js Application Developer", "MongoDB Associate"],
            deadline: "2026-11-25",
            description: "Phát triển hệ thống backend cho nền tảng mạng xã hội và giải trí trực tuyến."
        },
        {
            id: 4,
            title: "Golang Backend Developer",
            company: "Momo (M-Service)",
            position_id: 1,
            location: "TP. Hồ Chí Minh",
            salary: "20 - 40 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["Golang", "Microservices", "SQL", "Git", "Clean Architecture"],
            technologies: ["gRPC", "Redis", "Kafka", "Kubernetes"],
            certificates: ["AWS Certified Developer"],
            deadline: "2026-12-01",
            description: "Nâng cấp và duy trì các dịch vụ thanh toán QR, ví điện tử với yêu cầu tính sẵn sàng cao (High Availability)."
        },
        {
            id: 5,
            title: "Frontend Developer (ReactJS / TypeScript)",
            company: "Shopee Vietnam",
            position_id: 2,
            location: "TP. Hồ Chí Minh",
            salary: "18 - 32 triệu VNĐ",
            experience_required: "1 - 3 năm",
            skills: ["HTML5/CSS3", "JavaScript", "TypeScript", "ReactJS", "Redux"],
            technologies: ["Webpack", "Tailwind CSS", "Next.js", "Jest"],
            certificates: ["Meta Front-End Developer"],
            deadline: "2026-12-10",
            description: "Phát triển các tính năng giỏ hàng, thanh toán và chiến dịch khuyến mãi trên cổng thương mại điện tử Shopee."
        },
        {
            id: 6,
            title: "Web Frontend Developer (Vue.js / Bootstrap)",
            company: "Tiki Corporation",
            position_id: 2,
            location: "TP. Hồ Chí Minh",
            salary: "15 - 26 triệu VNĐ",
            experience_required: "1 - 2 năm",
            skills: ["HTML5/CSS3", "JavaScript", "VueJS", "Bootstrap", "Git"],
            technologies: ["Pinia", "Sass", "RESTful API", "Vite"],
            certificates: [],
            deadline: "2026-11-20",
            description: "Xây dựng dashboard quản trị cho người bán hàng và cổng tiếp nhận đơn hàng."
        },
        {
            id: 7,
            title: "Junior Frontend Developer (ReactJS/HTML/CSS)",
            company: "NashTech Vietnam",
            position_id: 2,
            location: "Hà Nội / TP.HCM",
            salary: "10 - 18 triệu VNĐ",
            experience_required: "Dưới 1 năm / Fresher",
            skills: ["HTML5/CSS3", "JavaScript", "ReactJS", "Bootstrap", "Git"],
            technologies: ["RESTful API", "CSS Modules", "NPM"],
            certificates: [],
            deadline: "2026-12-05",
            description: "Cơ hội cho sinh viên mới ra trường tham gia dự án phần mềm cho khách hàng châu Âu và Úc."
        },
        {
            id: 8,
            title: "Senior Frontend Engineer (Angular / TypeScript)",
            company: "KMS Technology",
            position_id: 2,
            location: "Đà Nẵng",
            salary: "25 - 45 triệu VNĐ",
            experience_required: "3+ năm",
            skills: ["TypeScript", "Angular", "RxJS", "HTML5/CSS3", "Unit Test"],
            technologies: ["NgRx", "SCSS", "CI/CD", "Karma"],
            certificates: [],
            deadline: "2026-12-20",
            description: "Chịu trách nhiệm kiến trúc frontend cho ứng dụng chăm sóc sức khỏe điện tử (Healthcare SaaS)."
        },
        {
            id: 9,
            title: "Fullstack Developer (Node.js & ReactJS)",
            company: "ZaloPay",
            position_id: 3,
            location: "TP. Hồ Chí Minh",
            salary: "22 - 38 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["JavaScript", "TypeScript", "ReactJS", "Node.js", "SQL"],
            technologies: ["PostgreSQL", "Docker", "Redis", "Next.js"],
            certificates: ["AWS Certified Developer"],
            deadline: "2026-11-30",
            description: "Xây dựng các mini-app trên nền tảng Zalo, tích hợp ví thanh toán và quản trị merchant."
        },
        {
            id: 10,
            title: "Fullstack Software Engineer (.NET & Angular)",
            company: "One Mount Group",
            position_id: 3,
            location: "Hà Nội",
            salary: "20 - 36 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["C#", ".NET Core", "Angular", "SQL", "Git"],
            technologies: ["SQL Server", "Docker", "Azure", "Microservices"],
            certificates: ["Microsoft Certified: Azure Developer Associate"],
            deadline: "2026-12-18",
            description: "Phát triển các giải pháp số hóa chuỗi cung ứng VinShop và bất động sản OneHousing."
        },
        {
            id: 11,
            title: "Fullstack Web Developer (Python & Vue.js)",
            company: "VNPT Information Technology",
            position_id: 3,
            location: "Hà Nội",
            salary: "15 - 25 triệu VNĐ",
            experience_required: "1 - 3 năm",
            skills: ["Python", "Django", "VueJS", "JavaScript", "SQL"],
            technologies: ["PostgreSQL", "Bootstrap", "Git", "Docker"],
            certificates: [],
            deadline: "2026-12-12",
            description: "Phát triển cổng thông tin hành chính công và các phần mềm dịch vụ giáo dục điện tử."
        },
        {
            id: 12,
            title: "Junior Data Analyst",
            company: "Techcombank",
            position_id: 4,
            location: "Hà Nội",
            salary: "14 - 22 triệu VNĐ",
            experience_required: "0 - 1 năm / Fresher",
            skills: ["SQL", "Python", "Power BI", "Excel nâng cao", "Phân tích dữ liệu"],
            technologies: ["Pandas", "Oracle DB", "Jupyter Notebook"],
            certificates: ["PL-300: Microsoft Power BI Data Analyst", "Google Data Analytics Certificate"],
            deadline: "2026-12-05",
            description: "Phân tích hành vi chi tiêu thẻ tín dụng, xây dựng các dashboard theo dõi chỉ số rủi ro tín dụng hàng tuần."
        },
        {
            id: 13,
            title: "BI Data Analyst (Tableau & SQL)",
            company: "VPBank",
            position_id: 4,
            location: "Hà Nội",
            salary: "18 - 30 triệu VNĐ",
            experience_required: "1 - 3 năm",
            skills: ["SQL", "Tableau", "Data Modeling", "Xác suất thống kê", "Python"],
            technologies: ["PostgreSQL", "Snowflake", "Excel"],
            certificates: ["Tableau Desktop Specialist"],
            deadline: "2026-12-25",
            description: "Xây dựng mô hình dữ liệu trực quan phục vụ khối Khách hàng Doanh nghiệp SME."
        },
        {
            id: 14,
            title: "Data Analyst - Product & Marketing",
            company: "Chợ Tốt (Carousell Group)",
            position_id: 4,
            location: "TP. Hồ Chí Minh",
            salary: "16 - 28 triệu VNĐ",
            experience_required: "1 - 2 năm",
            skills: ["SQL", "Python", "Google Analytics", "A/B Testing", "Trực quan hóa dữ liệu"],
            technologies: ["BigQuery", "Looker Studio", "Pandas"],
            certificates: ["Google Data Analytics Certificate"],
            deadline: "2026-11-28",
            description: "Đo lường hiệu quả các chiến dịch Marketing, phân tích phễu chuyển đổi người dùng trên app Chợ Tốt."
        },
        {
            id: 15,
            title: "DevOps Engineer (AWS & Kubernetes)",
            company: "FPT Software",
            position_id: 5,
            location: "Hà Nội",
            salary: "22 - 40 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD"],
            technologies: ["Terraform", "GitLab CI", "Prometheus", "Helm"],
            certificates: ["AWS Certified Solutions Architect", "CKA (Certified Kubernetes Administrator)"],
            deadline: "2026-12-30",
            description: "Vận hành hạ tầng Cloud cho các khách hàng tài chính quốc tế, đảm bảo uptime 99.9%."
        },
        {
            id: 16,
            title: "Cloud Infrastructure Engineer",
            company: "MB Bank",
            position_id: 5,
            location: "Hà Nội",
            salary: "20 - 38 triệu VNĐ",
            experience_required: "1 - 3 năm",
            skills: ["Linux", "Shell Scripting", "Docker", "CI/CD", "Mạng máy tính"],
            technologies: ["Jenkins", "Ansible", "Kubernetes", "Grafana"],
            certificates: ["Red Hat Certified System Administrator (RHCSA)", "AWS SysOps"],
            deadline: "2026-12-15",
            description: "Tự động hóa triển khai ứng dụng ngân hàng số MBBank, cấu hình cảnh báo và giám sát hệ thống tự động."
        },
        {
            id: 17,
            title: "Site Reliability Engineer (SRE / DevOps)",
            company: "VNG Corporation",
            position_id: 5,
            location: "TP. Hồ Chí Minh",
            salary: "25 - 45 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["Linux", "Python", "Docker", "Kubernetes", "Troubleshooting"],
            technologies: ["ELK Stack", "Prometheus", "Kafka", "GitOps"],
            certificates: ["CKA (Certified Kubernetes Administrator)"],
            deadline: "2026-12-10",
            description: "Duy trì tính sẵn sàng và khả năng chịu tải cho các game bom tấn và ứng dụng Zalo."
        },
        {
            id: 18,
            title: "Manual & Automation QA Tester",
            company: "KMS Technology",
            position_id: 6,
            location: "TP. Hồ Chí Minh",
            salary: "14 - 24 triệu VNĐ",
            experience_required: "1 - 2 năm",
            skills: ["Kiểm thử phần mềm", "Thiết kế Test Case", "Postman", "Selenium", "SQL"],
            technologies: ["Jira", "TestRail", "Java", "Git"],
            certificates: ["ISTQB Foundation Level (CTFL)"],
            deadline: "2026-12-05",
            description: "Thực hiện kiểm thử chức năng và phi chức năng, viết script tự động hóa kiểm thử hồi quy cho ứng dụng web."
        },
        {
            id: 19,
            title: "QC Tester (Fresher / Junior)",
            company: "FPT Information System",
            position_id: 6,
            location: "Hà Nội",
            salary: "9 - 15 triệu VNĐ",
            experience_required: "0 - 1 năm",
            skills: ["Kiểm thử phần mềm", "Tạo Test Case", "SQL cơ bản", "Kỹ năng giao tiếp"],
            technologies: ["Jira", "Postman", "Excel"],
            certificates: ["ISTQB Foundation Level (CTFL)"],
            deadline: "2026-11-20",
            description: "Hỗ trợ đội ngũ kiểm thử các phần mềm chính phủ điện tử, quản lý bệnh viện và giao thông thông minh."
        },
        {
            id: 20,
            title: "Senior Automation Test Engineer (Cypress / Playwright)",
            company: "Shopee Vietnam",
            position_id: 6,
            location: "TP. Hồ Chí Minh",
            salary: "25 - 40 triệu VNĐ",
            experience_required: "3+ năm",
            skills: ["Automation Testing", "JavaScript", "TypeScript", "CI/CD Integration", "API Testing"],
            technologies: ["Cypress", "Playwright", "Jenkins", "Docker"],
            certificates: ["ISTQB Advanced Level Test Automation Engineer"],
            deadline: "2026-12-28",
            description: "Thiết kế và duy trì framework kiểm thử tự động quy mô lớn cho hệ sinh thái Shopee."
        },
        {
            id: 21,
            title: "Flutter Mobile Developer",
            company: "Momo (M-Service)",
            position_id: 7,
            location: "TP. Hồ Chí Minh",
            salary: "16 - 30 triệu VNĐ",
            experience_required: "1 - 3 năm",
            skills: ["Flutter", "Dart", "RESTful API", "Git", "State Management (Bloc/Provider)"],
            technologies: ["Firebase", "SQLite", "GraphQL"],
            certificates: [],
            deadline: "2026-12-15",
            description: "Phát triển các module tiện ích mới trên siêu ứng dụng MoMo phục vụ hơn 30 triệu người dùng."
        },
        {
            id: 22,
            title: "React Native Developer",
            company: "Tiki Corporation",
            position_id: 7,
            location: "TP. Hồ Chí Minh",
            salary: "15 - 28 triệu VNĐ",
            experience_required: "1 - 2 năm",
            skills: ["React Native", "JavaScript", "TypeScript", "Redux", "Mobile UI"],
            technologies: ["Xcode", "Android Studio", "Firebase"],
            certificates: [],
            deadline: "2026-12-08",
            description: "Tối ưu hóa hiệu năng ứng dụng Tiki trên iOS và Android, cải thiện tốc độ load trang danh mục sản phẩm."
        },
        {
            id: 23,
            title: "iOS Native Developer (Swift)",
            company: "Viettel Digital",
            position_id: 7,
            location: "Hà Nội",
            salary: "20 - 35 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["Swift", "iOS SDK", "AutoLayout", "OOP", "Git"],
            technologies: ["CoreData", "Combine", "CocoaPods", "Fastlane"],
            certificates: ["Apple Certified Developer"],
            deadline: "2026-12-31",
            description: "Phát triển ứng dụng tài chính số Viettel Money phiên bản iOS native, bảo mật dữ liệu cấp độ ngân hàng."
        },
        {
            id: 24,
            title: "Android Native Developer (Kotlin)",
            company: "VNPT Technology",
            position_id: 7,
            location: "Hà Nội",
            salary: "16 - 28 triệu VNĐ",
            experience_required: "1 - 3 năm",
            skills: ["Kotlin", "Android SDK", "Jetpack Compose", "Coroutines", "MVVM"],
            technologies: ["Retrofit", "Room DB", "Dagger Hilt"],
            certificates: ["Google Associate Android Developer"],
            deadline: "2026-12-10",
            description: "Xây dựng ứng dụng nhà thông minh (Smart Home IoT) kết nối thiết bị phần cứng của VNPT."
        },
        {
            id: 25,
            title: "AI / Machine Learning Engineer",
            company: "VinAI Research",
            position_id: 8,
            location: "Hà Nội",
            salary: "25 - 50 triệu VNĐ",
            experience_required: "1 - 3 năm",
            skills: ["Python", "PyTorch", "Toán giải tích & Đại số", "Machine Learning", "Git"],
            technologies: ["OpenCV", "CUDA", "Docker", "Linux"],
            certificates: ["DeepLearning.AI Machine Learning Specialization", "AWS Certified Machine Learning"],
            deadline: "2026-12-25",
            description: "Nghiên cứu và huấn luyện các mô hình thị giác máy tính cho hệ thống lái xe tự hành VinFast."
        },
        {
            id: 26,
            title: "NLP Engineer (Natural Language Processing)",
            company: "Zalo AI Lab",
            position_id: 8,
            location: "TP. Hồ Chí Minh",
            salary: "22 - 42 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["Python", "NLP", "PyTorch", "Transformers", "Xử lý văn bản tiếng Việt"],
            technologies: ["HuggingFace", "BERT", "FastAPI", "ONNX"],
            certificates: ["DeepLearning.AI Deep Learning Specialization"],
            deadline: "2026-12-20",
            description: "Phát triển trợ lý giọng nói Kiki, mô hình tóm tắt văn bản và chatbot thông minh trên hệ sinh thái Zalo."
        },
        {
            id: 27,
            title: "Computer Vision Engineer",
            company: "FPT Software (FPT AI)",
            position_id: 8,
            location: "Quy Nhơn / Hà Nội",
            salary: "20 - 38 triệu VNĐ",
            experience_required: "1 - 3 năm",
            skills: ["Python", "Computer Vision", "TensorFlow", "PyTorch", "OpenCV"],
            technologies: ["YOLO", "Docker", "Triton Server"],
            certificates: [],
            deadline: "2026-12-15",
            description: "Xây dựng giải pháp định danh khách hàng điện tử (eKYC) và nhận diện tài liệu OCR cho ngân hàng."
        },
        {
            id: 28,
            title: "Backend Developer (Node.js & AWS Serverless)",
            company: "TymeX Vietnam",
            position_id: 1,
            location: "TP. Hồ Chí Minh",
            salary: "20 - 35 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["JavaScript", "TypeScript", "Node.js", "RESTful API", "SQL"],
            technologies: ["AWS Lambda", "DynamoDB", "Docker", "Jest"],
            certificates: ["AWS Certified Cloud Practitioner"],
            deadline: "2026-11-30",
            description: "Phát triển nền tảng ngân hàng số đa quốc gia (Digital Banking) phục vụ hàng triệu khách hàng Nam Phi & Philippines."
        },
        {
            id: 29,
            title: "Frontend Developer (ReactJS & WebSockets)",
            company: "SSI Securities (Chứng khoán SSI)",
            position_id: 2,
            location: "Hà Nội",
            salary: "18 - 32 triệu VNĐ",
            experience_required: "2+ năm",
            skills: ["HTML5/CSS3", "JavaScript", "ReactJS", "TypeScript", "WebSockets"],
            technologies: ["Chart.js", "Redux Toolkit", "Ant Design", "TradingView API"],
            certificates: [],
            deadline: "2026-12-18",
            description: "Xây dựng bảng giá chứng khoán thời gian thực tốc độ mili-giây, biểu đồ kỹ thuật chuyên sâu."
        },
        {
            id: 30,
            title: "Junior Data Analyst - Operations",
            company: "Giao Hàng Nhanh (GHN)",
            position_id: 4,
            location: "TP. Hồ Chí Minh",
            salary: "12 - 18 triệu VNĐ",
            experience_required: "0 - 1 năm",
            skills: ["SQL", "Excel nâng cao", "Power BI", "Phân tích dữ liệu", "Python"],
            technologies: ["Google Sheets", "PostgreSQL", "Pandas"],
            certificates: ["Google Data Analytics Certificate"],
            deadline: "2026-12-05",
            description: "Phân tích thời gian giao hàng, tối ưu hóa cung đường bưu tá và năng suất các kho bãi toàn quốc."
        }
    ],

    // 3. HỒ SƠ SINH VIÊN MẪU (ĐẦY ĐỦ 4 PHẦN)
    profile: {
        personal_info: {
            full_name: "Nguyễn Văn An",
            student_code: "20205012",
            email: "an.nguyen20@sis.hust.edu.vn",
            phone: "0987654321",
            university: "Đại học Bách Khoa Hà Nội",
            faculty: "Trường Công nghệ Thông tin & Truyền thông",
            major: "Khoa học Máy tính",
            academic_year: "K65 (2020 - 2025)",
            gpa: "3.42",
            target_position_id: 1, // Mặc định hướng Backend Developer
            bio: "Sinh viên năm cuối đam mê phát triển hệ thống backend phân tán, có kiến thức vững chắc về Python, SQL, RESTful API và Docker."
        },
        // Phần 1: Học phần đã học
        courses: [
            { id: 1, code: "IT3011", name: "Cấu trúc dữ liệu và giải thuật", credits: 3, grade: "A", term: "2022.1" },
            { id: 2, code: "IT3080", name: "Mạng máy tính", credits: 3, grade: "B+", term: "2022.2" },
            { id: 3, code: "IT3090", name: "Cơ sở dữ liệu", credits: 3, grade: "A", term: "2022.2" },
            { id: 4, code: "IT4010", name: "Lập trình Web", credits: 3, grade: "A", term: "2023.1" },
            { id: 5, code: "IT4060", name: "Lập trình mạng và hệ thống phân tán", credits: 3, grade: "B+", term: "2023.2" },
            { id: 6, code: "IT4409", name: "Kiểm thử và đảm bảo chất lượng phần mềm", credits: 2, grade: "A", term: "2023.2" }
        ],
        // Phần 2: Kỹ năng cá nhân (mức độ từ 1 đến 5)
        skills: [
            { id: 1, name: "Python", level: 4, category: "Ngôn ngữ lập trình", note: "Thành thạo lập trình OOP, xử lý cấu trúc dữ liệu" },
            { id: 2, name: "SQL", level: 4, category: "Cơ sở dữ liệu", note: "Viết truy vấn phức tạp, tối ưu chỉ mục index" },
            { id: 3, name: "Flask", level: 3, category: "Framework / Thư viện", note: "Xây dựng REST API, tích hợp SQLAlchemy" },
            { id: 4, name: "Git", level: 4, category: "Công cụ phát triển", note: "Sử dụng thành thạo Git branch, PR, merge rebase" },
            { id: 5, name: "HTML5/CSS3", level: 3, category: "Frontend cơ bản", note: "Cắt giao diện chuẩn responsive, Bootstrap" },
            { id: 6, name: "JavaScript", level: 3, category: "Ngôn ngữ lập trình", note: "ES6+, DOM, Async/Await" },
            { id: 7, name: "Docker", level: 2, category: "DevOps & Môi trường", note: "Biết viết Dockerfile cơ bản, docker-compose" }
        ],
        // Phần 3: Chứng chỉ
        certificates: [
            { id: 1, name: "TOEIC 785", organization: "ETS", issue_date: "2023-08-15", expiry_date: "2025-08-15", credential_url: "https://www.iigvietnam.com" },
            { id: 2, name: "Python PCEP Certified Entry-Level", organization: "Python Institute", issue_date: "2023-11-20", expiry_date: "", credential_url: "https://pythoninstitute.org" },
            { id: 3, name: "SQL for Data Science", organization: "Coursera (UC Davis)", issue_date: "2024-02-10", expiry_date: "", credential_url: "https://coursera.org" }
        ],
        // Phần 4: Kinh nghiệm & Dự án
        experiences: [
            {
                id: 1,
                title: "Thực tập sinh Backend (Python Intern)",
                company: "Công ty Cổ phần Công nghệ ABC",
                role_type: "Thực tập sinh",
                start_date: "2024-06-01",
                end_date: "2024-09-30",
                description: "Tham gia viết API xác thực người dùng bằng JWT, tối ưu hóa câu truy vấn SQL giảm 35% thời gian phản hồi."
            },
            {
                id: 2,
                title: "Trưởng nhóm Đồ án môn học Web Bán hàng",
                company: "Dự án cá nhân / Nhóm sinh viên",
                role_type: "Đồ án",
                start_date: "2023-09-01",
                end_date: "2023-12-20",
                description: "Thiết kế kiến trúc MVC bằng Flask, cơ sở dữ liệu PostgreSQL, tích hợp cổng thanh toán Sandbox VNPAY."
            }
        ]
    },

    // 4. KẾ HOẠCH HỌC TẬP & PHÁT TRIỂN
    plans: [
        {
            id: 1,
            title: "Học và thực hành chuyên sâu Docker & Containerization",
            category: "Kỹ năng thiếu (Backend)",
            type: "skill",
            status: "doing", // todo | doing | done
            target_date: "2026-11-30",
            note: "Làm chủ viết Multi-stage Dockerfile, Docker Compose và kết nối mạng giữa các container."
        },
        {
            id: 2,
            title: "Ôn thi chứng chỉ AWS Certified Cloud Practitioner (CLF-C02)",
            category: "Chứng chỉ nghề nghiệp",
            type: "certificate",
            status: "doing",
            target_date: "2026-12-25",
            note: "Học qua khóa học Stephane Maarek trên Udemy, luyện 6 đề thi thử."
        },
        {
            id: 3,
            title: "Nghiên cứu kiến trúc Microservices và gRPC với Go",
            category: "Nâng cao kỹ năng",
            type: "skill",
            status: "todo",
            target_date: "2027-01-15",
            note: "Đọc sách Designing Data-Intensive Applications của Martin Kleppmann."
        },
        {
            id: 4,
            title: "Xây dựng đồ án cá nhân: RESTful API mạng xã hội thu nhỏ",
            category: "Kinh nghiệm / Portfolio",
            type: "project",
            status: "done",
            target_date: "2026-09-15",
            note: "Hoàn thành API với Flask, Redis caching, Celery background worker và PostgreSQL."
        },
        {
            id: 5,
            title: "Thực hành cấu hình CI/CD Pipeline bằng GitHub Actions",
            category: "Kỹ năng thiếu (DevOps)",
            type: "skill",
            status: "todo",
            target_date: "2026-12-10",
            note: "Tự động chạy pytest và deploy container lên AWS EC2 khi push code."
        }
    ],

    // 5. THỐNG KÊ KỸ NĂNG THEO VỊ TRÍ NGHỀ NGHIỆP
    statistics: {
        1: { // Backend Developer
            position_name: "Lập trình viên Backend (Backend Developer)",
            total_jobs_analyzed: 5,
            top_skills: [
                { name: "SQL", count: 28, percentage: 93 },
                { name: "Python", count: 25, percentage: 83 },
                { name: "RESTful API", count: 24, percentage: 80 },
                { name: "Git", count: 23, percentage: 76 },
                { name: "Java", count: 20, percentage: 66 },
                { name: "Node.js", count: 18, percentage: 60 },
                { name: "Docker", count: 17, percentage: 56 },
                { name: "OOP", count: 15, percentage: 50 }
            ],
            technologies: [
                { name: "PostgreSQL", count: 19, percentage: 63 },
                { name: "Redis", count: 16, percentage: 53 },
                { name: "Docker", count: 15, percentage: 50 },
                { name: "Spring Boot", count: 12, percentage: 40 },
                { name: "Kafka", count: 10, percentage: 33 },
                { name: "FastAPI / Flask", count: 9, percentage: 30 }
            ],
            certificates: [
                { name: "AWS Certified Cloud Practitioner", count: 12, level: "Cơ bản" },
                { name: "AWS Solutions Architect Associate", count: 9, level: "Trung cấp" },
                { name: "Oracle Certified Professional Java", count: 7, level: "Chuyên sâu" },
                { name: "Python Institute PCAP/PCEP", count: 6, level: "Cơ bản" }
            ]
        },
        2: { // Frontend Developer
            position_name: "Lập trình viên Frontend (Frontend Developer)",
            total_jobs_analyzed: 5,
            top_skills: [
                { name: "JavaScript", count: 29, percentage: 96 },
                { name: "HTML5/CSS3", count: 28, percentage: 93 },
                { name: "ReactJS", count: 24, percentage: 80 },
                { name: "TypeScript", count: 21, percentage: 70 },
                { name: "Git", count: 20, percentage: 66 },
                { name: "Responsive Design", count: 19, percentage: 63 },
                { name: "Bootstrap / Tailwind", count: 18, percentage: 60 },
                { name: "VueJS", count: 12, percentage: 40 }
            ],
            technologies: [
                { name: "ReactJS", count: 22, percentage: 73 },
                { name: "Next.js", count: 14, percentage: 46 },
                { name: "Tailwind CSS", count: 13, percentage: 43 },
                { name: "VueJS", count: 11, percentage: 36 },
                { name: "Vite / Webpack", count: 10, percentage: 33 },
                { name: "Redux / Pinia", count: 8, percentage: 26 }
            ],
            certificates: [
                { name: "Meta Front-End Developer Professional Certificate", count: 11, level: "Toàn diện" },
                { name: "W3Schools Certified Front-End Developer", count: 5, level: "Cơ bản" }
            ]
        },
        3: { // Fullstack Developer
            position_name: "Lập trình viên Fullstack (Fullstack Developer)",
            total_jobs_analyzed: 3,
            top_skills: [
                { name: "JavaScript / TypeScript", count: 25, percentage: 89 },
                { name: "Node.js", count: 22, percentage: 78 },
                { name: "ReactJS", count: 20, percentage: 71 },
                { name: "SQL", count: 19, percentage: 67 },
                { name: "RESTful API", count: 18, percentage: 64 },
                { name: "Docker", count: 16, percentage: 57 }
            ],
            technologies: [
                { name: "PostgreSQL", count: 16, percentage: 57 },
                { name: "Docker", count: 14, percentage: 50 },
                { name: "Next.js", count: 12, percentage: 42 },
                { name: "MongoDB", count: 10, percentage: 35 }
            ],
            certificates: [
                { name: "AWS Certified Developer Associate", count: 8, level: "Trung cấp" },
                { name: "Microsoft Certified: Azure Developer", count: 6, level: "Trung cấp" }
            ]
        },
        4: { // Data Analyst
            position_name: "Chuyên viên Phân tích Dữ liệu (Data Analyst)",
            total_jobs_analyzed: 4,
            top_skills: [
                { name: "SQL", count: 27, percentage: 96 },
                { name: "Python", count: 24, percentage: 85 },
                { name: "Power BI", count: 22, percentage: 78 },
                { name: "Excel nâng cao", count: 20, percentage: 71 },
                { name: "Xác suất thống kê", count: 18, percentage: 64 },
                { name: "Tableau", count: 15, percentage: 53 }
            ],
            technologies: [
                { name: "Power BI", count: 20, percentage: 71 },
                { name: "Pandas / NumPy", count: 18, percentage: 64 },
                { name: "Tableau", count: 14, percentage: 50 },
                { name: "BigQuery / Snowflake", count: 11, percentage: 39 }
            ],
            certificates: [
                { name: "Google Data Analytics Professional Certificate", count: 15, level: "Toàn diện" },
                { name: "PL-300: Microsoft Power BI Data Analyst", count: 12, level: "Chuyên môn" },
                { name: "Tableau Desktop Specialist", count: 7, level: "Cơ bản" }
            ]
        },
        5: { // DevOps Engineer
            position_name: "Kỹ sư DevOps & Cloud (DevOps Engineer)",
            total_jobs_analyzed: 3,
            top_skills: [
                { name: "Linux", count: 26, percentage: 92 },
                { name: "Docker", count: 25, percentage: 89 },
                { name: "CI/CD", count: 24, percentage: 85 },
                { name: "Kubernetes", count: 22, percentage: 78 },
                { name: "AWS / Cloud", count: 21, percentage: 75 },
                { name: "Shell Scripting", count: 17, percentage: 60 }
            ],
            technologies: [
                { name: "Kubernetes (K8s)", count: 20, percentage: 71 },
                { name: "Terraform", count: 18, percentage: 64 },
                { name: "GitLab CI / Jenkins", count: 17, percentage: 60 },
                { name: "Prometheus & Grafana", count: 15, percentage: 53 }
            ],
            certificates: [
                { name: "AWS Certified Solutions Architect", count: 14, level: "Trung cấp" },
                { name: "CKA: Certified Kubernetes Administrator", count: 11, level: "Chuyên sâu" },
                { name: "RHCSA: Red Hat Certified System Administrator", count: 6, level: "Cơ bản" }
            ]
        },
        6: { // QA / Tester
            position_name: "Kỹ sư Kiểm thử Phần mềm (QA / QC Tester)",
            total_jobs_analyzed: 3,
            top_skills: [
                { name: "Kiểm thử phần mềm", count: 26, percentage: 92 },
                { name: "Thiết kế Test Case", count: 25, percentage: 89 },
                { name: "Postman / API Testing", count: 23, percentage: 82 },
                { name: "SQL cơ bản", count: 20, percentage: 71 },
                { name: "Selenium", count: 15, percentage: 53 }
            ],
            technologies: [
                { name: "Jira / Confluence", count: 22, percentage: 78 },
                { name: "Postman", count: 21, percentage: 75 },
                { name: "Selenium WebDriver", count: 14, percentage: 50 },
                { name: "Cypress / Playwright", count: 10, percentage: 35 }
            ],
            certificates: [
                { name: "ISTQB Certified Tester Foundation Level (CTFL)", count: 21, level: "Tiêu chuẩn ngành" },
                { name: "ISTQB Test Automation Engineer", count: 6, level: "Nâng cao" }
            ]
        },
        7: { // Mobile Developer
            position_name: "Lập trình viên Ứng dụng Di động (Mobile App Developer)",
            total_jobs_analyzed: 4,
            top_skills: [
                { name: "Flutter / Dart", count: 21, percentage: 75 },
                { name: "React Native", count: 19, percentage: 67 },
                { name: "RESTful API", count: 18, percentage: 64 },
                { name: "Git", count: 17, percentage: 60 },
                { name: "Swift / Kotlin", count: 15, percentage: 53 }
            ],
            technologies: [
                { name: "Flutter", count: 18, percentage: 64 },
                { name: "Firebase", count: 16, percentage: 57 },
                { name: "React Native", count: 15, percentage: 53 },
                { name: "Android Studio & Xcode", count: 14, percentage: 50 }
            ],
            certificates: [
                { name: "Google Associate Android Developer", count: 5, level: "Chuyên môn" },
                { name: "Meta React Native Specialization", count: 4, level: "Toàn diện" }
            ]
        },
        8: { // AI / ML Engineer
            position_name: "Kỹ sư Trí tuệ Nhân tạo & Học máy (AI / ML Engineer)",
            total_jobs_analyzed: 3,
            top_skills: [
                { name: "Python", count: 28, percentage: 96 },
                { name: "PyTorch", count: 23, percentage: 82 },
                { name: "Toán & Thống kê", count: 21, percentage: 75 },
                { name: "Machine Learning", count: 20, percentage: 71 },
                { name: "Deep Learning", count: 18, percentage: 64 },
                { name: "Computer Vision / NLP", count: 17, percentage: 60 }
            ],
            technologies: [
                { name: "PyTorch", count: 21, percentage: 75 },
                { name: "TensorFlow", count: 15, percentage: 53 },
                { name: "OpenCV", count: 14, percentage: 50 },
                { name: "HuggingFace Transformers", count: 12, percentage: 42 }
            ],
            certificates: [
                { name: "DeepLearning.AI Deep Learning Specialization", count: 14, level: "Tiêu chuẩn" },
                { name: "AWS Certified Machine Learning - Specialty", count: 7, level: "Nâng cao" }
            ]
        }
    }
};

// Đảm bảo MockData sẵn sàng trên Window
if (typeof window !== 'undefined') {
    window.MockData = MockData;
}
