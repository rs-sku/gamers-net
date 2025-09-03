const API_URL = 'http://localhost:8000/api/v1';

async function handleRequest(url, options) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        return response;
    } catch (error) {
        console.error('Network error:', error);
        throw new Error('Network error occurred. Please check your connection.');
    }
}

export async function login(credentials) {
    return handleRequest(`${API_URL}/users/login`, {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(credentials)
    });
}

export async function register(userData) {
    return handleRequest(`${API_URL}/users`, {
        method: 'POST',
        body: JSON.stringify(userData)
    });
}

export async function logout() {
    return handleRequest(`${API_URL}/users/logout`, {
        method: 'POST',
        credentials: 'include'
    });
}

export async function checkAuth() {
    return handleRequest(`${API_URL}/users`, {
        method: 'GET',
        credentials: 'include'
    });
}

export async function getAllUsers() {
    return handleRequest(`${API_URL}/users`, {
        method: 'GET',
        credentials: 'include'
    });
}
