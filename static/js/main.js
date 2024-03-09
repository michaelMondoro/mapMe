

var geoJSON = JSON.parse(jsonStr)
var markersByHost = {}; 

var map = L.map('map').setView([30, -50], 3);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
map.setZoom(3)

L.geoJSON(geoJSON, {
    pointToLayer: function (feature, latlng) {
        function getColor() {
            console.log(directHosts)
            console.log(typeof(feature['properties']['hostname']))
            if (directHosts.includes(feature['properties']['hostname'])) {
                return "#0047ec"
             } else {
                return "#ff7800";
            }
        }
        var marker = L.circleMarker(latlng, {
            radius: Math.max(feature['properties']['requests']/2, 3),
            fillColor: getColor(),
            color: getColor(),
            weight: 1,
            opacity: 1,
            fillOpacity: 0.7
        })
        markersByHost[feature['properties']['hostname']] = marker
        marker.on('click', () => {
            for (key in feature['properties']) {
                if (key != "client_id" && key != 'referer') {
                    if (key == "org") {
                        document.getElementById(key).innerHTML = `<a target='_blank' href='http://google.com/search?q=${feature['properties'][key]}'>${feature['properties'][key]}</a>`
                    } else {
                        document.getElementById(key).innerText = feature['properties'][key]
                    }
                }  
            }
            document.getElementById('dialog').showModal()
            document.getElementById('dialog').focus()
            
        })
        marker.bindPopup(feature['properties']['hostname'] + ` (${feature['properties']['requests']})`);
        marker.on('mouseover', () => {
            marker.openPopup()
        })
        marker.on('mouseout', function (e) {
            marker.closePopup();
        })
        return marker;
    }
}).addTo(map)


// Fix wierd styling of zoom controls
document.querySelector('.leaflet-control-zoom-out').role = ""
document.querySelector('.leaflet-control-zoom-in').role = ""

function pan(element) {
    map.panTo(markersByHost[element.id].getLatLng())
    map.setZoom(5)
    markersByHost[element.id].openPopup()
}

function clear_session() {
    $.ajax({
        url: '/clear_session',
        data: "",
        type: 'POST',
        success: function(response){
            console.log('success')
            location.reload()
        },
        error: function(error){
            console.log(error);
        }
    });
    
}