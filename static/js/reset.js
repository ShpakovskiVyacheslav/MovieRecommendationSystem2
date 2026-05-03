const codeInput = document.getElementById('code');
const passwordInput = document.getElementById('new_password');
const confirmInput = document.getElementById('confirm_password');
const submitBtn = document.getElementById('submitBtn');
const confirmError = document.getElementById('confirmError');
const resetForm = document.getElementById('resetForm');
const errorMessage = document.getElementById('errorMessage');

function checkPasswordStrength(password) {
    const lengthValid = password.length >= 8 && password.length <= 16;
    const lowercaseValid = /[a-z]/.test(password);
    const uppercaseValid = /[A-Z]/.test(password);
    const digitValid = /[0-9]/.test(password);
    const specialValid = /[!@#$%^&*]/.test(password);

    const lengthReq = document.getElementById('lengthReq');
    const lowercaseReq = document.getElementById('lowercaseReq');
    const uppercaseReq = document.getElementById('uppercaseReq');
    const digitReq = document.getElementById('digitReq');
    const specialReq = document.getElementById('specialReq');
    const strengthBox = document.getElementById('strengthBox');
    const strengthText = document.getElementById('strengthText');

    if (lengthReq) {
        lengthReq.className = lengthValid ? 'requirement valid' : 'requirement invalid';
        lengthReq.innerHTML = lengthValid ? '✓ 8-16 символов' : '✗ 8-16 символов';
    }
    if (lowercaseReq) {
        lowercaseReq.className = lowercaseValid ? 'requirement valid' : 'requirement invalid';
        lowercaseReq.innerHTML = lowercaseValid ? '✓ Строчные буквы (a-z)' : '✗ Строчные буквы (a-z)';
    }
    if (uppercaseReq) {
        uppercaseReq.className = uppercaseValid ? 'requirement valid' : 'requirement invalid';
        uppercaseReq.innerHTML = uppercaseValid ? '✓ Заглавные буквы (A-Z)' : '✗ Заглавные буквы (A-Z)';
    }
    if (digitReq) {
        digitReq.className = digitValid ? 'requirement valid' : 'requirement invalid';
        digitReq.innerHTML = digitValid ? '✓ Цифры (0-9)' : '✗ Цифры (0-9)';
    }
    if (specialReq) {
        specialReq.className = specialValid ? 'requirement valid' : 'requirement invalid';
        specialReq.innerHTML = specialValid ? '✓ Спецсимволы (!@#$%^&*)' : '✗ Спецсимволы (!@#$%^&*)';
    }

    const allValid = lengthValid && lowercaseValid && uppercaseValid && digitValid && specialValid;

    if (password.length > 0 && strengthBox) {
        strengthBox.style.display = 'block';

        let strength = 0;
        if (lengthValid) strength++;
        if (lowercaseValid) strength++;
        if (uppercaseValid) strength++;
        if (digitValid) strength++;
        if (specialValid) strength++;

        strengthBox.classList.remove('strength-weak', 'strength-medium', 'strength-strong');

        if (strength <= 2) {
            strengthBox.classList.add('strength-weak');
            if (strengthText) strengthText.innerText = 'Слабый';
        } else if (strength <= 4) {
            strengthBox.classList.add('strength-medium');
            if (strengthText) strengthText.innerText = 'Средний';
        } else {
            strengthBox.classList.add('strength-strong');
            if (strengthText) strengthText.innerText = 'Сильный';
        }
    } else if (strengthBox) {
        strengthBox.style.display = 'none';
    }

    return allValid;
}

function checkPasswordsMatch() {
    const password = passwordInput ? passwordInput.value : '';
    const confirm = confirmInput ? confirmInput.value : '';

    if (confirm.length > 0 && password !== confirm) {
        if (confirmError) confirmError.style.display = 'block';
        return false;
    } else {
        if (confirmError) confirmError.style.display = 'none';
        return true;
    }
}

function updateSubmitButton() {
    const passwordValid = checkPasswordStrength(passwordInput ? passwordInput.value : '');
    const passwordsMatch = checkPasswordsMatch();
    const passwordNotEmpty = passwordInput ? passwordInput.value.length > 0 : false;
    const codeNotEmpty = codeInput ? codeInput.value.length > 0 : false;

    if (submitBtn) {
        if (passwordValid && passwordsMatch && passwordNotEmpty && codeNotEmpty) {
            submitBtn.disabled = false;
        } else {
            submitBtn.disabled = true;
        }
    }
}

if (resetForm) {
    resetForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(resetForm);

        try {
            const response = await fetch('/reset_confirm', {
                method: 'POST',
                body: formData
            });

            const text = await response.text();

            if (text.includes('Неверный код')) {
                if (errorMessage) {
                    errorMessage.style.display = 'block';
                    errorMessage.innerHTML = '❌ Неверный код подтверждения. Попробуйте ещё раз.';
                }
                if (codeInput) codeInput.classList.add('invalid');
                setTimeout(() => {
                    if (errorMessage) errorMessage.style.display = 'none';
                    if (codeInput) codeInput.classList.remove('invalid');
                }, 3000);
            } else if (text.includes('Пароли не совпадают')) {
                if (errorMessage) {
                    errorMessage.style.display = 'block';
                    errorMessage.innerHTML = '❌ Пароли не совпадают';
                }
                setTimeout(() => {
                    if (errorMessage) errorMessage.style.display = 'none';
                }, 3000);
            } else if (text.includes('Код истёк')) {
                if (errorMessage) {
                    errorMessage.style.display = 'block';
                    errorMessage.innerHTML = '❌ Код истёк. Запросите новый код.';
                }
                setTimeout(() => {
                    if (errorMessage) errorMessage.style.display = 'none';
                    window.location.href = '/reset';
                }, 3000);
            } else if (response.ok || text.includes('redirect')) {
                window.location.href = '/';
            } else {
                if (errorMessage) {
                    errorMessage.style.display = 'block';
                    errorMessage.innerHTML = '❌ Ошибка. Попробуйте ещё раз.';
                }
                setTimeout(() => {
                    if (errorMessage) errorMessage.style.display = 'none';
                }, 3000);
            }
        } catch (error) {
            if (errorMessage) {
                errorMessage.style.display = 'block';
                errorMessage.innerHTML = '❌ Ошибка соединения. Попробуйте ещё раз.';
            }
            setTimeout(() => {
                if (errorMessage) errorMessage.style.display = 'none';
            }, 3000);
        }
    });
}

if (codeInput) codeInput.addEventListener('input', function() { updateSubmitButton(); });
if (passwordInput) passwordInput.addEventListener('input', function() { updateSubmitButton(); });
if (confirmInput) confirmInput.addEventListener('input', function() { updateSubmitButton(); });
