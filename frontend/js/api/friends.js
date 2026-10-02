const API_URL = 'http://localhost:8000/api/v1/users';

async function request(path, options = {}) {
    let response;
    try {
        response = await fetch(`${API_URL}${path}`, {
            ...options,
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
    } catch {
        throw new Error('Cannot reach the server. Check your connection and try again.');
    }

    const data = await response.json().catch(() => null);
    if (!response.ok) {
        const detail = data?.detail;
        const message = typeof detail === 'string' ? detail
            : Array.isArray(detail) ? detail.map(item => item.msg).join('; ')
            : 'The request failed. Please try again.';
        const error = new Error(message);
        error.status = response.status;
        throw error;
    }
    if (data === null) throw new Error('The server returned an invalid response. Please try again.');
    return data;
}

export async function getFriendshipOverview(nickname) {
    const [users, friends, incoming, outgoing] = await Promise.all([
        request(''),
        request(`/friends?${new URLSearchParams({ name: nickname })}`),
        request('/incoming-friend-requests?status=pending'),
        request('/outgoing-friend-requests?status=pending')
    ]);
    return { users, friends: friends.friends, incoming, outgoing };
}

export function sendFriendRequest(nickname) {
    return request(`/friend-request?${new URLSearchParams({ friend_name: nickname })}`, {
        method: 'POST'
    });
}

export function processFriendRequest(senderId, status) {
    return request(`/pending-friend-requests?${new URLSearchParams({ requesting_user_id: senderId })}`, {
        method: 'PATCH',
        body: JSON.stringify({ new_status: status })
    });
}
