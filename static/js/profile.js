/**
 * profile.js - Quản lý toàn diện hồ sơ sinh viên và 4 phần năng lực
 * Đề tài: NLCNPM23CS-38
 */

let currentProfile = null;

// Khởi tạo các Modal Bootstrap
let personalInfoModal = null;
let skillModal = null;
let courseModal = null;
let certModal = null;
let expModal = null;

document.addEventListener('DOMContentLoaded', () => {
    // Khởi tạo các thể hiện modal
    const pModalEl = document.getElementById('editPersonalInfoModal');
    if (pModalEl) personalInfoModal = new bootstrap.Modal(pModalEl);

    const sModalEl = document.getElementById('skillModal');
    if (sModalEl) skillModal = new bootstrap.Modal(sModalEl);

    const cModalEl = document.getElementById('courseModal');
    if (cModalEl) courseModal = new bootstrap.Modal(cModalEl);

    const crtModalEl = document.getElementById('certModal');
    if (crtModalEl) certModal = new bootstrap.Modal(crtModalEl);

    const eModalEl = document.getElementById('expModal');
    if (eModalEl) expModal = new bootstrap.Modal(eModalEl);

    // Gắn sự kiện nút mở Modal thêm mới
    document.getElementById('btnOpenAddSkillModal')?.addEventListener('click', openAddSkillModal);
    document.getElementById('btnOpenAddCourseModal')?.addEventListener('click', openAddCourseModal);
    document.getElementById('btnOpenAddCertModal')?.addEventListener('click', openAddCertModal);
    document.getElementById('btnOpenAddExpModal')?.addEventListener('click', openAddExpModal);

    // Gắn sự kiện Submit Forms
    document.getElementById('formPersonalInfo')?.addEventListener('submit', handleSavePersonalInfo);
    document.getElementById('formSkill')?.addEventListener('submit', handleSaveSkill);
    document.getElementById('formCourse')?.addEventListener('submit', handleSaveCourse);
    document.getElementById('formCert')?.addEventListener('submit', handleSaveCert);
    document.getElementById('formExp')?.addEventListener('submit', handleSaveExp);

    // Tải dữ liệu hồ sơ
    loadProfileData();
});

/**
 * Tải toàn bộ hồ sơ sinh viên từ API
 */
async function loadProfileData() {
    try {
        Utils.showLoading(true, 'Đang tải hồ sơ sinh viên...');
        const res = await API.profile.get();
        if (res.success && res.data) {
            currentProfile = res.data;
            renderPersonalInfo(res.data.personal_info);
            renderSkills(res.data.skills || []);
            renderCourses(res.data.courses || []);
            renderCertificates(res.data.certificates || []);
            renderExperiences(res.data.experiences || []);
        } else {
            Utils.showToast(res.message || 'Không thể tải hồ sơ!', 'danger');
        }
    } catch (e) {
        console.error(e);
        Utils.showToast('Lỗi khi nạp hồ sơ sinh viên!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}

// ==========================================
// 1. XỬ LÝ THÔNG TIN CÁ NHÂN
// ==========================================
function renderPersonalInfo(info) {
    if (!info) return;

    // Hiển thị ở Sidebar
    document.getElementById('profileCardName').textContent = info.full_name || 'Chưa đặt tên';
    document.getElementById('profileCardMajor').textContent = `${info.major || 'CNTT'} - ${info.academic_year || ''}`;
    document.getElementById('profileCardGpa').textContent = info.gpa || '0.0';
    document.getElementById('profileCardCode').textContent = `MSSV: ${info.student_code || '---'}`;
    document.getElementById('profileSideUniversity').textContent = info.university || 'Chưa cập nhật trường';
    document.getElementById('profileSideEmail').textContent = info.email || 'Chưa cập nhật email';
    document.getElementById('profileSidePhone').textContent = info.phone || 'Chưa cập nhật số điện thoại';
    document.getElementById('profileSideBio').textContent = info.bio || 'Chưa có thông tin mục tiêu nghề nghiệp.';

    // Điền vào form Modal chỉnh sửa
    document.getElementById('infoFullName').value = info.full_name || '';
    document.getElementById('infoStudentCode').value = info.student_code || '';
    document.getElementById('infoEmail').value = info.email || '';
    document.getElementById('infoPhone').value = info.phone || '';
    document.getElementById('infoUniversity').value = info.university || '';
    document.getElementById('infoFaculty').value = info.faculty || '';
    document.getElementById('infoMajor').value = info.major || '';
    document.getElementById('infoAcademicYear').value = info.academic_year || '';
    document.getElementById('infoGpa').value = info.gpa || '';
    document.getElementById('infoBio').value = info.bio || '';
}

async function handleSavePersonalInfo(e) {
    e.preventDefault();
    const btn = document.getElementById('btnSavePersonalInfo');
    Utils.setButtonLoading(btn, true);

    const payload = {
        full_name: document.getElementById('infoFullName').value.trim(),
        student_code: document.getElementById('infoStudentCode').value.trim(),
        email: document.getElementById('infoEmail').value.trim(),
        phone: document.getElementById('infoPhone').value.trim(),
        university: document.getElementById('infoUniversity').value.trim(),
        faculty: document.getElementById('infoFaculty').value.trim(),
        major: document.getElementById('infoMajor').value.trim(),
        academic_year: document.getElementById('infoAcademicYear').value.trim(),
        gpa: document.getElementById('infoGpa').value.trim(),
        bio: document.getElementById('infoBio').value.trim()
    };

    try {
        const res = await API.profile.updatePersonal(payload);
        if (res.success) {
            Utils.showToast('Đã lưu thông tin cá nhân!', 'success');
            renderPersonalInfo(payload);
            personalInfoModal?.hide();
        } else {
            Utils.showToast(res.message || 'Cập nhật thất bại!', 'danger');
        }
    } catch (err) {
        Utils.showToast('Lỗi máy chủ khi lưu thông tin!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

// ==========================================
// 2. XỬ LÝ KỸ NĂNG (SKILLS)
// ==========================================
function renderSkills(skills) {
    const tbody = document.getElementById('skillsTableBody');
    document.getElementById('countSkills').textContent = skills.length;
    if (!tbody) return;

    if (skills.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">Chưa có kỹ năng nào. Bấm "Thêm kỹ năng" để bắt đầu!</td></tr>`;
        return;
    }

    let html = '';
    skills.forEach(s => {
        html += `
            <tr>
                <td class="fw-semibold text-dark">${Utils.escapeHtml(s.name)}</td>
                <td><span class="badge badge-soft-primary">${Utils.escapeHtml(s.category || 'Khác')}</span></td>
                <td>${Utils.renderStars(s.level)}</td>
                <td class="text-muted small">${Utils.escapeHtml(s.note || '-')}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-secondary py-0 px-2 me-1" title="Sửa" onclick="openEditSkillModal(${s.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger py-0 px-2" title="Xóa" onclick="deleteSkill(${s.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function openAddSkillModal() {
    document.getElementById('skillModalTitle').innerHTML = '<i class="bi bi-tools text-primary me-2"></i>Thêm kỹ năng mới';
    document.getElementById('skillId').value = '';
    document.getElementById('skillName').value = '';
    document.getElementById('skillCategory').value = 'Ngôn ngữ lập trình';
    document.getElementById('skillLevel').value = 3;
    document.getElementById('skillLevelDisplay').textContent = '3/5';
    document.getElementById('skillNote').value = '';
    skillModal?.show();
}

function openEditSkillModal(id) {
    const skill = currentProfile.skills.find(s => s.id == id);
    if (!skill) return;

    document.getElementById('skillModalTitle').innerHTML = '<i class="bi bi-pencil-square text-primary me-2"></i>Chỉnh sửa kỹ năng';
    document.getElementById('skillId').value = skill.id;
    document.getElementById('skillName').value = skill.name || '';
    document.getElementById('skillCategory').value = skill.category || 'Ngôn ngữ lập trình';
    document.getElementById('skillLevel').value = skill.level || 3;
    document.getElementById('skillLevelDisplay').textContent = `${skill.level || 3}/5`;
    document.getElementById('skillNote').value = skill.note || '';
    skillModal?.show();
}

async function handleSaveSkill(e) {
    e.preventDefault();
    const id = document.getElementById('skillId').value;
    const btn = document.getElementById('btnSaveSkill');
    Utils.setButtonLoading(btn, true);

    const payload = {
        name: document.getElementById('skillName').value.trim(),
        category: document.getElementById('skillCategory').value,
        level: parseInt(document.getElementById('skillLevel').value) || 3,
        note: document.getElementById('skillNote').value.trim()
    };

    try {
        let res;
        if (id) {
            res = await API.profile.updateSkill(id, payload);
        } else {
            res = await API.profile.addSkill(payload);
        }

        if (res.success) {
            Utils.showToast(id ? 'Cập nhật kỹ năng thành công!' : 'Thêm kỹ năng thành công!', 'success');
            skillModal?.hide();
            await loadProfileData();
        } else {
            Utils.showToast(res.message || 'Lỗi lưu kỹ năng!', 'danger');
        }
    } catch (err) {
        Utils.showToast('Lỗi máy chủ khi lưu kỹ năng!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

function deleteSkill(id) {
    Utils.confirmModal({
        title: 'Xác nhận xóa kỹ năng',
        message: 'Bạn có chắc chắn muốn xóa kỹ năng này khỏi hồ sơ?',
        confirmText: 'Xóa kỹ năng',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
            const res = await API.profile.deleteSkill(id);
            if (res.success) {
                Utils.showToast('Đã xóa kỹ năng!', 'success');
                await loadProfileData();
            } else {
                Utils.showToast(res.message || 'Xóa thất bại!', 'danger');
            }
        }
    });
}

// ==========================================
// 3. XỬ LÝ HỌC PHẦN (COURSES)
// ==========================================
function renderCourses(courses) {
    const tbody = document.getElementById('coursesTableBody');
    document.getElementById('countCourses').textContent = courses.length;
    if (!tbody) return;

    if (courses.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">Chưa có học phần nào được thêm.</td></tr>`;
        return;
    }

    let html = '';
    courses.forEach(c => {
        html += `
            <tr>
                <td class="fw-semibold text-secondary">${Utils.escapeHtml(c.code)}</td>
                <td class="fw-semibold text-dark">${Utils.escapeHtml(c.name)}</td>
                <td class="text-center">${c.credits || 0}</td>
                <td class="text-center"><span class="badge bg-success-subtle text-success border border-success-subtle">${c.grade || 'A'}</span></td>
                <td>${Utils.escapeHtml(c.term || '-')}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-secondary py-0 px-2 me-1" title="Sửa" onclick="openEditCourseModal(${c.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger py-0 px-2" title="Xóa" onclick="deleteCourse(${c.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function openAddCourseModal() {
    document.getElementById('courseModalTitle').innerHTML = '<i class="bi bi-book text-primary me-2"></i>Thêm học phần mới';
    document.getElementById('courseId').value = '';
    document.getElementById('courseCode').value = '';
    document.getElementById('courseName').value = '';
    document.getElementById('courseCredits').value = 3;
    document.getElementById('courseGrade').value = 'A';
    document.getElementById('courseTerm').value = '';
    courseModal?.show();
}

function openEditCourseModal(id) {
    const course = currentProfile.courses.find(c => c.id == id);
    if (!course) return;

    document.getElementById('courseModalTitle').innerHTML = '<i class="bi bi-pencil-square text-primary me-2"></i>Chỉnh sửa học phần';
    document.getElementById('courseId').value = course.id;
    document.getElementById('courseCode').value = course.code || '';
    document.getElementById('courseName').value = course.name || '';
    document.getElementById('courseCredits').value = course.credits || 3;
    document.getElementById('courseGrade').value = course.grade || 'A';
    document.getElementById('courseTerm').value = course.term || '';
    courseModal?.show();
}

async function handleSaveCourse(e) {
    e.preventDefault();
    const id = document.getElementById('courseId').value;
    const btn = document.getElementById('btnSaveCourse');
    Utils.setButtonLoading(btn, true);

    const payload = {
        code: document.getElementById('courseCode').value.trim(),
        name: document.getElementById('courseName').value.trim(),
        credits: parseInt(document.getElementById('courseCredits').value) || 3,
        grade: document.getElementById('courseGrade').value,
        term: document.getElementById('courseTerm').value.trim()
    };

    try {
        let res;
        if (id) {
            res = await API.profile.updateCourse(id, payload);
        } else {
            res = await API.profile.addCourse(payload);
        }

        if (res.success) {
            Utils.showToast(id ? 'Cập nhật học phần thành công!' : 'Thêm học phần thành công!', 'success');
            courseModal?.hide();
            await loadProfileData();
        } else {
            Utils.showToast(res.message || 'Lỗi lưu học phần!', 'danger');
        }
    } catch (err) {
        Utils.showToast('Lỗi máy chủ khi lưu học phần!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

function deleteCourse(id) {
    Utils.confirmModal({
        title: 'Xác nhận xóa học phần',
        message: 'Bạn có chắc chắn muốn xóa học phần này?',
        confirmText: 'Xóa học phần',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
            const res = await API.profile.deleteCourse(id);
            if (res.success) {
                Utils.showToast('Đã xóa học phần!', 'success');
                await loadProfileData();
            } else {
                Utils.showToast(res.message || 'Xóa thất bại!', 'danger');
            }
        }
    });
}

// ==========================================
// 4. XỬ LÝ CHỨNG CHỈ (CERTIFICATES)
// ==========================================
function renderCertificates(certs) {
    const tbody = document.getElementById('certsTableBody');
    document.getElementById('countCerts').textContent = certs.length;
    if (!tbody) return;

    if (certs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">Chưa có chứng chỉ nào.</td></tr>`;
        return;
    }

    let html = '';
    certs.forEach(crt => {
        const verifyBtn = crt.credential_url 
            ? `<a href="${Utils.escapeHtml(crt.credential_url)}" target="_blank" class="btn btn-sm btn-outline-info py-0 px-2 text-decoration-none" title="Xem liên kết chứng thực"><i class="bi bi-box-arrow-up-right me-1"></i>Kiểm tra</a>`
            : `<span class="text-muted small">Không có</span>`;

        html += `
            <tr>
                <td class="fw-semibold text-dark">${Utils.escapeHtml(crt.name)}</td>
                <td><span class="badge badge-soft-secondary">${Utils.escapeHtml(crt.organization)}</span></td>
                <td>${Utils.formatDate(crt.issue_date)}</td>
                <td>${crt.expiry_date ? Utils.formatDate(crt.expiry_date) : '<span class="text-success small">Vô thời hạn</span>'}</td>
                <td>${verifyBtn}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-secondary py-0 px-2 me-1" title="Sửa" onclick="openEditCertModal(${crt.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger py-0 px-2" title="Xóa" onclick="deleteCert(${crt.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function openAddCertModal() {
    document.getElementById('certModalTitle').innerHTML = '<i class="bi bi-patch-check text-primary me-2"></i>Thêm chứng chỉ mới';
    document.getElementById('certId').value = '';
    document.getElementById('certName').value = '';
    document.getElementById('certOrg').value = '';
    document.getElementById('certIssueDate').value = '';
    document.getElementById('certExpiryDate').value = '';
    document.getElementById('certUrl').value = '';
    certModal?.show();
}

function openEditCertModal(id) {
    const cert = currentProfile.certificates.find(c => c.id == id);
    if (!cert) return;

    document.getElementById('certModalTitle').innerHTML = '<i class="bi bi-pencil-square text-primary me-2"></i>Chỉnh sửa chứng chỉ';
    document.getElementById('certId').value = cert.id;
    document.getElementById('certName').value = cert.name || '';
    document.getElementById('certOrg').value = cert.organization || '';
    document.getElementById('certIssueDate').value = cert.issue_date || '';
    document.getElementById('certExpiryDate').value = cert.expiry_date || '';
    document.getElementById('certUrl').value = cert.credential_url || '';
    certModal?.show();
}

async function handleSaveCert(e) {
    e.preventDefault();
    const id = document.getElementById('certId').value;
    const btn = document.getElementById('btnSaveCert');
    Utils.setButtonLoading(btn, true);

    const payload = {
        name: document.getElementById('certName').value.trim(),
        organization: document.getElementById('certOrg').value.trim(),
        issue_date: document.getElementById('certIssueDate').value,
        expiry_date: document.getElementById('certExpiryDate').value,
        credential_url: document.getElementById('certUrl').value.trim()
    };

    try {
        let res;
        if (id) {
            res = await API.profile.updateCertificate(id, payload);
        } else {
            res = await API.profile.addCertificate(payload);
        }

        if (res.success) {
            Utils.showToast(id ? 'Cập nhật chứng chỉ thành công!' : 'Thêm chứng chỉ thành công!', 'success');
            certModal?.hide();
            await loadProfileData();
        } else {
            Utils.showToast(res.message || 'Lỗi lưu chứng chỉ!', 'danger');
        }
    } catch (err) {
        Utils.showToast('Lỗi máy chủ khi lưu chứng chỉ!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

function deleteCert(id) {
    Utils.confirmModal({
        title: 'Xác nhận xóa chứng chỉ',
        message: 'Bạn có chắc chắn muốn xóa chứng chỉ này khỏi hồ sơ?',
        confirmText: 'Xóa chứng chỉ',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
            const res = await API.profile.deleteCertificate(id);
            if (res.success) {
                Utils.showToast('Đã xóa chứng chỉ!', 'success');
                await loadProfileData();
            } else {
                Utils.showToast(res.message || 'Xóa thất bại!', 'danger');
            }
        }
    });
}

// ==========================================
// 5. XỬ LÝ KINH NGHIỆM & DỰ ÁN (EXPERIENCES)
// ==========================================
function renderExperiences(exps) {
    const container = document.getElementById('experiencesContainer');
    document.getElementById('countExp').textContent = exps.length;
    if (!container) return;

    if (exps.length === 0) {
        Utils.renderEmptyState(container, {
            icon: 'bi-briefcase',
            title: 'Chưa có kinh nghiệm thực tế',
            message: 'Hãy bổ sung các kỳ thực tập, đồ án nghiên cứu hoặc hoạt động ngoại khóa để làm đẹp CV!'
        });
        return;
    }

    let html = '';
    exps.forEach(e => {
        const timeSpan = `${Utils.formatDate(e.start_date)} - ${e.end_date ? Utils.formatDate(e.end_date) : 'Hiện tại'}`;

        html += `
            <div class="col-12">
                <div class="card border p-3 bg-light-subtle rounded-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <h6 class="fw-bold text-dark mb-1">${Utils.escapeHtml(e.title)}</h6>
                            <div class="text-secondary small fw-medium">
                                <i class="bi bi-building me-1"></i>${Utils.escapeHtml(e.company)} 
                                <span class="mx-1">•</span>
                                <span class="badge badge-soft-primary">${Utils.escapeHtml(e.role_type || 'Dự án')}</span>
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-1">
                            <button class="btn btn-sm btn-outline-secondary py-1 px-2" title="Sửa" onclick="openEditExpModal(${e.id})">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger py-1 px-2" title="Xóa" onclick="deleteExp(${e.id})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="text-muted small mb-2"><i class="bi bi-calendar3 me-1"></i>${timeSpan}</div>
                    <p class="text-secondary small mb-0">${Utils.escapeHtml(e.description || 'Không có mô tả chi tiết.')}</p>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

function openAddExpModal() {
    document.getElementById('expModalTitle').innerHTML = '<i class="bi bi-briefcase text-primary me-2"></i>Thêm kinh nghiệm / dự án';
    document.getElementById('expId').value = '';
    document.getElementById('expTitle').value = '';
    document.getElementById('expCompany').value = '';
    document.getElementById('expRoleType').value = 'Thực tập sinh';
    document.getElementById('expStartDate').value = '';
    document.getElementById('expEndDate').value = '';
    document.getElementById('expDesc').value = '';
    expModal?.show();
}

function openEditExpModal(id) {
    const exp = currentProfile.experiences.find(e => e.id == id);
    if (!exp) return;

    document.getElementById('expModalTitle').innerHTML = '<i class="bi bi-pencil-square text-primary me-2"></i>Chỉnh sửa kinh nghiệm / dự án';
    document.getElementById('expId').value = exp.id;
    document.getElementById('expTitle').value = exp.title || '';
    document.getElementById('expCompany').value = exp.company || '';
    document.getElementById('expRoleType').value = exp.role_type || 'Thực tập sinh';
    document.getElementById('expStartDate').value = exp.start_date || '';
    document.getElementById('expEndDate').value = exp.end_date || '';
    document.getElementById('expDesc').value = exp.description || '';
    expModal?.show();
}

async function handleSaveExp(e) {
    e.preventDefault();
    const id = document.getElementById('expId').value;
    const btn = document.getElementById('btnSaveExp');
    Utils.setButtonLoading(btn, true);

    const payload = {
        title: document.getElementById('expTitle').value.trim(),
        company: document.getElementById('expCompany').value.trim(),
        role_type: document.getElementById('expRoleType').value,
        start_date: document.getElementById('expStartDate').value,
        end_date: document.getElementById('expEndDate').value,
        description: document.getElementById('expDesc').value.trim()
    };

    try {
        let res;
        if (id) {
            res = await API.profile.updateExperience(id, payload);
        } else {
            res = await API.profile.addExperience(payload);
        }

        if (res.success) {
            Utils.showToast(id ? 'Cập nhật kinh nghiệm thành công!' : 'Thêm kinh nghiệm thành công!', 'success');
            expModal?.hide();
            await loadProfileData();
        } else {
            Utils.showToast(res.message || 'Lỗi lưu kinh nghiệm!', 'danger');
        }
    } catch (err) {
        Utils.showToast('Lỗi máy chủ khi lưu kinh nghiệm!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

function deleteExp(id) {
    Utils.confirmModal({
        title: 'Xác nhận xóa kinh nghiệm',
        message: 'Bạn có chắc chắn muốn xóa kinh nghiệm/dự án này?',
        confirmText: 'Xóa kinh nghiệm',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
            const res = await API.profile.deleteExperience(id);
            if (res.success) {
                Utils.showToast('Đã xóa kinh nghiệm/dự án!', 'success');
                await loadProfileData();
            } else {
                Utils.showToast(res.message || 'Xóa thất bại!', 'danger');
            }
        }
    });
}
