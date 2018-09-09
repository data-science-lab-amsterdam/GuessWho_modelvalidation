var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;

var data;

var read_data = function()
{
    // read data from hidden container
    var raw_data = document.getElementById("data-container").getAttribute('accessKey');
    data = JSON.parse(decodeURIComponent(raw_data));

    // show image
    document.getElementById('image').src = data['url'];

    // show properties
    for (var key in data['features']) {
        var item = data['features'][key];
        var value = item['value'];
        var score = item['score'];
        console.log([key, value, score]);

        // fill dropdown with value
        var selector = `#input-${feature} select option[value=${value}]`;
        document.querySelector(selector).selected = true;
    }
}

var save_data = function() 
{
    // read values from dropdown fields
    var features = Object.keys(data['features']);
    }
    for (var key in data['features']) {
        var selected_value;
        opts = document.querySelectorAll(`#input-${key} select option`);
        opts.forEach(function(x) {
            if (x.selected==true) {
                selected_value = x.value;
            }
        });
        data['features'][key] = selected_value;
    }

    // put json into hidden data container
    var json_string = JSON.stringify(data['features']);
    document.getElementById('data-container2').accessKey = json_string;

var init = function() {

    var observer = new MutationObserver(function(mutations) {
        console.log('mutation observed!')
        mutations.forEach(function(mutation) {
            if (mutation.attributeName == "accesskey") {  // note the small k for key!
                console.log("data has been updated")
                read_data()
            }
        });
    });
    observer.observe(document.getElementById("data-container"), {
        attributes: true,
        characterData: true
    });

    document.getElementById('save-button').addEventListener('click', save_data);
}


// there is a problem with this: dash components haven't loaded yet
//window.addEventListener('DOMContentLoaded', init, false);

setTimeout(init, 1000);
