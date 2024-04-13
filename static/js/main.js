import * as map_utils from './map.js'

var user_status;
/**
 * Listeners
 */
window.addEventListener("scroll", () => {
    var headings = document.querySelectorAll('.fade');
    headings.forEach( (e) => {
        if (e.getBoundingClientRect().top < document.documentElement.clientHeight) {
            e.classList.add('fade-in-slow');
        }
    });
})

document.querySelector('.try-it').addEventListener("click", (e) => {
    document.querySelector('.start-dialog').close();
    document.querySelector('.start-dialog').showModal();
    map_utils.start_tracking()
})

document.querySelector('.start-button').addEventListener("click", () => {
    document.querySelector('.start-button').style.display = "none";
    document.querySelector('.page1').style.display = "none";
    document.querySelector('.page2').style.display = "none";
    document.querySelector('.prev-button').style.display = "none";
    document.querySelector('.stop-button').style.display = "block";
    document.querySelector('.loading').ariaBusy = "true";
    document.querySelector('.page3').style.display = "block";
    
})

document.querySelector('.stop-button').addEventListener("click", () => {
    document.querySelector('.start-article').ariaBusy = "false";
    document.querySelector('.stop-button').style.display = "none";
    document.querySelector('.results-button').style.display = "block";
    // document.querySelector('.loading').ariaBusy = "true";
    document.querySelector('.loading').innerText = "Generating your session report . . ."
    // map_utils.stop_tracking()
})

document.querySelector('.next-button').addEventListener("click", () => {
    poll_status(true)

    document.querySelector('.page1').style.display = "none";
    document.querySelector('.page2').style.display = "block";

    document.querySelector('.close-button').style.display = "none";
    document.querySelector('.next-button').style.display = "none";
    document.querySelector('.prev-button').style.display = "block";
    document.querySelector('.connect-button').style.display = "block";
})

document.querySelector('.prev-button').addEventListener("click", () => {
    document.querySelector('.page2').style.display = "none";
    document.querySelector('.page1').style.display = "block";

    document.querySelector('.prev-button').style.display = "none";
    document.querySelector('.start-button').style.display = "none";
    document.querySelector('.connect-button').style.display = "none";
    document.querySelector('.next-button').style.display = "block";
    document.querySelector('.close-button').style.display = "block";
})

document.querySelector('.results-button').addEventListener("click", () => {
    document.querySelector('.start-dialog').close();
})

document.querySelector('.close-button').addEventListener("click", () => {
    clearInterval(user_status);
    document.querySelector('.start-dialog').close();
})
document.querySelector('.connect-button').addEventListener("click", () => {
    poll_status()
})

document.getElementById('theme_toggle').addEventListener("click", () => {
    var html = document.getElementsByTagName('html')[0]
    if (html.dataset.theme === "dark") {
        html.dataset.theme = "light"
    } else {
        html.dataset.theme = "dark"
    }
})


/**
 * Initialize maps
 */
if (document.querySelector('#mini-map')) {
    const mini_map = map_utils.init_map('mini_map',[50.5, 30.5])
    L.marker([50.5, 30.5]).addTo(mini_map);
}

if  (document.querySelector('#map')) {
    console.log("creating main map")
    const map = map_utils.init_map('map',[50.5, 30.5])
    L.marker([50.5, 30.5]).addTo(map);
}

/**
 * Utilities
 */

function poll_status(auto) {
    $.ajax({
        url: '/poll',
        data: "",
        type: 'POST',
        success: function(response){
            if (response === "true"){
                console.log(response);
                clearInterval(user_status);
                var status = document.querySelector('.status');
                status.style.backgroundColor = "#28a745";
                status.innerText = "connected";

                document.querySelector('.connect-button').style.display = "none";
                document.querySelector('.start-button').style.display = "block";
            } else {
                if (auto !== true){
                    alert("There's something wrong - double check your browser settings");
                }
                
            }     
        },
        error: function(error){
            console.log("ERROR: " + error.data);
        }
    });
    // get_data()
    // clearInterval(refresh)
}