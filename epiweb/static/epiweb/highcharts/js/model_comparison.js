$(function () { 

categories = new Array()
svm = new Array()
nb = new Array()
ensemble = new Array()

categories.push('F-Score')
categories.push('Recall')
categories.push('Precision')
categories.push('Accuracy')

svm.push(0.784779)
nb.push(0.776496)
ensemble.push(0.859599)

svm.push(0.791028)
nb.push(0.773356)
ensemble.push(0.863833)

svm.push(0.778628)
nb.push(0.779662)
ensemble.push(0.855406)

svm.push(0.902905)
nb.push(0.902538)
ensemble.push(0.876618)


         $('#models').highcharts({
            chart: {
                type: 'bar'
            },
            title: {
                text: 'Model Performance Comparison'
            },
            subtitle: {
                text: "Comparing 3 Models"
            },            
            xAxis: {
                categories: categories
            },
            yAxis: {
                title: {
                    text: 'Alert Counts'
                }
            },
            plotOptions: {
                bar: {
                    dataLabels: {
                        enabled: true
                    }
                }
            },

            series: [{
                name: 'SVM',
                data: svm
            }, 
            {
                name: 'Naive Bayes',
                data: nb
            },
            {
                name: 'Ensemble',
                data: ensemble
            }]
        });
      });
