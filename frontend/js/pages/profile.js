import { logout, checkAuth, getAllUsers } from '../api/auth.js';
import { getUserGames, addUserGame, getAllGames } from '../api/games.js';
import { showNotification } from '../components/notification.js';

async function checkAuthentication() {
    try {
        const response = await checkAuth();
        if (!response.ok) {
            window.location.replace('http://localhost:8080/');
            return false;
        }
        document.body.style.display = 'block';
        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.replace('http://localhost:8080/');
        return false;
    }
}

async function fetchUsers() {
    try {
        const response = await getAllUsers();
        
        if (response.ok) {
            const users = await response.json();
            displayUsers(users);
        } else {
            showNotification('Failed to fetch users');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error fetching users');
    }
}

async function fetchUserGames() {
    try {
        const games = await getUserGames();
        displayGames(games);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error fetching games');
    }
}

function displayUsers(users) {
    const usersList = document.getElementById('users-list');
    usersList.innerHTML = '';
    
    users.forEach(user => {
        const li = document.createElement('li');
        li.className = 'data-item';
        li.textContent = `Nickname: ${user.nickname} | Email: ${user.email}`;
        usersList.appendChild(li);
    });
    
    document.getElementById('users-container').style.display = 'block';
    document.getElementById('games-container').style.display = 'none';
    document.getElementById('game-form').style.display = 'none';
}

function displayGames(games) {
    const gamesList = document.getElementById('games-list');
    gamesList.innerHTML = '';
    
    games.forEach(game => {
        const li = document.createElement('li');
        li.className = 'data-item';
        li.textContent = `Game: ${game.game_name}`;
        gamesList.appendChild(li);
    });
    
    document.getElementById('games-container').style.display = 'block';
    document.getElementById('users-container').style.display = 'none';
    document.getElementById('game-form').style.display = 'none';
}

// Обновляем функцию loadAvailableGames
async function loadAvailableGames() {
    try {
        const games = await getAllGames();
        console.log('Games data:', games);
        
        const gameSelect = document.getElementById('game-name');
        if (!gameSelect) {
            console.error('Game select element not found!');
            return;
        }
        
        gameSelect.innerHTML = '<option value="">Select a game</option>';
        
        games.forEach(game => {
            console.log('Adding game:', game);
            const option = document.createElement('option');
            option.value = game.id;
            option.textContent = game.name;
            gameSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading games:', error);
        showNotification('Error loading available games');
    }
}

function toggleGameForm() {
    const gameForm = document.getElementById('game-form');
    const usersContainer = document.getElementById('users-container');
    const gamesContainer = document.getElementById('games-container');
    
    if (gameForm.style.display === 'none' || gameForm.style.display === '') {
        gameForm.style.display = 'block';
        loadAvailableGames();
        usersContainer.style.display = 'none';
        gamesContainer.style.display = 'none';
    } else {
        gameForm.style.display = 'none';
    }
}

// Обновляем функцию handleAddGame
async function handleAddGame(event) {
    event?.preventDefault();
    
    const gameSelect = document.getElementById('game-name');
    const selectedOption = gameSelect.options[gameSelect.selectedIndex];
    const gameName = selectedOption.textContent;
    const errorElement = document.getElementById('game-error');
    
    errorElement.textContent = '';
    errorElement.style.display = 'none';
    
    if (!gameName) {
        errorElement.textContent = 'Please select a game';
        errorElement.style.display = 'block';
        return;
    }

    try {
        console.log('Sending game name:', gameName);
        const result = await addUserGame(gameName);
        console.log('Server response:', result);
        
        showNotification('Game added successfully!');
        gameSelect.value = '';
        await fetchUserGames();
        toggleGameForm();
    } catch (error) {
        console.error('Error:', error);
        errorElement.textContent = error.message;
        errorElement.style.display = 'block';
        showNotification(error.message);
    }
}

function handleAddGameError(status, data, errorElement) {
    if (status === 404) {
        errorElement.textContent = 'Game not found in our database';
    } else if (status === 409) {
        errorElement.textContent = 'You already have this game';
    } else {
        errorElement.textContent = data.detail || 'Failed to add game';
    }
    errorElement.style.display = 'block';
}

function initializeEventListeners() {
    document.getElementById('show-users-btn').addEventListener('click', fetchUsers);
    document.getElementById('show-games-btn').addEventListener('click', fetchUserGames);
    document.getElementById('add-game-btn').addEventListener('click', toggleGameForm);
    document.getElementById('submit-game-btn').addEventListener('click', (e) => handleAddGame(e));
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    const gameNameSelect = document.getElementById('game-name');
    gameNameSelect.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAddGame(e);
        }
    });
}

async function handleLogout() {
    try {
        const response = await logout();
        if (response.ok) {
            window.location.href = 'http://localhost:8080/';
        } else {
            showNotification('Failed to log out');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error during log out');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    if (await checkAuthentication()) {
        initializeEventListeners();
    }
});
