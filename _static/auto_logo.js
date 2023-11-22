const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)');

const faviconEl = document.createElement("link")
faviconEl.rel = "icon"
if (isDarkMode.matches) {
    faviconEl.href = "_static/logo_white.png"
} else {
    faviconEl.href = "_static/logo_black.png"
}
document.getElementsByTagName("head")[0].append(faviconEl)