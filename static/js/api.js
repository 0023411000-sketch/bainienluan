/**
 * api.js - Lớp giao tiếp API giữa Frontend và Backend Flask
 *
 * CÁCH CHUYỂN SANG BACKEND THẬT:
 * Chỉ cần đổi giá trị `USE_MOCK: false` ở bên dưới. Toàn bộ các trang sẽ tự động gọi HTTP fetch đến Backend!
 */

const API_CONFIG = {
    USE_MOCK: true,              // <<-- ĐỔI SANG false ĐỂ CHUYỂN SANG DÙNG API THẬT
    BASE_URL: '/api',            // Tiền tố URL backend Flask
    MOCK_DELAY_MS: 300           // Giả lập độ trễ mạng khi dùng mock để trải nghiệm chân thực
};

/**
 * Hàm trợ giúp gọi fetch API chuẩn hóa
 */
async function fetchAPI(endpoint, method = 'GET', body = null) {
    if (typeof showLoading === 'function') showLoading(true);
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        if (body instanceof FormData) {
            delete options.headers['Content-Type']; // Để trình duyệt tự đặt multipart/form-data boundary
            options.body = body;
        } else if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `Lỗi máy chủ (${response.status})`);
        }
        return await response.json();
    } catch (error) {
        console.error(`[API Error] ${method} ${endpoint}:`, error);
        if (typeof showAlert === 'function') {
            showAlert(error.message || 'Không thể kết nối đến máy chủ API', 'danger');
        }
        throw error;
    } finally {
        if (typeof showLoading === 'function') showLoading(false);
    }
}

/**
 * Trợ giúp tạo độ trễ giả lập cho Mock
 */
function mockDelay(result) {
    return new Promise(resolve => {
        if (typeof showLoading === 'function') showLoading(true);
        setTimeout(() => {
            if (typeof showLoading === 'function') showLoading(false);
            resolve(JSON.parse(JSON.stringify(result)));
        }, API_CONFIG.MOCK_DELAY_MS);
    });
}

// ==========================================
// ĐỐI TƯỢNG API CHÍNH
// ==========================================
const API = {
    // ------------------------------------------
    // 1. MODULE HỒ SƠ SINH VIÊN
    // ------------------------------------------
    getProfile: async () => {
        if (API_CONFIG.USE_MOCK) return mockDelay(MockData.profile);
        return await fetchAPI('/profile');
    },

    updatePersonalInfo: async (infoData) => {
        if (API_CONFIG.USE_MOCK) {
            Object.assign(MockData.profile.personal_info, infoData);
            return mockDelay({ success: true, message: "Cập nhật thông tin cá nhân thành công!" });
        }
        return await fetchAPI('/profile/personal-info', 'PUT', infoData);
    },

    addCourse: async (courseData) => {
        if (API_CONFIG.USE_MOCK) {
            const newCourse = { id: Date.now(), ...courseData };
            MockData.profile.courses.push(newCourse);
            return mockDelay({ success: true, data: newCourse, message: "Thêm học phần thành công!" });
        }
        return await fetchAPI('/profile/courses', 'POST', courseData);
    },

    deleteCourse: async (id) => {
        if (API_CONFIG.USE_MOCK) {
            MockData.profile.courses = MockData.profile.courses.filter(c => c.id !== id);
            return mockDelay({ success: true, message: "Đã xóa học phần!" });
        }
        return await fetchAPI(`/profile/courses/${id}`, 'DELETE');
    },

    addSkill: async (skillData) => {
        if (API_CONFIG.USE_MOCK) {
            const newSkill = { id: Date.now(), ...skillData };
            MockData.profile.skills.push(newSkill);
            return mockDelay({ success: true, data: newSkill, message: "Thêm kỹ năng thành công!" });
        }
        return await fetchAPI('/profile/skills', 'POST', skillData);
    },

    deleteSkill: async (id) => {
        if (API_CONFIG.USE_MOCK) {
            MockData.profile.skills = MockData.profile.skills.filter(s => s.id !== id);
            return mockDelay({ success: true, message: "Đã xóa kỹ năng!" });
        }
        return await fetchAPI(`/profile/skills/${id}`, 'DELETE');
    },

    addCertificate: async (certData) => {
        if (API_CONFIG.USE_MOCK) {
            const newCert = { id: Date.now(), ...certData };
            MockData.profile.certificates.push(newCert);
            return mockDelay({ success: true, data: newCert, message: "Thêm chứng chỉ thành công!" });
        }
        return await fetchAPI('/profile/certificates', 'POST', certData);
    },

    deleteCertificate: async (id) => {
        if (API_CONFIG.USE_MOCK) {
            MockData.profile.certificates = MockData.profile.certificates.filter(c => c.id !== id);
            return mockDelay({ success: true, message: "Đã xóa chứng chỉ!" });
        }
        return await fetchAPI(`/profile/certificates/${id}`, 'DELETE');
    },

    addExperience: async (expData) => {
        if (API_CONFIG.USE_MOCK) {
            const newExp = { id: Date.now(), ...expData };
            MockData.profile.experiences.push(newExp);
            return mockDelay({ success: true, data: newExp, message: "Thêm kinh nghiệm thành công!" });
        }
        return await fetchAPI('/profile/experiences', 'POST', expData);
    },

    deleteExperience: async (id) => {
        if (API_CONFIG.USE_MOCK) {
            MockData.profile.experiences = MockData.profile.experiences.filter(e => e.id !== id);
            return mockDelay({ success: true, message: "Đã xóa kinh nghiệm!" });
        }
        return await fetchAPI(`/profile/experiences/${id}`, 'DELETE');
    },

    // ------------------------------------------
    // 2. MODULE VỊ TRÍ & TIN TUYỂN DỤNG
    // ------------------------------------------
    getPositions: async () => {
        if (API_CONFIG.USE_MOCK) return mockDelay(MockData.positions);
        return await fetchAPI('/positions');
    },

    getJobs: async (filters = {}) => {
        if (API_CONFIG.USE_MOCK) {
            let list = [...MockData.jobs];
            if (filters.search) {
                const kw = filters.search.toLowerCase();
                list = list.filter(j => j.title.toLowerCase().includes(kw) || j.company.toLowerCase().includes(kw));
            }
            if (filters.position_id) {
                list = list.filter(j => j.position_id == filters.position_id);
            }
            return mockDelay({ jobs: list, total: list.length });
        }
        const query = new URLSearchParams(filters).toString();
        return await fetchAPI(`/jobs?${query}`);
    },

    saveJob: async (jobData) => {
        if (API_CONFIG.USE_MOCK) {
            if (jobData.id) {
                const idx = MockData.jobs.findIndex(j => j.id === jobData.id);
                if (idx !== -1) MockData.jobs[idx] = { ...MockData.jobs[idx], ...jobData };
            } else {
                jobData.id = Date.now();
                jobData.created_at = new Date().toISOString().split('T')[0];
                MockData.jobs.unshift(jobData);
            }
            return mockDelay({ success: true, message: "Lưu tin tuyển dụng thành công!" });
        }
        const method = jobData.id ? 'PUT' : 'POST';
        const url = jobData.id ? `/jobs/${jobData.id}` : '/jobs';
        return await fetchAPI(url, method, jobData);
    },

    deleteJob: async (id) => {
        if (API_CONFIG.USE_MOCK) {
            MockData.jobs = MockData.jobs.filter(j => j.id !== id);
            return mockDelay({ success: true, message: "Đã xóa tin tuyển dụng!" });
        }
        return await fetchAPI(`/jobs/${id}`, 'DELETE');
    },

    uploadCSV: async (file) => {
        if (API_CONFIG.USE_MOCK) {
            return mockDelay({ success: true, count: 5, message: "Đã nhập thành công 5 tin tuyển dụng từ file CSV (Giả lập)!" });
        }
        const formData = new FormData();
        formData.append('file', file);
        return await fetchAPI('/jobs/upload-csv', 'POST', formData);
    },

    // ------------------------------------------
    // 3. MODULE THỐNG KÊ KỸ NĂNG (CHART.JS)
    // ------------------------------------------
    getStatistics: async (positionId = 1) => {
        if (API_CONFIG.USE_MOCK) {
            const data = MockData.statistics[positionId] || MockData.statistics[1];
            return mockDelay(data);
        }
        return await fetchAPI(`/statistics?position_id=${positionId}`);
    },

    // ------------------------------------------
    // 4. MODULE SO SÁNH ĐỘ PHÙ HỢP
    // ------------------------------------------
    getComparison: async (positionId = 1) => {
        if (API_CONFIG.USE_MOCK) {
            const data = (MockData.comparison_by_position && MockData.comparison_by_position[positionId]) 
                ? MockData.comparison_by_position[positionId] 
                : MockData.comparison;
            return mockDelay(data);
        }
        return await fetchAPI(`/comparison?position_id=${positionId}`);
    },

    // ------------------------------------------
    // 5. MODULE KẾ HOẠCH & ROADMAP
    // ------------------------------------------
    getRoadmap: async () => {
        if (API_CONFIG.USE_MOCK) return mockDelay(MockData.roadmap);
        return await fetchAPI('/roadmap');
    },

    toggleRoadmapTask: async (taskId, isCompleted) => {
        if (API_CONFIG.USE_MOCK) {
            const task = MockData.roadmap.tasks.find(t => t.id === taskId);
            if (task) {
                task.is_completed = isCompleted;
                const completed = MockData.roadmap.tasks.filter(t => t.is_completed).length;
                MockData.roadmap.completed_items = completed;
                MockData.roadmap.progress_percentage = Math.round((completed / MockData.roadmap.total_items) * 100);
            }
            return mockDelay({ success: true, roadmap: MockData.roadmap });
        }
        return await fetchAPI(`/roadmap/tasks/${taskId}/toggle`, 'POST', { is_completed: isCompleted });
    },

    addRoadmapTask: async (taskData) => {
        if (API_CONFIG.USE_MOCK) {
            const newTask = {
                id: Date.now(),
                is_completed: false,
                ...taskData
            };
            MockData.roadmap.tasks.push(newTask);
            MockData.roadmap.total_items = MockData.roadmap.tasks.length;
            const completed = MockData.roadmap.tasks.filter(t => t.is_completed).length;
            MockData.roadmap.progress_percentage = Math.round((completed / MockData.roadmap.total_items) * 100);
            return mockDelay({ success: true, data: newTask, message: "Đã thêm mục tiêu vào kế hoạch!" });
        }
        return await fetchAPI('/roadmap/tasks', 'POST', taskData);
    },

    deleteRoadmapTask: async (taskId) => {
        if (API_CONFIG.USE_MOCK) {
            MockData.roadmap.tasks = MockData.roadmap.tasks.filter(t => t.id !== taskId);
            MockData.roadmap.total_items = MockData.roadmap.tasks.length;
            const completed = MockData.roadmap.tasks.filter(t => t.is_completed).length;
            MockData.roadmap.progress_percentage = MockData.roadmap.total_items > 0
                ? Math.round((completed / MockData.roadmap.total_items) * 100)
                : 0;
            return mockDelay({ success: true, message: "Đã xóa mục tiêu khỏi kế hoạch!" });
        }
        return await fetchAPI(`/roadmap/tasks/${taskId}`, 'DELETE');
    }
};
