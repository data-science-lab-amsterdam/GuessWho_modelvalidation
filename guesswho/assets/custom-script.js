
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

// determine which characters should be flipped
var updateComputerBoard = function(board)
{
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

// animate the flipping of characters
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

// show what the computer has done
var handleComputerMove = function()
{
    // read json data
    var raw_state = qs("#output-hidden-state").getAttribute('accessKey');
    var state = JSON.parse(decodeURIComponent(raw_state));

    if (state['question'][0] == 'character' && state['answer'] == true) {
        // computer has won
        endGame('computer');
    } else {
        // close waiting modal
        closeModal('waiting-modal');

        // show computer's question and answer
        var text = [
            '<strong>Computer\'s question:</strong> <em>"Is '+state['question'][0]+' '+state['question'][1]+'?"</em>',
            '<strong>Answer:</strong> <em>"'+(state['answer'] ? 'Yes' : 'No')+'</em>"'
        ].join('<br>');
        showModal('waiting-modal', {
            'text': text,
            'button-text': 'OK',
            'callback': function() {
                // after button press: flip character's on the computer's board
                closeModal('waiting-modal');
                updateComputerBoard(state['board']);
            }
        });
    }
}

// show feedback after a guess
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
    } else if (state == '0') {
        showModal('feedback-modal', {
            'text': 'Too bad! That\'s incorrect...',
            'style': 'is-danger',
            'button-text': 'OK',
            'callback': function() {
                closeModal('feedback-modal');
            }
        });
    } else if (state == '9') {
        showModal('feedback-modal', {
            'text': 'You\'ve already made a move. Click "End turn".',
            'style': 'is-warning',
            'button-text': 'Sorry. I won\'t try to cheat again',
            'callback': function() {
                closeModal('feedback-modal');
            }
        });
    }
}

// set some event listeners
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
