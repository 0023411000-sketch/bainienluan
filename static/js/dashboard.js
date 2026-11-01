/**
 * dashboard.js - Xử lý hiển thị số liệu thống kê và biểu đồ tổng quan
 * Đề tài: NLCNPM23CS-38
 */

// Lưu biến instance biểu đồ để hủy (destroy) trước khi vẽ lại
let dashboardChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
});

/**
 * Tải dữ liệu tổng quan từ API
 */
async function loadDashboardData() {
    try {
        const response = await API.dashboard.getSummary();
        if (response.success && response.data) {
            renderMetrics(response.data);
            renderChart(response.data.match_by_positions || []);
            renderRecentTodos(response.data.recent_todos || []);
        } else {
            Utils.showToast(response.message || 'Không thể tải dữ liệu bảng điều khiển!', 'warning');
        }
    } catch (error) {
        console.error('Lỗi tải dashboard:', error);
        Utils.showToast('Lỗi nạp dữ liệu bảng điều khiển!', 'danger');
    }
}

/**
 * Hiển thị 4 thẻ chỉ số thống kê
 */
function renderMetrics(data) {
    const totalSkillsEl = document.getElementById('statTotalSkills');
    const totalCertsEl = document.getElementById('statTotalCerts');
    const highestScoreEl = document.getElementById('statHighestScore');
    const highestPosEl = document.getElementById('statHighestPosition');
    const planProgressEl = document.getElementById('statPlanProgress');
    const planBarEl = document.getElementById('statPlanProgressBar');

    if (totalSkillsEl) totalSkillsEl.textContent = data.total_skills ?? 0;
    if (totalCertsEl) totalCertsEl.textContent = data.total_certificates ?? 0;

    if (data.highest_match) {
        if (highestScoreEl) highestScoreEl.textContent = `${data.highest_match.score}%`;
        if (highestPosEl) {
            highestPosEl.textContent = data.highest_match.name || 'Chưa xác định';
            highestPosEl.title = data.highest_match.name || '';
        }
    }

    const progress = data.plan_progress ?? 0;
    if (planProgressEl) planProgressEl.textContent = `${progress}%`;
    if (planBarEl) {
        planBarEl.style.width = `${progress}%`;
        planBarEl.setAttribute('aria-valuenow', progress);
    }
}

/**
 * Vẽ biểu đồ cột điểm phù hợp theo vị trí bằng Chart.js
 * Chú ý: Luôn kiểm tra và destroy instance cũ để tránh đè biểu đồ
 */
function renderChart(matchList) {
    const canvas = document.getElementById('matchScoreChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Hủy instance cũ nếu đã tồn tại
    if (dashboardChartInstance) {
        dashboardChartInstance.destroy();
    }

    const labels = matchList.map(item => item.name.split('(')[0].trim());
    const dataValues = matchList.map(item => item.score);

    // Bảng màu gradient sinh động tùy theo mức độ điểm
    const backgroundColors = dataValues.map(score => {
        if (score >= 70) return 'rgba(16, 185, 129, 0.85)'; // Xanh lá
        if (score >= 45) return 'rgba(59, 130, 246, 0.85)'; // Xanh dương
        return 'rgba(245, 158, 11, 0.85)';                 // Cam / Vàng
    });

    dashboardChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Mức độ phù hợp (%)',
                data: dataValues,
                backgroundColor: backgroundColors,
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return ` Mức độ phù hợp: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        callback: value => `${value}%`
                    },
                    grid: {
                        color: 'rgba(226, 232, 240, 0.6)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

/**
 * Hiển thị danh sách việc cần làm gần đây
 */
function renderRecentTodos(todos) {
    const listContainer = document.getElementById('recentTodoList');
    if (!listContainer) return;

    if (!todos || todos.length === 0) {
        Utils.renderEmptyState(listContainer, {
            icon: 'bi-check-all',
            title: 'Không còn việc tồn đọng',
            message: 'Tất cả kế hoạch đã hoàn thành hoặc bạn chưa lập kế hoạch mới.'
        });
        return;
    }

    let html = '';
    todos.forEach(item => {
        const statusBadge = item.status === 'doing' 
            ? '<span class="badge badge-soft-warning">Đang học</span>'
            : '<span class="badge badge-soft-secondary">Chưa bắt đầu</span>';

        html += `
            <div class="list-group-item px-3 py-3 border-0 border-bottom d-flex align-items-center justify-content-between gap-2" id="todo-item-${item.id}">
                <div class="d-flex align-items-start gap-2 overflow-hidden">
                    <button class="btn btn-sm btn-outline-success p-1 border-0 mt-0" title="Đánh dấu hoàn thành" onclick="markTodoComplete(${item.id})">
                        <i class="bi bi-circle fs-5"></i>
                    </button>
                    <div class="text-truncate">
                        <div class="fw-semibold text-dark text-truncate small">${Utils.escapeHtml(item.title)}</div>
                        <div class="text-muted small mt-1 d-flex align-items-center gap-2">
                            <span><i class="bi bi-calendar3 me-1"></i>${Utils.formatDate(item.target_date)}</span>
                            ${statusBadge}
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    listContainer.innerHTML = html;
}

/**
 * Đánh dấu nhanh việc cần làm là hoàn thành từ Dashboard
 */
async function markTodoComplete(id) {
    try {
        Utils.showLoading(true, 'Đang cập nhật trạng thái...');
        const res = await API.plan.updateStatus(id, 'done');
        if (res.success) {
            Utils.showToast('Đã đánh dấu hoàn thành mục tiêu!', 'success');
            // Tải lại dữ liệu tổng quan
            await loadDashboardData();
        } else {
            Utils.showToast(res.message || 'Cập nhật thất bại!', 'danger');
        }
    } catch (e) {
        Utils.showToast('Lỗi cập nhật trạng thái!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}
