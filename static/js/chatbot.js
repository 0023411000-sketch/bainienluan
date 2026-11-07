/**
 * chatbot.js - Giao diện & Logic kết nối API Chatbot góc phải dưới cùng (Cách 3 Hybrid AI + SQLite RAG)
 * Đề tài: NLCNPM23CS-38 - Hệ thống định hướng kỹ năng nghề nghiệp CNTT
 */

const ChatbotWidget = (() => {
    let isOpen = false;
    let isSending = false;
    let chatHistory = [];
    const STORAGE_KEY_API = 'it_career_chatbot_api_key';

    // =========================================================================
    // HÀM GỌI API CHATBOT TRUNG TÂM (KẾT NỐI BACKEND /api/chatbot + FALLBACK)
    // =========================================================================
    async function sendMessageToChatbotAPI(userMessage, history = []) {
        const botConfig = (typeof CONFIG !== 'undefined' && CONFIG.CHATBOT) ? CONFIG.CHATBOT : {
            PROVIDER: 'backend',
            API_URL: '/api/chatbot'
        };
        const savedUserKey = (localStorage.getItem(STORAGE_KEY_API) || botConfig.API_KEY || '').trim();

        const token = localStorage.getItem(CONFIG?.STORAGE_KEYS?.AUTH_TOKEN || 'it_career_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const currentUser = (typeof Utils !== 'undefined' && Utils.auth && typeof Utils.auth.getUser === 'function')
            ? Utils.auth.getUser()
            : null;

        const res = await fetch(botConfig.API_URL || '/api/chatbot', {
            method: 'POST',
            headers,
            credentials: 'same-origin',
            body: JSON.stringify({
                message: userMessage,
                history: history,
                api_key: savedUserKey,
                user_id: currentUser ? currentUser.id : null
            })
        });
        const result = await res.json();
        if (!res.ok || !result.success) {
            throw new Error(result.message || 'Không thể kết nối máy chủ Chatbot');
        }
        return result.data?.reply || 'Mình đã nhận được câu hỏi của bạn!';
    }

    // =========================================================================
    // CÁC HÀM XỬ LÝ GIAO DIỆN HỘP THOẠI CHAT
    // =========================================================================
    function formatBotMessage(text) {
        if (!text) return '';
        const escaped = Utils ? Utils.escapeHtml(text) : String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        return escaped
            .replace(/^###\s+(.*)$/gm, '<strong class="d-block mt-2 mb-1 text-primary">$1</strong>')
            .replace(/^##\s+(.*)$/gm, '<strong class="d-block mt-2 mb-1 text-primary">$1</strong>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`([^`]+)`/g, '<code class="px-1 rounded bg-light text-dark">$1</code>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    function appendMessage(role, content) {
        const container = document.getElementById('chatbotMessages');
        if (!container) return;

        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-msg ${role === 'user' ? 'chat-msg-user' : 'chat-msg-bot'}`;

        if (role === 'user') {
            msgDiv.innerHTML = `
                <div class="chat-msg-bubble">${Utils ? Utils.escapeHtml(content) : content}</div>
            `;
        } else {
            msgDiv.innerHTML = `
                <div class="chat-msg-avatar"><i class="bi bi-robot"></i></div>
                <div class="chat-msg-bubble">${formatBotMessage(content)}</div>
            `;
        }

        container.appendChild(msgDiv);
        container.scrollTop = container.scrollHeight;
    }

    function showTypingIndicator(show) {
        const container = document.getElementById('chatbotMessages');
        if (!container) return;

        const existing = document.getElementById('chatbotTypingIndicator');
        if (existing) existing.remove();

        if (show) {
            const typingDiv = document.createElement('div');
            typingDiv.id = 'chatbotTypingIndicator';
            typingDiv.className = 'chat-msg chat-msg-bot';
            typingDiv.innerHTML = `
                <div class="chat-msg-avatar"><i class="bi bi-robot"></i></div>
                <div class="chat-msg-bubble chat-typing-dots">
                    <span></span><span></span><span></span>
                </div>
            `;
            container.appendChild(typingDiv);
            container.scrollTop = container.scrollHeight;
        }
    }

    function toggleChatWindow(forceState) {
        const windowEl = document.getElementById('chatbotWindow');
        const toggleBtn = document.getElementById('chatbotToggleBtn');
        const iconEl = document.getElementById('chatbotLauncherIcon');
        const inputEl = document.getElementById('chatbotInput');

        if (!windowEl || !toggleBtn) return;

        isOpen = typeof forceState === 'boolean' ? forceState : !isOpen;
        toggleBtn.setAttribute('aria-expanded', String(isOpen));

        if (isOpen) {
            windowEl.classList.remove('d-none');
            toggleBtn.classList.add('active');
            if (iconEl) iconEl.className = 'bi bi-x-lg chatbot-launcher-icon';
            setTimeout(() => inputEl?.focus(), 120);
        } else {
            windowEl.classList.add('d-none');
            toggleBtn.classList.remove('active');
            if (iconEl) iconEl.className = 'bi bi-chat-left-text chatbot-launcher-icon';
        }
    }

    async function handleSendMessage(messageText) {
        const text = (messageText || '').trim();
        if (!text || isSending) return;

        const inputEl = document.getElementById('chatbotInput');
        const sendBtn = document.getElementById('chatbotSendBtn');
        if (inputEl) inputEl.value = '';

        appendMessage('user', text);
        isSending = true;
        if (sendBtn) sendBtn.disabled = true;
        showTypingIndicator(true);

        try {
            const reply = await sendMessageToChatbotAPI(text, chatHistory);
            showTypingIndicator(false);
            appendMessage('bot', reply);

            chatHistory.push({ role: 'user', content: text });
            chatHistory.push({ role: 'assistant', content: reply });
            if (chatHistory.length > 16) {
                chatHistory = chatHistory.slice(-16);
            }
        } catch (err) {
            showTypingIndicator(false);
            appendMessage('bot', `⚠️ ${err.message || 'Có lỗi xảy ra khi kết nối tới API Chatbot.'}`);
        } finally {
            isSending = false;
            if (sendBtn) sendBtn.disabled = false;
            inputEl?.focus();
        }
    }

    function resetConversation() {
        chatHistory = [];
        const container = document.getElementById('chatbotMessages');
        if (!container) return;
        container.innerHTML = `
            <div class="chat-msg chat-msg-bot">
                <div class="chat-msg-avatar">
                    <i class="bi bi-robot"></i>
                </div>
                <div class="chat-msg-bubble">
                    Cuộc trò chuyện đã được làm mới! 👋 Bạn cần mình tư vấn về vị trí nghề nghiệp, kỹ năng hay lộ trình học tập nào?
                </div>
            </div>
        `;
    }

    function init() {
        const toggleBtn = document.getElementById('chatbotToggleBtn');
        const closeBtn = document.getElementById('chatbotCloseBtn');
        const clearBtn = document.getElementById('chatbotClearBtn');
        const settingsToggleBtn = document.getElementById('chatbotSettingsToggleBtn');
        const settingsPanel = document.getElementById('chatbotSettingsPanel');
        const apiKeyInput = document.getElementById('chatbotApiKeyInput');
        const saveApiKeyBtn = document.getElementById('chatbotSaveApiKeyBtn');
        const formEl = document.getElementById('chatbotForm');
        const inputEl = document.getElementById('chatbotInput');
        const suggestionsEl = document.getElementById('chatbotSuggestions');

        if (apiKeyInput) {
            apiKeyInput.value = localStorage.getItem(STORAGE_KEY_API) || '';
        }

        toggleBtn?.addEventListener('click', () => toggleChatWindow());
        closeBtn?.addEventListener('click', () => toggleChatWindow(false));
        clearBtn?.addEventListener('click', resetConversation);

        settingsToggleBtn?.addEventListener('click', () => {
            settingsPanel?.classList.toggle('d-none');
        });

        saveApiKeyBtn?.addEventListener('click', () => {
            const val = (apiKeyInput?.value || '').trim();
            if (val) {
                localStorage.setItem(STORAGE_KEY_API, val);
                if (typeof Utils !== 'undefined') Utils.showToast('Đã lưu API Key cho Chatbot AI!', 'success');
            } else {
                localStorage.removeItem(STORAGE_KEY_API);
                if (typeof Utils !== 'undefined') Utils.showToast('Đã chuyển về chế độ AI tích hợp sẵn!', 'info');
            }
            settingsPanel?.classList.add('d-none');
        });

        formEl?.addEventListener('submit', (e) => {
            e.preventDefault();
            handleSendMessage(inputEl?.value || '');
        });

        suggestionsEl?.querySelectorAll('.chatbot-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const prompt = chip.getAttribute('data-prompt');
                if (prompt) handleSendMessage(prompt);
            });
        });
    }

    return {
        init,
        open: () => toggleChatWindow(true),
        close: () => toggleChatWindow(false),
        sendMessage: handleSendMessage
    };
})();

document.addEventListener('DOMContentLoaded', () => {
    ChatbotWidget.init();
});
