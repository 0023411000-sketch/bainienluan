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
    DEFAULT_PAGE_SIZE: 8,

    // =========================================================================
    // CẤU HÌNH API CHATBOT HỎI ĐÁP (GÓC PHẢI DƯỚI CÙNG)
    // Bạn có thể chọn 1 trong 4 chế độ tại PROVIDER:
    // - 'backend' : Gọi về Flask Backend (/api/chatbot trong app.py) - Khuyên dùng
    // - 'gemini'  : Gọi trực tiếp Google Gemini API (điền API_KEY bên dưới)
    // - 'openai'  : Gọi trực tiếp OpenAI / Groq / DeepSeek API (điền API_KEY bên dưới)
    // - 'custom'  : Gọi tới bất kỳ API URL / Webhook riêng nào của bạn
    // =========================================================================
    CHATBOT: {
        PROVIDER: 'backend',                  // 'backend' | 'gemini' | 'openai' | 'custom'
        API_URL: '/api/chatbot',              // Đổi thành URL API của bạn nếu dùng 'custom' hoặc 'openai'
        API_KEY: '',                          // Điền API Key của bạn vào đây (nếu gọi trực tiếp từ Frontend)
        MODEL: 'gemini-2.5-flash',            // Tên model (VD: 'gemini-2.5-flash' hoặc 'gpt-4o-mini')
        SYSTEM_PROMPT: 'Bạn là Trợ lý AI tư vấn định hướng kỹ năng nghề nghiệp cho sinh viên ngành Công nghệ Thông tin (IT Career Compass). Hãy trả lời ngắn gọn, súc tích, thân thiện bằng tiếng Việt.'
    }
};

// Đóng băng cấu hình để tránh ghi đè ngoài ý muốn
Object.freeze(CONFIG);
