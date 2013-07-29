       $(function () {

        twitter_data = new Array()
        google_data = new Array()
        bing_data = new Array()

        //Extract Twitter data
        for (var i=0;i<trendsdata[1].length;i++)
        {
            twitter_data.push([trendsdata[1][i][0]*1000, trendsdata[1][i][1]]) 
        }
        
        //Extract Google data
        for (var i=0;i<trendsdata[2].length;i++)
        {
            google_data.push([trendsdata[2][i][0]*1000, trendsdata[2][i][1]]) 
        }
        
        //Extract Bing data
        for (var i=0;i<trendsdata[3].length;i++)
        {
            bing_data.push([trendsdata[3][i][0]*1000, trendsdata[3][i][1]]) 
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
                data: twitter_data
            },
            {
                name: 'Google',
                data: google_data
            },
            {
                name: 'Bing',
                data: bing_data
            }
            
            ]
        });
    });
    
