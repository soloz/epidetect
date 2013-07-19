       $(function () {
alert(mydata2)
        $('#container2').highcharts({
            chart: {
                type: 'spline'
            },
            title: {
                text: 'Trends of Diseases on The Social Media'
            },
            subtitle: {
                text: date
            },
            xAxis: {
                type: 'datetime',
		dateTimeLabelFormats: {
			day: '%e. %b'
        	}
		    },
            yAxis: {
                title: {
                    text: 'Social Media Counts'
                },
                min: 0
            },
            tooltip: {
                formatter: function() {
                        return '<b>'+ this.series.name +'</b><br/>'+
                        Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y +' reports';
                }
            },
            
            series: [{
                name: 'Twitter',
                data: [
                    [Date.UTC(2013,  6,  16), length(date)],
                    [Date.UTC(2013, 6, 17), 15],
                    [Date.UTC(2013, 6, 18), 5],
                    [Date.UTC(2013, 6, 19), 16]
                ]
            }]
        });
    });
    
