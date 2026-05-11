const emailInput = document.getElementById('email');
const usernameInput = document.getElementById('username');
const loginInput = document.getElementById('login');
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

    if (isValid && email.length > matchedDomain.length) {
        emailReq.className = 'requirement valid';
        emailReq.innerHTML = '✓ Почта подтверждена (' + matchedDomain + ')';
        return true;
    } else {
        emailReq.className = 'requirement invalid';
        emailReq.innerHTML = '✗ Только @gmail.com, @yandex.ru, @mail.ru';
        return false;
    }
}

function checkUsername(username) {
    const usernameReq = document.getElementById('usernameReq');
    const isValid = username.length >= 3 && username.length <= 20;

    if (username.length === 0) {
        usernameReq.className = 'requirement invalid';
        usernameReq.innerHTML = '✗ Имя пользователя (3-20 символов)';
    } else if (isValid) {
        usernameReq.className = 'requirement valid';
        usernameReq.innerHTML = '✓ Имя пользователя (3-20 символов)';
    } else {
        usernameReq.className = 'requirement invalid';
        usernameReq.innerHTML = '✗ Имя пользователя должно быть от 3 до 20 символов';
    }

    return isValid;
}

function checkLogin(login) {
    const loginReq = document.getElementById('loginReq');
    const isValid = login.length >= 3 && login.length <= 20;

    if (login.length === 0) {
        loginReq.className = 'requirement invalid';
        loginReq.innerHTML = '✗ Логин (3-20 символов)';
    } else if (isValid) {
        loginReq.className = 'requirement valid';
        loginReq.innerHTML = '✓ Логин (3-20 символов)';
    } else {
        loginReq.className = 'requirement invalid';
        loginReq.innerHTML = '✗ Логин должен быть от 3 до 20 символов';
    }

    return isValid;
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

    lengthReq.className = lengthValid ? 'requirement valid' : 'requirement invalid';
    lengthReq.innerHTML = lengthValid ? '✓ 8-16 символов' : '✗ 8-16 символов';

    lowercaseReq.className = lowercaseValid ? 'requirement valid' : 'requirement invalid';
    lowercaseReq.innerHTML = lowercaseValid ? '✓ Строчные буквы (a-z)' : '✗ Строчные буквы (a-z)';

    uppercaseReq.className = uppercaseValid ? 'requirement valid' : 'requirement invalid';
    uppercaseReq.innerHTML = uppercaseValid ? '✓ Заглавные буквы (A-Z)' : '✗ Заглавные буквы (A-Z)';

    digitReq.className = digitValid ? 'requirement valid' : 'requirement invalid';
    digitReq.innerHTML = digitValid ? '✓ Цифры (0-9)' : '✗ Цифры (0-9)';

    specialReq.className = specialValid ? 'requirement valid' : 'requirement invalid';
    specialReq.innerHTML = specialValid ? '✓ Спецсимволы (!@#$%^&*)' : '✗ Спецсимволы (!@#$%^&*)';

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
    const emailValid = checkEmail(emailInput.value);
    const usernameValid = checkUsername(usernameInput ? usernameInput.value : '');
    const loginValid = checkLogin(loginInput ? loginInput.value : '');
    const passwordValid = checkPasswordStrength(passwordInput.value);
    const passwordsMatch = checkPasswordsMatch();
    const passwordNotEmpty = passwordInput.value.length > 0;

    if (emailValid && usernameValid && loginValid && passwordValid && passwordsMatch && passwordNotEmpty) {
        submitBtn.disabled = false;
    } else {
        submitBtn.disabled = true;
    }
}

emailInput.addEventListener('input', function() { updateSubmitButton(); });
usernameInput.addEventListener('input', function() { updateSubmitButton(); });
loginInput.addEventListener('input', function() { updateSubmitButton(); });
passwordInput.addEventListener('input', function() { updateSubmitButton(); });
confirmInput.addEventListener('input', function() { updateSubmitButton(); });

checkEmail(emailInput.value);
checkUsername(usernameInput.value);
checkLogin(loginInput.value);
