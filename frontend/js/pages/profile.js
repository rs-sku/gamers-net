import { logout, checkAuth } from '../api/auth.js';
import { getUserGames, addUserGame, getAllGames } from '../api/games.js';
import { showNotification } from '../components/notification.js';
import { initializeFriends } from './friends.js';

let currentUserId;

function showSection(sectionId) {
    const sections = ['friends-container', 'users-container', 'games-container', 'game-form'];
    sections.forEach(id => {
        document.getElementById(id).style.display = id === sectionId ? 'block' : 'none';
    });
    document.querySelectorAll('.profile-navigation button').forEach((button, index) => {
        button.setAttribute('aria-pressed', String(sections[index] === sectionId));
    });
}

async function checkAuthentication() {
    try {
        const response = await checkAuth();
        if (!response.ok) {
            window.location.replace('http://localhost:8080/');
            return false;
        }
        const user = await response.json();
        document.getElementById('profile-nickname').textContent = user.nickname;
        document.body.style.display = 'block';
        return user;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.replace('http://localhost:8080/');
        return false;
    }
}

async function fetchUserGames() {
    showSection('games-container');
    try {
        const games = await getUserGames(currentUserId);
        displayGames(games);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error fetching games');
    }
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
    
    if (gameForm.style.display === 'none' || gameForm.style.display === '') {
        showSection('game-form');
        loadAvailableGames();
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
    
    if (!gameSelect.value) {
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
    const currentUser = await checkAuthentication();
    if (currentUser) {
        currentUserId = currentUser.id;
        initializeEventListeners();
        initializeFriends(currentUser, showSection);
    }
});
