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

    const selectEl = document.getElementById('comparePositionSelect');
    const btnRun = document.getElementById('btnRunCompare');
    if (btnRun) {
        btnRun.addEventListener('click', () => {
            if (selectEl && selectEl.value) {
                runComparison(selectEl.value);
            }
        });
    }

    if (selectEl) {
        selectEl.addEventListener('change', () => {
            if (selectEl.value) {
                runComparison(selectEl.value);
            }
        });
    }

    // Nút thêm kỹ năng thiếu vào Kế hoạch học tập
    document.getElementById('btnAddMissingToPlan')?.addEventListener('click', handleAddMissingSkillsToPlan);

    // Tự động chạy so sánh vị trí đang chọn
    if (selectEl && selectEl.value) {
        runComparison(selectEl.value);
    }
}

/**
 * Tải danh mục vị trí vào dropdown và ưu tiên chọn vị trí mục tiêu của sinh viên
 */
async function loadComparePositions() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        let preferredPosId = urlParams.get('position_id');
        if (!preferredPosId) {
            try {
                const profRes = await API.profile.get();
                if (profRes.success && profRes.data?.personal_info?.target_position_id) {
                    preferredPosId = String(profRes.data.personal_info.target_position_id);
                }
            } catch (_) {}
        }

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
                if (preferredPosId ? String(p.id) === String(preferredPosId) : idx === 0) {
                    opt.selected = true;
                }
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
        summaryEl.innerHTML = `
            <div class="d-flex align-items-start gap-2">
                <i class="bi bi-chat-quote-fill text-primary fs-5 mt-1 flex-shrink-0"></i>
                <p class="mb-0 text-white" style="line-height: 1.6; font-size: 0.95rem;">${Utils.escapeHtml(data.summary)}</p>
            </div>
        `;
    }

    // Danh sách kỹ năng Đã có (Badge xanh)
    const haveContainer = document.getElementById('skillsHaveContainer');
    if (haveContainer) {
        if (have.length === 0) {
            haveContainer.innerHTML = `<span class="text-muted small">Chưa đáp ứng kỹ năng đặc thù nào.</span>`;
        } else {
            const byCourses = data.have_by_courses || [];
            haveContainer.innerHTML = have.map(s => byCourses.includes(s)
                ? `<span class="badge badge-soft-primary me-1 mb-2 p-2 fs-7 fw-medium" title="Đáp ứng nhờ học phần đã học"><i class="bi bi-book me-1"></i>${Utils.escapeHtml(s)}</span>`
                : `<span class="badge badge-soft-success me-1 mb-2 p-2 fs-7 fw-medium"><i class="bi bi-check2 me-1"></i>${Utils.escapeHtml(s)}</span>`
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

    // Hiển thị chứng chỉ khuyến nghị & gợi ý khóa học
    renderRecommendations(data.recommended_certs || [], data.missing_certs || [], data.recommendations || [], data.suggested_academic_courses || []);

    // Hiển thị lịch sử đối sánh
    renderComparisonHistory(data.history || []);
}

/**
 * Hiển thị danh sách chứng chỉ ưu tiên, môn học đại học và khóa học gợi ý cho kỹ năng còn thiếu
 */
function renderRecommendations(recCerts, missingCerts, recommendations, suggestedAcademicCourses = []) {
    const normKey = (s) => String(s || '').trim().toLowerCase().replace(/\s+/g, ' ');

    // Chuẩn hóa và lọc danh sách khóa học đề xuất (tối đa 6 khóa học chất lượng)
    const seenRecTitles = new Set();
    const seenSkills = new Set();
    const uniqueRecs = [];
    (recommendations || []).forEach((rec, originalIdx) => {
        if (!rec || !rec.title) return;
        const kTitle = normKey(rec.title);
        const kSkill = normKey(rec.skill_name);

        if (seenRecTitles.has(kTitle)) return;
        if (kTitle.includes('khóa học thực chiến') && seenSkills.has(kSkill)) return;

        seenRecTitles.add(kTitle);
        if (kSkill) seenSkills.add(kSkill);
        uniqueRecs.push({ rec, originalIdx });
    });
    const displayRecs = uniqueRecs.slice(0, 6);

    // Kiểm tra chứng chỉ có được bao hàm trong thẻ khóa học bên dưới không
    const isCertCovered = (certName) => {
        const c = normKey(certName);
        return displayRecs.some(({ rec }) => {
            const t = normKey(rec.title);
            const s = normKey(rec.skill_name);
            if (c === t || t.includes(c) || c.includes(t)) return true;
            if (c.includes('cka') && (t.includes('cka') || t.includes('kubernetes'))) return true;
            if (c.includes('pl-300') && (t.includes('pl-300') || t.includes('power bi'))) return true;
            if (c.includes('meta') && (t.includes('meta') || t.includes('react'))) return true;
            if (c.includes('aws') && (t.includes('aws') || s.includes('aws'))) return true;
            if ((c.includes('rhcsa') || c.includes('linux')) && (t.includes('linux') || s.includes('linux'))) return true;
            if (c.includes('istqb') && (t.includes('istqb') || t.includes('test') || s.includes('test'))) return true;
            if (c.includes('tableau') && (t.includes('tableau') || s.includes('tableau'))) return true;
            if (c.includes('deeplearning') && (t.includes('deep learning') || s.includes('pytorch') || s.includes('tensorflow'))) return true;
            return false;
        });
    };

    const certsContainer = document.getElementById('recommendedCertsContainer');
    if (certsContainer) {
        // Chỉ hiển thị chứng chỉ độc lập chưa có thẻ học tập bên dưới
        const standaloneCerts = (recCerts || []).filter(c => !isCertCovered(c));
        if (standaloneCerts.length === 0) {
            certsContainer.innerHTML = `<span class="text-muted small">Các chứng chỉ chuyên môn liên quan đã được tích hợp chi tiết trong lộ trình học tập bên dưới.</span>`;
        } else {
            certsContainer.innerHTML = standaloneCerts.map(c => {
                const isMissing = !missingCerts || missingCerts.length === 0 || missingCerts.includes(c);
                const badgeClass = isMissing
                    ? 'bg-warning-subtle text-dark border border-warning-subtle'
                    : 'bg-success-subtle text-success border border-success-subtle';
                const icon = isMissing ? 'bi-award text-warning' : 'bi-check-circle-fill text-success';
                return `<span class="badge ${badgeClass} me-1 mb-1 p-2"><i class="bi ${icon} me-1"></i>${Utils.escapeHtml(c)}</span>`;
            }).join('');
        }
    }

    // Hiển thị Môn học Đại học CNTT đề xuất
    const acadContainer = document.getElementById('academicCoursesContainer');
    if (acadContainer) {
        if (!suggestedAcademicCourses || suggestedAcademicCourses.length === 0) {
            acadContainer.innerHTML = `<div class="col-12 text-muted small">Bạn đã hoàn thành các môn học CNTT trọng tâm của vị trí này.</div>`;
        } else {
            acadContainer.innerHTML = suggestedAcademicCourses.map((c, cIdx) => `
                <div class="col-12">
                    <div class="border rounded-3 p-2 px-3 bg-light-subtle d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
                        <div>
                            <div class="d-flex align-items-center gap-2 mb-1">
                                <span class="badge bg-secondary-subtle text-dark border font-monospace">${Utils.escapeHtml(c.code)}</span>
                                <span class="fw-bold text-dark small">${Utils.escapeHtml(c.name)}</span>
                                <span class="badge bg-light text-secondary border small">${c.credits || 3} tín chỉ</span>
                            </div>
                            <div class="text-secondary small">
                                ${(c.matched_missing_skills || []).map(sk => `<span class="badge badge-soft-danger me-1"><i class="bi bi-tag me-1"></i>${Utils.escapeHtml(sk)}</span>`).join('')}
                                <span class="text-muted ms-1">${Utils.escapeHtml(c.reason || c.description || '')}</span>
                            </div>
                        </div>
                        <div class="text-md-end flex-shrink-0">
                            <button type="button" class="btn btn-sm btn-outline-primary py-1 px-2" onclick="addAcademicCourseToPlan(${cIdx})">
                                <i class="bi bi-calendar-plus me-1"></i>Vào Kế hoạch
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    const recsContainer = document.getElementById('courseRecommendationsContainer');
    const badgeRecsCount = document.getElementById('badgeRecsCount');
    if (badgeRecsCount) {
        const totalRecs = (recommendations ? recommendations.length : 0) + (suggestedAcademicCourses ? suggestedAcademicCourses.length : 0);
        badgeRecsCount.textContent = `${totalRecs} gợi ý`;
    }
    if (!recsContainer) return;

    if (displayRecs.length === 0) {
        recsContainer.innerHTML = `<div class="col-12 text-muted small">Bạn đã đáp ứng đầy đủ kỹ năng cốt lõi của vị trí này!</div>`;
        return;
    }

    recsContainer.innerHTML = displayRecs.map(({ rec, originalIdx: idx }) => {
        const isCertType = rec.rec_type === 'certificate' || (rec.title && (rec.title.includes('Certificate') || rec.title.includes('Certification') || rec.title.includes('CKA') || rec.title.includes('PL-300') || rec.title.includes('Specialization')));
        const typeBadge = isCertType
            ? `<span class="badge bg-warning-subtle text-dark border border-warning-subtle small me-1"><i class="bi bi-award-fill text-warning me-1"></i>Chứng chỉ</span>`
            : '';
        return `
        <div class="col-12">
            <div class="border rounded-3 p-2 px-3 bg-light-subtle d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
                <div>
                    <div class="d-flex align-items-center gap-2 mb-1">
                        <span class="badge badge-soft-danger">${Utils.escapeHtml(rec.skill_name)}</span>
                        ${typeBadge}
                        <span class="fw-bold text-dark small">${Utils.escapeHtml(rec.title)}</span>
                    </div>
                    <div class="text-muted small">
                        <i class="bi bi-building me-1"></i>${Utils.escapeHtml(rec.provider || 'Coursera / Udemy')}
                        <span class="mx-1">•</span>
                        <i class="bi bi-clock me-1"></i>${Utils.escapeHtml(rec.duration || '4 tuần')}
                    </div>
                </div>
                <div class="text-md-end flex-shrink-0">
                    <button type="button" class="btn btn-sm btn-outline-primary py-1 px-2" onclick="addSingleRecToPlan(${idx})">
                        <i class="bi bi-plus-lg me-1"></i>Thêm lộ trình
                    </button>
                </div>
            </div>
        </div>
    `;
    }).join('');
}

async function addAcademicCourseToPlan(index) {
    if (!lastComparisonResult || !lastComparisonResult.suggested_academic_courses) return;
    const c = lastComparisonResult.suggested_academic_courses[index];
    if (!c) return;

    try {
        const res = await API.plan.create({
            title: `Học phần: ${c.name} (${c.code})`,
            category: `Học phần cho vị trí ${lastComparisonResult.position_name}`,
            type: 'course',
            status: 'todo',
            target_date: '2026-12-31',
            note: c.description || c.reason || 'Môn học CNTT trọng tâm.'
        });
        if (res.success) {
            Utils.showToast(`Đã thêm môn "${c.name}" vào Kế hoạch học tập!`, 'success');
        }
    } catch (e) {
        Utils.showToast('Lỗi khi thêm vào kế hoạch học tập!', 'danger');
    }
}

/**
 * Thêm 1 khóa học / chứng chỉ gợi ý vào Kế hoạch học tập
 */
async function addSingleRecToPlan(index) {
    if (!lastComparisonResult || !lastComparisonResult.recommendations) return;
    const rec = lastComparisonResult.recommendations[index];
    if (!rec) return;

    try {
        const res = await API.plan.create({
            title: `${rec.title} (Bổ sung ${rec.skill_name})`,
            category: `Thiếu cho vị trí ${lastComparisonResult.position_name}`,
            type: rec.rec_type === 'certificate' ? 'certificate' : 'course',
            status: 'todo',
            target_date: '2026-12-31',
            note: `${rec.provider || ''} - Thời lượng: ${rec.duration || '4 tuần'}. ${rec.description || ''}`.trim()
        });
        if (res.success) {
            Utils.showToast(`Đã thêm "${rec.skill_name}" vào Kế hoạch học tập!`, 'success');
        }
    } catch (e) {
        Utils.showToast('Lỗi khi thêm vào kế hoạch học tập!', 'danger');
    }
}

/**
 * Hiển thị lịch sử đánh giá gần đây
 */
function renderComparisonHistory(historyList) {
    const container = document.getElementById('comparisonHistoryContainer');
    if (!container) return;

    if (!historyList || historyList.length === 0) {
        container.innerHTML = `<div class="p-3 text-center text-muted small">Chưa có lịch sử đánh giá.</div>`;
        return;
    }

    container.innerHTML = historyList.map(h => {
        const badgeColor = h.score >= 75 ? 'badge-soft-success' : (h.score >= 50 ? 'badge-soft-primary' : 'badge-soft-warning');
        return `
            <div class="list-group-item px-3 py-2 d-flex align-items-center justify-content-between border-0 border-bottom">
                <div class="text-truncate me-2">
                    <div class="fw-semibold text-dark small text-truncate">${Utils.escapeHtml(h.position_name)}</div>
                    <small class="text-muted">Đạt ${h.matched_count || 0} • Thiếu ${h.missing_count || 0} kỹ năng</small>
                </div>
                <span class="badge ${badgeColor} rounded-pill">${h.score}%</span>
            </div>
        `;
    }).join('');
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
                backgroundColor: [mainColor, '#2C2825'],
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
