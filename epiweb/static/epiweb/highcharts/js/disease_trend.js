       $(function () {

        chartdata = new Array()

        for (var i=0;i<mydata.length;i++)
        {
            chartdata.push([mydata[i][0]*1000, mydata[i][1]]) 
        }

        $('#container2').highcharts({
            chart: {
                type: 'spline'
            },
            title: {
                text: 'Trends of Diseases on The Social Media'
            },
            subtitle: {
                text: 'Hello'
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
                data: chartdata
            }]
        });
    });
    
