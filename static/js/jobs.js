/**
 * jobs.js - Quản lý tin tuyển dụng và chức năng nhập dữ liệu từ file CSV
 * Đề tài: NLCNPM23CS-38
 */

let currentJobPage = 1;
let currentJobSearch = '';
let currentFilterPositionId = '';
let jobModal = null;
let csvModal = null;
let cachedJobs = [];
let parsedCsvRecords = [];

document.addEventListener('DOMContentLoaded', () => {
    // Khởi tạo các Modal
    const jModalEl = document.getElementById('jobModal');
    if (jModalEl) jobModal = new bootstrap.Modal(jModalEl);

    const cModalEl = document.getElementById('csvImportModal');
    if (cModalEl) csvModal = new bootstrap.Modal(cModalEl);

    // Gắn sự kiện nút
    document.getElementById('btnOpenAddJobModal')?.addEventListener('click', openAddJobModal);
    document.getElementById('btnOpenCsvModal')?.addEventListener('click', openCsvModal);
    document.getElementById('jobForm')?.addEventListener('submit', handleSaveJob);

    // Bắt sự kiện tìm kiếm & lọc
    document.getElementById('searchJobInput')?.addEventListener('input', Utils.debounce((e) => {
        currentJobSearch = e.target.value.trim();
        currentJobPage = 1;
        loadJobs();
    }, 300));

    document.getElementById('filterPositionSelect')?.addEventListener('change', (e) => {
        currentFilterPositionId = e.target.value;
        currentJobPage = 1;
        loadJobs();
    });

    // Xử lý đọc file CSV
    document.getElementById('csvFileInput')?.addEventListener('change', handleCsvFileSelect);
    document.getElementById('btnConfirmImportCsv')?.addEventListener('click', handleConfirmImportCsv);
    document.getElementById('btnDownloadSampleCsv')?.addEventListener('click', downloadSampleCsv);

    // Khởi tạo dữ liệu
    initPage();
});

/**
 * Khởi tạo dữ liệu trang: nạp danh mục vị trí và danh sách tin tuyển dụng
 */
async function initPage() {
    await loadPositionsOptions();
    await loadJobs();
}

/**
 * Nạp danh mục vị trí vào các dropdown bộ lọc và dropdown của Modal
 */
async function loadPositionsOptions() {
    try {
        const res = await API.positions.getAll({ limit: 100 });
        if (res.success && res.data) {
            const positions = res.data.items || [];
            const filterSelect = document.getElementById('filterPositionSelect');
            const jobPosSelect = document.getElementById('jobPositionId');

            if (filterSelect) {
                positions.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.name;
                    filterSelect.appendChild(opt);
                });
            }

            if (jobPosSelect) {
                jobPosSelect.innerHTML = '';
                positions.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.name;
                    jobPosSelect.appendChild(opt);
                });
            }
        }
    } catch (e) {
        console.error('Lỗi nạp danh mục vị trí:', e);
    }
}

/**
 * Tải danh sách tin tuyển dụng theo trang, từ khóa và bộ lọc
 */
async function loadJobs() {
    try {
        Utils.showLoading(true, 'Đang tải tin tuyển dụng...');
        const res = await API.jobs.getAll({
            q: currentJobSearch,
            position_id: currentFilterPositionId,
            page: currentJobPage,
            limit: CONFIG.DEFAULT_PAGE_SIZE
        });

        if (res.success && res.data) {
            cachedJobs = res.data.items || [];
            document.getElementById('totalJobsBadge').textContent = res.data.total ?? cachedJobs.length;
            renderJobsTable(cachedJobs);
            Utils.renderPagination('jobsPaginationContainer', res.data.page, res.data.total_pages, (newPage) => {
                currentJobPage = newPage;
                loadJobs();
            });
        } else {
            Utils.showToast(res.message || 'Không thể tải tin tuyển dụng!', 'danger');
        }
    } catch (e) {
        console.error(e);
        Utils.showToast('Lỗi nạp tin tuyển dụng!', 'danger');
    } finally {
        Utils.showLoading(false);
    }
}

/**
 * Hiển thị bảng danh sách tin tuyển dụng
 */
function renderJobsTable(jobs) {
    const tbody = document.getElementById('jobsTableBody');
    if (!tbody) return;

    if (jobs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-5 text-muted">Không tìm thấy tin tuyển dụng nào phù hợp với tiêu chí tìm kiếm.</td></tr>`;
        return;
    }

    let html = '';
    jobs.forEach(job => {
        // Badges kỹ năng và công nghệ
        const skillBadges = (job.skills || []).slice(0, 3).map(s => 
            `<span class="badge badge-soft-primary me-1 mb-1">${Utils.escapeHtml(s)}</span>`
        ).join('');
        const techBadges = (job.technologies || []).slice(0, 2).map(t => 
            `<span class="badge badge-soft-secondary me-1 mb-1">${Utils.escapeHtml(t)}</span>`
        ).join('');

        const deadlineText = job.deadline ? Utils.formatDate(job.deadline) : 'Không giới hạn';

        html += `
            <tr>
                <td>
                    <div class="fw-bold text-dark">${Utils.escapeHtml(job.title)}</div>
                    <small class="text-muted"><i class="bi bi-clock me-1"></i>Hạn nộp: ${deadlineText}</small>
                </td>
                <td>
                    <div class="fw-semibold text-secondary"><i class="bi bi-building me-1 text-primary"></i>${Utils.escapeHtml(job.company)}</div>
                    <small class="text-muted"><i class="bi bi-geo-alt me-1"></i>${Utils.escapeHtml(job.location || 'Toàn quốc')}</small>
                </td>
                <td>
                    <span class="badge bg-success-subtle text-success border border-success-subtle fw-semibold">${Utils.escapeHtml(job.salary || 'Thỏa thuận')}</span>
                    <div class="small text-muted mt-1">${Utils.escapeHtml(job.experience_required || 'Không yêu cầu')}</div>
                </td>
                <td>
                    <div>${skillBadges} ${techBadges}</div>
                </td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-secondary py-1 px-2 me-1" title="Sửa" onclick="openEditJobModal(${job.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger py-1 px-2" title="Xóa" onclick="deleteJob(${job.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

// ==========================================
// THÊM / SỬA / XÓA TIN TUYỂN DỤNG
// ==========================================
function openAddJobModal() {
    document.getElementById('jobModalTitle').innerHTML = '<i class="bi bi-briefcase text-primary me-2"></i>Đăng tin tuyển dụng mới';
    document.getElementById('jobId').value = '';
    document.getElementById('jobTitle').value = '';
    document.getElementById('jobCompany').value = '';
    document.getElementById('jobLocation').value = 'Hà Nội';
    document.getElementById('jobSalary').value = '15 - 25 triệu VNĐ';
    document.getElementById('jobExperience').value = '1 - 2 năm';
    document.getElementById('jobDeadline').value = '';
    document.getElementById('jobSkills').value = '';
    document.getElementById('jobTechnologies').value = '';
    document.getElementById('jobCertificates').value = '';
    document.getElementById('jobDescription').value = '';
    jobModal?.show();
}

function openEditJobModal(id) {
    const job = cachedJobs.find(j => j.id == id);
    if (!job) return;

    document.getElementById('jobModalTitle').innerHTML = '<i class="bi bi-pencil-square text-primary me-2"></i>Chỉnh sửa tin tuyển dụng';
    document.getElementById('jobId').value = job.id;
    document.getElementById('jobTitle').value = job.title || '';
    document.getElementById('jobPositionId').value = job.position_id || 1;
    document.getElementById('jobCompany').value = job.company || '';
    document.getElementById('jobLocation').value = job.location || '';
    document.getElementById('jobSalary').value = job.salary || '';
    document.getElementById('jobExperience').value = job.experience_required || '';
    document.getElementById('jobDeadline').value = job.deadline || '';
    document.getElementById('jobSkills').value = Array.isArray(job.skills) ? job.skills.join(', ') : (job.skills || '');
    document.getElementById('jobTechnologies').value = Array.isArray(job.technologies) ? job.technologies.join(', ') : (job.technologies || '');
    document.getElementById('jobCertificates').value = Array.isArray(job.certificates) ? job.certificates.join(', ') : (job.certificates || '');
    document.getElementById('jobDescription').value = job.description || '';
    jobModal?.show();
}

async function handleSaveJob(e) {
    e.preventDefault();
    const id = document.getElementById('jobId').value;
    const btn = document.getElementById('btnSaveJob');
    Utils.setButtonLoading(btn, true);

    const payload = {
        title: document.getElementById('jobTitle').value.trim(),
        position_id: parseInt(document.getElementById('jobPositionId').value) || 1,
        company: document.getElementById('jobCompany').value.trim(),
        location: document.getElementById('jobLocation').value.trim(),
        salary: document.getElementById('jobSalary').value.trim(),
        experience_required: document.getElementById('jobExperience').value.trim(),
        deadline: document.getElementById('jobDeadline').value,
        skills: document.getElementById('jobSkills').value.trim(),
        technologies: document.getElementById('jobTechnologies').value.trim(),
        certificates: document.getElementById('jobCertificates').value.trim(),
        description: document.getElementById('jobDescription').value.trim()
    };

    try {
        let res;
        if (id) {
            res = await API.jobs.update(id, payload);
        } else {
            res = await API.jobs.create(payload);
        }

        if (res.success) {
            Utils.showToast(id ? 'Cập nhật tin tuyển dụng thành công!' : 'Đăng tin tuyển dụng thành công!', 'success');
            jobModal?.hide();
            await loadJobs();
        } else {
            Utils.showToast(res.message || 'Lỗi lưu tin tuyển dụng!', 'danger');
        }
    } catch (err) {
        Utils.showToast('Lỗi máy chủ khi lưu tin tuyển dụng!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

function deleteJob(id) {
    Utils.confirmModal({
        title: 'Xác nhận xóa tin tuyển dụng',
        message: 'Bạn có chắc chắn muốn xóa tin tuyển dụng này khỏi hệ thống?',
        confirmText: 'Xóa tin',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
            const res = await API.jobs.delete(id);
            if (res.success) {
                Utils.showToast('Đã xóa tin tuyển dụng!', 'success');
                await loadJobs();
            } else {
                Utils.showToast(res.message || 'Xóa thất bại!', 'danger');
            }
        }
    });
}

// ==========================================
// XỬ LÝ NHẬP FILE CSV VÀ XEM TRƯỚC 5 DÒNG
// ==========================================
function openCsvModal() {
    parsedCsvRecords = [];
    document.getElementById('csvFileInput').value = '';
    document.getElementById('csvPreviewArea').classList.add('d-none');
    document.getElementById('btnConfirmImportCsv').disabled = true;
    csvModal?.show();
}

/**
 * Đọc file CSV bằng FileReader trong JavaScript thuần
 */
function handleCsvFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
        Utils.showToast('Vui lòng chọn tập tin có định dạng .csv!', 'warning');
        e.target.value = '';
        return;
    }

    const reader = new FileReader();
    reader.onload = function (event) {
        const text = event.target.result;
        parseAndPreviewCsv(text);
    };
    reader.onerror = function () {
        Utils.showToast('Không thể đọc file CSV!', 'danger');
    };
    reader.readAsText(file, 'UTF-8');
}

/**
 * Phân tích cú pháp CSV và hiển thị 5 dòng đầu tiên
 */
function parseAndPreviewCsv(csvText) {
    const lines = csvText.split(/\r\n|\n/).filter(line => line.trim().length > 0);
    if (lines.length < 2) {
        Utils.showToast('File CSV không có dữ liệu hoặc thiếu tiêu đề cột!', 'warning');
        return;
    }

    // Tách dòng tiêu đề (Header)
    const headers = splitCsvLine(lines[0]);
    parsedCsvRecords = [];

    // Tách các dòng dữ liệu
    for (let i = 1; i < lines.length; i++) {
        const values = splitCsvLine(lines[i]);
        if (values.length === headers.length) {
            const rowObj = {};
            headers.forEach((h, idx) => {
                rowObj[h.trim()] = values[idx].trim();
            });
            parsedCsvRecords.push(rowObj);
        }
    }

    if (parsedCsvRecords.length === 0) {
        Utils.showToast('Không phân tích được dòng dữ liệu nào từ file CSV!', 'danger');
        return;
    }

    // Hiển thị xem trước 5 dòng đầu
    renderCsvPreview(headers, parsedCsvRecords.slice(0, 5), parsedCsvRecords.length);
}

/**
 * Trợ giúp tách 1 dòng CSV hỗ trợ có dấu ngoặc kép
 */
function splitCsvLine(line) {
    const values = [];
    let current = '';
    let insideQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"' || char === "'") {
            insideQuotes = !insideQuotes;
        } else if (char === ',' && !insideQuotes) {
            values.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    values.push(current);
    return values;
}

/**
 * Render bảng xem trước CSV
 */
function renderCsvPreview(headers, previewRows, totalRows) {
    const headerEl = document.getElementById('csvPreviewHeader');
    const bodyEl = document.getElementById('csvPreviewBody');
    const countEl = document.getElementById('csvTotalRecordsCount');
    const previewArea = document.getElementById('csvPreviewArea');
    const confirmBtn = document.getElementById('btnConfirmImportCsv');

    // Header
    headerEl.innerHTML = '<tr>' + headers.map(h => `<th class="text-nowrap">${Utils.escapeHtml(h)}</th>`).join('') + '</tr>';

    // Body
    let bodyHtml = '';
    previewRows.forEach(row => {
        bodyHtml += '<tr>' + headers.map(h => `<td class="text-truncate" style="max-width: 150px;">${Utils.escapeHtml(row[h] || '')}</td>`).join('') + '</tr>';
    });
    bodyEl.innerHTML = bodyHtml;

    countEl.innerHTML = `<i class="bi bi-check-circle-fill text-success me-1"></i>Hợp lệ! Tổng cộng có <strong>${totalRows}</strong> tin tuyển dụng sẵn sàng nhập vào hệ thống.`;
    previewArea.classList.remove('d-none');
    confirmBtn.disabled = false;
}

/**
 * Xác nhận gửi dữ liệu CSV đã parse lên API
 */
async function handleConfirmImportCsv() {
    if (parsedCsvRecords.length === 0) return;
    const btn = document.getElementById('btnConfirmImportCsv');
    Utils.setButtonLoading(btn, true);

    try {
        const res = await API.jobs.importCSV(parsedCsvRecords);
        if (res.success) {
            Utils.showToast(res.message || `Đã nhập thành công ${parsedCsvRecords.length} tin tuyển dụng!`, 'success');
            csvModal?.hide();
            await loadJobs();
        } else {
            Utils.showToast(res.message || 'Lỗi nhập dữ liệu từ CSV!', 'danger');
        }
    } catch (e) {
        Utils.showToast('Lỗi máy chủ khi gửi dữ liệu CSV!', 'danger');
    } finally {
        Utils.setButtonLoading(btn, false);
    }
}

/**
 * Tải file CSV mẫu chuẩn
 */
function downloadSampleCsv() {
    const csvContent = "title,company,position_id,location,salary,experience_required,skills,technologies,certificates,deadline,description\n" +
        '"Senior Backend Developer","Viettel Solutions","1","Hà Nội","25 - 40 triệu VNĐ","3+ năm","Java;Spring Boot;SQL;Microservices","Kafka;Docker;Oracle","AWS Solutions Architect","2026-12-31","Xây dựng giải pháp thành phố thông minh Smart City"\n' +
        '"Frontend ReactJS Engineer","VNPAY","2","Hà Nội","18 - 30 triệu VNĐ","2+ năm","JavaScript;TypeScript;ReactJS;HTML5/CSS3","Redux;Tailwind CSS;Webpack","","2026-12-15","Phát triển các cổng thanh toán điện tử và VNPAY-QR"';

    const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = "tin_tuyen_dung_mau.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    Utils.showToast('Đã tải xuống file CSV mẫu!', 'info');
}
