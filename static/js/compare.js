/**
 * compare.js - Xử lý chức năng so sánh đối soát hồ sơ sinh viên với vị trí tuyển dụng
 * Đề tài: NLCNPM23CS-38
 */

let scoreChartInstance = null;
let lastComparisonResult = null;

document.addEventListener('DOMContentLoaded', () => {
    initComparePage();
});

/**
 * Khởi tạo trang so sánh
 */
async function initComparePage() {
    await loadComparePositions();

    const btnRun = document.getElementById('btnRunCompare');
    if (btnRun) {
        btnRun.addEventListener('click', () => {
            const selectEl = document.getElementById('comparePositionSelect');
            if (selectEl && selectEl.value) {
                runComparison(selectEl.value);
            }
        });
    }

    // Nút thêm kỹ năng thiếu vào Kế hoạch học tập
    document.getElementById('btnAddMissingToPlan')?.addEventListener('click', handleAddMissingSkillsToPlan);

    // Tự động chạy so sánh vị trí đầu tiên
    const selectEl = document.getElementById('comparePositionSelect');
    if (selectEl && selectEl.value) {
        runComparison(selectEl.value);
    }
}

/**
 * Tải danh mục vị trí vào dropdown
 */
async function loadComparePositions() {
    try {
        const res = await API.positions.getAll({ limit: 100 });
        if (res.success && res.data) {
            const selectEl = document.getElementById('comparePositionSelect');
            if (!selectEl) return;
            selectEl.innerHTML = '';

            const items = res.data.items || [];
            items.forEach((p, idx) => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.name;
                if (idx === 0) opt.selected = true;
                selectEl.appendChild(opt);
            });
        }
    } catch (e) {
        console.error('Lỗi nạp dropdown vị trí:', e);
    }
}

/**
 * Gọi API so sánh hồ sơ sinh viên với vị trí nghề nghiệp
 */
async function runComparison(positionId) {
    const btnRun = document.getElementById('btnRunCompare');
    Utils.setButtonLoading(btnRun, true);

    try {
        Utils.showLoading(true, 'Đang đối chiếu hồ sơ với các tin tuyển dụng...');
        const res = await API.compare.compareWithPosition(positionId);

        if (res.success && res.data) {
            lastComparisonResult = res.data;
            renderComparisonResult(res.data);
            document.getElementById('compareResultContainer').classList.remove('d-none');
        } else {
            Utils.showToast(res.message || 'Không thể tính toán so sánh!', 'danger');
        }
    } catch (e) {
        console.error(e);
        Utils.showToast('Lỗi khi thực hiện so sánh hồ sơ!', 'danger');
    } finally {
        Utils.setButtonLoading(btnRun, false);
        Utils.showLoading(false);
    }
}

/**
 * Hiển thị toàn bộ kết quả so sánh
 */
function renderComparisonResult(data) {
    const score = data.score ?? 0;
    const have = data.have || [];
    const missing = data.missing || [];

    // Điểm số & Xếp loại
    document.getElementById('matchScoreNumber').textContent = `${score}%`;
    const gradeEl = document.getElementById('matchScoreGrade');
    if (score >= 75) {
        gradeEl.textContent = 'Mức độ phù hợp: Rất Cao';
        gradeEl.className = 'small fw-bold text-success';
    } else if (score >= 50) {
        gradeEl.textContent = 'Mức độ phù hợp: Khá';
        gradeEl.className = 'small fw-bold text-primary';
    } else {
        gradeEl.textContent = 'Cần bổ sung nhiều kỹ năng';
        gradeEl.className = 'small fw-bold text-warning';
    }

    // Số lượng
    document.getElementById('countSkillsHave').textContent = `${have.length} kỹ năng`;
    document.getElementById('countSkillsMissing').textContent = `${missing.length} kỹ năng`;
    document.getElementById('badgeHaveCount').textContent = have.length;
    document.getElementById('badgeMissingCount').textContent = missing.length;

    // Nhận xét kết luận
    const summaryEl = document.getElementById('compareSummaryText');
    if (summaryEl) {
        summaryEl.innerHTML = `<p class="mb-0 text-dark" style="line-height: 1.6;">${Utils.escapeHtml(data.summary)}</p>`;
    }

    // Danh sách kỹ năng Đã có (Badge xanh)
    const haveContainer = document.getElementById('skillsHaveContainer');
    if (haveContainer) {
        if (have.length === 0) {
            haveContainer.innerHTML = `<span class="text-muted small">Chưa đáp ứng kỹ năng đặc thù nào.</span>`;
        } else {
            haveContainer.innerHTML = have.map(s => 
                `<span class="badge badge-soft-success me-1 mb-2 p-2 fs-7 fw-medium"><i class="bi bi-check2 me-1"></i>${Utils.escapeHtml(s)}</span>`
            ).join('');
        }
    }

    // Danh sách kỹ năng Còn thiếu (Badge đỏ)
    const missingContainer = document.getElementById('skillsMissingContainer');
    if (missingContainer) {
        if (missing.length === 0) {
            missingContainer.innerHTML = `<span class="text-success small fw-semibold"><i class="bi bi-check-all me-1"></i>Hồ sơ đã đáp ứng đầy đủ yêu cầu!</span>`;
        } else {
            missingContainer.innerHTML = missing.map(s => 
                `<span class="badge badge-soft-danger me-1 mb-2 p-2 fs-7 fw-medium"><i class="bi bi-dash-circle me-1"></i>${Utils.escapeHtml(s)}</span>`
            ).join('');
        }
    }

    // Vẽ biểu đồ Doughnut
    renderScoreDoughnutChart(score);
}

/**
 * Vẽ biểu đồ Doughnut thể hiện điểm phần trăm phù hợp bằng Chart.js
 */
function renderScoreDoughnutChart(score) {
    const canvas = document.getElementById('scoreDoughnutChart');
    if (!canvas) return;

    // Hủy instance biểu đồ cũ
    if (scoreChartInstance) {
        scoreChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    let mainColor = '#10b981'; // Xanh lá
    if (score < 50) mainColor = '#f59e0b'; // Cam
    if (score < 30) mainColor = '#ef4444'; // Đỏ

    scoreChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [mainColor, '#e2e8f0'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '78%',
            plugins: {
                tooltip: { enabled: false },
                legend: { display: false }
            },
            animation: {
                animateRotate: true,
                duration: 900
            }
        }
    });
}

/**
 * Thêm các kỹ năng còn thiếu vào Kế hoạch học tập
 */
async function handleAddMissingSkillsToPlan() {
    if (!lastComparisonResult || !lastComparisonResult.missing || lastComparisonResult.missing.length === 0) {
        Utils.showToast('Không có kỹ năng còn thiếu nào để thêm vào kế hoạch!', 'info');
        return;
    }

    const missing = lastComparisonResult.missing;
    Utils.confirmModal({
        title: 'Thêm vào Kế hoạch học tập',
        message: `Bạn có muốn tự động tạo ${missing.length} mục tiêu học tập mới cho các kỹ năng còn thiếu: ${missing.slice(0, 3).join(', ')}... ?`,
        confirmText: 'Tạo kế hoạch',
        confirmClass: 'btn-primary',
        onConfirm: async () => {
            Utils.showLoading(true, 'Đang khởi tạo các mục kế hoạch...');
            let count = 0;
            for (const skillName of missing) {
                await API.plan.create({
                    title: `Nghiên cứu và thành thạo kỹ năng ${skillName}`,
                    category: `Thiếu cho vị trí ${lastComparisonResult.position_name}`,
                    type: 'skill',
                    status: 'todo',
                    target_date: '2026-12-31',
                    note: 'Tự động tạo từ màn hình Đánh giá độ phù hợp'
                });
                count++;
            }
            Utils.showLoading(false);
            Utils.showToast(`Đã thêm thành công ${count} kỹ năng vào Kế hoạch học tập!`, 'success');
        }
    });
}
