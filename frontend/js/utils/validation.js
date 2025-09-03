export function validatePassword(password) {
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        digit: /[0-9]/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    return {
        isValid: Object.values(requirements).every(Boolean),
        message: !Object.values(requirements).every(Boolean) ?
            'Password must be at least 8 characters long, contain at least one uppercase letter, ' +
            'one lowercase letter, one digit and one special character' : ''
    };
}

export function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return {
        isValid: emailRegex.test(email),
        message: !emailRegex.test(email) ? 'Please enter a valid email address' : ''
    };
}

export function validateNickname(nickname) {
    return {
        isValid: nickname.length >= 3 && nickname.length <= 20,
        message: nickname.length < 3 || nickname.length > 20 ? 
            'Nickname must be between 3 and 20 characters' : ''
    };
}
