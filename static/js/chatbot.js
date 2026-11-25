/**
 * chatbot.js - Giao diện & Logic kết nối API Chatbot góc phải dưới cùng (Hybrid AI + SQLite RAG)
 * Đề tài: NLCNPM23CS-38 - Hệ thống định hướng kỹ năng nghề nghiệp CNTT
 *
 * Hỗ trợ lưu trữ xuyên suốt cuộc trò chuyện, trạng thái đóng/mở và nội dung nháp
 * khi người dùng chuyển qua lại giữa tất cả các tab/thư mục trên website.
 */

const ChatbotWidget = (() => {
    let isOpen = false;
    let isSending = false;
    let isInitialized = false;
    let chatHistory = [];
    let guestMeta = null;
    let pendingPollTimer = null;

    const STORAGE_KEY_API = 'it_career_chatbot_api_key';
    const STORAGE_PREFIX_USER = 'it_career_chat_state_u_';
    const STORAGE_KEY_GUEST = 'it_career_chat_state_guest';
    const MAX_LOCAL_MESSAGES = 40;

    // =========================================================================
    // QUẢN LÝ LƯU TRỮ TRẠNG THÁI HỘI THOẠI XUYÊN SUỐT CÁC TAB / TRANG
    // =========================================================================
    function getCurrentUser() {
        return (typeof Utils !== 'undefined' && Utils.auth && typeof Utils.auth.getUser === 'function')
            ? Utils.auth.getUser()
            : null;
    }

    function isUserAuthenticated() {
        return !!(typeof Utils !== 'undefined' && Utils.auth && typeof Utils.auth.isAuthenticated === 'function' && Utils.auth.isAuthenticated());
    }

    function getStateStorageAndKey() {
        const user = getCurrentUser();
        if (isUserAuthenticated() && user && user.id) {
            return {
                storage: window.localStorage,
                key: `${STORAGE_PREFIX_USER}${user.id}`
            };
        }
        return {
            storage: window.sessionStorage,
            key: STORAGE_KEY_GUEST
        };
    }

    function loadLocalState() {
        try {
            const { storage, key } = getStateStorageAndKey();
            const raw = storage.getItem(key);
            if (!raw) return null;
            const parsed = JSON.parse(raw);
            if (!parsed || typeof parsed !== 'object') return null;
            return {
                messages: Array.isArray(parsed.messages) ? parsed.messages : [],
                isOpen: Boolean(parsed.isOpen),
                draft: typeof parsed.draft === 'string' ? parsed.draft : '',
                guestMeta: parsed.guestMeta || null,
                pendingSince: typeof parsed.pendingSince === 'number' ? parsed.pendingSince : 0
            };
        } catch (e) {
            return null;
        }
    }

    function saveLocalState(overrides = {}) {
        try {
            const { storage, key } = getStateStorageAndKey();
            const inputEl = document.getElementById('chatbotInput');
            const prev = loadLocalState() || {};
            const nextState = {
                messages: (overrides.messages !== undefined ? overrides.messages : chatHistory).slice(-MAX_LOCAL_MESSAGES),
                isOpen: overrides.isOpen !== undefined ? Boolean(overrides.isOpen) : isOpen,
                draft: overrides.draft !== undefined ? overrides.draft : (inputEl ? inputEl.value : (prev.draft || '')),
                guestMeta: overrides.guestMeta !== undefined ? overrides.guestMeta : guestMeta,
                pendingSince: overrides.pendingSince !== undefined ? overrides.pendingSince : (prev.pendingSince || 0)
            };
            storage.setItem(key, JSON.stringify(nextState));
        } catch (e) {
            // Bỏ qua nếu trình duyệt chặn Storage
        }
    }

    // =========================================================================
    // HÀM GỌI API CHATBOT TRUNG TÂM (KẾT NỐI BACKEND /api/chatbot + HISTORY)
    // =========================================================================
    function buildAuthHeaders() {
        const token = localStorage.getItem(CONFIG?.STORAGE_KEYS?.AUTH_TOKEN || 'it_career_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }

    async function sendMessageToChatbotAPI(userMessage, history = []) {
        const botConfig = (typeof CONFIG !== 'undefined' && CONFIG.CHATBOT) ? CONFIG.CHATBOT : {
            PROVIDER: 'backend',
            API_URL: '/api/chatbot'
        };
        const savedUserKey = (localStorage.getItem(STORAGE_KEY_API) || botConfig.API_KEY || '').trim();
        const currentUser = getCurrentUser();

        const res = await fetch(botConfig.API_URL || '/api/chatbot', {
            method: 'POST',
            headers: buildAuthHeaders(),
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
        return {
            reply: result.data?.reply || 'Mình đã nhận được câu hỏi của bạn!',
            is_guest: !!result.data?.is_guest,
            require_login: !!result.data?.require_login,
            guest_remaining: result.data?.guest_remaining,
            guest_limit: result.data?.guest_limit
        };
    }

    async function fetchServerChatHistory() {
        const res = await fetch('/api/chatbot/history', {
            method: 'GET',
            headers: buildAuthHeaders(),
            credentials: 'same-origin'
        });
        if (!res.ok) return null;
        const result = await res.json();
        return result && result.success ? result.data : null;
    }

    async function clearServerChatHistory() {
        try {
            await fetch('/api/chatbot/history', {
                method: 'DELETE',
                headers: buildAuthHeaders(),
                credentials: 'same-origin'
            });
        } catch (e) {
            // Không chặn UI nếu mạng gián đoạn
        }
    }

    // =========================================================================
    // CÁC HÀM XỬ LÝ GIAO DIỆN HỘP THOẠI CHAT
    // =========================================================================
    function lockChatbotForLogin() {
        const inputEl = document.getElementById('chatbotInput');
        const sendBtn = document.getElementById('chatbotSendBtn');
        const statusEl = document.getElementById('chatbotStatusText');
        const suggestionsEl = document.getElementById('chatbotSuggestions');

        if (inputEl) {
            inputEl.disabled = true;
            inputEl.placeholder = 'Vui lòng đăng nhập để tiếp tục hỏi AI...';
        }
        if (sendBtn) sendBtn.disabled = true;
        if (statusEl) statusEl.textContent = 'Cần đăng nhập để tiếp tục';
        suggestionsEl?.querySelectorAll('.chatbot-chip').forEach(chip => {
            chip.disabled = true;
        });
    }

    function unlockChatbotInput() {
        const inputEl = document.getElementById('chatbotInput');
        const sendBtn = document.getElementById('chatbotSendBtn');
        const suggestionsEl = document.getElementById('chatbotSuggestions');

        if (inputEl) {
            inputEl.disabled = false;
            inputEl.placeholder = 'Nhập câu hỏi của bạn...';
        }
        if (sendBtn && !isSending) sendBtn.disabled = false;
        suggestionsEl?.querySelectorAll('.chatbot-chip').forEach(chip => {
            chip.disabled = false;
        });
    }

    function getWelcomeBubbleHtml(isReset = false) {
        if (!isUserAuthenticated()) {
            return `
                <div class="chat-msg chat-msg-bot">
                    <div class="chat-msg-avatar">
                        <i class="bi bi-robot"></i>
                    </div>
                    <div class="chat-msg-bubble">
                        Xin chào! 👋 Bạn đang ở <strong>chế độ khách</strong> (tối đa 4 câu hỏi chung ngắn). Hãy <a href="/login" class="fw-bold text-primary text-decoration-underline">đăng nhập</a> để được tư vấn chuyên sâu!
                    </div>
                </div>
            `;
        }
        if (isReset) {
            return `
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
        return `
            <div class="chat-msg chat-msg-bot">
                <div class="chat-msg-avatar">
                    <i class="bi bi-robot"></i>
                </div>
                <div class="chat-msg-bubble">
                    Xin chào! 👋 Mình là <strong>Trợ lý AI Định hướng Nghề nghiệp CNTT</strong> (đã kết nối trực tiếp với hồ sơ & CSDL tuyển dụng của bạn).<br>
                    Bạn có thể bấm chọn câu hỏi nhanh bên dưới hoặc hỏi bất kỳ câu hỏi nào nhé!
                </div>
            </div>
        `;
    }

    function applyChatbotAuthModeUI() {
        const statusEl = document.getElementById('chatbotStatusText');
        const suggestionsEl = document.getElementById('chatbotSuggestions');

        if (isUserAuthenticated()) {
            if (statusEl) statusEl.textContent = 'Đã kết nối AI + CSDL SQLite';
            unlockChatbotInput();
            return;
        }

        if (statusEl) {
            if (guestMeta && guestMeta.require_login) {
                statusEl.textContent = 'Cần đăng nhập để tiếp tục';
            } else if (guestMeta && typeof guestMeta.guest_remaining === 'number' && guestMeta.guest_limit) {
                statusEl.textContent = `Chế độ khách (Còn ${guestMeta.guest_remaining}/${guestMeta.guest_limit} lượt)`;
            } else {
                statusEl.textContent = 'Chế độ khách (Hỏi đáp chung)';
            }
        }

        if (suggestionsEl) {
            suggestionsEl.innerHTML = `
                <div class="d-flex gap-1 overflow-auto pb-1 chatbot-chips-scroll">
                    <button type="button" class="btn btn-sm chatbot-chip" data-prompt="Xin chào, bạn có thể làm gì?">
                        👋 Giới thiệu AI
                    </button>
                    <button type="button" class="btn btn-sm chatbot-chip" data-prompt="Website IT Career Compass dùng để làm gì?">
                        🌐 Tổng quan website
                    </button>
                    <button type="button" class="btn btn-sm chatbot-chip" data-prompt="Làm sao để đăng nhập và dùng tính năng chuyên sâu?">
                        🔑 Cách dùng chuyên sâu
                    </button>
                </div>
            `;
            suggestionsEl.querySelectorAll('.chatbot-chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    const prompt = chip.getAttribute('data-prompt');
                    if (prompt) handleSendMessage(prompt);
                });
            });
        }

        if (guestMeta && guestMeta.require_login) {
            lockChatbotForLogin();
        }
    }

    function formatBotMessage(text) {
        if (!text) return '';
        const escaped = Utils ? Utils.escapeHtml(text) : String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        return escaped
            .replace(/^####\s+(.*)$/gm, '<strong class="d-block mt-2 mb-1 text-primary">$1</strong>')
            .replace(/^###\s+(.*)$/gm, '<strong class="d-block mt-2 mb-1 text-primary">$1</strong>')
            .replace(/^##\s+(.*)$/gm, '<strong class="d-block mt-2 mb-1 text-primary">$1</strong>')
            .replace(/^\s*[-*•]\s+(.*)$/gm, '• $1')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\[([^\]]+)\]\((\/[^\s)]+)\)/g, '<a href="$2" class="fw-bold text-primary text-decoration-underline">$1</a>')
            .replace(/\n/g, '<br>');
    }

    function scrollMessagesToBottom() {
        const container = document.getElementById('chatbotMessages');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    function appendMessageElement(role, content) {
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
    }

    function renderAllMessages(isReset = false) {
        const container = document.getElementById('chatbotMessages');
        if (!container) return;

        container.innerHTML = getWelcomeBubbleHtml(isReset);
        chatHistory.forEach(item => {
            if (!item || !item.content) return;
            appendMessageElement(item.role === 'user' ? 'user' : 'bot', item.content);
        });
        scrollMessagesToBottom();
    }

    function appendMessage(role, content) {
        appendMessageElement(role, content);
        scrollMessagesToBottom();
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
            scrollMessagesToBottom();
        }
    }

    function toggleChatWindow(forceState, options = {}) {
        const { skipFocus = false, skipSave = false } = options;
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
            scrollMessagesToBottom();
            if (!skipFocus) {
                setTimeout(() => inputEl?.focus(), 100);
            }
        } else {
            windowEl.classList.add('d-none');
            toggleBtn.classList.remove('active');
            if (iconEl) iconEl.className = 'bi bi-chat-left-text chatbot-launcher-icon';
        }

        if (!skipSave) {
            saveLocalState({ isOpen });
        }
    }

    async function handleSendMessage(messageText) {
        const text = (messageText || '').trim();
        if (!text || isSending) return;

        const inputEl = document.getElementById('chatbotInput');
        const sendBtn = document.getElementById('chatbotSendBtn');
        if (inputEl) inputEl.value = '';

        const historyBeforeSend = chatHistory.slice(-16);

        // Lưu ngay câu hỏi của người dùng để nếu chuyển tab tức thì cũng không mất câu vừa hỏi
        chatHistory.push({ role: 'user', content: text });
        if (chatHistory.length > MAX_LOCAL_MESSAGES) {
            chatHistory = chatHistory.slice(-MAX_LOCAL_MESSAGES);
        }
        saveLocalState({ messages: chatHistory, draft: '', pendingSince: Date.now() });

        appendMessage('user', text);
        isSending = true;
        if (sendBtn) sendBtn.disabled = true;
        showTypingIndicator(true);

        try {
            const data = await sendMessageToChatbotAPI(text, historyBeforeSend);
            const reply = data.reply;
            showTypingIndicator(false);
            appendMessage('bot', reply);

            if (data.is_guest && typeof data.guest_remaining === 'number') {
                guestMeta = {
                    guest_remaining: data.guest_remaining,
                    guest_limit: data.guest_limit,
                    require_login: !!data.require_login
                };
                const statusEl = document.getElementById('chatbotStatusText');
                if (statusEl) {
                    statusEl.textContent = data.require_login
                        ? 'Cần đăng nhập để tiếp tục'
                        : `Chế độ khách (Còn ${data.guest_remaining}/${data.guest_limit} lượt)`;
                }
            }

            if (data.require_login) {
                lockChatbotForLogin();
            }

            chatHistory.push({ role: 'assistant', content: reply });
            if (chatHistory.length > MAX_LOCAL_MESSAGES) {
                chatHistory = chatHistory.slice(-MAX_LOCAL_MESSAGES);
            }
            saveLocalState({ messages: chatHistory, guestMeta, pendingSince: 0 });
        } catch (err) {
            showTypingIndicator(false);
            const errMsg = `⚠️ ${err.message || 'Có lỗi xảy ra khi kết nối tới API Chatbot.'}`;
            appendMessage('bot', errMsg);
            chatHistory.push({ role: 'assistant', content: errMsg });
            saveLocalState({ messages: chatHistory, pendingSince: 0 });
        } finally {
            isSending = false;
            const inputLocked = !!(inputEl && inputEl.disabled);
            if (sendBtn && !inputLocked) sendBtn.disabled = false;
            if (!inputLocked) inputEl?.focus();
        }
    }

    async function resetConversation() {
        if (pendingPollTimer) {
            clearTimeout(pendingPollTimer);
            pendingPollTimer = null;
        }
        chatHistory = [];
        saveLocalState({ messages: [], draft: '', pendingSince: 0 });
        renderAllMessages(true);
        applyChatbotAuthModeUI();
        await clearServerChatHistory();
    }

    async function syncHistoryFromBackendOnLoad(initialPendingSince = 0, attempt = 0) {
        if (isSending) return;
        try {
            const serverData = await fetchServerChatHistory();
            if (!serverData || isSending) return;

            if (serverData.is_guest) {
                guestMeta = {
                    guest_remaining: serverData.guest_remaining,
                    guest_limit: serverData.guest_limit,
                    require_login: !!serverData.require_login
                };
                applyChatbotAuthModeUI();
            }

            const serverMsgs = Array.isArray(serverData.messages) ? serverData.messages : [];
            const lastLocal = chatHistory[chatHistory.length - 1];
            const lastServer = serverMsgs[serverMsgs.length - 1];

            // Đồng bộ nếu máy chủ có nhiều tin nhắn hơn (ví dụ câu trả lời hoàn tất khi đang chuyển tab hoặc đăng nhập từ trình duyệt mới)
            if (
                serverMsgs.length > chatHistory.length ||
                (serverMsgs.length > 0 && lastLocal && lastLocal.role === 'user' && lastServer && lastServer.role === 'assistant')
            ) {
                showTypingIndicator(false);
                chatHistory = serverMsgs.slice(-MAX_LOCAL_MESSAGES);
                saveLocalState({ messages: chatHistory, guestMeta, pendingSince: 0 });
                renderAllMessages(false);
                return;
            }

            // Nếu người dùng vừa gửi câu hỏi rồi bấm chuyển tab ngay khi AI đang suy nghĩ (< 25 giây)
            const stillWaitingReply =
                initialPendingSince > 0 &&
                Date.now() - initialPendingSince < 25000 &&
                lastLocal &&
                lastLocal.role === 'user' &&
                attempt < 8;

            if (stillWaitingReply) {
                showTypingIndicator(true);
                pendingPollTimer = setTimeout(() => {
                    syncHistoryFromBackendOnLoad(initialPendingSince, attempt + 1);
                }, 2000);
            } else if (initialPendingSince > 0) {
                showTypingIndicator(false);
                saveLocalState({ pendingSince: 0 });
            }
        } catch (e) {
            // Giữ nguyên dữ liệu LocalStorage nếu ngoại tuyến
        }
    }

    function init() {
        if (isInitialized) return;
        const windowEl = document.getElementById('chatbotWindow');
        if (!windowEl) return;
        isInitialized = true;

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

        // 1. Khôi phục tức thì cuộc trò chuyện, trạng thái mở/đóng & bản nháp khi chuyển tab
        const saved = loadLocalState();
        if (saved) {
            chatHistory = saved.messages;
            guestMeta = saved.guestMeta;
            if (inputEl && saved.draft) {
                inputEl.value = saved.draft;
            }
        }

        toggleBtn?.addEventListener('click', () => toggleChatWindow());
        closeBtn?.addEventListener('click', () => toggleChatWindow(false));
        clearBtn?.addEventListener('click', resetConversation);

        inputEl?.addEventListener('input', () => {
            saveLocalState({ draft: inputEl.value });
        });

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

        applyChatbotAuthModeUI();
        renderAllMessages(false);

        if (saved && saved.isOpen) {
            toggleChatWindow(true, { skipFocus: true, skipSave: true });
        }

        // 2. Đồng bộ ngầm với CSDL SQLite trên máy chủ (không gây chớp nháy giao diện)
        syncHistoryFromBackendOnLoad(saved ? saved.pendingSince : 0);
    }

    return {
        init,
        open: () => toggleChatWindow(true),
        close: () => toggleChatWindow(false),
        sendMessage: handleSendMessage
    };
})();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ChatbotWidget.init());
} else {
    ChatbotWidget.init();
}
