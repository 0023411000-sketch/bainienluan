/**
 * comparison.js - Xử lý logic hiển thị Kết quả so sánh hồ sơ
 * Dữ liệu API nhận về định dạng:
 * {
 *   "diem_phu_hop": 72,
 *   "ky_nang_co": ["Python", "Flask", "SQL"],
 *   "ky_nang_thieu": ["Docker", "Git nâng cao"]
 * }
 */

// Biến lưu trữ biểu đồ Chart.js để destroy/re-create khi chuyển vị trí
let matchChartInstance = null;

// Dữ liệu mẫu dự phòng (fallback) nếu API chưa kết nối
const DEFAULT_FALLBACK_DATA = {
    diem_phu_hop: 72,
    ky_nang_co: ["Python", "Flask", "SQL"],
    ky_nang_thieu: ["Docker", "Git nâng cao"],
    target_position: "Lập trình viên Backend (Python)"
};

document.addEventListener('DOMContentLoaded', () => {
    // 1. Tải dữ liệu ban đầu
    loadComparisonData();

    // 2. Lắng nghe sự kiện thay đổi vị trí từ dropdown
    const positionSelect = document.getElementById('positionSelect');
    if (positionSelect) {
        positionSelect.addEventListener('change', (e) => {
            loadComparisonData(e.target.value);
        });
    }

    // 3. Lắng nghe nút "Đánh giá lại"
    const btnRefresh = document.getElementById('btnRefreshComparison');
    if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
            const currentPositionId = positionSelect ? positionSelect.value : 1;
            loadComparisonData(currentPositionId, true);
        });
    }
});

/**
 * Tải dữ liệu so sánh từ API
 * @param {number|string} positionId - ID của vị trí tuyển dụng
 * @param {boolean} showToastOnSuccess - Có hiển thị toast thông báo không
 */
async function loadComparisonData(positionId = 1, showToastOnSuccess = false) {
    try {
        let result = null;

        // Gọi API qua wrapper API trong static/js/api.js
        if (typeof API !== 'undefined' && typeof API.getComparison === 'function') {
            result = await API.getComparison(positionId);
        } else {
            console.warn("API.getComparison không tìm thấy, sử dụng dữ liệu mặc định.");
            result = DEFAULT_FALLBACK_DATA;
        }

        // Đảm bảo dữ liệu đúng định dạng yêu cầu
        if (!result) {
            showEmptyState(true);
            return;
        }

        showEmptyState(false);
        renderComparisonView(result);

        if (showToastOnSuccess && typeof showAlert === 'function') {
            showAlert('Đã cập nhật lại kết quả so sánh mới nhất!', 'success');
        }

    } catch (error) {
        console.error("Lỗi khi tải kết quả so sánh:", error);
        // Hiển thị fallback để sinh viên vẫn thấy giao diện chạy được ngay
        renderComparisonView(DEFAULT_FALLBACK_DATA);
        if (typeof showAlert === 'function') {
            showAlert('Đang hiển thị dữ liệu so sánh mẫu do lỗi kết nối API.', 'warning');
        }
    }
}

/**
 * Hiển thị dữ liệu lên giao diện
 * @param {Object} data - Dữ liệu JSON từ API
 */
function renderComparisonView(data) {
    const score = Number(data.diem_phu_hop) || 0;
    const skillsMatched = Array.isArray(data.ky_nang_co) ? data.ky_nang_co : [];
    const skillsMissing = Array.isArray(data.ky_nang_thieu) ? data.ky_nang_thieu : [];
    const totalSkills = skillsMatched.length + skillsMissing.length;

    // 1. Cập nhật số điểm ở tâm biểu đồ
    const displayScoreEl = document.getElementById('displayScore');
    if (displayScoreEl) {
        animateScoreCounter(displayScoreEl, score);
    }

    // 2. Cập nhật nhãn phân loại điểm (Badge)
    const scoreBadge = document.getElementById('scoreBadge');
    if (scoreBadge) {
        scoreBadge.className = 'score-level-badge';
        if (score >= 75) {
            scoreBadge.classList.add('level-high');
            scoreBadge.textContent = 'Rất phù hợp';
        } else if (score >= 50) {
            scoreBadge.classList.add('level-medium');
            scoreBadge.textContent = 'Khá tốt';
        } else {
            scoreBadge.classList.add('level-low');
            scoreBadge.textContent = 'Cần nỗ lực';
        }
    }

    // 3. Cập nhật thông số tóm tắt
    const displayTargetPosition = document.getElementById('displayTargetPosition');
    const positionSelect = document.getElementById('positionSelect');
    if (displayTargetPosition) {
        displayTargetPosition.textContent = data.target_position 
            || (positionSelect ? positionSelect.options[positionSelect.selectedIndex].text : 'Vị trí đã chọn');
    }

    const totalEl = document.getElementById('displayTotalSkills');
    if (totalEl) totalEl.textContent = totalSkills;

    const countMatchedEl = document.getElementById('countMatched');
    if (countMatchedEl) countMatchedEl.textContent = skillsMatched.length;

    const countMissingEl = document.getElementById('countMissing');
    if (countMissingEl) countMissingEl.textContent = skillsMissing.length;

    const badgeCountMatched = document.getElementById('badgeCountMatched');
    if (badgeCountMatched) badgeCountMatched.textContent = `${skillsMatched.length} kỹ năng`;

    const badgeCountMissing = document.getElementById('badgeCountMissing');
    if (badgeCountMissing) badgeCountMissing.textContent = `${skillsMissing.length} kỹ năng`;

    // 4. Render danh sách Kỹ năng đã có (Màu xanh lá)
    renderSkillBadges('matchedSkillsList', skillsMatched, 'available', 'bi-check-circle-fill');

    // 5. Render danh sách Kỹ năng còn thiếu (Màu đỏ/cam)
    renderSkillBadges('missingSkillsList', skillsMissing, 'lacking', 'bi-exclamation-triangle-fill');

    // 6. Nhận xét & Lời khuyên
    const recText = document.getElementById('recommendationText');
    if (recText) {
        if (data.ghi_chu) {
            recText.textContent = data.ghi_chu;
        } else if (skillsMissing.length > 0) {
            recText.textContent = `Hồ sơ của bạn đã đáp ứng ${score}% yêu cầu. Hãy tập trung bổ sung các kỹ năng: ${skillsMissing.join(', ')} để đạt cơ hội trúng tuyển cao nhất!`;
        } else {
            recText.textContent = 'Tuyệt vời! Bạn đã đáp ứng đầy đủ tất cả kỹ năng cần thiết cho vị trí này. Hãy tự tin nộp hồ sơ!';
        }
    }

    // 7. Vẽ biểu đồ Doughnut Chart.js
    renderDoughnutChart(score);
}

/**
 * Render danh sách Badge kỹ năng
 */
function renderSkillBadges(containerId, skillArray, type, iconClass) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!skillArray || skillArray.length === 0) {
        container.innerHTML = `<span class="text-muted small fst-italic">Không có kỹ năng nào.</span>`;
        return;
    }

    const badgeClass = type === 'available' ? 'badge-skill-available' : 'badge-skill-lacking';

    container.innerHTML = skillArray.map(skill => `
        <span class="${badgeClass}">
            <i class="bi ${iconClass}"></i>
            <span>${escapeHtml(skill)}</span>
        </span>
    `).join('');
}

/**
 * Khởi tạo và cập nhật Biểu đồ Doughnut Chart.js
 * @param {number} score - Điểm phù hợp (0 - 100)
 */
function renderDoughnutChart(score) {
    const canvas = document.getElementById('matchDoughnutChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const remaining = Math.max(0, 100 - score);

    // Xác định màu sắc phần phù hợp dựa trên điểm số
    let mainColor = '#10b981'; // Xanh lá mặc định
    let hoverColor = '#059669';
    if (score < 50) {
        mainColor = '#f43f5e'; // Đỏ nếu dưới 50%
        hoverColor = '#e11d48';
    } else if (score < 75) {
        mainColor = '#2563eb'; // Xanh dương nếu từ 50-74%
        hoverColor = '#1d4ed8';
    }

    // Nếu biểu đồ đã tồn tại, hủy và vẽ lại để mượt mà
    if (matchChartInstance) {
        matchChartInstance.destroy();
    }

    matchChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Điểm phù hợp (%)', 'Còn thiếu (%)'],
            datasets: [{
                data: [score, remaining],
                backgroundColor: [mainColor, '#f1f5f9'],
                hoverBackgroundColor: [hoverColor, '#e2e8f0'],
                borderWidth: 0,
                spacing: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '76%', // Độ rỗng ở giữa để hiển thị số phần trăm
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 900
            },
            plugins: {
                legend: {
                    display: false // Ẩn chú thích vì đã có text ở tâm và thống kê bên dưới
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.label}: ${context.raw}%`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Hiệu ứng chạy số phần trăm tăng dần từ 0 lên điểm số thật
 */
function animateScoreCounter(element, targetScore) {
    let current = 0;
    const duration = 600; // ms
    const stepTime = 20; // ms
    const steps = duration / stepTime;
    const increment = targetScore / steps;

    const timer = setInterval(() => {
        current += increment;
        if (current >= targetScore) {
            element.textContent = Math.round(targetScore);
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, stepTime);
}

/**
 * Ẩn/Hiện trạng thái không có dữ liệu
 */
function showEmptyState(show) {
    const resultBox = document.getElementById('comparisonResultContainer');
    const emptyBox = document.getElementById('comparisonEmptyState');

    if (resultBox) resultBox.classList.toggle('d-none', show);
    if (emptyBox) emptyBox.classList.toggle('d-none', !show);
}

/**
 * Tránh lỗi XSS khi render chuỗi người dùng
 */
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
