export function showNotification(message) {
    const notification = document.getElementById('notification');
    if (!notification) return;

    // Удаляем предыдущую анимацию, если она есть
    notification.classList.remove('show');
    
    // Триггерим reflow для перезапуска анимации
    void notification.offsetWidth;
    
    notification.textContent = message;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}
