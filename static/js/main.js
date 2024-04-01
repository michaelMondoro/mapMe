import * as map_utils from './map.js'

window.addEventListener("scroll", () => {
    var headings = document.querySelectorAll('.fade');
    headings.forEach( (e) => {
        if (e.getBoundingClientRect().top < document.documentElement.clientHeight) {
            e.classList.add('fade-in-slow');
        }
    });
})

document.getElementById('theme_toggle').addEventListener("click", () => {
    var html = document.getElementsByTagName('html')[0]
    if (html.dataset.theme === "dark") {
        html.dataset.theme = "light"
    } else {
        html.dataset.theme = "dark"
    }
})

if (document.querySelector('#mini-map')) {
    const mini_map = map_utils.init_map('mini_map',[50.5, 30.5])
    L.marker([50.5, 30.5]).addTo(mini_map);
}

if  (document.querySelector('#map')) {
    console.log("creating main map")
    const map = map_utils.init_map('map',[50.5, 30.5])
    L.marker([50.5, 30.5]).addTo(map);
}
