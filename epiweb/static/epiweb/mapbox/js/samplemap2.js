
$(function () {

geolocationdata = new Array()
colors = new Array()
colors.push('#CC0033')
colors.push('#0099ff')

//Unpacking Coordinates data
for (var i=1;i<mapsdata.length;i++)
{

var jsonobject =
   {
    type: 'Feature',
    geometry: {
        type: 'Point',
        coordinates: [mapsdata[i][0][0], mapsdata[i][0][1]]
    },
    properties: {
        title: mapsdata[i][1],
        // http://mapbox.com/developers/simplestyle/
        'marker-color': colors[i-1]
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
