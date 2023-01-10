function nick(nickname, targetSelector) {
    let target = document.querySelector(targetSelector);
    if (!target) return;

    target.setRangeText(
        `**${nickname}**, `,
        target.selectionStart,
        target.selectionEnd,
        "end"
    );
    target.focus();
}

function toggle(event, targetSelector, toggleClass) {
    let element = event.target;
    element.parentElement.querySelector(targetSelector).classList.toggle(toggleClass);
}
