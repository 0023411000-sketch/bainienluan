/**
 * plan.js - Gợi ý và theo dõi kế hoạch phát triển kỹ năng cá nhân
 * Đề tài: NLCNPM23CS-38
 */

let allPlans = [];
let currentFilterStatus = 'all';
let planModal = null;

document.addEventListener('DOMContentLoaded', () => {
    const modalEl = document.getElementById('planModal');
    if (modalEl) planModal = new bootstrap.Modal(modalEl);

    // Gắn sự kiện các nút
    document.getElementById('btnOpenAddPlanModal')?.addEventListener('click', openAddPlanModal);
    document.getElementById('planForm')?.addEventListener('submit', handleSavePlan);

    // Bộ lọc trạng thái
    const filterGroup = document.getElementById('planStatusFilterGroup');
    if (filterGroup) {
        filterGroup.querySelectorAll('button[data-status]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                filterGroup.querySelectorAll('button').forEach(b => b.classList.remove('active', 'btn-primary'));
                e.currentTarget.classList.add('active');
                currentFilterStatus = e.currentTarget.getAttribute('data-status');
                renderPlanCards();
            });
        });
    }

    // Tải dữ liệu ban đầu
    loadPlanData();
});

/**
 * Tải danh sách kế hoạch từ API
 */
async function loadPlanData() {
    try {
        Utils.showLoading(true, 'Đang tải kế hoạch học tập...');
        const res = await API.plan.getAll();
        if (res.success && res.data) {
            allPlans = res.data || [];
            updatePlanStatistics();
            renderPlanCards();
        } else {
            Utils.showToast(res.message || 'Không thể tải kế hoạch!', 'danger');
        }
    } catch (e) {
        console.error(e);
        Utils.showToast('Lỗi khi nạp dữ liệu kế hoạch!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}

/**
 * Cập nhật thanh tiến độ và số lượng thống kê
 */
function updatePlanStatistics() {
    const total = allPlans.length;
    const done = allPlans.filter(p => p.status === 'done').length;
    const doing = allPlans.filter(p => p.status === 'doing').length;
    const todo = allPlans.filter(p => p.status === 'todo').length;

    const percent = total > 0 ? Math.round((done / total) * 100) : 0;

    document.getElementById('planOverallPercent').textContent = `${percent}%`;
    const barEl = document.getElementById('planOverallBar');
    if (barEl) {
        barEl.style.width = `${percent}%`;
        barEl.setAttribute('aria-valuenow', percent);
    }

    document.getElementById('countTotalPlan').textContent = total;
    document.getElementById('countDonePlan').textContent = done;
    document.getElementById('countDoingPlan').textContent = doing;
    document.getElementById('countTodoPlan').textContent = todo;
}

/**
 * Hiển thị danh sách thẻ mục tiêu kế hoạch
 */
function renderPlanCards() {
    const container = document.getElementById('planItemsContainer');
    if (!container) return;

    let items = allPlans;
    if (currentFilterStatus !== 'all') {
        items = allPlans.filter(p => p.status === currentFilterStatus);
    }

    if (items.length === 0) {
        Utils.renderEmptyState(container, {
            icon: 'bi-calendar2-x',
            title: 'Không có mục tiêu nào trong mục này',
            message: 'Bấm nút "Thêm mục tiêu mới" ở trên để xây dựng lộ trình rèn luyện cho bản thân.'
        });
        return;
    }

    let html = '';
    items.forEach(item => {
        // Trạng thái & Style
        let statusBadge = '<span class="badge badge-soft-secondary">Chưa bắt đầu</span>';
        let cardBorderClass = '';
        if (item.status === 'doing') {
            statusBadge = '<span class="badge badge-soft-warning"><i class="bi bi-hourglass-split me-1"></i>Đang học</span>';
            cardBorderClass = 'border-warning';
        } else if (item.status === 'done') {
            statusBadge = '<span class="badge badge-soft-success"><i class="bi bi-check-all me-1"></i>Hoàn thành</span>';
            cardBorderClass = 'border-success';
        }

        // Icon theo loại hình
        let typeIcon = 'bi-tools';
        if (item.type === 'certificate') typeIcon = 'bi-award-fill text-warning';
        else if (item.type === 'project') typeIcon = 'bi-laptop text-primary';
        else if (item.type === 'course') typeIcon = 'bi-book text-info';

        html += `
            <div class="col-md-6 col-xl-4" id="plan-card-${item.id}">
                <div class="card h-100 shadow-sm border ${cardBorderClass} bg-white p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="badge bg-light text-secondary border small">
                            <i class="bi ${typeIcon} me-1"></i>${Utils.escapeHtml(item.category || 'Mục tiêu')}
                        </span>
                        <!-- Dropdown chuyển trạng thái nhanh -->
                        <div class="dropdown">
                            <button class="btn btn-sm btn-light border py-0 px-2 dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                ${statusBadge}
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 small">
                                <li><a class="dropdown-item py-1" href="javascript:void(0)" onclick="quickChangeStatus(${item.id}, 'todo')"><i class="bi bi-circle me-2 text-secondary"></i>Chưa bắt đầu</a></li>
                                <li><a class="dropdown-item py-1" href="javascript:void(0)" onclick="quickChangeStatus(${item.id}, 'doing')"><i class="bi bi-hourglass-split me-2 text-warning"></i>Đang học</a></li>
                                <li><a class="dropdown-item py-1" href="javascript:void(0)" onclick="quickChangeStatus(${item.id}, 'done')"><i class="bi bi-check-circle-fill me-2 text-success"></i>Hoàn thành</a></li>
                            </ul>
                        </div>
                    </div>

                    <h6 class="fw-bold text-dark my-2" style="min-height: 42px;">
                        ${Utils.escapeHtml(item.title)}
                    </h6>

                    <p class="text-secondary small mb-3 flex-grow-1" style="min-height: 40px;">
                        ${Utils.escapeHtml(item.note || 'Không có ghi chú thêm.')}
                    </p>

                    <div class="border-top pt-2 d-flex align-items-center justify-content-between text-muted small">
                        <span><i class="bi bi-calendar-event me-1"></i>Hạn: ${Utils.formatDate(item.target_date)}</span>
                        <div class="d-flex gap-1">
                            <button class="btn btn-sm btn-outline-secondary py-0 px-2" title="Chỉnh sửa" onclick="openEditPlanModal(${item.id})">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger py-0 px-2" title="Xóa" onclick="deletePlan(${item.id})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

/**
 * Đổi nhanh trạng thái một mục kế hoạch
 */
async function quickChangeStatus(id, newStatus) {
    try {
        Utils.showLoading(true, 'Đang cập nhật trạng thái mục tiêu...');
        const res = await API.plan.updateStatus(id, newStatus);
        if (res.success) {
            Utils.showToast('Đã cập nhật trạng thái kế hoạch!', 'success');
            await loadPlanData();
        } else {
            Utils.showToast(res.message || 'Cập nhật thất bại!', 'danger');
        }
    } catch (e) {
        Utils.showToast('Lỗi máy chủ khi cập nhật!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}

function openAddPlanModal() {
    document.getElementById('planModalTitle').innerHTML = '<i class="bi bi-card-checklist text-primary me-2"></i>Thêm mục tiêu mới';
    document.getElementById('planId').value = '';
    document.getElementById('planTitle').value = '';
    document.getElementById('planCategory').value = 'Kỹ năng chuyên môn';
    document.getElementById('planType').value = 'skill';
    document.getElementById('planStatus').value = 'todo';
    document.getElementById('planTargetDate').value = '2026-12-31';
    document.getElementById('planNote').value = '';
    planModal?.show();
}

function openEditPlanModal(id) {
    const item = allPlans.find(p => p.id == id);
    if (!item) return;

    document.getElementById('planModalTitle').innerHTML = '<i class="bi bi-pencil-square text-primary me-2"></i>Chỉnh sửa mục tiêu';
    document.getElementById('planId').value = item.id;
    document.getElementById('planTitle').value = item.title || '';
    document.getElementById('planCategory').value = item.category || '';
    document.getElementById('planType').value = item.type || 'skill';
    document.getElementById('planStatus').value = item.status || 'todo';
    document.getElementById('planTargetDate').value = item.target_date || '';
    document.getElementById('planNote').value = item.note || '';
    planModal?.show();
}

async function handleSavePlan(e) {
    e.preventDefault();
    const id = document.getElementById('planId').value;
    const btn = document.getElementById('btnSavePlan');
    Utils.setButtonLoading(btn, true);

    const payload = {
        title: document.getElementById('planTitle').value.trim(),
        category: document.getElementById('planCategory').value.trim(),
        type: document.getElementById('planType').value,
        status: document.getElementById('planStatus').value,
        target_date: document.getElementById('planTargetDate').value,
        note: document.getElementById('planNote').value.trim()
    };

    try {
        let res;
        if (id) {
            res = await API.plan.update(id, payload);
        } else {
            res = await API.plan.create(payload);
        }

        if (res.success) {
            Utils.showToast(id ? 'Cập nhật mục tiêu thành công!' : 'Thêm mục tiêu mới thành công!', 'success');
            planModal?.hide();
            await loadPlanData();
        } else {
            Utils.showToast(res.message || 'Lỗi lưu mục tiêu!', 'danger');
        }
    } catch (err) {
        Utils.showToast('Lỗi máy chủ khi lưu mục tiêu!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

function deletePlan(id) {
    Utils.confirmModal({
        title: 'Xác nhận xóa mục tiêu',
        message: 'Bạn có chắc chắn muốn xóa mục tiêu này khỏi kế hoạch?',
        confirmText: 'Xóa mục tiêu',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
            const res = await API.plan.delete(id);
            if (res.success) {
                Utils.showToast('Đã xóa mục tiêu khỏi kế hoạch!', 'success');
                await loadPlanData();
            } else {
                Utils.showToast(res.message || 'Xóa thất bại!', 'danger');
            }
        }
    });
}
