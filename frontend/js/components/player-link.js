export function playerLink(user, currentUserId) {
    const link = document.createElement('a');
    link.className = 'player-link';
    link.textContent = user.nickname;
    link.href = user.id === currentUserId
        ? 'templates/pages/profile.html'
        : `templates/pages/player.html?${new URLSearchParams({ user_id: user.id })}`;
    return link;
}
