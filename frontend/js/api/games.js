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
        
        const data = await response.json();
        
        if (!response.ok) {
            if (data.detail === 'Pair user_id and game_id already exists') {
                throw new Error('You already have this game');
            }
            throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail));
        }
        
        return data;
    } catch (error) {
        console.error('Request error:', error);
        throw new Error(error.message || 'Network error occurred');
    }
}

export async function getUserGames() {
    return handleRequest(`${API_URL}/games`, {
        method: 'GET',
        credentials: 'include'
    });
}

export async function addUserGame(gameName) {
    return handleRequest(`${API_URL}/games`, {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ name: gameName })
    });
}

export async function getAllGames() {
    return handleRequest(`${API_URL}/games/all`, {
        method: 'GET',
        credentials: 'include'
    });
}
