var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;

var data;

var read_data = function()
{
    var raw_data = document.getElementById("data-container").getAttribute('accessKey');
    data = JSON.parse(decodeURIComponent(raw_data));

    // show image
    document.getElementById('image').src = data['url'];

    // show properties
    var features = data['features'];
    //for (var i = 0; i < features.length; i++) {
    for (var key in data['features']) {
        var item = data['features'][key];
        console.log(key);
        var value = item['value'];
        var score = item['score'];
        console.log(value);
        //document.getElementById(feature).value = value;
        selector = `#input-${feature} select option[value=${value}]`;
        document.querySelector(selector).selected = true;
    }
}

var save_data = function() 
{
    // read values from dropdown fields
    console.log(data['features'])
    for (var i = 0; i < data['features'].length; i++) {
        var selected_value;
        opts = document.querySelectorAll(`#input-${feature} select option`);
        opts.forEach(function(x) {
            if (x.selected==true) {
                selected_value = x.value;
            }
        });

    // put json into hidden data container
}

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
