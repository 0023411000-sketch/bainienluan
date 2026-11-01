/**
 * utils.js - Các hàm tiện ích dùng chung trong toàn bộ hệ thống
 * Đề tài: NLCNPM23CS-38
 */

const Utils = {
    /**
     * Chống XSS bằng cách mã hóa các ký tự đặc biệt HTML
     * @param {string} text - Chuỗi đầu vào
     * @returns {string} Chuỗi an toàn
     */
    escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    },

    /**
     * Hiển thị thông báo Toast góc màn hình bằng Bootstrap 5
     * @param {string} message - Nội dung thông báo
     * @param {'success'|'danger'|'warning'|'info'} type - Loại thông báo
     * @param {number} duration - Thời gian hiển thị (ms)
     */
    showToast(message, type = 'success', duration = 3500) {
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        const icons = {
            success: 'bi-check-circle-fill text-success',
            danger: 'bi-exclamation-triangle-fill text-danger',
            warning: 'bi-exclamation-circle-fill text-warning',
            info: 'bi-info-circle-fill text-info'
        };

        const titles = {
            success: 'Thành công',
            danger: 'Lỗi',
            warning: 'Cảnh báo',
            info: 'Thông báo'
        };

        const toastId = 'toast_' + Date.now();
        const toastEl = document.createElement('div');
        toastEl.id = toastId;
        toastEl.className = 'toast shadow-lg border-0';
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');

        toastEl.innerHTML = `
            <div class="toast-header bg-white border-bottom-0 pb-1">
                <i class="bi ${icons[type] || icons.info} fs-5 me-2"></i>
                <strong class="me-auto text-dark">${titles[type] || 'Thông báo'}</strong>
                <small class="text-muted">vừa xong</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Đóng"></button>
            </div>
            <div class="toast-body pt-1 pb-3 text-secondary">
                ${this.escapeHtml(message)}
            </div>
        `;

        container.appendChild(toastEl);
        const bsToast = new bootstrap.Toast(toastEl, { delay: duration });
        bsToast.show();

        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    },

    /**
     * Bật / tắt Spinner loading toàn trang hoặc vùng chứa
     * @param {boolean} show - Bật/tắt
     * @param {string} text - Thông điệp tải
     */
    showLoading(show = true, text = 'Đang tải dữ liệu...') {
        const overlay = document.getElementById('globalLoading');
        const textEl = document.getElementById('loadingText');
        if (!overlay) return;

        if (show) {
            if (textEl) textEl.textContent = text;
            overlay.classList.remove('d-none');
            overlay.classList.add('d-flex');
        } else {
            overlay.classList.remove('d-flex');
            overlay.classList.add('d-none');
        }
    },

    /**
     * Quản lý trạng thái nút bấm khi đang gửi request để chống nhấn đúp (double-click)
     * @param {HTMLButtonElement} btn - Phần tử button
     * @param {boolean} isLoading - Đang xử lý hay không
     * @param {string} originalHtml - Nội dung ban đầu của nút
     */
    setButtonLoading(btn, isLoading, originalHtml = '') {
        if (!btn) return;
        if (isLoading) {
            btn.dataset.originalHtml = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Đang xử lý...`;
        } else {
            btn.disabled = false;
            btn.innerHTML = originalHtml || btn.dataset.originalHtml || 'Xác nhận';
        }
    },

    /**
     * Hộp thoại xác nhận hành động bằng Modal Bootstrap
     * @param {Object} options
     * @param {string} options.title - Tiêu đề hộp thoại
     * @param {string} options.message - Nội dung hỏi
     * @param {string} [options.confirmText] - Nhãn nút xác nhận
     * @param {string} [options.confirmClass] - Class giao diện nút (btn-danger, btn-primary)
     * @param {Function} options.onConfirm - Callback thực thi khi người dùng bấm xác nhận
     */
    confirmModal({ title = 'Xác nhận', message = 'Bạn có chắc chắn muốn thực hiện hành động này?', confirmText = 'Xóa dữ liệu', confirmClass = 'btn-danger', onConfirm }) {
        let modalEl = document.getElementById('universalConfirmModal');
        if (!modalEl) {
            modalEl = document.createElement('div');
            modalEl.id = 'universalConfirmModal';
            modalEl.className = 'modal fade';
            modalEl.setAttribute('tabindex', '-1');
            modalEl.setAttribute('aria-hidden', 'true');
            modalEl.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content border-0 shadow">
                        <div class="modal-header border-0 pb-0">
                            <h5 class="modal-title fw-bold text-dark" id="confirmModalTitle">Xác nhận</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Đóng"></button>
                        </div>
                        <div class="modal-body py-3 text-secondary" id="confirmModalBody">
                            Nội dung xác nhận
                        </div>
                        <div class="modal-footer border-0 pt-0">
                            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Hủy bỏ</button>
                            <button type="button" class="btn" id="confirmModalBtn">Đồng ý</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modalEl);
        }

        document.getElementById('confirmModalTitle').textContent = title;
        document.getElementById('confirmModalBody').textContent = message;
        const confirmBtn = document.getElementById('confirmModalBtn');
        confirmBtn.className = `btn ${confirmClass}`;
        confirmBtn.textContent = confirmText;

        const bsModal = new bootstrap.Modal(modalEl);

        // Xóa listener cũ trước khi gắn listener mới
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        newConfirmBtn.addEventListener('click', async () => {
            bsModal.hide();
            if (typeof onConfirm === 'function') {
                await onConfirm();
            }
        });

        bsModal.show();
    },

    /**
     * Định dạng ngày tháng kiểu Việt Nam (DD/MM/YYYY)
     * @param {string} dateStr - Chuỗi ngày YYYY-MM-DD
     * @returns {string} Chuỗi hiển thị đẹp
     */
    formatDate(dateStr) {
        if (!dateStr) return 'Chưa xác định';
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return dateStr;
        const d = String(date.getDate()).padStart(2, '0');
        const m = String(date.getMonth() + 1).padStart(2, '0');
        const y = date.getFullYear();
        return `${d}/${m}/${y}`;
    },

    /**
     * Kỹ thuật Debounce giảm tần suất gọi hàm (dành cho ô tìm kiếm)
     */
    debounce(fn, delay = 300) {
        let timer = null;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    },

    /**
     * Tạo giao diện thanh phân trang chuẩn Bootstrap 5
     */
    renderPagination(containerId, currentPage, totalPages, onPageChange) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '<ul class="pagination pagination-sm justify-content-center mb-0 gap-1">';

        // Nút trang trước
        html += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <button class="page-link rounded-2" data-page="${currentPage - 1}" aria-label="Trang trước">
                    <i class="bi bi-chevron-left"></i>
                </button>
            </li>
        `;

        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
                html += `
                    <li class="page-item ${currentPage === i ? 'active' : ''}">
                        <button class="page-link rounded-2 ${currentPage === i ? 'fw-bold' : ''}" data-page="${i}">${i}</button>
                    </li>
                `;
            } else if (i === currentPage - 2 || i === currentPage + 2) {
                html += `<li class="page-item disabled"><span class="page-link rounded-2">...</span></li>`;
            }
        }

        // Nút trang sau
        html += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <button class="page-link rounded-2" data-page="${currentPage + 1}" aria-label="Trang sau">
                    <i class="bi bi-chevron-right"></i>
                </button>
            </li>
        `;

        html += '</ul>';
        container.innerHTML = html;

        // Bắt sự kiện chuyển trang
        container.querySelectorAll('button[data-page]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const targetPage = parseInt(e.currentTarget.getAttribute('data-page'));
                if (targetPage >= 1 && targetPage <= totalPages && targetPage !== currentPage) {
                    onPageChange(targetPage);
                }
            });
        });
    },

    /**
     * Tạo hiển thị ngôi sao đánh giá kỹ năng 1 - 5
     */
    renderStars(level) {
        const fullStars = Math.min(Math.max(parseInt(level) || 1, 1), 5);
        let starsHtml = '<span class="text-warning d-inline-flex gap-1 align-items-center" title="Mức độ: ' + fullStars + '/5">';
        for (let i = 1; i <= 5; i++) {
            if (i <= fullStars) {
                starsHtml += '<i class="bi bi-star-fill"></i>';
            } else {
                starsHtml += '<i class="bi bi-star text-black-50"></i>';
            }
        }
        starsHtml += ` <small class="text-muted ms-1">(${fullStars}/5)</small></span>`;
        return starsHtml;
    },

    /**
     * Tạo khối Empty State thông báo khi không có dữ liệu
     */
    renderEmptyState(container, { icon = 'bi-folder-x', title = 'Không tìm thấy dữ liệu', message = 'Hiện tại chưa có thông tin nào được hiển thị.', actionBtn = '' }) {
        if (!container) return;
        container.innerHTML = `
            <div class="text-center py-5 px-3">
                <div class="empty-state-icon mb-3 text-secondary opacity-50" style="font-size: 3.5rem;">
                    <i class="bi ${icon}"></i>
                </div>
                <h5 class="fw-bold text-dark mb-2">${this.escapeHtml(title)}</h5>
                <p class="text-muted small mb-3 mx-auto" style="max-width: 420px;">${this.escapeHtml(message)}</p>
                ${actionBtn ? actionBtn : ''}
            </div>
        `;
    },

    // Quản lý phiên đăng nhập lưu trong Storage
    auth: {
        getUser() {
            try {
                const data = localStorage.getItem(CONFIG.STORAGE_KEYS.USER_INFO);
                return data ? JSON.parse(data) : {
                    id: 1,
                    email: "an.nguyen20@sis.hust.edu.vn",
                    full_name: "Nguyễn Văn An",
                    role: "student"
                };
            } catch (e) {
                return null;
            }
        },
        setUser(user) {
            localStorage.setItem(CONFIG.STORAGE_KEYS.USER_INFO, JSON.stringify(user));
            localStorage.setItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN, user.token || ('user_' + (user.id || 1)));
        },
        clearSession() {
            localStorage.removeItem(CONFIG.STORAGE_KEYS.USER_INFO);
            localStorage.removeItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
        },
        isAuthenticated() {
            return !!localStorage.getItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
        }
    }
};

// Gắn Utils vào Window
if (typeof window !== 'undefined') {
    window.Utils = Utils;
}
