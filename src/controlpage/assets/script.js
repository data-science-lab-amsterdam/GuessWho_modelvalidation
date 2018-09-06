var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;


var read_data = function()
{
    var raw_data = document.getElementById("data-container").getAttribute('accessKey');
    var data = JSON.parse(decodeURIComponent(raw_data));

    // show image
    document.getElementById('image').src = data['url'];

    // show properties
    var features = data['features'];
    for (var i = 0; i < features.length; i++) {
        var item = features[i];
        var feature = "hidden-" + item['key'];
        console.log(feature);
        var value = item['value'];
        console.log(value)
        document.getElementById(feature).value = value;
    }
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
}


// there is a problem with this: dash components haven't loaded yet
//window.addEventListener('DOMContentLoaded', init, false);

setTimeout(init, 1000);
