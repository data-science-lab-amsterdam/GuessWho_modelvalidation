var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;


var show_graphs = function()
{
    // fetch data
    var raw_data = document.getElementById("data-container").getAttribute('accessKey');
    data = JSON.parse(decodeURIComponent(raw_data));

    // for each feature...
    for (var key in data['features']) {
        var item = data['features'][key];
        var value = item['value'];
        var score = item['score'];
        console.log([key, value, score]);

        var color_class = 'is-success';
        if (score < 55) {
            color_class = 'is-danger'
        } else if (score < 80) {
            color_class = 'is-warning'
        }
        document.getElementById('graph-container-'+key).innerHTML = '<progress class="progress show-value is-medium '+color_class+'" value="'+score+'" max="100">'+score+'%</progress>'
        //show_graph('graph-container-hair_colour', ['licht', 'donker', 'geen'], [0.1, 0.84, 0.06]);
    }

}


var show_graph = function(element_id, labels, scores)
{
    Highcharts.chart(element_id, {
    chart: {
        type: 'bar'
    },
    title:{
        text:''
    },
    xAxis: {
        categories: labels,
        title: {
            text: null
        }
    },
    yAxis: {
        min: 0,
        title: {
            text: 'probability',
            align: 'high'
        },
        labels: {
            overflow: 'justify'
        }
    },
    plotOptions: {
        bar: {
            dataLabels: {
                enabled: true
            }
        }
    },
    credits: {
        enabled: false
    },
    series: [{
        name: '',
        showInLegend: false,
        data: scores
    }]
});
}

var init = function() {

    // listen for changes (by back-end) in hidden data-container

    var observer = new MutationObserver(function(mutations) {
        console.log('mutation observed!')
        mutations.forEach(function(mutation) {
            if (mutation.attributeName == "accesskey") {  // note the small k for key!
                console.log("data has been updated")
                // hide the waiting modal
                document.getElementById('waiting-modal').className='modal'; /* removed the is-active class */

                // show graphs
                show_graphs()
            }
        });
    });
    observer.observe(document.getElementById("data-container"), {
        attributes: true,
        characterData: true
    });

    // listen for change in image selection\
    document.querySelector('#start-model-button').addEventListener('click', function() {
        console.log('Models being scored in the back-end');
        // show waiting modal
        document.getElementById('waiting-modal').className='modal is-active';
    })
}


// there is a problem with this: dash components haven't loaded yet
//window.addEventListener('DOMContentLoaded', init, false);

setTimeout(init, 1000);
