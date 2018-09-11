var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;

var init = function() {

    // listen for changes (by back-end) in hidden data-container

    var observer = new MutationObserver(function(mutations) {
        console.log('mutation observed!')
        mutations.forEach(function(mutation) {
            if (mutation.attributeName == "accesskey") {  // note the small k for key!
                console.log("data has been updated")
                // hide the waiting modal
                document.getElementById('waiting-modal').className='modal'; /* removed the is-active class */
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
