
$(function () {



geolocationdata = new Array()

colors = new Array()
colors.push('#CC0033')
colors.push('#0099ff')
colors.push('#ffff00')

var randomnumber=Math.floor(Math.random()*4)

//Unpacking Coordinates data
for (var i=0;i<mapsdata[1].length;i++)
{

randomnumber=Math.floor(Math.random()*3)

var jsonobject =
   {
    type: 'Feature',
    geometry: {
        type: 'Point',
        coordinates: [mapsdata[1][i][0][0], mapsdata[1][i][0][1]]
    },
    properties: {
        title: mapsdata[1][i][1],
        // http://mapbox.com/developers/simplestyle/
        'marker-color': colors[randomnumber]
    }
    };
    geolocationdata.push(jsonobject);
}
   
var map = L.mapbox.map('map', 'examples.map-20v6611k')
    .setView([jsonobject.geometry.coordinates[1], jsonobject.geometry.coordinates[0]], 2);


map.markerLayer.setGeoJSON(geolocationdata);

function resetColors() {
    for (var i = 0; i < geolocationdata.length; i++) {
        geolocationdata[i].properties['marker-color'] = geolocationdata[i].properties['old-color'] ||
            geolocationdata[i].properties['marker-color'];
    }
    map.markerLayer.setGeoJSON(geolocationdata);
}

map.markerLayer.on('click',function(e) {
    resetColors();
    e.layer.feature.properties['old-color'] = e.layer.feature.properties['marker-color'];
    e.layer.feature.properties['marker-color'] = '#000';
    map.markerLayer.setGeoJSON(geolocationdata);
});

map.on('click', resetColors);

});
