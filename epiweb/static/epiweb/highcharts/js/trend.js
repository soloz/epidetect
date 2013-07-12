      $(function () { 
         $('#container').highcharts({
            chart: {
                type: 'bar'
            },
            title: {
                text: 'Alerts Statistics'
            },
            subtitle: {
                text: 'Europe'
            },            
            xAxis: {
                categories: ['UK: Disease 1', 'Germany: Disease 2', 'Poland: Disease 3']
            },
            yAxis: {
                title: {
                    text: 'Social Media Report Counts'
                }
            },
            series: [{
                name: 'Present',
                data: [1, 0, 4]
            }, {
                name: '2-Week Average',
                data: [5, 7, 3]
            }]
        });
      });