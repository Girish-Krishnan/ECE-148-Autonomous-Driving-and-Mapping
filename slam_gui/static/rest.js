let map = document.getElementById('map');

setInterval(async function() {

    fetch('/update_map')
        .then(data => {
 map.src = '/static/map.png?time=' + new Date().getTime();
        })
}, 1000);