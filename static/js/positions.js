/**
 * positions.js - Quản lý danh mục vị trí nghề nghiệp
 * Đề tài: NLCNPM23CS-38
 */

let currentPositionPage = 1;
let currentSearchTerm = '';
let positionModal = null;
let cachedPositions = [];

document.addEventListener('DOMContentLoaded', () => {
    const modalEl = document.getElementById('positionModal');
    if (modalEl) {
        positionModal = new bootstrap.Modal(modalEl);
    }

    // Nút mở Modal thêm mới
    document.getElementById('btnOpenAddPositionModal')?.addEventListener('click', openAddPositionModal);

    // Form submit
    document.getElementById('positionForm')?.addEventListener('submit', handleSavePosition);

    // Tìm kiếm với Debounce 300ms
    const searchInput = document.getElementById('searchPositionInput');
    if (searchInput) {
        searchInput.addEventListener('input', Utils.debounce((e) => {
            currentSearchTerm = e.target.value.trim();
            currentPositionPage = 1;
            loadPositions();
        }, 300));
    }

    loadPositions();
});

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
            document.getElementById('totalPositionsBadge').textContent = res.data.total ?? cachedPositions.length;
            renderPositionsTable(cachedPositions);
            Utils.renderPagination('positionsPaginationContainer', res.data.page, res.data.total_pages, (newPage) => {
                currentPositionPage = newPage;
                loadPositions();
            });
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
        const skillsBadges = (p.core_skills || []).slice(0, 5).map(s => 
            `<span class="badge badge-soft-primary me-1 mb-1">${Utils.escapeHtml(s)}</span>`
        ).join('') + ((p.core_skills || []).length > 5 ? `<span class="badge bg-light text-secondary border">+${p.core_skills.length - 5}</span>` : '');

        let demandBadge = '<span class="badge badge-soft-warning">Trung bình</span>';
        if (p.demand_level === 'Rất cao') demandBadge = '<span class="badge badge-soft-danger">Rất cao</span>';
        else if (p.demand_level === 'Cao') demandBadge = '<span class="badge badge-soft-success">Cao</span>';

        html += `
            <tr>
                <td class="text-muted small">${(currentPositionPage - 1) * CONFIG.DEFAULT_PAGE_SIZE + index + 1}</td>
                <td>
                    <div class="fw-bold text-dark">${Utils.escapeHtml(p.name)}</div>
                    <small class="text-muted">${Utils.escapeHtml(p.code || '')} - ${Utils.escapeHtml(p.description || '')}</small>
                </td>
                <td>${skillsBadges}</td>
                <td>${demandBadge}</td>
                <td class="text-end">
                    <a href="/statistics?position_id=${p.id}" class="btn btn-sm btn-outline-info py-1 px-2 me-1" title="Xem thống kê">
                        <i class="bi bi-bar-chart"></i>
                    </a>
                    <button class="btn btn-sm btn-outline-secondary py-1 px-2 me-1" title="Sửa" onclick="openEditPositionModal(${p.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger py-1 px-2" title="Xóa" onclick="deletePosition(${p.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
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
