/**
 * mock_data.js - Dữ liệu giả lập cho 5 module frontend
 * Giúp giao diện hoạt động hoàn chỉnh độc lập trong lúc chờ Backend Flask + SQLite
 */

const MockData = {
    // ==========================================
    // MODULE 1: HỒ SƠ SINH VIÊN
    // ==========================================
    profile: {
        personal_info: {
            full_name: "Nguyễn Văn An",
            student_code: "21020001",
            email: "an.nguyen@sinhvien.edu.vn",
            phone: "0912345678",
            major: "Công nghệ thông tin",
            university: "Đại học Công nghệ",
            gpa: 3.45,
            target_position_id: 1 // Vị trí mong muốn: Backend Developer
        },
        courses: [
            { id: 1, code: "INT2204", name: "Lập trình nâng cao (C/C++)", credits: 3, grade: "A", semester: "Học kỳ 1 - 2022" },
            { id: 2, code: "INT2209", name: "Cơ sở dữ liệu", credits: 3, grade: "B+", semester: "Học kỳ 2 - 2022" },
            { id: 3, code: "INT2215", name: "Lập trình web", credits: 3, grade: "A", semester: "Học kỳ 1 - 2023" },
            { id: 4, code: "INT3105", name: "Cấu trúc dữ liệu và giải thuật", credits: 4, grade: "A", semester: "Học kỳ 1 - 2023" },
            { id: 5, code: "INT3306", name: "Phát triển ứng dụng Web nâng cao", credits: 3, grade: "B+", semester: "Học kỳ 2 - 2023" }
        ],
        skills: [
            { id: 1, name: "Python", category: "Ngôn ngữ", level: "Thành thạo" },
            { id: 2, name: "JavaScript", category: "Ngôn ngữ", level: "Khá" },
            { id: 3, name: "SQL", category: "Cơ sở dữ liệu", level: "Thành thạo" },
            { id: 4, name: "Flask", category: "Framework", level: "Khá" },
            { id: 5, name: "Git", category: "Công cụ", level: "Thành thạo" },
            { id: 6, name: "HTML/CSS", category: "Frontend", level: "Khá" }
        ],
        certificates: [
            { id: 1, name: "IELTS 6.5", issuer: "IDP", issue_date: "2023-06-15", url: "https://example.com/cert/1" },
            { id: 2, name: "Python for Everybody", issuer: "Coursera / UMich", issue_date: "2023-09-20", url: "https://coursera.org/verify/xyz" }
        ],
        experiences: [
            { id: 1, title: "Thực tập sinh Python Backend", organization: "Công ty Công nghệ FPT", start_date: "2023-11-01", end_date: "2024-02-28", description: "Hỗ trợ xây dựng API bằng Flask, truy vấn cơ sở dữ liệu SQLite/PostgreSQL, viết unit test." },
            { id: 2, title: "Trưởng nhóm Dự án Web Quản lý thư viện", organization: "Đồ án môn học", start_date: "2023-08-15", end_date: "2023-10-30", description: "Thiết kế kiến trúc MVC, tích hợp xác thực tài khoản và phân quyền người dùng." }
        ]
    },

    // ==========================================
    // MODULE 2: VỊ TRÍ NGHỀ NGHIỆP & TIN TUYỂN DỤNG
    // ==========================================
    positions: [
        { id: 1, code: "BACKEND_DEV", name: "Lập trình viên Backend (Python/Java/NodeJS)", job_count: 42 },
        { id: 2, code: "FRONTEND_DEV", name: "Lập trình viên Frontend (React/Vue/HTML/CSS)", job_count: 38 },
        { id: 3, code: "FULLSTACK_DEV", name: "Lập trình viên Fullstack", job_count: 27 },
        { id: 4, code: "DATA_ANALYST", name: "Chuyên viên phân tích dữ liệu (Data Analyst)", job_count: 21 },
        { id: 5, code: "DEVOPS_ENG", name: "Kỹ sư DevOps / Cloud", job_count: 15 }
    ],

    jobs: [
        {
            id: 1,
            title: "Lập trình viên Backend Python (Junior/Fresher)",
            company: "VNG Corporation",
            position_id: 1,
            position_name: "Lập trình viên Backend",
            location: "Hà Nội",
            salary: "12,000,000 - 18,000,000 VNĐ",
            skills_required: ["Python", "Flask", "SQL", "Docker", "Git", "RESTful API"],
            experience_level: "Fresher / Dưới 1 năm",
            created_at: "2026-03-20",
            source_url: "https://topcv.vn/job/1"
        },
        {
            id: 2,
            title: "Junior Backend Developer (Node.js/Python)",
            company: "FPT Software",
            position_id: 1,
            position_name: "Lập trình viên Backend",
            location: "Đà Nẵng",
            salary: "10,000,000 - 16,000,000 VNĐ",
            skills_required: ["Python", "SQL", "PostgreSQL", "Git", "Redis", "Linux"],
            experience_level: "Fresher / Dưới 1 năm",
            created_at: "2026-03-18",
            source_url: "https://itviec.com/job/2"
        },
        {
            id: 3,
            title: "Frontend Developer (HTML/CSS/JS, React)",
            company: "Tiki Tech",
            position_id: 2,
            position_name: "Lập trình viên Frontend",
            location: "TP. Hồ Chí Minh",
            salary: "14,000,000 - 20,000,000 VNĐ",
            skills_required: ["HTML/CSS", "JavaScript", "React", "Bootstrap", "Git", "Responsive Web"],
            experience_level: "1 - 2 năm kinh nghiệm",
            created_at: "2026-03-22",
            source_url: "https://topcv.vn/job/3"
        },
        {
            id: 4,
            title: "Data Analyst Fresher",
            company: "Shopee Vietnam",
            position_id: 4,
            position_name: "Chuyên viên phân tích dữ liệu",
            location: "Hà Nội",
            salary: "12,000,000 - 17,000,000 VNĐ",
            skills_required: ["SQL", "Python", "Power BI", "Excel", "Data Visualization", "Thống kê"],
            experience_level: "Fresher",
            created_at: "2026-03-23",
            source_url: "https://itviec.com/job/4"
        },
        {
            id: 5,
            title: "DevOps Engineer Fresher/Junior",
            company: "Viettel Digital",
            position_id: 5,
            position_name: "Kỹ sư DevOps / Cloud",
            location: "Hà Nội",
            salary: "15,000,000 - 22,000,000 VNĐ",
            skills_required: ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS", "Python"],
            experience_level: "Dưới 1 năm",
            created_at: "2026-03-24",
            source_url: "https://topcv.vn/job/5"
        }
    ],

    // ==========================================
    // MODULE 3: THỐNG KÊ KỸ NĂNG THEO VỊ TRÍ (CHART.JS)
    // ==========================================
    statistics: {
        // ID 1: Backend Dev
        1: {
            top_skills: [
                { name: "SQL / RDBMS", count: 38, percentage: 90 },
                { name: "Python / Java / C#", count: 35, percentage: 83 },
                { name: "RESTful API", count: 32, percentage: 76 },
                { name: "Git", count: 30, percentage: 71 },
                { name: "Docker", count: 26, percentage: 62 },
                { name: "Redis / Caching", count: 18, percentage: 43 },
                { name: "Linux cơ bản", count: 16, percentage: 38 },
                { name: "Microservices", count: 12, percentage: 29 }
            ],
            top_certificates: [
                { name: "AWS Certified Cloud Practitioner / Solutions Architect", count: 19 },
                { name: "IELTS 6.0+ / TOEIC 650+", count: 16 },
                { name: "Oracle Certified Professional: Java", count: 8 },
                { name: "Python Institute (PCAP)", count: 7 }
            ],
            experience_distribution: {
                "Fresher / Thực tập": 35,
                "Junior (1-2 năm)": 45,
                "Middle (2-4 năm)": 20
            }
        },
        // ID 2: Frontend Dev
        2: {
            top_skills: [
                { name: "JavaScript (ES6+)", count: 36, percentage: 95 },
                { name: "HTML5 / CSS3", count: 35, percentage: 92 },
                { name: "React / Vue", count: 30, percentage: 79 },
                { name: "Bootstrap / Tailwind", count: 26, percentage: 68 },
                { name: "Git", count: 24, percentage: 63 },
                { name: "REST API Integration", count: 22, percentage: 58 },
                { name: "TypeScript", count: 19, percentage: 50 }
            ],
            top_certificates: [
                { name: "Meta Front-End Developer Certificate", count: 14 },
                { name: "IELTS / TOEIC", count: 12 },
                { name: "FreeCodeCamp Responsive Web Design", count: 9 }
            ],
            experience_distribution: {
                "Fresher / Thực tập": 40,
                "Junior (1-2 năm)": 45,
                "Middle (2-4 năm)": 15
            }
        }
    },

    // ==========================================
    // MODULE 4: KẾT QUẢ SO SÁNH ĐỘ PHÙ HỢP (%)
    // ==========================================
    comparison: {
        target_position: "Lập trình viên Backend (Python)",
        diem_phu_hop: 72,
        ky_nang_co: ["Python", "Flask", "SQL"],
        ky_nang_thieu: ["Docker", "Git nâng cao"],
        tong_so_ky_nang: 5,
        ghi_chu: "Bạn đã đáp ứng tốt các kỹ năng nền tảng. Cần bổ sung Docker và Git nâng cao để nâng điểm phù hợp lên trên 85%."
    },
    // Dữ liệu so sánh mở rộng theo từng vị trí (khi chọn từ dropdown)
    comparison_by_position: {
        1: {
            target_position: "Lập trình viên Backend (Python)",
            diem_phu_hop: 72,
            ky_nang_co: ["Python", "Flask", "SQL"],
            ky_nang_thieu: ["Docker", "Git nâng cao"],
            tong_so_ky_nang: 5,
            ghi_chu: "Bạn đã đáp ứng tốt các kỹ năng nền tảng. Cần bổ sung Docker và Git nâng cao để nâng điểm phù hợp lên trên 85%."
        },
        2: {
            target_position: "Lập trình viên Frontend (React/Vue)",
            diem_phu_hop: 55,
            ky_nang_co: ["HTML/CSS", "JavaScript", "Git"],
            ky_nang_thieu: ["React", "TypeScript", "Tailwind CSS"],
            tong_so_ky_nang: 6,
            ghi_chu: "Bạn có kiến thức web căn bản nhưng thiếu framework hiện đại (React/Vue) và TypeScript."
        },
        3: {
            target_position: "Lập trình viên Fullstack",
            diem_phu_hop: 60,
            ky_nang_co: ["Python", "Flask", "SQL", "HTML/CSS"],
            ky_nang_thieu: ["React/Vue", "Docker", "CI/CD"],
            tong_so_ky_nang: 7,
            ghi_chu: "Cần hoàn thiện cả mảng frontend hiện đại và kiến thức DevOps triển khai ứng dụng."
        },
        4: {
            target_position: "Chuyên viên phân tích dữ liệu (Data Analyst)",
            diem_phu_hop: 65,
            ky_nang_co: ["Python", "SQL"],
            ky_nang_thieu: ["Power BI", "Pandas", "Thống kê chuyên sâu"],
            tong_so_ky_nang: 5,
            ghi_chu: "Nền tảng SQL và Python rất thích hợp, cần luyện thêm các công cụ trực quan hóa như Power BI."
        },
        5: {
            target_position: "Kỹ sư DevOps / Cloud",
            diem_phu_hop: 35,
            ky_nang_co: ["Git", "Python cơ bản"],
            ky_nang_thieu: ["Linux nâng cao", "Docker", "Kubernetes", "CI/CD", "AWS/GCP"],
            tong_so_ky_nang: 7,
            ghi_chu: "Vị trí này đòi hỏi nhiều kiến thức về hạ tầng, hệ điều hành và công cụ tự động hóa."
        }
    },

    // ==========================================
    // MODULE 5: KẾ HOẠCH PHÁT TRIỂN & ROADMAP
    // ==========================================
    roadmap: {
        total_items: 7,
        completed_items: 3,
        progress_percentage: 43,
        tasks: [
            { id: 1, title: "Nắm vững Docker cơ bản và Docker Compose", type: "Kỹ năng", target_date: "2026-04-15", is_completed: true, priority: "Cao", course_ref: "Docker for Beginners (Udemy)" },
            { id: 2, title: "Xây dựng dự án CRUD chuẩn RESTful API với Flask & SQLite", type: "Dự án", target_date: "2026-04-30", is_completed: true, priority: "Cao", course_ref: "Đồ án cá nhân" },
            { id: 3, title: "Ôn tập và lấy chứng chỉ TOEIC 700+ hoặc nâng cấp IELTS", type: "Chứng chỉ", target_date: "2026-05-15", is_completed: true, priority: "Trung bình", course_ref: "Chứng chỉ ngoại ngữ" },
            { id: 4, title: "Học cơ chế Redis Caching và áp dụng vào dự án Backend", type: "Kỹ năng", target_date: "2026-05-30", is_completed: false, priority: "Trung bình", course_ref: "Tài liệu Redis.io" },
            { id: 5, title: "Làm quen với thao tác dòng lệnh Linux & VPS cơ bản", type: "Kỹ năng", target_date: "2026-06-15", is_completed: false, priority: "Trung bình", course_ref: "Linux Journey" },
            { id: 6, title: "Ôn tập kiến thức phỏng vấn thuật toán (LeetCode Top 50 Easy/Medium)", type: "Luyện phỏng vấn", target_date: "2026-06-30", is_completed: false, priority: "Cao", course_ref: "LeetCode / HackerRank" },
            { id: 7, title: "Đăng ký thi chứng chỉ AWS Certified Cloud Practitioner", type: "Chứng chỉ", target_date: "2026-07-20", is_completed: false, priority: "Khuyến khích", course_ref: "AWS Skill Builder" }
        ]
    }
};
