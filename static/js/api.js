/**
 * api.js - Lớp giao tiếp API tập trung (Centralized API Service)
 * Đề tài: NLCNPM23CS-38
 *
 * TÍNH NĂNG ĐẶC BIỆT:
 * Chuyển đổi giữa chế độ Dữ liệu giả (Mock) và Backend Flask thật 100% bằng cách
 * thay đổi giá trị cờ `USE_MOCK` trong file `static/js/config.js`.
 */

// Hàm gọi fetch chuẩn hóa gửi request đến Backend Flask thật
async function httpFetch(endpoint, method = 'GET', data = null) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    };

    // Đính kèm Token xác thực nếu có
    const token = localStorage.getItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    if (data) {
        if (data instanceof FormData) {
            delete options.headers['Content-Type'];
            options.body = data;
        } else {
            options.body = JSON.stringify(data);
        }
    }

    try {
        const response = await fetch(url, options);
        const result = await response.json().catch(() => ({
            success: false,
            message: `Lỗi phân tích phản hồi máy chủ (HTTP ${response.status})`
        }));

        if (!response.ok) {
            throw new Error(result.message || `Lỗi máy chủ: mã HTTP ${response.status}`);
        }
        return result;
    } catch (error) {
        console.error(`[API Network Error] ${method} ${url}:`, error);
        throw error;
    }
}

// Hàm giả lập độ trễ mạng khi dùng Mock Data
function mockResponse(data, isSuccess = true, message = "") {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (isSuccess) {
                resolve({
                    success: true,
                    data: JSON.parse(JSON.stringify(data)),
                    message: message || "Thành công"
                });
            } else {
                reject(new Error(message || "Có lỗi xảy ra trong quá trình xử lý!"));
            }
        }, CONFIG.MOCK_DELAY_MS);
    });
}

// ĐỐI TƯỢNG API CHÍNH DÙNG CHO TOÀN BỘ FRONTEND
const API = {
    // ==========================================
    // 1. XÁC THỰC (AUTH)
    // ==========================================
    auth: {
        async login(credentials) {
            if (CONFIG.USE_MOCK) {
                if (credentials.email && credentials.password) {
                    const mockUser = {
                        id: 1,
                        email: credentials.email,
                        full_name: "Nguyễn Văn An",
                        role: "student"
                    };
                    Utils.auth.setUser(mockUser);
                    return mockResponse(mockUser, true, "Đăng nhập thành công!");
                }
                return mockResponse(null, false, "Email hoặc mật khẩu không chính xác!");
            }
            const res = await httpFetch('/auth/login', 'POST', credentials);
            if (res.success && res.data) {
                Utils.auth.setUser(res.data);
            }
            return res;
        },

        async register(userData) {
            if (CONFIG.USE_MOCK) {
                const newUser = {
                    id: Date.now(),
                    email: userData.email,
                    full_name: userData.full_name || "Sinh viên mới",
                    role: "student"
                };
                Utils.auth.setUser(newUser);
                return mockResponse(newUser, true, "Đăng ký tài khoản thành công!");
            }
            const res = await httpFetch('/auth/register', 'POST', userData);
            if (res.success && res.data) {
                Utils.auth.setUser(res.data);
            }
            return res;
        },

        async logout() {
            Utils.auth.clearSession();
            if (CONFIG.USE_MOCK) {
                return mockResponse(null, true, "Đã đăng xuất");
            }
            return await httpFetch('/auth/logout', 'POST');
        }
    },

    // ==========================================
    // 2. DASHBOARD TỔNG QUAN
    // ==========================================
    dashboard: {
        async getSummary() {
            if (CONFIG.USE_MOCK) {
                const totalSkills = MockData.profile.skills.length;
                const totalCerts = MockData.profile.certificates.length;
                
                // Tính điểm phù hợp cao nhất dựa trên các vị trí
                const matchScores = MockData.positions.map(pos => {
                    const mySkillNames = MockData.profile.skills.map(s => s.name.toLowerCase());
                    const matched = pos.core_skills.filter(cs => mySkillNames.some(ms => ms.includes(cs.toLowerCase()) || cs.toLowerCase().includes(ms)));
                    const score = Math.round((matched.length / pos.core_skills.length) * 100);
                    return {
                        id: pos.id,
                        name: pos.name,
                        score: score
                    };
                });

                const highest = matchScores.reduce((max, cur) => cur.score > max.score ? cur : max, matchScores[0]);

                const doneCount = MockData.plans.filter(p => p.status === 'done').length;
                const progressPercent = MockData.plans.length ? Math.round((doneCount / MockData.plans.length) * 100) : 0;

                const data = {
                    total_skills: totalSkills,
                    total_certificates: totalCerts,
                    highest_match: highest,
                    plan_progress: progressPercent,
                    match_by_positions: matchScores,
                    recent_todos: MockData.plans.filter(p => p.status !== 'done').slice(0, 5)
                };
                return mockResponse(data);
            }
            return await httpFetch('/dashboard');
        }
    },

    // ==========================================
    // 3. HỒ SƠ SINH VIÊN (PROFILE)
    // ==========================================
    profile: {
        async get() {
            if (CONFIG.USE_MOCK) {
                return mockResponse(MockData.profile);
            }
            return await httpFetch('/profile');
        },

        async updatePersonal(infoData) {
            if (CONFIG.USE_MOCK) {
                Object.assign(MockData.profile.personal_info, infoData);
                return mockResponse(MockData.profile.personal_info, true, "Cập nhật thông tin cá nhân thành công!");
            }
            return await httpFetch('/profile', 'PUT', infoData);
        },

        // --- HỌC PHẦN (COURSES) ---
        async addCourse(course) {
            if (CONFIG.USE_MOCK) {
                const newCourse = { id: Date.now(), ...course };
                MockData.profile.courses.push(newCourse);
                return mockResponse(newCourse, true, "Thêm học phần thành công!");
            }
            return await httpFetch('/profile/courses', 'POST', course);
        },
        async updateCourse(id, course) {
            if (CONFIG.USE_MOCK) {
                const idx = MockData.profile.courses.findIndex(c => c.id == id);
                if (idx !== -1) {
                    MockData.profile.courses[idx] = { ...MockData.profile.courses[idx], ...course };
                    return mockResponse(MockData.profile.courses[idx], true, "Cập nhật học phần thành công!");
                }
                return mockResponse(null, false, "Không tìm thấy học phần!");
            }
            return await httpFetch(`/profile/courses/${id}`, 'PUT', course);
        },
        async deleteCourse(id) {
            if (CONFIG.USE_MOCK) {
                MockData.profile.courses = MockData.profile.courses.filter(c => c.id != id);
                return mockResponse(null, true, "Xóa học phần thành công!");
            }
            return await httpFetch(`/profile/courses/${id}`, 'DELETE');
        },

        // --- KỸ NĂNG (SKILLS) ---
        async addSkill(skill) {
            if (CONFIG.USE_MOCK) {
                const newSkill = { id: Date.now(), ...skill, level: parseInt(skill.level) || 1 };
                MockData.profile.skills.push(newSkill);
                return mockResponse(newSkill, true, "Thêm kỹ năng thành công!");
            }
            return await httpFetch('/profile/skills', 'POST', skill);
        },
        async updateSkill(id, skill) {
            if (CONFIG.USE_MOCK) {
                const idx = MockData.profile.skills.findIndex(s => s.id == id);
                if (idx !== -1) {
                    MockData.profile.skills[idx] = { ...MockData.profile.skills[idx], ...skill, level: parseInt(skill.level) || 1 };
                    return mockResponse(MockData.profile.skills[idx], true, "Cập nhật kỹ năng thành công!");
                }
                return mockResponse(null, false, "Không tìm thấy kỹ năng!");
            }
            return await httpFetch(`/profile/skills/${id}`, 'PUT', skill);
        },
        async deleteSkill(id) {
            if (CONFIG.USE_MOCK) {
                MockData.profile.skills = MockData.profile.skills.filter(s => s.id != id);
                return mockResponse(null, true, "Xóa kỹ năng thành công!");
            }
            return await httpFetch(`/profile/skills/${id}`, 'DELETE');
        },

        // --- CHỨNG CHỈ (CERTIFICATES) ---
        async addCertificate(cert) {
            if (CONFIG.USE_MOCK) {
                const newCert = { id: Date.now(), ...cert };
                MockData.profile.certificates.push(newCert);
                return mockResponse(newCert, true, "Thêm chứng chỉ thành công!");
            }
            return await httpFetch('/profile/certificates', 'POST', cert);
        },
        async updateCertificate(id, cert) {
            if (CONFIG.USE_MOCK) {
                const idx = MockData.profile.certificates.findIndex(c => c.id == id);
                if (idx !== -1) {
                    MockData.profile.certificates[idx] = { ...MockData.profile.certificates[idx], ...cert };
                    return mockResponse(MockData.profile.certificates[idx], true, "Cập nhật chứng chỉ thành công!");
                }
                return mockResponse(null, false, "Không tìm thấy chứng chỉ!");
            }
            return await httpFetch(`/profile/certificates/${id}`, 'PUT', cert);
        },
        async deleteCertificate(id) {
            if (CONFIG.USE_MOCK) {
                MockData.profile.certificates = MockData.profile.certificates.filter(c => c.id != id);
                return mockResponse(null, true, "Xóa chứng chỉ thành công!");
            }
            return await httpFetch(`/profile/certificates/${id}`, 'DELETE');
        },

        // --- KINH NGHIỆM / DỰ ÁN (EXPERIENCES) ---
        async addExperience(exp) {
            if (CONFIG.USE_MOCK) {
                const newExp = { id: Date.now(), ...exp };
                MockData.profile.experiences.push(newExp);
                return mockResponse(newExp, true, "Thêm kinh nghiệm/dự án thành công!");
            }
            return await httpFetch('/profile/experiences', 'POST', exp);
        },
        async updateExperience(id, exp) {
            if (CONFIG.USE_MOCK) {
                const idx = MockData.profile.experiences.findIndex(e => e.id == id);
                if (idx !== -1) {
                    MockData.profile.experiences[idx] = { ...MockData.profile.experiences[idx], ...exp };
                    return mockResponse(MockData.profile.experiences[idx], true, "Cập nhật kinh nghiệm thành công!");
                }
                return mockResponse(null, false, "Không tìm thấy kinh nghiệm!");
            }
            return await httpFetch(`/profile/experiences/${id}`, 'PUT', exp);
        },
        async deleteExperience(id) {
            if (CONFIG.USE_MOCK) {
                MockData.profile.experiences = MockData.profile.experiences.filter(e => e.id != id);
                return mockResponse(null, true, "Xóa kinh nghiệm thành công!");
            }
            return await httpFetch(`/profile/experiences/${id}`, 'DELETE');
        }
    },

    // ==========================================
    // 4. VỊ TRÍ NGHỀ NGHIỆP (POSITIONS)
    // ==========================================
    positions: {
        async getAll({ q = '', page = 1, limit = 8 } = {}) {
            if (CONFIG.USE_MOCK) {
                let items = MockData.positions;
                if (q.trim()) {
                    const term = q.toLowerCase().trim();
                    items = items.filter(p => 
                        p.name.toLowerCase().includes(term) || 
                        p.description.toLowerCase().includes(term) ||
                        p.core_skills.some(s => s.toLowerCase().includes(term))
                    );
                }
                const total = items.length;
                const totalPages = Math.ceil(total / limit) || 1;
                const start = (page - 1) * limit;
                const pagedItems = items.slice(start, start + limit);

                return mockResponse({
                    items: pagedItems,
                    total: total,
                    page: page,
                    limit: limit,
                    total_pages: totalPages
                });
            }
            const query = new URLSearchParams({ q, page, limit }).toString();
            return await httpFetch(`/positions?${query}`);
        },

        async getById(id) {
            if (CONFIG.USE_MOCK) {
                const pos = MockData.positions.find(p => p.id == id);
                if (pos) return mockResponse(pos);
                return mockResponse(null, false, "Không tìm thấy vị trí!");
            }
            return await httpFetch(`/positions/${id}`);
        },

        async create(posData) {
            if (CONFIG.USE_MOCK) {
                const newPos = {
                    id: Date.now(),
                    ...posData,
                    core_skills: Array.isArray(posData.core_skills) ? posData.core_skills : (posData.core_skills || '').split(',').map(s => s.trim()).filter(Boolean)
                };
                MockData.positions.push(newPos);
                return mockResponse(newPos, true, "Thêm vị trí nghề nghiệp thành công!");
            }
            return await httpFetch('/positions', 'POST', posData);
        },

        async update(id, posData) {
            if (CONFIG.USE_MOCK) {
                const idx = MockData.positions.findIndex(p => p.id == id);
                if (idx !== -1) {
                    const skills = Array.isArray(posData.core_skills) ? posData.core_skills : (posData.core_skills || '').split(',').map(s => s.trim()).filter(Boolean);
                    MockData.positions[idx] = { ...MockData.positions[idx], ...posData, core_skills: skills };
                    return mockResponse(MockData.positions[idx], true, "Cập nhật vị trí thành công!");
                }
                return mockResponse(null, false, "Không tìm thấy vị trí!");
            }
            return await httpFetch(`/positions/${id}`, 'PUT', posData);
        },

        async delete(id) {
            if (CONFIG.USE_MOCK) {
                MockData.positions = MockData.positions.filter(p => p.id != id);
                return mockResponse(null, true, "Xóa vị trí nghề nghiệp thành công!");
            }
            return await httpFetch(`/positions/${id}`, 'DELETE');
        }
    },

    // ==========================================
    // 5. TIN TUYỂN DỤNG (JOBS)
    // ==========================================
    jobs: {
        async getAll({ q = '', position_id = '', page = 1, limit = 8 } = {}) {
            if (CONFIG.USE_MOCK) {
                let items = MockData.jobs;
                if (position_id) {
                    items = items.filter(j => j.position_id == position_id);
                }
                if (q.trim()) {
                    const term = q.toLowerCase().trim();
                    items = items.filter(j => 
                        j.title.toLowerCase().includes(term) ||
                        j.company.toLowerCase().includes(term) ||
                        j.skills.some(s => s.toLowerCase().includes(term)) ||
                        j.technologies.some(t => t.toLowerCase().includes(term))
                    );
                }
                const total = items.length;
                const totalPages = Math.ceil(total / limit) || 1;
                const start = (page - 1) * limit;
                const pagedItems = items.slice(start, start + limit);

                return mockResponse({
                    items: pagedItems,
                    total: total,
                    page: page,
                    limit: limit,
                    total_pages: totalPages
                });
            }
            const query = new URLSearchParams({ q, position_id, page, limit }).toString();
            return await httpFetch(`/jobs?${query}`);
        },

        async getById(id) {
            if (CONFIG.USE_MOCK) {
                const job = MockData.jobs.find(j => j.id == id);
                if (job) return mockResponse(job);
                return mockResponse(null, false, "Không tìm thấy tin tuyển dụng!");
            }
            return await httpFetch(`/jobs/${id}`);
        },

        async create(jobData) {
            if (CONFIG.USE_MOCK) {
                const parseArray = (field) => Array.isArray(field) ? field : (field || '').split(',').map(s => s.trim()).filter(Boolean);
                const newJob = {
                    id: Date.now(),
                    ...jobData,
                    position_id: parseInt(jobData.position_id) || 1,
                    skills: parseArray(jobData.skills),
                    technologies: parseArray(jobData.technologies),
                    certificates: parseArray(jobData.certificates)
                };
                MockData.jobs.unshift(newJob);
                return mockResponse(newJob, true, "Đăng tin tuyển dụng thành công!");
            }
            return await httpFetch('/jobs', 'POST', jobData);
        },

        async update(id, jobData) {
            if (CONFIG.USE_MOCK) {
                const idx = MockData.jobs.findIndex(j => j.id == id);
                if (idx !== -1) {
                    const parseArray = (field) => Array.isArray(field) ? field : (field || '').split(',').map(s => s.trim()).filter(Boolean);
                    MockData.jobs[idx] = {
                        ...MockData.jobs[idx],
                        ...jobData,
                        position_id: parseInt(jobData.position_id) || MockData.jobs[idx].position_id,
                        skills: parseArray(jobData.skills),
                        technologies: parseArray(jobData.technologies),
                        certificates: parseArray(jobData.certificates)
                    };
                    return mockResponse(MockData.jobs[idx], true, "Cập nhật tin tuyển dụng thành công!");
                }
                return mockResponse(null, false, "Không tìm thấy tin tuyển dụng!");
            }
            return await httpFetch(`/jobs/${id}`, 'PUT', jobData);
        },

        async delete(id) {
            if (CONFIG.USE_MOCK) {
                MockData.jobs = MockData.jobs.filter(j => j.id != id);
                return mockResponse(null, true, "Xóa tin tuyển dụng thành công!");
            }
            return await httpFetch(`/jobs/${id}`, 'DELETE');
        },

        async importCSV(records) {
            if (CONFIG.USE_MOCK) {
                let count = 0;
                records.forEach(row => {
                    const parseArr = (str) => (str || '').split(';').map(s => s.trim()).filter(Boolean);
                    const newJob = {
                        id: Date.now() + Math.floor(Math.random() * 1000),
                        title: row.title || 'Vị trí tuyển dụng',
                        company: row.company || 'Doanh nghiệp IT',
                        position_id: parseInt(row.position_id) || 1,
                        location: row.location || 'Toàn quốc',
                        salary: row.salary || 'Thỏa thuận',
                        experience_required: row.experience_required || 'Không yêu cầu',
                        skills: parseArr(row.skills),
                        technologies: parseArr(row.technologies),
                        certificates: parseArr(row.certificates),
                        deadline: row.deadline || '2026-12-31',
                        description: row.description || ''
                    };
                    MockData.jobs.unshift(newJob);
                    count++;
                });
                return mockResponse({ imported_count: count }, true, `Đã nhập thành công ${count} tin tuyển dụng từ CSV!`);
            }
            return await httpFetch('/jobs/import-csv', 'POST', { records });
        }
    },

    // ==========================================
    // 6. THỐNG KÊ KỸ NĂNG (STATISTICS)
    // ==========================================
    statistics: {
        async getByPosition(position_id) {
            if (CONFIG.USE_MOCK) {
                const stat = MockData.statistics[position_id] || MockData.statistics[1];
                return mockResponse(stat);
            }
            return await httpFetch(`/statistics/${position_id}`);
        }
    },

    // ==========================================
    // 7. SO SÁNH HỒ SƠ & VỊ TRÍ (COMPARE)
    // ==========================================
    compare: {
        async compareWithPosition(position_id) {
            if (CONFIG.USE_MOCK) {
                const pos = MockData.positions.find(p => p.id == position_id) || MockData.positions[0];
                const jobsOfPos = MockData.jobs.filter(j => j.position_id == position_id);
                
                // Tập hợp các kỹ năng & công nghệ yêu cầu trong các tin tuyển dụng
                const reqSkillSet = new Set();
                pos.core_skills.forEach(s => reqSkillSet.add(s));
                jobsOfPos.forEach(j => {
                    j.skills.forEach(s => reqSkillSet.add(s));
                });
                const allRequirements = Array.from(reqSkillSet);

                const userSkills = MockData.profile.skills.map(s => s.name.trim().toLowerCase());
                
                const have = [];
                const missing = [];

                allRequirements.forEach(req => {
                    const reqLower = req.toLowerCase();
                    const isMatched = userSkills.some(userSkill => 
                        userSkill === reqLower ||
                        userSkill.includes(reqLower) ||
                        reqLower.includes(userSkill)
                    );
                    if (isMatched) {
                        have.push(req);
                    } else {
                        missing.push(req);
                    }
                });

                const total = have.length + missing.length;
                const score = total > 0 ? Math.round((have.length / total) * 100) : 0;

                let summary = "";
                if (score >= 75) {
                    summary = `Tuyệt vời! Hồ sơ của bạn đạt mức độ phù hợp rất cao (${score}%) đối với vị trí "${pos.name}". Bạn đã nắm vững các kỹ năng cốt lõi (${have.slice(0, 4).join(', ')}). Hãy nhanh chóng trau dồi thêm ${missing.slice(0, 2).join(', ')} để tự tin ứng tuyển các vị trí lương cao!`;
                } else if (score >= 50) {
                    summary = `Khá tốt! Mức độ phù hợp của bạn là ${score}%. Bạn đã có nền tảng ban đầu với (${have.slice(0, 3).join(', ')}), tuy nhiên thị trường đang yêu cầu bổ sung các kỹ năng quan trọng như: ${missing.slice(0, 4).join(', ')}. Hãy lập kế hoạch học tập ngay!`;
                } else {
                    summary = `Mức độ phù hợp hiện tại là ${score}%. Vị trí "${pos.name}" đòi hỏi nhiều kiến thức chuyên sâu mà bạn chưa cập nhật trong hồ sơ. Khuyến nghị bạn bổ sung các kỹ năng: ${missing.slice(0, 5).join(', ')} vào Lộ trình học tập.`;
                }

                const result = {
                    position_id: pos.id,
                    position_name: pos.name,
                    score: score,
                    have: have,
                    missing: missing,
                    summary: summary,
                    recommended_certs: (MockData.statistics[position_id]?.certificates || []).map(c => c.name)
                };

                return mockResponse(result);
            }
            return await httpFetch('/compare', 'POST', { position_id });
        }
    },

    // ==========================================
    // 8. KẾ HOẠCH HỌC TẬP (PLAN)
    // ==========================================
    plan: {
        async getAll() {
            if (CONFIG.USE_MOCK) {
                return mockResponse(MockData.plans);
            }
            return await httpFetch('/plan');
        },

        async create(planData) {
            if (CONFIG.USE_MOCK) {
                const newPlan = {
                    id: Date.now(),
                    ...planData,
                    status: planData.status || 'todo'
                };
                MockData.plans.unshift(newPlan);
                return mockResponse(newPlan, true, "Đã thêm mục mới vào kế hoạch!");
            }
            return await httpFetch('/plan', 'POST', planData);
        },

        async update(id, planData) {
            if (CONFIG.USE_MOCK) {
                const idx = MockData.plans.findIndex(p => p.id == id);
                if (idx !== -1) {
                    MockData.plans[idx] = { ...MockData.plans[idx], ...planData };
                    return mockResponse(MockData.plans[idx], true, "Cập nhật kế hoạch thành công!");
                }
                return mockResponse(null, false, "Không tìm thấy kế hoạch!");
            }
            return await httpFetch(`/plan/${id}`, 'PUT', planData);
        },

        async updateStatus(id, status) {
            if (CONFIG.USE_MOCK) {
                const idx = MockData.plans.findIndex(p => p.id == id);
                if (idx !== -1) {
                    MockData.plans[idx].status = status;
                    return mockResponse(MockData.plans[idx], true, "Cập nhật trạng thái thành công!");
                }
                return mockResponse(null, false, "Không tìm thấy kế hoạch!");
            }
            return await httpFetch(`/plan/${id}`, 'PUT', { status });
        },

        async delete(id) {
            if (CONFIG.USE_MOCK) {
                MockData.plans = MockData.plans.filter(p => p.id != id);
                return mockResponse(null, true, "Xóa mục kế hoạch thành công!");
            }
            return await httpFetch(`/plan/${id}`, 'DELETE');
        }
    }
};

// Gắn API vào Window
if (typeof window !== 'undefined') {
    window.API = API;
}
