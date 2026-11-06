/**
 * main.js - Các hàm tiện ích dùng chung trong toàn bộ hệ thống
 */

document.addEventListener('DOMContentLoaded', () => {
    // Khởi tạo tooltips của Bootstrap nếu có
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});

/**
 * Hiển thị thông báo động (Alert) ở đầu trang
 * @param {string} message - Nội dung thông báo
 * @param {'success'|'danger'|'warning'|'info'} type - Loại thông báo (màu sắc)
 * @param {number} autoDismissMs - Thời gian tự đóng (ms), mặc định 4000ms, 0 là không đóng
 */
function showAlert(message, type = 'info', autoDismissMs = 4000) {
    const container = document.getElementById('dynamicAlertContainer');
    if (!container) return;

    const alertId = 'alert-' + Date.now();
    const iconMap = {
        success: 'bi-check-circle-fill',
        danger: 'bi-exclamation-triangle-fill',
        warning: 'bi-exclamation-circle-fill',
        info: 'bi-info-circle-fill'
    };
    const iconClass = iconMap[type] || 'bi-info-circle-fill';

    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show shadow-sm d-flex align-items-center" role="alert">
            <i class="bi ${iconClass} fs-5 me-2"></i>
            <div class="flex-grow-1">${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Đóng"></button>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', alertHtml);

    if (autoDismissMs > 0) {
        setTimeout(() => {
            const alertEl = document.getElementById(alertId);
            if (alertEl) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
                bsAlert.close();
            }
        }, autoDismissMs);
    }
}

/**
 * Điều khiển trạng thái Loading toàn trang
 * @param {boolean} show - true: bật spinner, false: tắt
 * @param {string} text - Thông điệp loading
 */
function showLoading(show, text = 'Đang tải dữ liệu...') {
    const loader = document.getElementById('globalLoading');
    const loadingText = document.getElementById('loadingText');
    if (!loader) return;

    if (show) {
        if (loadingText) loadingText.textContent = text;
        loader.classList.remove('d-none');
    } else {
        loader.classList.add('d-none');
    }
}

/**
 * Định dạng chuỗi ngày tháng sang DD/MM/YYYY
 * @param {string} dateString 
 * @returns {string}
 */
function formatDate(dateString) {
    if (!dateString) return 'Chưa có';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return date.toLocaleDateString('vi-VN');
}

/**
 * Kiểm tra tính hợp lệ của Form (Client-side validation)
 * @param {HTMLFormElement} formElement
 * @returns {boolean}
 */
function validateForm(formElement) {
    if (!formElement.checkValidity()) {
        formElement.classList.add('was-validated');
        return false;
    }
    formElement.classList.remove('was-validated');
    return true;
}
