import { login, register } from '../api/auth.js';
import { showNotification } from '../components/notification.js';
import { validatePassword, validateEmail, validateNickname } from '../utils/validation.js';

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

    // Validate inputs
    const nicknameValidation = validateNickname(nickname);
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);

    if (!nicknameValidation.isValid) {
        document.getElementById('nickname-error').textContent = nicknameValidation.message;
        return;
    }
    if (!emailValidation.isValid) {
        document.getElementById('email-error').textContent = emailValidation.message;
        return;
    }
    if (!passwordValidation.isValid) {
        document.getElementById('password-error').textContent = passwordValidation.message;
        return;
    }

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
    }
}

function handleRegistrationError(data) {
    if (data.detail.includes('Password')) {
        document.getElementById('password-error').textContent = data.detail;
    } else if (data.detail.includes('Email')) {
        document.getElementById('email-error').textContent = data.detail;
    } else if (data.detail.includes('Nickname')) {
        document.getElementById('nickname-error').textContent = data.detail;
    } else {
        document.getElementById('nickname-error').textContent = data.detail;
    }
}

function handleLoginError(status, data) {
    if (status === 404) {
        showNotification('User does not exist');
        document.getElementById('nickname-error').textContent = 'User does not exist';
    } else if (status === 400) {
        showNotification('Wrong password');
        document.getElementById('password-error').textContent = 'Wrong password';
    } else {
        showNotification(data.detail || 'Login failed');
        document.getElementById('password-error').textContent = data.detail || 'Login failed';
    }
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

    const newForm = joinForm.cloneNode(true);
    joinForm.parentNode.replaceChild(newForm, joinForm);
    
    newForm.addEventListener('submit', loginFormSubmit);
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

    const newForm = joinForm.cloneNode(true);
    joinForm.parentNode.replaceChild(newForm, joinForm);
    
    newForm.addEventListener('submit', joinFormSubmit);
    showLoginBtn.removeEventListener('click', showJoinForm);
    showLoginBtn.addEventListener('click', showLoginForm);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeForm);
