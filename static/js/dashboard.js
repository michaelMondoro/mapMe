import * as map_utils from './map.js'

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
    
}