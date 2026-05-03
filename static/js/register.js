const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const confirmInput = document.getElementById('confirm_password');
const submitBtn = document.getElementById('submitBtn');
const confirmError = document.getElementById('confirmError');

function checkEmail(email) {
    const allowedDomains = ['@gmail.com', '@yandex.ru', '@mail.ru'];
    let isValid = false;
    let matchedDomain = '';

    for (const domain of allowedDomains) {
        if (email.toLowerCase().endsWith(domain)) {
            isValid = true;
            matchedDomain = domain;
            break;
        }
    }

    const emailReq = document.getElementById('emailReq');
    const emailHint = document.getElementById('emailHint');

    if (isValid && email.length > matchedDomain.length) {
        if (emailReq) {
            emailReq.className = 'requirement valid';
            emailReq.innerHTML = '✓ Почта подтверждена (' + matchedDomain + ')';
        }
        emailInput.classList.add('valid-email');
        emailInput.classList.remove('invalid-email');
        if (emailHint) {
            emailHint.innerHTML = '✓ Отлично!';
            emailHint.style.color = '#198754';
        }
        return true;
    } else {
        if (emailReq) {
            emailReq.className = 'requirement invalid';
            emailReq.innerHTML = '✗ Только @gmail.com, @yandex.ru, @mail.ru';
        }
        emailInput.classList.add('invalid-email');
        emailInput.classList.remove('valid-email');
        if (emailHint) {
            emailHint.innerHTML = '✗ Допустимые почты: example@gmail.com, example@yandex.ru, example@mail.ru';
            emailHint.style.color = '#dc3545';
        }
        return false;
    }
}

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
    const password = passwordInput.value;
    const confirm = confirmInput.value;

    if (confirm.length > 0 && password !== confirm) {
        if (confirmError) confirmError.style.display = 'block';
        return false;
    } else {
        if (confirmError) confirmError.style.display = 'none';
        return true;
    }
}

function updateSubmitButton() {
    const emailValid = checkEmail(emailInput.value);
    const passwordValid = checkPasswordStrength(passwordInput.value);
    const passwordsMatch = checkPasswordsMatch();
    const passwordNotEmpty = passwordInput.value.length > 0;

    if (submitBtn) {
        if (emailValid && passwordValid && passwordsMatch && passwordNotEmpty) {
            submitBtn.disabled = false;
        } else {
            submitBtn.disabled = true;
        }
    }
}

if (emailInput) emailInput.addEventListener('input', function() { updateSubmitButton(); });
if (passwordInput) passwordInput.addEventListener('input', function() { updateSubmitButton(); });
if (confirmInput) confirmInput.addEventListener('input', function() { updateSubmitButton(); });

if (emailInput) checkEmail(emailInput.value);
