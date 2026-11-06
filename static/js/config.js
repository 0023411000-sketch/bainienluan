/**
 * config.js - Cấu hình hệ thống Frontend
 * Đề tài: NLCNPM23CS-38 - Hệ thống định hướng kỹ năng nghề nghiệp CNTT
 */

const CONFIG = {
    // CỜ CẤU HÌNH QUAN TRỌNG:
    // Đổi sang false để ngắt Mock và kết nối trực tiếp đến Backend Flask thật
    USE_MOCK: false,

    // Địa chỉ gốc của API backend
    API_BASE_URL: '/api',

    // Thời gian giả lập độ trễ mạng (ms) khi chạy Mock để trải nghiệm cảm giác gọi server
    MOCK_DELAY_MS: 300,

    // Thời gian tự tắt thông báo Toast (ms)
    TOAST_DURATION: 3500,

    // Khóa lưu phiên đăng nhập trong LocalStorage/SessionStorage
    STORAGE_KEYS: {
        AUTH_TOKEN: 'it_career_token',
        USER_INFO: 'it_career_user'
    },

    // Phân trang mặc định
    DEFAULT_PAGE_SIZE: 8
};

// Đóng băng cấu hình để tránh ghi đè ngoài ý muốn
Object.freeze(CONFIG);
