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

    // Chuyển nhanh sang tab gợi ý môn học
    document.getElementById('btnGoToSuggestionsTab')?.addEventListener('click', () => {
        const tabBtn = document.getElementById('suggestions-tab');
        if (tabBtn) {
            const tab = new bootstrap.Tab(tabBtn);
            tab.show();
            tabBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });

    // Gắn sự kiện Submit Forms
    document.getElementById('formPersonalInfo')?.addEventListener('submit', handleSavePersonalInfo);
    document.getElementById('formSkill')?.addEventListener('submit', handleSaveSkill);
    document.getElementById('formCourse')?.addEventListener('submit', handleSaveCourse);
    document.getElementById('formCert')?.addEventListener('submit', handleSaveCert);
    document.getElementById('formExp')?.addEventListener('submit', handleSaveExp);

    // Chặn nhập chữ / ký tự đặc biệt (kể cả bộ gõ Tiếng Việt IME) vào ô Số điện thoại
    const phoneInput = document.getElementById('infoPhone');
    if (phoneInput) {
        const sanitizePhoneInput = () => {
            const cleaned = phoneInput.value.replace(/\D+/g, '').slice(0, 11);
            if (phoneInput.value !== cleaned) {
                phoneInput.value = cleaned;
            }
        };
        phoneInput.addEventListener('keydown', (ev) => {
            if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
            const allowedKeys = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'];
            if (allowedKeys.includes(ev.key)) return;
            if (!/^\d$/.test(ev.key)) {
                ev.preventDefault();
            }
        });
        phoneInput.addEventListener('input', sanitizePhoneInput);
        phoneInput.addEventListener('compositionend', sanitizePhoneInput);
        phoneInput.addEventListener('blur', sanitizePhoneInput);
    }

    // Gắn sự kiện Đổi ảnh đại diện
    const avatarInput = document.getElementById('avatarFileInput');
    document.getElementById('btnQuickChangeAvatar')?.addEventListener('click', () => avatarInput?.click());
    document.getElementById('btnModalUploadAvatar')?.addEventListener('click', () => avatarInput?.click());
    if (avatarInput) {
        avatarInput.addEventListener('change', handleAvatarFileChange);
    }

    // Gắn sự kiện chọn ảnh đại diện mẫu (Presets)
    document.querySelectorAll('.preset-avatar-btn').forEach(btn => {
        btn.addEventListener('click', handleSelectPresetAvatar);
    });

    // Gắn sự kiện Tải CV cá nhân ở tab Kinh nghiệm & gỡ CV trong Modal Kinh nghiệm
    const quickCvInput = document.getElementById('quickCvFileInput');
    document.getElementById('btnQuickUploadCv')?.addEventListener('click', () => quickCvInput?.click());
    if (quickCvInput) {
        quickCvInput.addEventListener('change', handleQuickCvUpload);
    }
    document.getElementById('btnDeleteGeneralCv')?.addEventListener('click', handleDeleteGeneralCv);
    document.getElementById('btnSetTargetFromCv')?.addEventListener('click', handleSetTargetFromCv);
    document.getElementById('expCvFileInput')?.addEventListener('change', handleExpModalCvSelect);
    document.getElementById('btnClearExpCv')?.addEventListener('click', () => {
        const fileEl = document.getElementById('expCvFileInput');
        if (fileEl) fileEl.value = '';
        document.getElementById('expCvUrl').value = '';
        document.getElementById('expCvName').value = '';
        document.getElementById('expCurrentCvBox')?.classList.add('d-none');
        document.getElementById('expModalCvPreviewBox')?.classList.add('d-none');
    });

    // Tải dữ liệu hồ sơ
    loadProfileData();
});

/**
 * Tải toàn bộ hồ sơ sinh viên từ API
 */
async function loadProfileData() {
    try {
        Utils.showLoading(true, 'Đang tải hồ sơ sinh viên...');
        try {
            const posRes = await API.positions.getAll({ limit: 100 });
            if (posRes.success && posRes.data && posRes.data.items) {
                const targetSelect = document.getElementById('infoTargetPosition');
                if (targetSelect && posRes.data.items.length > 0) {
                    targetSelect.innerHTML = posRes.data.items
                        .map(p => `<option value="${p.id}">${Utils.escapeHtml(p.name)}</option>`)
                        .join('');
                }
            }
        } catch (_) {}
        const res = await API.profile.get();
        if (res.success && res.data) {
            currentProfile = res.data;
            renderPersonalInfo(res.data.personal_info);
            renderSkills(res.data.skills || []);
            renderCourses(res.data.courses || []);
            renderCertificates(res.data.certificates || []);
            renderExperiences(res.data.experiences || []);
            renderCvCourseAnalysis(res.data.cv_analysis || null);
            if (res.data.evaluation) {
                renderProfileEvaluation(res.data.evaluation);
            }
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
// 1. XỬ LÝ THÔNG TIN CÁ NHÂN & ẢNH ĐẠI DIỆN
// ==========================================
function updateAvatarDisplay(avatarUrl) {
    const cardImg = document.getElementById('profileAvatarImg');
    const cardIcon = document.getElementById('profileAvatarIcon');
    const modalImg = document.getElementById('modalAvatarPreviewImg');
    const modalIcon = document.getElementById('modalAvatarPreviewIcon');
    const infoAvatarUrl = document.getElementById('infoAvatarUrl');
    const navImg = document.getElementById('navUserAvatarImg');
    const navIcon = document.getElementById('navUserAvatarIcon');

    if (infoAvatarUrl) infoAvatarUrl.value = avatarUrl || '';

    if (avatarUrl) {
        if (cardImg) { cardImg.src = avatarUrl; cardImg.classList.remove('d-none'); }
        if (cardIcon) cardIcon.classList.add('d-none');
        if (modalImg) { modalImg.src = avatarUrl; modalImg.classList.remove('d-none'); }
        if (modalIcon) modalIcon.classList.add('d-none');
        if (navImg) { navImg.src = avatarUrl; navImg.classList.remove('d-none'); }
        if (navIcon) navIcon.classList.add('d-none');
    } else {
        if (cardImg) cardImg.classList.add('d-none');
        if (cardIcon) cardIcon.classList.remove('d-none');
        if (modalImg) modalImg.classList.add('d-none');
        if (modalIcon) modalIcon.classList.remove('d-none');
        if (navImg) navImg.classList.add('d-none');
        if (navIcon) navIcon.classList.remove('d-none');
    }

    // Đánh dấu ảnh mẫu đang chọn nếu khớp URL
    document.querySelectorAll('.preset-avatar-btn').forEach(btn => {
        if (btn.getAttribute('data-avatar') === avatarUrl) {
            btn.classList.add('border-primary', 'shadow');
            btn.classList.remove('border-transparent');
        } else {
            btn.classList.remove('border-primary', 'shadow');
            btn.classList.add('border-transparent');
        }
    });
}

async function handleAvatarFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/svg+xml'];
    if (!validTypes.includes(file.type)) {
        Utils.showToast('Định dạng ảnh không hợp lệ (hỗ trợ JPG, PNG, WEBP, GIF, SVG)!', 'warning');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        Utils.showToast('Kích thước ảnh tối đa là 5MB!', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('avatar', file);

    try {
        Utils.showLoading(true, 'Đang tải lên ảnh đại diện...');
        const res = await API.profile.uploadAvatar(formData);
        if (res.success && res.data && res.data.avatar_url) {
            const newUrl = res.data.avatar_url;
            updateAvatarDisplay(newUrl);

            const currentUser = Utils.auth.getUser() || {};
            Utils.auth.setUser({ ...currentUser, avatar_url: newUrl });

            Utils.showToast('Cập nhật ảnh đại diện thành công!', 'success');
        } else {
            Utils.showToast(res.message || 'Tải lên ảnh thất bại!', 'danger');
        }
    } catch (err) {
        Utils.showToast(err.message || 'Lỗi khi tải ảnh lên máy chủ!', 'danger');
    } finally {
        Utils.showLoading(false);
        e.target.value = '';
    }
}

async function handleSelectPresetAvatar(e) {
    const btn = e.currentTarget;
    const avatarUrl = btn.getAttribute('data-avatar');
    if (!avatarUrl) return;

    try {
        Utils.showLoading(true, 'Đang áp dụng ảnh đại diện mẫu...');
        const res = await API.profile.uploadAvatar({ avatar_url: avatarUrl });
        if (res.success) {
            updateAvatarDisplay(avatarUrl);
            const currentUser = Utils.auth.getUser() || {};
            Utils.auth.setUser({ ...currentUser, avatar_url: avatarUrl });
            Utils.showToast('Đã chọn ảnh đại diện mẫu thành công!', 'success');
        } else {
            Utils.showToast(res.message || 'Không thể áp dụng ảnh mẫu!', 'danger');
        }
    } catch (err) {
        Utils.showToast('Lỗi khi cập nhật ảnh đại diện mẫu!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}

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
    const targetPosEl = document.getElementById('infoTargetPosition');
    if (targetPosEl && info.target_position_id) {
        targetPosEl.value = String(info.target_position_id);
        const selectedOpt = targetPosEl.options[targetPosEl.selectedIndex];
        const sideTargetEl = document.getElementById('profileSideTargetPos');
        if (sideTargetEl && selectedOpt) sideTargetEl.textContent = selectedOpt.textContent;
        const sideDetailLink = document.getElementById('linkSideTargetDetail');
        if (sideDetailLink) sideDetailLink.href = `/positions?id=${info.target_position_id}`;
    }
    const navNameEl = document.getElementById('navUserFullName');
    if (navNameEl && info.full_name) navNameEl.textContent = info.full_name;

    // Cập nhật ảnh đại diện & banner CV chung
    updateAvatarDisplay(info.avatar_url || '');
    renderGeneralCvBanner(info.cv_url || '', info.cv_name || '');

    // Điền vào form Modal chỉnh sửa
    document.getElementById('infoFullName').value = info.full_name || '';
    document.getElementById('infoStudentCode').value = info.student_code || '';
    document.getElementById('infoEmail').value = info.email || '';
    document.getElementById('infoPhone').value = (info.phone || '').replace(/\D+/g, '').slice(0, 11);
    document.getElementById('infoUniversity').value = info.university || '';
    document.getElementById('infoFaculty').value = info.faculty || '';
    document.getElementById('infoMajor').value = info.major || '';
    const academicYearEl = document.getElementById('infoAcademicYear');
    if (academicYearEl) {
        academicYearEl.querySelectorAll('option[data-dynamic-year="true"]').forEach(el => el.remove());
        const yr = (info.academic_year || '').trim();
        if (yr) {
            const exists = Array.from(academicYearEl.options).some(opt => opt.value === yr);
            if (!exists) {
                const customOpt = document.createElement('option');
                customOpt.value = yr;
                customOpt.textContent = yr;
                customOpt.dataset.dynamicYear = 'true';
                academicYearEl.insertBefore(customOpt, academicYearEl.firstChild);
            }
            academicYearEl.value = yr;
        } else {
            academicYearEl.value = '2023 - 2027';
        }
    }
    document.getElementById('infoGpa').value = info.gpa || '';
    document.getElementById('infoBio').value = info.bio || '';
}

async function handleSavePersonalInfo(e) {
    e.preventDefault();
    const phoneEl = document.getElementById('infoPhone');
    const rawPhone = (phoneEl?.value || '').trim();
    const cleanPhone = rawPhone.replace(/\D+/g, '');
    if (rawPhone !== cleanPhone || (cleanPhone && !/^0\d{9,10}$/.test(cleanPhone))) {
        Utils.showToast('Số điện thoại không hợp lệ! Vui lòng chỉ nhập 10–11 chữ số (bắt đầu bằng số 0).', 'warning');
        phoneEl?.focus();
        return;
    }

    const btn = document.getElementById('btnSavePersonalInfo');
    Utils.setButtonLoading(btn, true);

    const payload = {
        full_name: document.getElementById('infoFullName').value.trim(),
        student_code: document.getElementById('infoStudentCode').value.trim(),
        email: document.getElementById('infoEmail').value.trim(),
        phone: cleanPhone,
        university: document.getElementById('infoUniversity').value.trim(),
        faculty: document.getElementById('infoFaculty').value.trim(),
        major: document.getElementById('infoMajor').value.trim(),
        academic_year: document.getElementById('infoAcademicYear').value.trim(),
        gpa: document.getElementById('infoGpa').value.trim(),
        target_position_id: parseInt(document.getElementById('infoTargetPosition')?.value) || 1,
        bio: document.getElementById('infoBio').value.trim(),
        avatar_url: document.getElementById('infoAvatarUrl')?.value?.trim() || ''
    };

    try {
        const res = await API.profile.updatePersonal(payload);
        if (res.success) {
            const currentUser = Utils.auth.getUser() || {};
            Utils.auth.setUser({ ...currentUser, full_name: payload.full_name, email: payload.email, avatar_url: payload.avatar_url });
            renderPersonalInfo(payload);
            personalInfoModal?.hide();
            await loadProfileData();
            const score = currentProfile?.evaluation?.score ?? 0;
            const posName = currentProfile?.evaluation?.target_position?.name || '';
            Utils.showToast(`Đã lưu thông tin cá nhân! Mức độ phù hợp với vị trí "${posName}" hiện tại là ${score}%.`, 'success');
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
function getSkillLevelBadgeHtml(level) {
    const lv = Math.min(Math.max(parseInt(level) || 3, 1), 5);
    const map = {
        1: { label: 'Nhập môn', cls: 'bg-secondary-subtle text-secondary border-secondary-subtle' },
        2: { label: 'Cơ bản', cls: 'bg-info-subtle text-info border-info-subtle' },
        3: { label: 'Khá', cls: 'bg-primary-subtle text-primary border-primary-subtle' },
        4: { label: 'Thành thạo', cls: 'bg-success-subtle text-success border-success-subtle' },
        5: { label: 'Chuyên gia', cls: 'bg-warning-subtle text-warning border-warning-subtle' }
    };
    const item = map[lv] || map[3];
    return `<span class="badge ${item.cls} border px-2 py-1">${item.label}</span>`;
}

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
                <td>${getSkillLevelBadgeHtml(s.level)}</td>
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
    const lvEl = document.getElementById('skillLevel');
    if (lvEl) lvEl.value = '3';
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
    const lvEl = document.getElementById('skillLevel');
    if (lvEl) lvEl.value = String(skill.level || 3);
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
        level: parseInt(document.getElementById('skillLevel')?.value) || 3,
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
            skillModal?.hide();
            await loadProfileData();
            const score = currentProfile?.evaluation?.score ?? 0;
            Utils.showToast(`${id ? 'Cập nhật' : 'Thêm'} kỹ năng thành công! Mức độ phù hợp với nghề nghiệp hiện tại là ${score}%.`, 'success');
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
            courseModal?.hide();
            await loadProfileData();
            const score = currentProfile?.evaluation?.score ?? 0;
            Utils.showToast(`${id ? 'Cập nhật' : 'Thêm'} học phần thành công! Mức độ phù hợp với nghề nghiệp hiện tại là ${score}%.`, 'success');
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
            certModal?.hide();
            await loadProfileData();
            const score = currentProfile?.evaluation?.score ?? 0;
            Utils.showToast(`${id ? 'Cập nhật' : 'Thêm'} chứng chỉ thành công! Mức độ phù hợp với nghề nghiệp hiện tại là ${score}%.`, 'success');
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
// 5. XỬ LÝ KINH NGHIỆM, DỰ ÁN & TẢI CV LÊN + LỌC MÔN HỌC TỪ CV
// ==========================================
let latestCvAnalysis = null;

async function uploadCvFileHelper(file, saveToProfile = false, extraHint = '') {
    const formData = new FormData();
    formData.append('cv', file);
    if (saveToProfile) {
        formData.append('save_to_profile', '1');
    }
    if (extraHint) {
        formData.append('extra_hint', extraHint);
    }
    if (API.profile && typeof API.profile.uploadCv === 'function') {
        return await API.profile.uploadCv(formData);
    }
    const raw = await fetch('/api/profile/cv', { method: 'POST', body: formData });
    return await raw.json();
}

function renderCvCourseAnalysis(analysis) {
    latestCvAnalysis = analysis || null;
    const card = document.getElementById('cvAnalysisCoursesCard');
    if (!card) return;
    if (!analysis || !analysis.detected_position) {
        card.classList.add('d-none');
        return;
    }

    card.classList.remove('d-none');
    const detPos = analysis.detected_position;
    document.getElementById('cvDetectedPositionName').textContent = detPos.name || '';

    const noteEl = document.getElementById('cvAnalysisSourceNote');
    if (noteEl) {
        noteEl.textContent = analysis.matched_from_cv_text
            ? `(Trích xuất từ tệp: ${analysis.cv_name || 'CV'})`
            : `(Tệp ${analysis.cv_name || 'CV'} không chứa văn bản — đang lọc theo định hướng hiện tại)`;
    }

    const currentTargetId = Number(currentProfile?.personal_info?.target_position_id || 0);
    const setTargetBtn = document.getElementById('btnSetTargetFromCv');
    if (setTargetBtn) {
        setTargetBtn.classList.toggle('d-none', Number(detPos.id) === currentTargetId);
    }

    const skillsWrap = document.getElementById('cvDetectedSkillsWrap');
    if (skillsWrap) {
        const detSkills = analysis.detected_skills || [];
        if (detSkills.length > 0) {
            skillsWrap.innerHTML = `<span class="me-1">Kỹ năng phát hiện trong CV:</span>` +
                detSkills.map(s => `<span class="badge bg-success-subtle text-success border border-success-subtle me-1 mb-1">${Utils.escapeHtml(s)}</span>`).join('');
        } else {
            skillsWrap.innerHTML = `<span class="text-muted">Đã lọc danh sách các học phần cốt lõi tương ứng với ngành <strong>${Utils.escapeHtml(detPos.name)}</strong>.</span>`;
        }
    }

    const tbody = document.getElementById('cvFilteredCoursesTbody');
    if (!tbody) return;
    const courses = analysis.filtered_courses || [];
    if (courses.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-3 text-muted">Chưa có học phần gợi ý cho ngành này.</td></tr>`;
        return;
    }

    tbody.innerHTML = courses.map((c, idx) => {
        const matchedBadges = (c.cv_matched_skills || []).map(sk =>
            `<span class="badge bg-success-subtle text-success border border-success-subtle me-1 mb-1" title="Đã có trong CV"><i class="bi bi-check2 me-1"></i>${Utils.escapeHtml(sk)}</span>`
        ).join('');
        const suppBadges = (c.skills_to_supplement || []).slice(0, 4).map(sk =>
            `<span class="badge badge-soft-primary me-1 mb-1" title="Kỹ năng môn học trang bị thêm">${Utils.escapeHtml(sk)}</span>`
        ).join('');

        const actionHtml = c.already_learned
            ? `<span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1"><i class="bi bi-check-circle-fill me-1"></i>Đã hoàn thành</span>`
            : `<div class="btn-group btn-group-sm">
                   <button type="button" class="btn btn-outline-primary py-0 px-2" onclick="addCvCourseToPlanByIdx(${idx})">
                       <i class="bi bi-calendar-plus me-1"></i>Kế hoạch
                   </button>
                   <button type="button" class="btn btn-outline-success py-0 px-2" onclick="markCvCourseLearnedByIdx(${idx})">
                       <i class="bi bi-check2 me-1"></i>Đã học
                   </button>
               </div>`;

        return `
            <tr>
                <td><span class="badge bg-secondary-subtle text-dark border font-monospace">${Utils.escapeHtml(c.code)}</span></td>
                <td>
                    <div class="fw-semibold text-dark">${Utils.escapeHtml(c.name)}</div>
                    <div class="text-muted text-truncate" style="max-width: 260px;" title="${Utils.escapeHtml(c.description || '')}">${Utils.escapeHtml(c.description || '')}</div>
                </td>
                <td class="text-center"><span class="badge bg-light text-dark border">${c.credits || 3} TC</span></td>
                <td>${matchedBadges}${suppBadges}</td>
                <td class="text-end text-nowrap">${actionHtml}</td>
            </tr>
        `;
    }).join('');
}

function addCvCourseToPlanByIdx(idx) {
    const c = latestCvAnalysis?.filtered_courses?.[idx];
    if (!c) return;
    addSuggestedCourseToPlan(c.code, c.name, c.description || `Môn học phù hợp với ngành ${latestCvAnalysis?.detected_position?.name || ''} trích xuất từ CV.`);
}

function markCvCourseLearnedByIdx(idx) {
    const c = latestCvAnalysis?.filtered_courses?.[idx];
    if (!c) return;
    markCourseAsLearned(c.code, c.name, c.credits || 3);
}

async function handleSetTargetFromCv() {
    const posId = latestCvAnalysis?.detected_position?.id;
    if (!posId) return;
    const btn = document.getElementById('btnSetTargetFromCv');
    Utils.setButtonLoading(btn, true);
    try {
        const res = API.profile && typeof API.profile.setTargetPosition === 'function'
            ? await API.profile.setTargetPosition(posId)
            : await (await fetch('/api/profile/target-position', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ position_id: posId })
            })).json();
        if (res.success) {
            Utils.showToast(res.message || 'Đã đồng bộ vị trí mục tiêu theo CV!', 'success');
            await loadProfileData();
        } else {
            Utils.showToast(res.message || 'Không thể cập nhật vị trí mục tiêu!', 'danger');
        }
    } catch (e) {
        Utils.showToast('Lỗi máy chủ!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

async function handleExpModalCvSelect(e) {
    const file = e.target.files?.[0];
    const previewBox = document.getElementById('expModalCvPreviewBox');
    if (!file || !previewBox) return;

    const hint = `${document.getElementById('expTitle')?.value || ''} ${document.getElementById('expDesc')?.value || ''}`.trim();
    previewBox.classList.remove('d-none');
    previewBox.innerHTML = `<span class="text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Đang đọc CV và lọc các môn học phù hợp với ngành...</span>`;

    try {
        const res = await uploadCvFileHelper(file, false, hint);
        if (!res.success || !res.data) {
            previewBox.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle me-1"></i>${Utils.escapeHtml(res.message || 'Không thể phân tích tệp CV!')}</span>`;
            e.target.value = '';
            return;
        }
        document.getElementById('expCvUrl').value = res.data.cv_url || '';
        document.getElementById('expCvName').value = res.data.cv_name || '';

        const currentBox = document.getElementById('expCurrentCvBox');
        const currentLink = document.getElementById('expCurrentCvLink');
        if (currentBox && currentLink) {
            currentBox.classList.remove('d-none');
            currentLink.href = res.data.cv_url;
            currentLink.textContent = res.data.cv_name;
        }
        e.target.value = '';

        const analysis = res.data.cv_analysis;
        if (analysis && analysis.detected_position) {
            renderCvCourseAnalysis(analysis);
            const coursesBadges = (analysis.filtered_courses || []).map(c =>
                `<span class="badge ${c.already_learned ? 'bg-success-subtle text-success border-success-subtle' : 'bg-primary-subtle text-primary border-primary-subtle'} border me-1 mb-1">
                    ${c.already_learned ? '✓ ' : ''}${Utils.escapeHtml(c.code)} - ${Utils.escapeHtml(c.name)}
                 </span>`
            ).join('');
            previewBox.innerHTML = `
                <div class="fw-bold text-dark mb-1">
                    <i class="bi bi-stars text-primary me-1"></i>Ngành nhận diện từ CV:
                    <span class="text-primary">${Utils.escapeHtml(analysis.detected_position.name)}</span>
                </div>
                <div class="text-secondary mb-1">Các môn học phù hợp với ngành trong CV (${analysis.total_courses} môn):</div>
                <div>${coursesBadges || '<span class="text-muted">Chưa có môn học tương ứng</span>'}</div>
            `;
        } else {
            previewBox.classList.add('d-none');
        }
    } catch (err) {
        console.error(err);
        previewBox.innerHTML = `<span class="text-danger">Lỗi kết nối khi phân tích CV!</span>`;
    }
}

function renderGeneralCvBanner(cvUrl, cvName) {
    const banner = document.getElementById('profileGeneralCvBanner');
    if (!banner) return;
    if (!cvUrl) {
        banner.classList.add('d-none');
        return;
    }
    banner.classList.remove('d-none');
    const displayName = cvName || cvUrl.split('/').pop() || 'CV_Sinh_Vien.pdf';
    const nameEl = document.getElementById('profileGeneralCvName');
    const viewBtn = document.getElementById('btnViewGeneralCv');
    const dlBtn = document.getElementById('btnDownloadGeneralCv');
    if (nameEl) {
        nameEl.textContent = displayName;
        nameEl.href = cvUrl;
    }
    if (viewBtn) viewBtn.href = cvUrl;
    if (dlBtn) {
        dlBtn.href = cvUrl;
        dlBtn.setAttribute('download', displayName);
    }
}

async function handleQuickCvUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
        Utils.showLoading(true, 'Đang tải tệp CV lên hệ thống...');
        const res = await uploadCvFileHelper(file, true);
        if (res.success && res.data) {
            if (currentProfile?.personal_info) {
                currentProfile.personal_info.cv_url = res.data.cv_url;
                currentProfile.personal_info.cv_name = res.data.cv_name;
            }
            renderGeneralCvBanner(res.data.cv_url, res.data.cv_name);
            if (res.data.cv_analysis) {
                renderCvCourseAnalysis(res.data.cv_analysis);
            }
            Utils.showToast(res.message || 'Đã tải CV lên thành công!', 'success');
        } else {
            Utils.showToast(res.message || 'Tải CV thất bại!', 'danger');
        }
    } catch (err) {
        console.error(err);
        Utils.showToast('Lỗi kết nối khi tải CV lên!', 'danger');
    } finally {
        e.target.value = '';
        Utils.showLoading(false);
    }
}

function handleDeleteGeneralCv() {
    Utils.confirmModal({
        title: 'Gỡ tệp CV cá nhân',
        message: 'Bạn có chắc chắn muốn gỡ tệp CV đính kèm hiện tại không?',
        confirmText: 'Gỡ CV',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
            const raw = API.profile && typeof API.profile.deleteCv === 'function'
                ? await API.profile.deleteCv()
                : await (await fetch('/api/profile/cv', { method: 'DELETE' })).json();
            if (raw.success) {
                if (currentProfile?.personal_info) {
                    currentProfile.personal_info.cv_url = '';
                    currentProfile.personal_info.cv_name = '';
                }
                renderGeneralCvBanner('', '');
                await loadProfileData();
                Utils.showToast('Đã gỡ tệp CV cá nhân!', 'info');
            } else {
                Utils.showToast(raw.message || 'Không thể gỡ tệp CV!', 'danger');
            }
        }
    });
}

function renderExperiences(exps) {
    const container = document.getElementById('experiencesContainer');
    document.getElementById('countExp').textContent = exps.length;
    if (!container) return;

    if (exps.length === 0) {
        Utils.renderEmptyState(container, {
            icon: 'bi-briefcase',
            title: 'Chưa có kinh nghiệm thực tế',
            message: 'Hãy bổ sung các kỳ thực tập, đồ án nghiên cứu hoặc tải CV của bạn lên!'
        });
        return;
    }

    let html = '';
    exps.forEach(e => {
        const timeSpan = `${Utils.formatDate(e.start_date)} - ${e.end_date ? Utils.formatDate(e.end_date) : 'Hiện tại'}`;
        const cvDisplayName = e.cv_name || (e.cv_url ? e.cv_url.split('/').pop() : '');
        const cvHtml = e.cv_url
            ? `<div class="mt-2 pt-2 border-top d-flex flex-wrap align-items-center gap-2">
                   <a href="${Utils.escapeHtml(e.cv_url)}" target="_blank" class="btn btn-sm btn-outline-primary py-1 px-2 text-decoration-none">
                       <i class="bi bi-file-earmark-person me-1"></i>Xem CV: ${Utils.escapeHtml(cvDisplayName)}
                   </a>
                   <a href="${Utils.escapeHtml(e.cv_url)}" download="${Utils.escapeHtml(cvDisplayName)}" class="btn btn-sm btn-outline-success py-1 px-2" title="Tải CV xuống">
                       <i class="bi bi-download"></i>
                   </a>
               </div>`
            : '';

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
                    ${cvHtml}
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
    const fileEl = document.getElementById('expCvFileInput');
    if (fileEl) fileEl.value = '';
    document.getElementById('expCvUrl').value = '';
    document.getElementById('expCvName').value = '';
    document.getElementById('expCurrentCvBox')?.classList.add('d-none');
    document.getElementById('expModalCvPreviewBox')?.classList.add('d-none');
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

    const fileEl = document.getElementById('expCvFileInput');
    if (fileEl) fileEl.value = '';
    const cvUrl = exp.cv_url || '';
    const cvName = exp.cv_name || (cvUrl ? cvUrl.split('/').pop() : '');
    document.getElementById('expCvUrl').value = cvUrl;
    document.getElementById('expCvName').value = cvName;
    const currentBox = document.getElementById('expCurrentCvBox');
    const currentLink = document.getElementById('expCurrentCvLink');
    if (currentBox && currentLink) {
        if (cvUrl) {
            currentBox.classList.remove('d-none');
            currentLink.href = cvUrl;
            currentLink.textContent = cvName || 'CV_dinh_kem.pdf';
        } else {
            currentBox.classList.add('d-none');
        }
    }
    document.getElementById('expModalCvPreviewBox')?.classList.add('d-none');
    expModal?.show();
}

async function handleSaveExp(e) {
    e.preventDefault();
    const id = document.getElementById('expId').value;
    const btn = document.getElementById('btnSaveExp');
    Utils.setButtonLoading(btn, true);

    try {
        let cvUrl = document.getElementById('expCvUrl')?.value?.trim() || '';
        let cvName = document.getElementById('expCvName')?.value?.trim() || '';
        const cvFile = document.getElementById('expCvFileInput')?.files?.[0];

        if (cvFile) {
            const uploadRes = await uploadCvFileHelper(cvFile, false);
            if (!uploadRes.success || !uploadRes.data) {
                Utils.showToast(uploadRes.message || 'Lỗi tải tệp CV đính kèm!', 'danger');
                return;
            }
            cvUrl = uploadRes.data.cv_url;
            cvName = uploadRes.data.cv_name;
        }

        const payload = {
            title: document.getElementById('expTitle').value.trim(),
            company: document.getElementById('expCompany').value.trim(),
            role_type: document.getElementById('expRoleType').value,
            start_date: document.getElementById('expStartDate').value,
            end_date: document.getElementById('expEndDate').value,
            description: document.getElementById('expDesc').value.trim(),
            cv_url: cvUrl,
            cv_name: cvName
        };

        let res;
        if (id) {
            res = await API.profile.updateExperience(id, payload);
        } else {
            res = await API.profile.addExperience(payload);
        }

        if (res.success) {
            expModal?.hide();
            await loadProfileData();
            const score = currentProfile?.evaluation?.score ?? 0;
            Utils.showToast(`${id ? 'Cập nhật' : 'Thêm'} kinh nghiệm thành công! Mức độ phù hợp với nghề nghiệp hiện tại là ${score}%.`, 'success');
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

// ==========================================
// 6. ĐÁNH GIÁ ĐỘ PHÙ HỢP VỚI NGHỀ VÀ GỢI Ý MÔN HỌC
// ==========================================
function renderProfileEvaluation(evaluation) {
    if (!evaluation) return;

    const score = evaluation.score ?? 0;
    const posName = evaluation.target_position?.name || evaluation.position_name || 'Lập trình viên Backend';
    const demandLevel = evaluation.target_position?.demand_level || 'Nhu cầu cao';
    const haveSkills = evaluation.have || [];
    const missingSkills = evaluation.missing || [];
    const suggestedCourses = evaluation.suggested_academic_courses || [];
    const recommendations = evaluation.recommendations || [];
    const recommendedCerts = evaluation.recommended_certs || [];

    // 1. Cập nhật Tiêu đề và Điểm số trên Card
    const targetNameEl = document.getElementById('evalTargetPositionName');
    if (targetNameEl) targetNameEl.textContent = posName;

    const demandEl = document.getElementById('evalTargetDemand');
    if (demandEl) demandEl.textContent = demandLevel;

    const scoreEl = document.getElementById('evalScorePercent');
    if (scoreEl) scoreEl.textContent = `${score}%`;

    const progBar = document.getElementById('evalProgressBar');
    const circleProg = document.getElementById('evalCircleProgress');
    const badgeEl = document.getElementById('evalScoreBadge');

    let colorClass = 'primary';
    let gradeText = 'Mức độ phù hợp: Khá Tốt';
    let strokeColor = '#0d6efd';

    if (score >= 75) {
        colorClass = 'success';
        gradeText = 'Mức độ phù hợp: Rất Cao';
        strokeColor = '#198754';
    } else if (score >= 50) {
        colorClass = 'primary';
        gradeText = 'Mức độ phù hợp: Khá Tốt';
        strokeColor = '#0d6efd';
    } else {
        colorClass = 'warning';
        gradeText = 'Cần bổ sung thêm kỹ năng';
        strokeColor = '#ffc107';
    }

    if (scoreEl) {
        scoreEl.className = `fs-1 fw-bold lh-1 text-${colorClass}`;
    }
    if (badgeEl) {
        badgeEl.textContent = gradeText;
        badgeEl.className = `small fw-bold text-${colorClass}`;
    }
    if (progBar) {
        progBar.style.width = `${score}%`;
        progBar.className = `progress-bar progress-bar-striped progress-bar-animated bg-${colorClass}`;
    }
    if (circleProg) {
        circleProg.setAttribute('stroke-dasharray', `${score}, 100`);
        circleProg.setAttribute('stroke', strokeColor);
    }

    // Nhận xét tóm tắt từ hệ thống
    const summaryEl = document.getElementById('evalSummaryText');
    if (summaryEl) {
        summaryEl.textContent = evaluation.summary || 'Hệ thống đã hoàn tất phân tích hồ sơ của bạn với dữ liệu tuyển dụng thực tế.';
    }

    // Các thẻ thống kê nhanh
    const countHaveEl = document.getElementById('evalCountHave');
    if (countHaveEl) countHaveEl.textContent = `${haveSkills.length} kỹ năng`;

    const countMissingEl = document.getElementById('evalCountMissing');
    if (countMissingEl) countMissingEl.textContent = `${missingSkills.length} kỹ năng`;

    const expStatusEl = document.getElementById('evalExperienceStatus');
    if (expStatusEl) {
        const exp = evaluation.experience || {};
        if (exp.met) {
            expStatusEl.textContent = 'Đã đáp ứng';
            expStatusEl.className = 'text-success fw-bold fs-6';
        } else {
            expStatusEl.textContent = `Cần ${exp.required_years || 1} năm`;
            expStatusEl.className = 'text-warning fw-bold fs-6';
        }
    }

    const countSugEl = document.getElementById('evalCountSuggested');
    if (countSugEl) countSugEl.textContent = `${suggestedCourses.length} môn`;

    const tabBadge = document.getElementById('countSuggestedCourses');
    if (tabBadge) tabBadge.textContent = suggestedCourses.length;

    const pageBadge = document.getElementById('badgeSuggestedCount');
    if (pageBadge) pageBadge.textContent = `${suggestedCourses.length} môn đề xuất`;

    const posTitleEl = document.getElementById('suggestionsPositionTitle');
    if (posTitleEl) posTitleEl.textContent = posName;

    // 2. Render bảng danh sách Môn học Đại học CNTT gợi ý
    renderSuggestedCourses(suggestedCourses);

    // 3. Render các khóa học trực tuyến & chứng chỉ bổ trợ
    renderSuggestedOnlineCourses(recommendations, recommendedCerts);
}

function renderSuggestedCourses(courses) {
    const tbody = document.getElementById('suggestedCoursesTableBody');
    if (!tbody) return;

    if (!courses || courses.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4 text-success">
                    <i class="bi bi-patch-check-fill fs-3 me-2 align-middle"></i>
                    <strong>Tuyệt vời! Bạn đã hoàn thành các môn học trọng tâm hoặc đã đáp ứng đầy đủ kỹ năng cốt lõi cho vị trí này!</strong>
                </td>
            </tr>
        `;
        return;
    }

    let html = '';
    courses.forEach((c, idx) => {
        const missingBadges = (c.matched_missing_skills || []).map(sk => 
            `<span class="badge badge-soft-danger me-1 mb-1 small"><i class="bi bi-tag me-1"></i>${Utils.escapeHtml(sk)}</span>`
        ).join('');

        const coreBadge = c.is_core ? `<span class="badge badge-soft-primary me-1 mb-1 small"><i class="bi bi-star-fill me-1"></i>Môn chuyên ngành cốt lõi</span>` : '';

        const reasonNote = c.reason ? `<div class="text-muted small mt-1"><i class="bi bi-info-circle me-1"></i>${Utils.escapeHtml(c.reason)}</div>` : '';

        const escapedCode = Utils.escapeHtml(c.code);
        const escapedName = Utils.escapeHtml(c.name);
        const escapedDesc = Utils.escapeHtml(c.description || '');

        html += `
            <tr>
                <td>
                    <span class="badge bg-secondary-subtle text-dark border font-monospace px-2 py-1">${escapedCode}</span>
                </td>
                <td>
                    <div class="fw-bold text-dark">${escapedName}</div>
                    <div class="text-secondary small text-truncate" style="max-width: 280px;" title="${escapedDesc}">${escapedDesc}</div>
                </td>
                <td class="text-center">
                    <span class="badge bg-light text-dark border px-2 py-1 fw-bold">${c.credits || 3} TC</span>
                </td>
                <td>
                    <div>${missingBadges || coreBadge}</div>
                    ${reasonNote}
                </td>
                <td class="text-end">
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-outline-primary" title="Thêm môn này vào kế hoạch học tập" onclick="addSuggestedAcademicByIdx(${idx})">
                            <i class="bi bi-calendar-plus me-1"></i>Vào Kế hoạch
                        </button>
                        <button type="button" class="btn btn-outline-success" title="Đánh dấu đã hoàn thành và lưu điểm" onclick="markCourseLearnedByIdx(${idx})">
                            <i class="bi bi-check2 me-1"></i>Đã học
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function renderSuggestedOnlineCourses(recs, certs) {
    const container = document.getElementById('suggestedOnlineCoursesContainer');
    if (!container) return;

    const normKey = (s) => String(s || '').trim().toLowerCase().replace(/\s+/g, ' ');

    // 1. Lọc và chuẩn hóa danh sách khóa học (loại bỏ trùng lặp tiêu đề và trùng kỹ năng)
    const seenRecs = new Set();
    const seenSkills = new Set();
    const uniqueRecs = [];

    (recs || []).forEach((r, originalIdx) => {
        if (!r || !r.title) return;
        const kTitle = normKey(r.title);
        const kSkill = normKey(r.skill_name);

        if (seenRecs.has(kTitle)) return;

        // Nếu là khóa học thực chiến generic và kỹ năng này đã được bao hàm trong một khóa học khác -> bỏ qua
        const isGeneric = kTitle.includes('khóa học thực chiến');
        if (isGeneric && seenSkills.has(kSkill)) return;

        seenRecs.add(kTitle);
        if (kSkill) seenSkills.add(kSkill);
        uniqueRecs.push({ r, originalIdx });
    });

    // Giới hạn tối đa 6 khóa học gợi ý chất lượng nhất
    const displayRecs = uniqueRecs.slice(0, 6);

    // 2. Hàm kiểm tra xem chứng chỉ có trùng/đã được thể hiện bằng một thẻ khóa học bên dưới không
    const isCertCoveredByRec = (certName, recItem) => {
        const c = normKey(certName);
        const t = normKey(recItem.title);
        const s = normKey(recItem.skill_name);

        if (c === t || t.includes(c) || c.includes(t)) return true;
        if (c.includes('cka') && (t.includes('cka') || t.includes('kubernetes'))) return true;
        if (c.includes('pl-300') && (t.includes('pl-300') || t.includes('power bi'))) return true;
        if (c.includes('meta') && (t.includes('meta') || t.includes('react'))) return true;
        if (c.includes('aws') && (t.includes('aws') || s.includes('aws'))) return true;
        if ((c.includes('rhcsa') || c.includes('linux')) && (t.includes('linux') || s.includes('linux'))) return true;
        if (c.includes('istqb') && (t.includes('istqb') || t.includes('test') || s.includes('test'))) return true;
        if (c.includes('tableau') && (t.includes('tableau') || s.includes('tableau'))) return true;
        if (c.includes('pcep') && (t.includes('pcep') || s.includes('python'))) return true;
        if (c.includes('deeplearning') && (t.includes('deep learning') || s.includes('pytorch') || s.includes('tensorflow'))) return true;
        return false;
    };

    // 3. Lọc danh sách chứng chỉ: chỉ giữ lại chứng chỉ độc lập CHƯA được hiển thị thành thẻ bên dưới
    const seenCerts = new Set();
    const standaloneCerts = (certs || []).filter(crt => {
        const k = normKey(crt);
        if (!k || seenCerts.has(k)) return false;
        seenCerts.add(k);
        // Nếu chứng chỉ này đã có một thẻ khóa học tương ứng bên dưới -> không hiển thị lặp ở khung trên
        const isCovered = displayRecs.some(({ r }) => isCertCoveredByRec(crt, r));
        return !isCovered;
    });

    // Chỉ hiển thị khung chứng chỉ nếu còn chứng chỉ độc lập cần bổ sung
    let certsHtml = '';
    if (standaloneCerts.length > 0) {
        certsHtml = `
            <div class="col-12 mb-2">
                <div class="p-3 bg-light-subtle border rounded-3">
                    <div class="small fw-semibold text-dark mb-2">
                        <i class="bi bi-award-fill text-warning me-1"></i>Chứng chỉ chuyên môn ưu tiên bổ sung:
                    </div>
                    <div>
                        ${standaloneCerts.map(crt => `<span class="badge bg-warning-subtle text-dark border border-warning-subtle me-2 mb-1 p-2"><i class="bi bi-patch-check text-warning me-1"></i>${Utils.escapeHtml(crt)}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    if (displayRecs.length === 0 && standaloneCerts.length === 0) {
        container.innerHTML = `<div class="col-12 text-muted small p-2">Không có khóa học trực tuyến bổ trợ nào thêm.</div>`;
        return;
    }

    let recsHtml = displayRecs.map(({ r, originalIdx: idx }) => {
        const titleEscaped = Utils.escapeHtml(r.title);
        const skillEscaped = Utils.escapeHtml(r.skill_name || 'Kỹ năng CNTT');
        const isCertType = r.rec_type === 'certificate' || (r.title && (r.title.includes('Certificate') || r.title.includes('Certification') || r.title.includes('CKA') || r.title.includes('PL-300') || r.title.includes('Specialization')));
        const typeBadge = isCertType
            ? `<span class="badge bg-warning-subtle text-dark border border-warning-subtle small me-1"><i class="bi bi-award-fill text-warning me-1"></i>Chứng chỉ nghề nghiệp</span>`
            : '';

        return `
            <div class="col-md-6">
                <div class="border rounded-3 p-3 bg-white h-100 d-flex flex-column justify-content-between shadow-sm">
                    <div>
                        <div class="d-flex justify-content-between align-items-start gap-2 flex-wrap mb-2">
                            <div class="d-flex flex-wrap gap-1 min-w-0">
                                <span class="badge badge-soft-danger text-truncate"><i class="bi bi-tag-fill me-1"></i>${skillEscaped}</span>
                                ${typeBadge}
                            </div>
                            <span class="badge bg-secondary-subtle text-secondary border small flex-shrink-0">${Utils.escapeHtml(r.provider || 'Coursera / Udemy')}</span>
                        </div>
                        <h6 class="fw-bold text-dark mb-1">${titleEscaped}</h6>
                        <p class="text-secondary small mb-3">${Utils.escapeHtml(r.description || 'Khóa học bồi dưỡng kỹ năng thực tế theo yêu cầu tuyển dụng.')}</p>
                    </div>
                    <div class="d-flex justify-content-between align-items-center pt-2 border-top">
                        <span class="text-muted small"><i class="bi bi-clock me-1"></i>${Utils.escapeHtml(r.duration || '4 tuần')}</span>
                        <div class="btn-group btn-group-sm">
                            <button type="button" class="btn btn-outline-primary" onclick="addSuggestedOnlineByIdx(${idx})">
                                <i class="bi bi-calendar-plus me-1"></i>Lên kế hoạch
                            </button>
                            <a href="${Utils.escapeHtml(r.url || 'https://www.coursera.org')}" target="_blank" class="btn btn-light border" title="Xem khóa học">
                                <i class="bi bi-box-arrow-up-right"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = certsHtml + recsHtml;
}

function addSuggestedAcademicByIdx(idx) {
    const c = currentProfile?.evaluation?.suggested_academic_courses?.[idx];
    if (!c) return;
    addSuggestedCourseToPlan(c.code, c.name, c.description || c.reason || '');
}

function markCourseLearnedByIdx(idx) {
    const c = currentProfile?.evaluation?.suggested_academic_courses?.[idx];
    if (!c) return;
    markCourseAsLearned(c.code, c.name, c.credits || 3);
}

function addSuggestedOnlineByIdx(idx) {
    const r = currentProfile?.evaluation?.recommendations?.[idx];
    if (!r) return;
    addSuggestedCourseToPlan(r.skill_name || 'Khóa học', r.title, r.description || '');
}

async function addSuggestedCourseToPlan(code, name, description) {
    try {
        Utils.showLoading(true, 'Đang thêm vào kế hoạch học tập...');
        const payload = {
            title: `Học phần: ${name} (${code})`,
            category: 'Học phần đại học',
            type: 'course',
            status: 'todo',
            target_date: '2026-12-31',
            note: description || `Môn học đề xuất cho vị trí mục tiêu.`
        };
        const res = await API.plan.create(payload);
        if (res.success) {
            Utils.showToast(`Đã thêm môn "${name}" vào Kế hoạch học tập!`, 'success');
        } else {
            Utils.showToast(res.message || 'Không thể thêm vào kế hoạch!', 'danger');
        }
    } catch (e) {
        console.error(e);
        Utils.showToast('Lỗi khi thêm môn học vào kế hoạch!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}

function markCourseAsLearned(code, name, credits) {
    document.getElementById('courseModalTitle').innerHTML = '<i class="bi bi-book text-success me-2"></i>Ghi nhận hoàn thành học phần';
    document.getElementById('courseId').value = '';
    document.getElementById('courseCode').value = code;
    document.getElementById('courseName').value = name;
    document.getElementById('courseCredits').value = credits || 3;
    document.getElementById('courseGrade').value = 'A';
    document.getElementById('courseTerm').value = '';
    courseModal?.show();
}
