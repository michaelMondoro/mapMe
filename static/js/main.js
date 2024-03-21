window.addEventListener("scroll", () => {
    var headings = document.querySelectorAll('.fade');
    headings.forEach( (e) => {
        if (e.getBoundingClientRect().top < document.documentElement.clientHeight) {
            e.classList.add('fade-in-slow');
        }
    });
})

function toggle_theme() {
    html = document.getElementsByTagName('html')[0]
    if (html.dataset.theme === "dark") {
        html.dataset.theme = "light"
    } else {
        html.dataset.theme = "dark"
    }
}
