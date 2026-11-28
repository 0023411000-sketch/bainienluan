/**
 * positions.js - Quản lý danh mục vị trí nghề nghiệp & Xem chi tiết mục tiêu vị trí
 * Đề tài: NLCNPM23CS-38
 */

let currentPositionPage = 1;
let currentSearchTerm = '';
let positionModal = null;
let positionDetailModal = null;
let cachedPositions = [];
let currentTargetPositionId = null;
let currentDetailPositionId = null;
let initialUrlDetailHandled = false;

document.addEventListener('DOMContentLoaded', () => {
    const modalEl = document.getElementById('positionModal');
    if (modalEl) {
        positionModal = new bootstrap.Modal(modalEl);
    }
    const detailModalEl = document.getElementById('positionDetailModal');
    if (detailModalEl) {
        positionDetailModal = new bootstrap.Modal(detailModalEl);
    }

    // Phân quyền hiển thị nút Thêm vị trí mới (chỉ Admin)
    const addBtn = document.getElementById('btnOpenAddPositionModal');
    if (addBtn) {
        if (Utils.auth.isAdmin()) {
            addBtn.addEventListener('click', openAddPositionModal);
        } else {
            addBtn.classList.add('d-none');
        }
    }

    // Form submit & nút đặt vị trí mục tiêu
    document.getElementById('positionForm')?.addEventListener('submit', handleSavePosition);
    document.getElementById('btnSetTargetFromDetail')?.addEventListener('click', handleSetTargetFromDetail);

    // Tìm kiếm chỉ bắt đầu khi người dùng nhập xong và nhấn nút Tìm kiếm (hoặc Enter)
    const searchForm = document.getElementById('searchPositionForm');
    const searchInput = document.getElementById('searchPositionInput');
    const clearSearchBtn = document.getElementById('btnClearPositionSearch');

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            currentSearchTerm = (searchInput?.value || '').trim();
            currentPositionPage = 1;
            if (clearSearchBtn) clearSearchBtn.classList.toggle('d-none', !currentSearchTerm);
            loadPositions();
        });
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            currentSearchTerm = '';
            currentPositionPage = 1;
            clearSearchBtn.classList.add('d-none');
            loadPositions();
        });
    }

    loadPositions();
});

function getDemandBadgeHtml(level) {
    if (level === 'Rất cao') return '<span class="badge badge-soft-danger">Rất cao</span>';
    if (level === 'Cao') return '<span class="badge badge-soft-success">Cao</span>';
    if (level === 'Ổn định') return '<span class="badge badge-soft-primary">Ổn định</span>';
    return `<span class="badge badge-soft-warning">${Utils.escapeHtml(level || 'Trung bình')}</span>`;
}

/**
 * Tải danh sách vị trí nghề nghiệp từ API
 */
async function loadPositions() {
    try {
        Utils.showLoading(true, 'Đang tải danh sách vị trí nghề nghiệp...');
        const res = await API.positions.getAll({
            q: currentSearchTerm,
            page: currentPositionPage,
            limit: CONFIG.DEFAULT_PAGE_SIZE
        });

        if (res.success && res.data) {
            cachedPositions = res.data.items || [];
            if (res.data.target_position_id) {
                currentTargetPositionId = Number(res.data.target_position_id);
            }
            document.getElementById('totalPositionsBadge').textContent = res.data.total ?? cachedPositions.length;
            renderPositionsTable(cachedPositions);
            Utils.renderPagination('positionsPaginationContainer', res.data.page, res.data.total_pages, (newPage) => {
                currentPositionPage = newPage;
                loadPositions();
            });

            // Tự động mở chi tiết nếu trên URL có ?id=...
            if (!initialUrlDetailHandled) {
                initialUrlDetailHandled = true;
                const urlId = new URLSearchParams(window.location.search).get('id');
                if (urlId && /^\d+$/.test(urlId)) {
                    openPositionDetailModal(Number(urlId));
                }
            }
        } else {
            Utils.showToast(res.message || 'Không thể tải danh sách vị trí!', 'danger');
        }
    } catch (e) {
        console.error(e);
        Utils.showToast('Lỗi khi tải vị trí nghề nghiệp!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}

/**
 * Hiển thị bảng vị trí
 */
function renderPositionsTable(items) {
    const tbody = document.getElementById('positionsTableBody');
    if (!tbody) return;

    if (items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-5 text-muted">Không tìm thấy vị trí nghề nghiệp nào phù hợp.</td></tr>`;
        return;
    }

    let html = '';
    items.forEach((p, index) => {
        const allSkills = p.core_skills || [];
        const skillsBadges = allSkills.slice(0, 5).map(s =>
            `<span class="badge badge-soft-primary me-1 mb-1">${Utils.escapeHtml(s)}</span>`
        ).join('') + (allSkills.length > 5
            ? `<span class="badge bg-light text-primary border" role="button" title="Xem đầy đủ ${allSkills.length} kỹ năng" onclick="openPositionDetailModal(${p.id})">+${allSkills.length - 5}</span>`
            : '');

        const demandBadge = getDemandBadgeHtml(p.demand_level);
        const isTarget = currentTargetPositionId && Number(p.id) === Number(currentTargetPositionId);
        const targetBadge = isTarget
            ? `<span class="badge bg-primary-subtle text-primary border border-primary-subtle ms-1"><i class="bi bi-bullseye me-1"></i>Mục tiêu</span>`
            : '';

        html += `
            <tr>
                <td class="text-muted small">${(currentPositionPage - 1) * CONFIG.DEFAULT_PAGE_SIZE + index + 1}</td>
                <td>
                    <div class="d-flex flex-wrap align-items-center gap-1">
                        <a href="javascript:void(0)" class="fw-bold text-dark text-decoration-none" onclick="openPositionDetailModal(${p.id})" title="Xem chi tiết vị trí">
                            ${Utils.escapeHtml(p.name)}
                        </a>
                        ${targetBadge}
                    </div>
                    <small class="text-muted">${Utils.escapeHtml(p.code || '')} - ${Utils.escapeHtml(p.description || '')}</small>
                </td>
                <td>${skillsBadges}</td>
                <td>${demandBadge}</td>
                <td class="text-end text-nowrap">
                    <button class="btn btn-sm btn-outline-primary py-1 px-2 me-1" title="Xem chi tiết vị trí nghề nghiệp" onclick="openPositionDetailModal(${p.id})">
                        <i class="bi bi-eye me-1"></i>Chi tiết
                    </button>
                    <a href="/statistics?position_id=${p.id}" class="btn btn-sm btn-outline-info py-1 px-2 me-1" title="Xem thống kê kỹ năng">
                        <i class="bi bi-bar-chart"></i>
                    </a>
                    ${Utils.auth.isAdmin() ? `
                    <button class="btn btn-sm btn-outline-secondary py-1 px-2 me-1" title="Sửa" onclick="openEditPositionModal(${p.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger py-1 px-2" title="Xóa" onclick="deletePosition(${p.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                    ` : ''}
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

/**
 * Mở Modal Xem chi tiết vị trí nghề nghiệp
 */
async function openPositionDetailModal(id) {
    currentDetailPositionId = Number(id);
    try {
        Utils.showLoading(true, 'Đang tải chi tiết vị trí nghề nghiệp...');
        const res = await API.positions.getById(id);
        if (!res.success || !res.data) {
            Utils.showToast(res.message || 'Không thể tải thông tin vị trí!', 'danger');
            return;
        }
        const pos = res.data;
        const evalData = pos.evaluation || null;

        document.getElementById('detailPosCode').textContent = pos.code || `POS_${pos.id}`;
        document.getElementById('detailPosDemandBadge').innerHTML = getDemandBadgeHtml(pos.demand_level);
        document.getElementById('detailPosName').textContent = pos.name || '';
        document.getElementById('detailPosDesc').textContent = pos.description || 'Chưa có mô tả chi tiết.';

        const isTarget = Boolean(pos.is_target_position || (currentTargetPositionId && Number(pos.id) === Number(currentTargetPositionId)));
        const targetBadgeEl = document.getElementById('detailPosTargetBadge');
        const setTargetBtn = document.getElementById('btnSetTargetFromDetail');
        if (targetBadgeEl) {
            targetBadgeEl.classList.toggle('d-none', !isTarget);
        }
        if (setTargetBtn) {
            if (isTarget) {
                setTargetBtn.disabled = true;
                setTargetBtn.className = 'btn btn-success btn-sm';
                setTargetBtn.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Đang là vị trí mục tiêu';
            } else {
                setTargetBtn.disabled = false;
                setTargetBtn.className = 'btn btn-outline-primary btn-sm';
                setTargetBtn.innerHTML = '<i class="bi bi-bullseye me-1"></i>Chọn làm vị trí mục tiêu';
            }
        }

        // Khối đánh giá phù hợp với hồ sơ sinh viên
        const fitBox = document.getElementById('detailPosFitBox');
        const haveSet = new Set((evalData?.have || []).map(s => s.toLowerCase()));
        if (fitBox) {
            if (evalData) {
                fitBox.classList.remove('d-none');
                const score = evalData.score ?? 0;
                document.getElementById('detailPosScore').textContent = `${score}%`;
                const bar = document.getElementById('detailPosProgressBar');
                if (bar) {
                    bar.style.width = `${score}%`;
                    bar.className = score >= 75 ? 'progress-bar bg-success' : (score >= 50 ? 'progress-bar bg-primary' : 'progress-bar bg-warning');
                }
                document.getElementById('detailPosHaveCount').textContent = (evalData.have || []).length;
                document.getElementById('detailPosMissingCount').textContent = (evalData.missing || []).length;
                const exp = evalData.experience || {};
                document.getElementById('detailPosExpText').textContent = exp.required_years > 0
                    ? `${exp.required_years}+ năm (bạn có ${exp.user_years || 0} năm)`
                    : 'Không bắt buộc (Phù hợp Fresher/Thực tập)';
            } else {
                fitBox.classList.add('d-none');
            }
        }

        // Toàn bộ danh sách kỹ năng cốt lõi (không cắt bớt)
        const coreSkills = pos.core_skills || [];
        document.getElementById('detailPosSkillTotal').textContent = coreSkills.length;
        const skillsListEl = document.getElementById('detailPosSkillsList');
        if (skillsListEl) {
            if (coreSkills.length === 0) {
                skillsListEl.innerHTML = '<span class="text-muted small">Chưa cập nhật kỹ năng cốt lõi.</span>';
            } else {
                skillsListEl.innerHTML = coreSkills.map(sk => {
                    const sl = sk.toLowerCase();
                    const matched = Array.from(haveSet).some(h => h === sl || h.includes(sl) || sl.includes(h));
                    return matched
                        ? `<span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-2"><i class="bi bi-check-circle-fill me-1"></i>${Utils.escapeHtml(sk)}</span>`
                        : `<span class="badge badge-soft-primary px-2 py-2">${Utils.escapeHtml(sk)}</span>`;
                }).join('');
            }
        }

        // Gợi ý học phần tiêu biểu
        const coursesBox = document.getElementById('detailPosCoursesBox');
        const coursesList = document.getElementById('detailPosCoursesList');
        const suggestedCourses = (evalData?.suggested_academic_courses || []).slice(0, 4);
        if (coursesBox && coursesList) {
            if (suggestedCourses.length > 0) {
                coursesBox.classList.remove('d-none');
                coursesList.innerHTML = suggestedCourses.map(c =>
                    `<span class="badge bg-light text-dark border px-2 py-2"><i class="bi bi-book text-primary me-1"></i>${Utils.escapeHtml(c.code)} - ${Utils.escapeHtml(c.name)}</span>`
                ).join('');
            } else {
                coursesBox.classList.add('d-none');
            }
        }

        // Tin tuyển dụng thực tế của vị trí này
        const relatedJobs = pos.related_jobs || [];
        document.getElementById('detailPosJobTotal').textContent = pos.total_jobs ?? relatedJobs.length;
        const allJobsLink = document.getElementById('detailPosAllJobsLink');
        if (allJobsLink) allJobsLink.href = `/jobs?position_id=${pos.id}`;

        const jobsListEl = document.getElementById('detailPosJobsList');
        if (jobsListEl) {
            if (relatedJobs.length === 0) {
                jobsListEl.innerHTML = `<div class="p-3 text-center text-muted small">Hiện chưa có tin tuyển dụng nào gắn với vị trí này.</div>`;
            } else {
                jobsListEl.innerHTML = relatedJobs.map(j => `
                    <div class="list-group-item d-flex flex-wrap justify-content-between align-items-center gap-2 py-2 px-3">
                        <div>
                            <div class="fw-semibold text-dark small">${Utils.escapeHtml(j.title)}</div>
                            <div class="text-muted" style="font-size: 0.78rem;">
                                <i class="bi bi-building me-1"></i>${Utils.escapeHtml(j.company)}
                                <span class="mx-1">•</span>
                                <i class="bi bi-geo-alt me-1"></i>${Utils.escapeHtml(j.location || 'Toàn quốc')}
                            </div>
                        </div>
                        <span class="badge bg-success-subtle text-success border border-success-subtle">${Utils.escapeHtml(j.salary || 'Thỏa thuận')}</span>
                    </div>
                `).join('');
            }
        }

        // Cập nhật link Đối sánh & Thống kê
        const compareLink = document.getElementById('detailPosCompareLink');
        if (compareLink) compareLink.href = `/compare?position_id=${pos.id}`;
        const statsLink = document.getElementById('detailPosStatsLink');
        if (statsLink) statsLink.href = `/statistics?position_id=${pos.id}`;

        positionDetailModal?.show();
    } catch (e) {
        console.error(e);
        Utils.showToast('Lỗi khi tải chi tiết vị trí nghề nghiệp!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}

/**
 * Đặt vị trí đang xem làm Vị trí nghề nghiệp mục tiêu của sinh viên
 */
async function handleSetTargetFromDetail() {
    if (!currentDetailPositionId) return;
    const btn = document.getElementById('btnSetTargetFromDetail');
    Utils.setButtonLoading(btn, true);
    try {
        let res;
        if (API.profile && typeof API.profile.setTargetPosition === 'function') {
            res = await API.profile.setTargetPosition(currentDetailPositionId);
        } else {
            const raw = await fetch('/api/profile/target-position', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ position_id: currentDetailPositionId })
            });
            res = await raw.json();
        }

        if (res.success) {
            currentTargetPositionId = Number(currentDetailPositionId);
            Utils.showToast(res.message || 'Đã cập nhật vị trí nghề nghiệp mục tiêu!', 'success');
            document.getElementById('detailPosTargetBadge')?.classList.remove('d-none');
            if (btn) {
                btn.disabled = true;
                btn.className = 'btn btn-success btn-sm';
                btn.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Đang là vị trí mục tiêu';
            }
            renderPositionsTable(cachedPositions);
        } else {
            Utils.showToast(res.message || 'Không thể đặt vị trí mục tiêu!', 'danger');
        }
    } catch (err) {
        console.error(err);
        Utils.showToast('Lỗi kết nối máy chủ!', 'danger');
    } finally {
        if (btn && !btn.disabled) {
            Utils.setButtonLoading(btn, false);
        }
    }
}

function openAddPositionModal() {
    document.getElementById('positionModalTitle').innerHTML = '<i class="bi bi-diagram-3 text-primary me-2"></i>Thêm vị trí mới';
    document.getElementById('posId').value = '';
    document.getElementById('posName').value = '';
    document.getElementById('posCode').value = '';
    document.getElementById('posDescription').value = '';
    document.getElementById('posCoreSkills').value = '';
    document.getElementById('posDemandLevel').value = 'Cao';
    positionModal?.show();
}

function openEditPositionModal(id) {
    const pos = cachedPositions.find(p => p.id == id);
    if (!pos) return;

    document.getElementById('positionModalTitle').innerHTML = '<i class="bi bi-pencil-square text-primary me-2"></i>Chỉnh sửa vị trí';
    document.getElementById('posId').value = pos.id;
    document.getElementById('posName').value = pos.name || '';
    document.getElementById('posCode').value = pos.code || '';
    document.getElementById('posDescription').value = pos.description || '';
    document.getElementById('posCoreSkills').value = Array.isArray(pos.core_skills) ? pos.core_skills.join(', ') : (pos.core_skills || '');
    document.getElementById('posDemandLevel').value = pos.demand_level || 'Cao';
    positionModal?.show();
}

async function handleSavePosition(e) {
    e.preventDefault();
    const id = document.getElementById('posId').value;
    const btn = document.getElementById('btnSavePosition');
    Utils.setButtonLoading(btn, true);

    const payload = {
        name: document.getElementById('posName').value.trim(),
        code: document.getElementById('posCode').value.trim(),
        description: document.getElementById('posDescription').value.trim(),
        core_skills: document.getElementById('posCoreSkills').value.trim(),
        demand_level: document.getElementById('posDemandLevel').value
    };

    try {
        let res;
        if (id) {
            res = await API.positions.update(id, payload);
        } else {
            res = await API.positions.create(payload);
        }

        if (res.success) {
            Utils.showToast(id ? 'Cập nhật vị trí thành công!' : 'Thêm vị trí mới thành công!', 'success');
            positionModal?.hide();
            await loadPositions();
        } else {
            Utils.showToast(res.message || 'Lỗi lưu vị trí!', 'danger');
        }
    } catch (err) {
        Utils.showToast('Lỗi máy chủ khi lưu vị trí!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

function deletePosition(id) {
    Utils.confirmModal({
        title: 'Xác nhận xóa vị trí',
        message: 'Bạn có chắc chắn muốn xóa vị trí nghề nghiệp này? Việc này có thể ảnh hưởng đến các tin tuyển dụng liên quan.',
        confirmText: 'Xóa vị trí',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
            const res = await API.positions.delete(id);
            if (res.success) {
                Utils.showToast('Đã xóa vị trí thành công!', 'success');
                await loadPositions();
            } else {
                Utils.showToast(res.message || 'Xóa thất bại!', 'danger');
            }
        }
    });
}
