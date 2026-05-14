const codeInput = document.getElementById('code');
const passwordInput = document.getElementById('new_password');
const confirmInput = document.getElementById('confirm_password');
const submitBtn = document.getElementById('submitBtn');
const confirmError = document.getElementById('confirmError');
const resetForm = document.getElementById('resetForm');
const errorMessage = document.getElementById('errorMessage');

const lengthReq = document.getElementById('lengthReq');
const lowercaseReq = document.getElementById('lowercaseReq');
const uppercaseReq = document.getElementById('uppercaseReq');
const digitReq = document.getElementById('digitReq');
const specialReq = document.getElementById('specialReq');

function checkPasswordStrength(password) {
    const lengthValid = password.length >= 8 && password.length <= 16;
    const lowercaseValid = /[a-z]/.test(password);
    const uppercaseValid = /[A-Z]/.test(password);
    const digitValid = /[0-9]/.test(password);
    const specialValid = /[!@#$%^&*]/.test(password);

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
    return allValid;
}

function checkPasswordsMatch() {
    const password = passwordInput.value;
    const confirm = confirmInput.value;

    if (confirm.length > 0 && password !== confirm) {
        confirmError.style.display = 'block';
        return false;
    } else {
        confirmError.style.display = 'none';
        return true;
    }
}

function updateSubmitButton() {
    const passwordValid = checkPasswordStrength(passwordInput.value);
    const passwordsMatch = checkPasswordsMatch();
    const passwordNotEmpty = passwordInput.value.length > 0;
    const codeNotEmpty = codeInput.value.length > 0;

    if (passwordValid && passwordsMatch && passwordNotEmpty && codeNotEmpty) {
        submitBtn.disabled = false;
    } else {
        submitBtn.disabled = true;
    }
}

resetForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(resetForm);

    try {
        const response = await fetch('/reset_confirm', {
            method: 'POST',
            body: formData
        });

        const text = await response.text();

        if (text.includes('Пароль должен содержать')) {
            errorMessage.style.display = 'block';
            errorMessage.innerHTML = '❌ ' + text;
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 3000);
        } else if (text.includes('Неверный код')) {
            errorMessage.style.display = 'block';
            errorMessage.innerHTML = '❌ Неверный код подтверждения. Попробуйте ещё раз.';
            codeInput.classList.add('invalid');
            setTimeout(() => {
                errorMessage.style.display = 'none';
                codeInput.classList.remove('invalid');
            }, 3000);
        } else if (text.includes('Пароли не совпадают')) {
            errorMessage.style.display = 'block';
            errorMessage.innerHTML = '❌ Пароли не совпадают';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 3000);
        } else if (text.includes('Код истёк')) {
            errorMessage.style.display = 'block';
            errorMessage.innerHTML = '❌ Код истёк. Запросите новый код.';
            setTimeout(() => {
                errorMessage.style.display = 'none';
                window.location.href = '/reset';
            }, 3000);
        } else if (response.ok || text.includes('redirect')) {
            window.location.href = '/';
        } else {
            errorMessage.style.display = 'block';
            errorMessage.innerHTML = '❌ Ошибка. Попробуйте ещё раз.';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 3000);
        }
    } catch (error) {
        errorMessage.style.display = 'block';
        errorMessage.innerHTML = '❌ Ошибка соединения. Попробуйте ещё раз.';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 3000);
    }
});

codeInput.addEventListener('input', updateSubmitButton);
passwordInput.addEventListener('input', updateSubmitButton);
confirmInput.addEventListener('input', updateSubmitButton);
