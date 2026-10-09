import { setButtonLoading } from '../components/button-loading.js';
import { login, register } from '../api/auth.js';
import { showNotification } from '../components/notification.js';

let joinForm;
let showLoginBtn;

function initializeForm() {
    joinForm = document.getElementById('join-form');
    showLoginBtn = document.getElementById('show-login');

    joinForm.addEventListener('submit', joinFormSubmit);
    showLoginBtn.addEventListener('click', showLoginForm);
}

async function joinFormSubmit(e) {
    e.preventDefault();
    document.querySelectorAll('.error').forEach(el => el.textContent = '');

    const nickname = document.getElementById('nickname').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!nickname.trim()) {
        document.getElementById('nickname-error').textContent = 'Please enter your nickname';
        return;
    }
    if (!email.trim()) {
        document.getElementById('email-error').textContent = 'Please enter your email';
        return;
    }
    if (!password.trim()) {
        document.getElementById('password-error').textContent = 'Please enter your password';
        return;
    }

    const submit = joinForm.querySelector('button[type="submit"]');
    if (submit.disabled) return;
    setButtonLoading(submit, true);
    showLoginBtn.disabled = true;
    try {
        const response = await register({ nickname, email, password });

        if (response.ok) {
            showNotification('Registration successful! You can now log in');
            setTimeout(() => showLoginBtn.click(), 1000);
        } else {
            const data = await response.json();
            handleRegistrationError(data);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('An error occurred during registration');
    } finally {
        setButtonLoading(submit, false);
        showLoginBtn.disabled = false;
    }
}

async function loginFormSubmit(e) {
    e.preventDefault();
    document.querySelectorAll('.error').forEach(el => el.textContent = '');

    const loginInput = document.getElementById('nickname').value;
    const password = document.getElementById('password').value;

    if (!loginInput.trim()) {
        document.getElementById('nickname-error').textContent = 'Please enter your email or nickname';
        return;
    }
    if (!password.trim()) {
        document.getElementById('password-error').textContent = 'Please enter your password';
        return;
    }

    const submit = joinForm.querySelector('button[type="submit"]');
    if (submit.disabled) return;
    setButtonLoading(submit, true);
    showLoginBtn.disabled = true;
    try {
        const response = await login({
            email: loginInput.includes('@') ? loginInput : null,
            nickname: !loginInput.includes('@') ? loginInput : null,
            password
        });

        if (response.ok) {
            showNotification('Login successful!');
            setTimeout(() => {
                window.location.href = 'http://localhost:8080/templates/pages/profile.html';
            }, 1000);
        } else {
            const data = await response.json();
            handleLoginError(response.status, data);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('An error occurred during login');
    } finally {
        setButtonLoading(submit, false);
        showLoginBtn.disabled = false;
    }
}

function showApiErrors(data, fallbackField = 'nickname') {
    const errors = Array.isArray(data.detail) ? data.detail : [{ msg: data.detail }];
    const messages = [];
    errors.forEach(error => {
        const field = error.loc?.[error.loc.length - 1];
        const targetField = ['nickname', 'email', 'password'].includes(field) ? field : fallbackField;
        const target = document.getElementById(`${targetField}-error`);
        const message = typeof error.msg === 'string'
            ? error.msg.replace(/^Value error, /, '') : 'The request failed. Please try again.';
        target.textContent += `${target.textContent ? '; ' : ''}${message}`;
        messages.push(message);
    });
    return messages.join('; ');
}

function handleRegistrationError(data) {
    const detail = typeof data.detail === 'string' ? data.detail : '';
    const field = /password/i.test(detail) ? 'password' : /email/i.test(detail) ? 'email' : 'nickname';
    showApiErrors(data, field);
}

function handleLoginError(status, data) {
    const field = status === 400 ? 'password' : 'nickname';
    // The login email is entered in the nickname input.
    if (Array.isArray(data.detail)) {
        data.detail = data.detail.map(error => ({
            ...error,
            loc: error.loc?.map(part => part === 'email' ? 'nickname' : part)
        }));
    }
    showNotification(showApiErrors(data, field));
}

function showLoginForm() {
    console.log('Switching to login form');
    
    joinForm.reset();
    document.querySelectorAll('.error').forEach(el => el.textContent = '');

    document.querySelector('h1').textContent = 'Log in to GamersNet';
    document.querySelector('label[for="nickname"]').textContent = 'Email or nickname';
    document.getElementById('nickname').name = 'login';
    
    const emailField = document.getElementById('email');
    emailField.removeAttribute('required');
    emailField.parentElement.style.display = 'none';
    
    document.querySelector('button[type="submit"]').textContent = 'Log in';
    showLoginBtn.textContent = 'Create account';

    joinForm.removeEventListener('submit', joinFormSubmit);
    joinForm.addEventListener('submit', loginFormSubmit);
    showLoginBtn.removeEventListener('click', showLoginForm);
    showLoginBtn.addEventListener('click', showJoinForm);
}

function showJoinForm() {
    console.log('Switching to join form');
    
    joinForm.reset();
    document.querySelectorAll('.error').forEach(el => el.textContent = '');

    document.querySelector('h1').textContent = 'GamersNet';
    document.querySelector('label[for="nickname"]').textContent = 'Nickname';
    document.getElementById('nickname').name = 'nickname';
    
    const emailField = document.getElementById('email');
    emailField.setAttribute('required', '');
    emailField.parentElement.style.display = 'block';
    
    document.querySelector('button[type="submit"]').textContent = 'Create account';
    showLoginBtn.textContent = 'Log in';

    joinForm.removeEventListener('submit', loginFormSubmit);
    joinForm.addEventListener('submit', joinFormSubmit);
    showLoginBtn.removeEventListener('click', showJoinForm);
    showLoginBtn.addEventListener('click', showLoginForm);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeForm);
