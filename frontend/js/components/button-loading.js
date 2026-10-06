export function setButtonLoading(button, loading, label = 'Loading…') {
    if (loading) {
        if (button.getAttribute('aria-busy') === 'true') return;
        button.dataset.idleLabel = button.textContent;
        button.dataset.idleWidth = button.style.width;
        button.dataset.idleDisabled = String(button.disabled);
        button.style.width = `${button.getBoundingClientRect().width}px`;
        const text = document.createElement('span');
        text.className = 'button-loading-label';
        text.textContent = label;
        text.title = label;
        button.replaceChildren(text);
        button.disabled = true;
        button.setAttribute('aria-busy', 'true');
    } else if (button.getAttribute('aria-busy') === 'true') {
        button.textContent = button.dataset.idleLabel;
        button.style.width = button.dataset.idleWidth;
        button.disabled = button.dataset.idleDisabled === 'true';
        button.removeAttribute('aria-busy');
    }
}
