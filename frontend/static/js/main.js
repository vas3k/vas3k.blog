function initializeImageZoom() {
    Lightense(document.querySelectorAll(".post img"), {
        time: 50,
        padding: 40,
        offset: 40,
        keyboard: true,
        cubicBezier: "cubic-bezier(.2, 0, .1, 1)",
        background: "rgba(0, 0, 0, .1)",
        zIndex: 6,
    });
}

function initializeHighlightJS() {
    hljs.initHighlightingOnLoad();
}

function initializePoorManEmoji() {
    let isApple = /iPad|iPhone|iPod|OS X/.test(navigator.userAgent) && !window.MSStream;
    if (!isApple) {
        document.body = twemoji.parse(document.body, { base: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/" });
    }
}

function initializeExternalLinks() {
    let anchors = document.querySelectorAll("a");
    anchors.forEach(anchor => {
        if (anchor.hostname !== window.location.hostname) {
            anchor.setAttribute("target", "_blank");
            anchor.setAttribute("rel", "noopener");
        }
    });
}

function initializeAutoResizableTextareas() {
    function onTextareaInput() {
        this.style.height = 0;
        this.style.height = (this.scrollHeight) + "px";
    }

    const textareas = document.querySelectorAll("textarea");
    textareas.forEach(textarea => {
        textarea.setAttribute("style", "height:" + (textarea.scrollHeight) + "px;overflow-y:hidden;");
        textarea.addEventListener("input", onTextareaInput, false);
    });
}

function initializeSpoilers() {
    let spoilers = document.querySelectorAll(".block-spoiler");
    spoilers.forEach(spoiler => spoiler.addEventListener("click", event => {
        spoiler.querySelector(".block-spoiler-button").classList.toggle("block-spoiler-button-hidden");
        spoiler.querySelector(".block-spoiler-text").classList.toggle("block-spoiler-text-visible");
    }));
}

function toggleTheme(event) {
    let theme = event.target.checked ? "dark" : "light";
    document.documentElement.setAttribute("theme", theme);
    localStorage.setItem("theme", theme);
}

function toggleHeaderSearch(event, targetId) {
    let searchForm = document.querySelector(targetId);
    searchForm.classList.toggle("header-search-hidden");
    searchForm.querySelector(".header-search-form-input").focus();

    event.target.classList.toggle("header-menu-full");
}

window.addEventListener("DOMContentLoaded", function() {
    console.log("Initializing js...")
    initializeImageZoom();
    initializePoorManEmoji();
    initializeSpoilers();
    initializeExternalLinks();
    initializeAutoResizableTextareas();
    initializeHighlightJS();
    console.log("Done")
});
