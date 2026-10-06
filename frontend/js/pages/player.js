import { setButtonLoading } from '../components/button-loading.js';
import { checkAuth, getAllUsers } from '../api/auth.js';
import { getUserGames } from '../api/games.js';
import { getFriends } from '../api/friends.js';
import { playerLink } from '../components/player-link.js';

const element = id => document.getElementById(id);
const userId = Number(new URLSearchParams(window.location.search).get('user_id'));
let currentUser;
let users = [];
let player;

function redirectToLogin() {
    window.location.replace('templates/pages/login.html');
}

function message(list, text) {
    const item = document.createElement('li');
    item.className = 'list-message';
    item.textContent = text;
    list.replaceChildren(item);
}

async function loadList(kind, fetchItems, renderItem, emptyMessage) {
    const list = element(`player-${kind}`);
    const retry = element(`retry-${kind}-btn`);
    const count = element(`player-${kind}-count`);
    if (retry.disabled) return;
    setButtonLoading(retry, true);
    list.setAttribute('aria-busy', 'true');
    try {
        const items = await fetchItems();
        count.textContent = `(${items.length})`;
        retry.dataset.idleLabel = 'Refresh';
        if (items.length) list.replaceChildren(...items.map(renderItem));
        else message(list, emptyMessage);
    } catch (error) {
        if (error.status === 401) return redirectToLogin();
        message(list, `Could not load ${kind}. ${error.message}`);
        retry.dataset.idleLabel = 'Try again';
    } finally {
        list.setAttribute('aria-busy', 'false');
        setButtonLoading(retry, false);
    }
}

function loadGames() {
    return loadList('games', () => getUserGames(player.id), game => {
        const item = document.createElement('li');
        item.className = 'data-item';
        item.textContent = game.game_name;
        return item;
    }, 'No games added yet.');
}

function loadFriends() {
    return loadList('friends', async () => (await getFriends(player.nickname)).friends, nickname => {
        const item = document.createElement('li');
        item.className = 'data-item friend-item';
        const friend = users.find(user => user.nickname === nickname);
        if (friend) item.appendChild(playerLink(friend, currentUser.id));
        else item.textContent = nickname;
        return item;
    }, 'No friends yet.');
}

async function loadProfile() {
    const retry = element('retry-profile-btn');
    if (retry.disabled) return;
    setButtonLoading(retry, true);
    element('retry-games-btn').disabled = true;
    element('retry-friends-btn').disabled = true;
    element('player-error').hidden = true;
    element('player-content').setAttribute('aria-busy', 'true');
    element('player-status').textContent = '';
    try {
        const authResponse = await checkAuth();
        if (authResponse.status === 401) return redirectToLogin();
        if (!authResponse.ok) throw new Error('Could not verify your session. Try again.');
        currentUser = await authResponse.json();
        if (!Number.isSafeInteger(userId) || userId <= 0) {
            element('player-status').textContent = 'Invalid player link. Select a player from your profile.';
            return;
        }
        if (userId === currentUser.id) {
            window.location.replace('templates/pages/profile.html');
            return;
        }
        const response = await getAllUsers();
        if (response.status === 401) return redirectToLogin();
        if (!response.ok) throw new Error('Could not load the player profile. Try again.');
        users = await response.json();
        player = users.find(user => user.id === userId);
        if (!player) {
            element('player-status').textContent = 'Player not found. They may have deleted their account.';
            return;
        }
        element('player-name').textContent = player.nickname;
        document.title = `${player.nickname} - GamersNet`;
        element('player-status').textContent = '';
        element('player-content').hidden = false;
        retry.dataset.idleLabel = 'Refresh';
        element('retry-games-btn').disabled = false;
        element('retry-friends-btn').disabled = false;
        await Promise.all([loadGames(), loadFriends()]);
    } catch (error) {
        element('player-status').textContent = '';
        element('player-error').textContent = error.message;
        element('player-error').hidden = false;
        retry.dataset.idleLabel = 'Try again';
    } finally {
        element('player-content').setAttribute('aria-busy', 'false');
        setButtonLoading(retry, false);
    }
}

element('retry-profile-btn').addEventListener('click', loadProfile);
element('retry-games-btn').addEventListener('click', loadGames);
element('retry-friends-btn').addEventListener('click', loadFriends);
loadProfile();
