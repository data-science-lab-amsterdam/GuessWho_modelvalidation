
var num_flipped_player = 0;
var flipped_player = {};
var num_flipped_computer = 0;
var flipped_computer = {};

var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;

var qs = function(x) { return document.querySelector(x) };
var qsa = function(x) { return document.querySelectorAll(x) };

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

var endGame = function(winner)
{
    closeModal('waiting-modal');
    document.getElementById('end-modal-content').innerHTML = (
        winner == 'computer' ?
        'Too bad. The computer has guessed its character correctly and won the game!' :
        'Congratulations, you\'ve won the game!'
    );
    btn_class = (winner == 'computer' ? 'is-danger' : 'is-succes')
    document.getElementById('end-modal-button').className = 'button is-medium '+btn_class;
    document.getElementById('end-modal').className = 'modal is-active';
    document.getElementById('end-modal-button').addEventListener('click', function() {location.reload()})
}

var updateComputerBoard = function(board)
{
    // flip the selected characters
    //var num_flipped_computer = 0;
    var to_be_flipped = [];
    var elm;
    for (var id in board) {
        if (!board.hasOwnProperty(id)) {
            // The current property is not a direct property of the object
            continue;
        }
        if (!board[id]) {
            if (!flipped_computer[id]) {
                to_be_flipped.push(id);
            }
        }
    }
    console.log(to_be_flipped);
    if (to_be_flipped.length > 0) {
        flipCharacters(to_be_flipped, 0);
    }

}

var flipCharacters = function(ids, idx)
{
    var id = ids[idx];
    console.log('flipping character: '+ids[idx]);
    // flip character
    document.getElementById('img-p1-character-'+id).src = '/images/closed_blue.png';

    // update the progress bar
    num_flipped_computer += 1;
    flipped_computer[id] = true;
    var total_options = document.getElementById('computer-board').children.length - 1;
    var progress = Math.round((num_flipped_computer/total_options) * 100);
    document.getElementById('computer-progress').value = progress;

    if (idx+1 < ids.length) {
        setTimeout(function() {flipCharacters(ids, idx+1)}, 200);
    }
}

var showModal = function(id, options)
{
    var options = options || {};
    if (options['text'] != null) {
        qs('#'+id+'-content').innerHTML = options['text'];
    }
    if (options['button-text'] != null) {
        qs('#'+id+'-button').innerHTML = options['button-text'];
    }
    if (options['callback'] != null) {
        var callback = options['callback'];
    } else {
        var callback = function() { closeModal(id) };
    }
    qs('#'+id+'-button').className = ['button', (options['style'] || "is-info")].join(' ');
    qs('#'+id+'-button').addEventListener('click', callback);

    document.getElementById(id).className = 'modal is-active'
}

var closeModal = function(id)
{
    document.getElementById(id).className = 'modal'
}

var handleComputerMove = function()
{
    // read json data
    var raw_state = qs("#output-hidden-state").getAttribute('accessKey');
    var state = JSON.parse(decodeURIComponent(raw_state));

    if (state['question'][0] == 'character' && state['answer'] == true) {
        endGame('computer');
    } else {
        // close waiting modal
        closeModal('waiting-modal');

        // show computer move
        var text = [
            'Computers question: "Is '+state['question'][0]+' '+state['question'][1]+'?"',
            'Answer: "'+(state['answer'] ? 'Yes' : 'No')+'"'
        ].join('<br>');
        showModal('waiting-modal', {
            'text': text,
            'button-text': 'OK',
            'callback': function() {
                closeModal('waiting-modal');
                updateComputerBoard(state['board']);
            }
        });
    }
}

var handleGuessAnswer = function()
{
    var state = qs("#output-hidden-guess").getAttribute('accessKey');
    if (state == '1') {
        showModal('feedback-modal', {
            'text': 'Congratulations! You have guessed your character and won the game!',
            'style': 'is-success',
            'button-text': 'OK',
            'callback': function() {
                location.reload();
            }
        });
    } else {
        showModal('feedback-modal', {
            'text': 'Too bad! That\'s incorrect...',
            'style': 'is-danger',
            'button-text': 'OK',
            'callback': function() {
                closeModal('feedback-modal');
            }
        });
    }
}

var init = function() {

    var mo1 = new MutationObserver(function(mutations) {
        console.log('mutation observed!')
        mutations.forEach(function(mutation) {
            if (mutation.attributeName == "accesskey") {  // note the small k for key!
                console.log("computer board changed");
                handleComputerMove();
            }
        });
    });
    mo1.observe(qs("#output-hidden-state"), {
        attributes: true,
        characterData: true
    });

    var mo2 = new MutationObserver(function(mutations) {
        console.log('mutation observed!')
        mutations.forEach(function(mutation) {
            if (mutation.attributeName == "accesskey") {  // note the small k for key!
                console.log("guess answer changed");
                handleGuessAnswer();
            }
        });
    });
    mo2.observe(qs("#output-hidden-guess"), {
        attributes: true,
        characterData: true
    });

    qs('#input-endturn-button').addEventListener('click', function() {
        showModal('waiting-modal', {
            'text': 'Waiting for computer to move...',
            'button-text': 'OK'
        });
    })
    qs('#waiting-modal-button').addEventListener('click', function() {
        closeModal('waiting-modal');
    })

}


// there is a problem with this: dash components haven't loaded yet
//window.addEventListener('DOMContentLoaded', init, false);

setTimeout(init, 1500);
