import { getFriendshipOverview, sendFriendRequest, processFriendRequest } from '../api/friends.js';
import { showNotification } from '../components/notification.js';
import { playerLink } from '../components/player-link.js';

export function initializeFriends(currentUser, showSection) {
    let state = { users: [], friends: [], incoming: [], outgoing: [] };
    let loaded = false;
    let loading = false;
    let saving = false;
    let refreshPromise = null;
    const element = id => document.getElementById(id);

    function showError(message = '') {
        element('friendship-error').textContent = message;
        element('friendship-error').style.display = message ? 'block' : 'none';
    }

    function handleError(error) {
        if (error.status === 401) {
            window.location.replace('templates/pages/login.html');
            return;
        }
        showError(error.message);
    }

    function row(nickname, email) {
        const item = document.createElement('li');
        item.className = 'data-item friend-item';
        const info = document.createElement('div');
        info.className = 'player-info';
        const user = state.users.find(user => user.nickname === nickname);
        const name = user ? playerLink(user, currentUser.id) : document.createElement('strong');
        name.textContent = nickname;
        info.appendChild(name);
        if (email) {
            const address = document.createElement('span');
            address.className = 'player-email';
            address.textContent = email;
            info.appendChild(address);
        }
        item.appendChild(info);
        return item;
    }

    function badge(item, text) {
        const label = document.createElement('span');
        label.className = 'friend-status';
        label.textContent = text;
        item.appendChild(label);
    }

    function actions(item, user, incoming = false) {
        const controls = document.createElement('div');
        controls.className = 'friend-actions';
        const choices = incoming ? [['accepted', 'Accept'], ['rejected', 'Decline']] : [['send', 'Add friend']];
        choices.forEach(([action, label]) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `btn ${action === 'rejected' ? 'btn-secondary' : 'btn-primary'}`;
            button.textContent = label;
            button.dataset.friendAction = action;
            button.dataset.userId = user.id;
            button.setAttribute('aria-label', `${label}: ${user.nickname}`);
            button.disabled = loading || saving || !loaded;
            controls.appendChild(button);
        });
        item.appendChild(controls);
    }

    function renderList(id, items, emptyMessage, makeRow) {
        const list = element(id);
        list.replaceChildren();
        if (!items.length) {
            const message = document.createElement('li');
            message.className = 'list-message';
            message.textContent = loaded ? emptyMessage : 'Load players and requests with Refresh.';
            list.appendChild(message);
        } else {
            items.forEach(item => list.appendChild(makeRow(item)));
        }
    }

    function getUser(id) {
        return state.users.find(user => user.id === id) || { id, nickname: `Player #${id}` };
    }

    function renderUsers() {
        const search = element('user-search').value.trim().toLowerCase();
        const users = state.users.filter(user => user.nickname.toLowerCase().includes(search));
        renderList('users-list', users, search ? 'No players match your search.' : 'No players yet.', user => {
            const item = row(user.nickname, user.email);
            item.dataset.userId = user.id;
            if (user.id === currentUser.id) badge(item, 'You');
            else if (state.friends.includes(user.nickname)) badge(item, 'Friends');
            else if (state.incoming.some(request => request.requesting_user_id === user.id)) actions(item, user, true);
            else if (state.outgoing.some(request => request.requested_user_id === user.id)) badge(item, 'Request sent');
            else actions(item, user);
            return item;
        });
    }

    function render() {
        element('friends-count').textContent = `(${state.friends.length})`;
        element('incoming-count').textContent = `(${state.incoming.length})`;
        element('outgoing-count').textContent = `(${state.outgoing.length})`;
        element('incoming-nav-count').textContent = state.incoming.length ? ` · ${state.incoming.length} incoming` : '';
        element('friendship-status').textContent = saving ? 'Saving request…' : loading ? 'Refreshing friends and requests…' : '';
        element('refresh-friends-btn').disabled = loading || saving;
        element('refresh-friends-btn').textContent = loading ? 'Refreshing…' : 'Refresh';
        element('send-friend-request-btn').disabled = loading || saving || !loaded;
        element('send-friend-request-btn').textContent = saving ? 'Saving…' : 'Send request';
        element('friends-container').setAttribute('aria-busy', String(loading || saving));
        renderList('friends-list', state.friends, 'No friends yet. Find a player or send a request by nickname.', nickname => row(nickname));
        renderList('incoming-requests-list', state.incoming, 'No incoming requests.', request => {
            const user = getUser(request.requesting_user_id);
            const item = row(user.nickname);
            item.dataset.userId = user.id;
            actions(item, user, true);
            return item;
        });
        renderList('outgoing-requests-list', state.outgoing, 'No outgoing requests.', request => {
            const user = getUser(request.requested_user_id);
            const item = row(user.nickname);
            item.dataset.userId = user.id;
            badge(item, 'Pending');
            return item;
        });
        renderUsers();
    }

    function refresh() {
        if (refreshPromise) return refreshPromise;
        loading = true;
        render();
        refreshPromise = (async () => {
            try {
                state = await getFriendshipOverview(currentUser.nickname);
                loaded = true;
                showError();
            } catch (error) {
                handleError(error);
            } finally {
                loading = false;
                refreshPromise = null;
                render();
            }
        })();
        return refreshPromise;
    }

    async function mutate(action, user) {
        if (loading || saving || !loaded) return false;
        saving = true;
        showError();
        render();
        let success = false;
        try {
            if (action === 'send') {
                const request = await sendFriendRequest(user.nickname);
                state.outgoing.push(request);
                showNotification('Friend request sent!');
            } else {
                await processFriendRequest(user.id, action);
                state.incoming = state.incoming.filter(request => request.requesting_user_id !== user.id);
                if (action === 'accepted' && !state.friends.includes(user.nickname)) state.friends.push(user.nickname);
                showNotification(action === 'accepted' ? 'Friend request accepted!' : 'Friend request declined.');
            }
            success = true;
        } catch (error) {
            handleError(error);
            // Another tab may already have changed this request.
            if ([400, 404, 409].includes(error.status)) {
                await refresh();
                showError(error.message);
            }
        } finally {
            if (success) await refresh();
            saving = false;
            render();
        }
        return success;
    }

    element('friend-request-form').addEventListener('submit', async event => {
        event.preventDefault();
        const nickname = element('friend-nickname').value.trim();
        if (!nickname) return showError('Enter a nickname.');
        if (nickname === currentUser.nickname) return showError('You cannot send a friend request to yourself.');
        if (state.friends.includes(nickname)) return showError('You are already friends.');
        const user = state.users.find(user => user.nickname === nickname);
        if (user && state.outgoing.some(request => request.requested_user_id === user.id)) return showError('A request to this player is already pending.');
        if (user && state.incoming.some(request => request.requesting_user_id === user.id)) return showError('This player has already sent you a request. Accept or decline it below.');
        if (await mutate('send', { nickname })) element('friend-nickname').value = '';
    });

    document.querySelector('.content-container').addEventListener('click', event => {
        const button = event.target.closest('button[data-friend-action]');
        if (button && !button.disabled) mutate(button.dataset.friendAction, getUser(Number(button.dataset.userId)));
    });
    element('user-search').addEventListener('input', renderUsers);
    element('refresh-friends-btn').addEventListener('click', refresh);
    [['show-friends-btn', 'friends-container'], ['show-users-btn', 'users-container']].forEach(([button, section]) => {
        element(button).addEventListener('click', () => {
            showSection(section);
            if (!saving) refresh();
        });
    });

    function refreshVisible() {
        const visible = ['friends-container', 'users-container'].some(id => element(id).style.display === 'block');
        if (document.visibilityState === 'visible' && visible && !saving) refresh();
    }
    window.addEventListener('focus', refreshVisible);
    document.addEventListener('visibilitychange', refreshVisible);
    const timer = window.setInterval(refreshVisible, 30000);
    window.addEventListener('pagehide', () => window.clearInterval(timer), { once: true });
    showSection('friends-container');
    refresh();
}
