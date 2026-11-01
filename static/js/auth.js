/**
 * auth.js - Xử lý đăng nhập và đăng ký tài khoản người dùng
 * Đề tài: NLCNPM23CS-38
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. CHỨC NĂNG ẨN / HIỆN MẬT KHẨU
    const togglePasswordBtn = document.getElementById('togglePasswordBtn');
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', () => {
            const pwdInput = document.getElementById('loginPassword');
            const icon = togglePasswordBtn.querySelector('i');
            if (pwdInput.type === 'password') {
                pwdInput.type = 'text';
                icon.className = 'bi bi-eye-slash';
            } else {
                pwdInput.type = 'password';
                icon.className = 'bi bi-eye';
            }
        });
    }

    // 2. FORM ĐĂNG NHẬP
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const emailInput = document.getElementById('loginEmail');
            const passwordInput = document.getElementById('loginPassword');
            const submitBtn = document.getElementById('btnLoginSubmit');
            const emailFeedback = document.getElementById('loginEmailFeedback');
            const passwordFeedback = document.getElementById('loginPasswordFeedback');

            // Reset trạng thái lỗi
            let isValid = true;
            emailInput.classList.remove('is-invalid');
            passwordInput.classList.remove('is-invalid');
            if (emailFeedback) emailFeedback.classList.add('d-none');
            if (passwordFeedback) passwordFeedback.classList.add('d-none');

            const email = emailInput.value.trim();
            const password = passwordInput.value.trim();

            // Kiểm tra email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!email || !emailRegex.test(email)) {
                emailInput.classList.add('is-invalid');
                if (emailFeedback) {
                    emailFeedback.textContent = 'Vui lòng nhập định dạng email hợp lệ (vd: an@domain.com)';
                    emailFeedback.classList.remove('d-none');
                }
                isValid = false;
            }

            // Kiểm tra mật khẩu
            if (!password || password.length < 6) {
                passwordInput.classList.add('is-invalid');
                if (passwordFeedback) {
                    passwordFeedback.textContent = 'Mật khẩu phải có ít nhất 6 ký tự!';
                    passwordFeedback.classList.remove('d-none');
                }
                isValid = false;
            }

            if (!isValid) return;

            // Chặn bấm lặp và gửi API
            Utils.setButtonLoading(submitBtn, true);

            try {
                const response = await API.auth.login({ email, password });
                if (response.success) {
                    Utils.showToast(response.message || 'Đăng nhập thành công! Đang chuyển hướng...', 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 800);
                } else {
                    Utils.showToast(response.message || 'Email hoặc mật khẩu không chính xác', 'danger');
                    passwordInput.classList.add('is-invalid');
                    Utils.setButtonLoading(submitBtn, false);
                }
            } catch (err) {
                Utils.showToast(err.message || 'Lỗi kết nối máy chủ khi đăng nhập!', 'danger');
                Utils.setButtonLoading(submitBtn, false);
            }
        });
    }

    // 3. FORM ĐĂNG KÝ
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const fullNameInput = document.getElementById('regFullName');
            const emailInput = document.getElementById('regEmail');
            const passwordInput = document.getElementById('regPassword');
            const confirmInput = document.getElementById('regConfirmPassword');
            const termsInput = document.getElementById('regTerms');
            const submitBtn = document.getElementById('btnRegisterSubmit');

            const fullNameFeedback = document.getElementById('regFullNameFeedback');
            const emailFeedback = document.getElementById('regEmailFeedback');
            const passwordFeedback = document.getElementById('regPasswordFeedback');
            const confirmFeedback = document.getElementById('regConfirmPasswordFeedback');
            const termsFeedback = document.getElementById('regTermsFeedback');

            let isValid = true;

            // Reset validate UI
            [fullNameInput, emailInput, passwordInput, confirmInput, termsInput].forEach(el => el.classList.remove('is-invalid'));
            [fullNameFeedback, emailFeedback, passwordFeedback, confirmFeedback, termsFeedback].forEach(el => el && el.classList.add('d-none'));

            const fullName = fullNameInput.value.trim();
            const email = emailInput.value.trim();
            const password = passwordInput.value;
            const confirm = confirmInput.value;

            // Kiểm tra họ tên
            if (!fullName) {
                fullNameInput.classList.add('is-invalid');
                if (fullNameFeedback) fullNameFeedback.classList.remove('d-none');
                isValid = false;
            }

            // Kiểm tra email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!email || !emailRegex.test(email)) {
                emailInput.classList.add('is-invalid');
                if (emailFeedback) {
                    emailFeedback.textContent = 'Định dạng email không hợp lệ!';
                    emailFeedback.classList.remove('d-none');
                }
                isValid = false;
            }

            // Kiểm tra mật khẩu
            if (!password || password.length < 6) {
                passwordInput.classList.add('is-invalid');
                if (passwordFeedback) {
                    passwordFeedback.textContent = 'Mật khẩu phải từ 6 ký tự trở lên!';
                    passwordFeedback.classList.remove('d-none');
                }
                isValid = false;
            }

            // Kiểm tra khớp mật khẩu
            if (password !== confirm) {
                confirmInput.classList.add('is-invalid');
                if (confirmFeedback) {
                    confirmFeedback.textContent = 'Mật khẩu nhập lại không trùng khớp!';
                    confirmFeedback.classList.remove('d-none');
                }
                isValid = false;
            }

            // Kiểm tra điều khoản
            if (!termsInput.checked) {
                termsInput.classList.add('is-invalid');
                if (termsFeedback) termsFeedback.classList.remove('d-none');
                isValid = false;
            }

            if (!isValid) return;

            // Chặn bấm lặp
            Utils.setButtonLoading(submitBtn, true);

            try {
                const response = await API.auth.register({
                    full_name: fullName,
                    email: email,
                    password: password
                });

                if (response.success) {
                    Utils.showToast('Tài khoản đã tạo thành công! Đang chuyển đến trang chủ...', 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    Utils.showToast(response.message || 'Đăng ký thất bại, vui lòng thử lại.', 'danger');
                    Utils.setButtonLoading(submitBtn, false);
                }
            } catch (err) {
                Utils.showToast(err.message || 'Lỗi máy chủ khi đăng ký tài khoản!', 'danger');
                Utils.setButtonLoading(submitBtn, false);
            }
        });
    }
});
