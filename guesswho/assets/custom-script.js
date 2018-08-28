
var num_flipped_player = 0;
var flipped_player = {};

var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;


var clickCharacter = function(player_id, i)
{
    if (player_id == 1) {
        return false;
    }

    if (flipped_player[i]) {
        return false;
    }

    // flip the clicked image
    document.getElementById('img-p2-character-'+i).src = './images/closed_red.png';

    // update the progress bar
    num_flipped_player += 1;
    flipped_player[i] = true;

    var total_options = document.getElementById('player-board').children.length - 1;
    var progress = Math.round((num_flipped_player/total_options) * 100);
    document.getElementById('player-progress').value = progress;
};

var endGame = function(winner) {
    document.getElementById('end-modal').innerHTML = (
        winner == 'computer' ?
        'Too bad. The computer has won the game!' :
        'Congratulations, you\'ve won the game!'
    );
    document.getElementById('end-modal').setAttribute('className', 'modal is-active');
}

var update_computer_board = function()
{
    // flip the selected characters
    var raw_state = document.getElementById("output-hidden-state").getAttribute('accessKey');
    if (raw_state == 'FINISHED') {
        endGame('computer');
    } else {
        var state = JSON.parse(decodeURIComponent(raw_state));
        console.log(state);
        var num_flipped_computer = 0;
        for (var prop in state) {
            if (!state.hasOwnProperty(prop)) {
                // The current property is not a direct property of the object
                continue;
            }
            if (!state[prop]) {
                document.getElementById('img-p1-character-'+prop).src = '/images/closed_blue.png';
                num_flipped_computer += 1;
            }
        }

        // update the progress bar
        var total_options = document.getElementById('computer-board').children.length - 1;
        var progress = Math.round((num_flipped_computer/total_options) * 100);
        document.getElementById('computer-progress').value = progress;
    }
}



var init = function() {

    var observer = new MutationObserver(function(mutations) {
        console.log('mutation observed!')
        mutations.forEach(function(mutation) {
            if (mutation.attributeName == "accesskey") {  // note the small k for key!
                console.log("attributes changed")
                update_computer_board()
            }
        });
    });
    observer.observe(document.getElementById("output-hidden-state"), {
        attributes: true,
        characterData: true
    });

}


// there is a problem with this: dash components haven't loaded yet
//window.addEventListener('DOMContentLoaded', init, false);

setTimeout(init, 1000);
