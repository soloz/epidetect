$(function () { 

categories = new Array()
presentdata = new Array()
avgdata = new Array()

for (var i=0;i<countrydata[1].length;i++)
{
    categories.push (countrydata[1][i][0]+': '+ countrydata[1][i][2]);
    presentdata.push(countrydata[1][i][1])
    avgdata.push(1)

}


         $('#container').highcharts({
            chart: {
                type: 'bar'
            },
            title: {
                text: 'Alerts Statistics'
            },
            subtitle: {
                text: countrydata[1][1][2]
            },            
            xAxis: {
                categories: categories
            },
            yAxis: {
                title: {
                    text: 'Alert Counts'
                }
            },
            series: [{
                name: 'Present',
                data: presentdata
            }, {
                name: '2-Week Average',
                data: avgdata
            }]
        });
      });
