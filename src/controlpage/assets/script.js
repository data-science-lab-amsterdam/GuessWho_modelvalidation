var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;

var data;

var read_data = function()
{
    // read data from hidden container
    var raw_data = document.getElementById("data-container").getAttribute('accessKey');
    data = JSON.parse(decodeURIComponent(raw_data));

    // hide the waiting modal
    document.getElementById('waiting-modal').className='modal'; /* removed the is-active class */

    // show image
    //document.getElementById('image').src = data['url'];
    //already handled by a Dash callback function

    // show properties
    for (var key in data['features']) {
        var item = data['features'][key];
        var value = item['value'];
        var score = item['score'];
        console.log([key, value, score]);

        // fill dropdown with value
        var selector = `#input-${key} select option[value=${value}]`;
        document.querySelector(selector).selected = true;
    }
}

var getSelectedDropdownValue = function(id)
{
    var selected_value;
    opts = document.querySelectorAll(`#${id} select option`);
    opts.forEach(function(x) {
        if (x.selected==true) {
            selected_value = x.value;
        }
    });
    return selected_value
}

var save_data = function() 
{
    // read values from dropdown fields
    var features = Object.keys(data['features']);

    for (var key in data['features']) {
        var selected_value = getSelectedDropdownValue(`input-${key}`)
        data['features'][key] = selected_value;
    }

    // put json into hidden data container
    var json_string = JSON.stringify(data['features']);
    console.log(json_string);
    document.getElementById('data-container2').accessKey = json_string;
    document.getElementById('testdiv').value = json_string;
}

var init = function() {

    // listen for changes (by back-end) in hidden data-container

    var observer = new MutationObserver(function(mutations) {
        console.log('mutation observed!')
        mutations.forEach(function(mutation) {
            if (mutation.attributeName == "accesskey") {  // note the small k for key!
                console.log("data has been updated")
                //read_data()
                // hide the waiting modal
                document.getElementById('waiting-modal').className='modal'; /* removed the is-active class */
            }
        });
    });
    observer.observe(document.getElementById("data-container"), {
        attributes: true,
        characterData: true
    });

    // listen for click on save button
    //document.getElementById('save-button').addEventListener('mouseover', save_data);

    // listen for change in image selection\
    /*
    document.querySelector('#image-dropdown').addEventListener('change', function() {
        console.log('image changed');
        // show waiting modal
        //document.getElementById('waiting-modal').className='modal is-active';

        // put selected value in hidden field to fire Dash callback
        var value = getSelectedDropdownValue('image-dropdown');
        document.getElementById('hidden-input-image').accessKey = value;
    })
    */
}


// there is a problem with this: dash components haven't loaded yet
//window.addEventListener('DOMContentLoaded', init, false);

setTimeout(init, 1000);
