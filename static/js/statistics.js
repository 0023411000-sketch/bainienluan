/**
 * statistics.js - Hiển thị biểu đồ thống kê kỹ năng và công nghệ theo vị trí tuyển dụng
 * Đề tài: NLCNPM23CS-38
 */

// Lưu thể hiện hai biểu đồ Chart.js để hủy trước khi vẽ lại
let skillsBarChartInstance = null;
let techPieChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    initStatisticsPage();
});

/**
 * Khởi tạo trang thống kê
 */
async function initStatisticsPage() {
    await loadPositionsDropdown();

    const selectEl = document.getElementById('statPositionSelect');
    if (selectEl) {
        selectEl.addEventListener('change', (e) => {
            loadStatisticsForPosition(e.target.value);
        });

        // Đọc tham số URL ?position_id= nếu có
        const urlParams = new URLSearchParams(window.location.search);
        const paramId = urlParams.get('position_id');
        if (paramId && selectEl.querySelector(`option[value="${paramId}"]`)) {
            selectEl.value = paramId;
        }

        // Tải vị trí đang chọn
        if (selectEl.value) {
            loadStatisticsForPosition(selectEl.value);
        }
    }
}

/**
 * Nạp danh mục vị trí vào dropdown
 */
async function loadPositionsDropdown() {
    try {
        const res = await API.positions.getAll({ limit: 100 });
        if (res.success && res.data) {
            const selectEl = document.getElementById('statPositionSelect');
            if (!selectEl) return;
            selectEl.innerHTML = '';

            const items = res.data.items || [];
            items.forEach((pos, idx) => {
                const opt = document.createElement('option');
                opt.value = pos.id;
                opt.textContent = pos.name;
                if (idx === 0) opt.selected = true;
                selectEl.appendChild(opt);
            });
        }
    } catch (e) {
        console.error('Lỗi nạp dropdown vị trí:', e);
    }
}

/**
 * Tải số liệu thống kê cho vị trí đã chọn
 */
async function loadStatisticsForPosition(positionId) {
    if (!positionId) return;

    try {
        Utils.showLoading(true, 'Đang phân tích dữ liệu tuyển dụng...');
        const res = await API.statistics.getByPosition(positionId);

        if (res.success && res.data) {
            const data = res.data;
            document.getElementById('totalJobsAnalyzedCount').textContent = `${data.total_jobs_analyzed || 5} tin`;

            renderSkillsHorizontalBarChart(data.top_skills || []);
            renderTechnologiesPieChart(data.technologies || []);
            renderCertificatesList(data.certificates || []);
        } else {
            Utils.showToast(res.message || 'Không có dữ liệu thống kê!', 'warning');
        }
    } catch (e) {
        console.error(e);
        Utils.showToast('Lỗi khi nạp dữ liệu thống kê kỹ năng!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}

/**
 * Vẽ biểu đồ cột ngang (Horizontal Bar Chart) hiển thị Top kỹ năng
 */
function renderSkillsHorizontalBarChart(skills) {
    const canvas = document.getElementById('skillsHorizontalBarChart');
    if (!canvas) return;

    // Hủy instance cũ
    if (skillsBarChartInstance) {
        skillsBarChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    const labels = skills.map(s => s.name);
    const dataValues = skills.map(s => s.percentage || s.count);

    skillsBarChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tần suất xuất hiện (%)',
                data: dataValues,
                backgroundColor: 'rgba(37, 99, 235, 0.85)',
                borderColor: '#1d4ed8',
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            indexAxis: 'y', // Chuyển trục sang cột ngang
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            return ` Xuất hiện trong ${ctx.parsed.x}% tin tuyển dụng`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: val => `${val}%`
                    },
                    grid: {
                        color: 'rgba(226, 232, 240, 0.6)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            weight: '500'
                        }
                    }
                }
            }
        }
    });
}

/**
 * Vẽ biểu đồ tròn/doughnut (Technologies Pie Chart)
 */
function renderTechnologiesPieChart(technologies) {
    const canvas = document.getElementById('technologiesPieChart');
    if (!canvas) return;

    // Hủy instance cũ
    if (techPieChartInstance) {
        techPieChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    const labels = technologies.map(t => t.name);
    const dataValues = technologies.map(t => t.count || t.percentage);

    const colors = [
        '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#64748b'
    ];

    techPieChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 10,
                        font: {
                            size: 11
                        }
                    }
                }
            },
            cutout: '62%'
        }
    });
}

/**
 * Hiển thị danh sách chứng chỉ nghề nghiệp phổ biến
 */
function renderCertificatesList(certificates) {
    const container = document.getElementById('popularCertificatesList');
    if (!container) return;

    if (certificates.length === 0) {
        container.innerHTML = `<div class="p-3 text-center text-muted small">Vị trí này không có yêu cầu chứng chỉ đặc thù.</div>`;
        return;
    }

    let html = '';
    certificates.forEach(c => {
        html += `
            <div class="list-group-item px-3 py-2 d-flex align-items-center justify-content-between border-0 border-bottom">
                <div>
                    <div class="fw-semibold text-dark small"><i class="bi bi-award-fill text-warning me-2"></i>${Utils.escapeHtml(c.name)}</div>
                    <small class="text-muted">${Utils.escapeHtml(c.level || 'Khuyến nghị')}</small>
                </div>
                <span class="badge bg-light text-secondary border">${c.count} lượt nhắc</span>
            </div>
        `;
    });
    container.innerHTML = html;
}
