
var num_flipped = 0;
var flipped = {};

var clickCharacter = function(player_id, i)
{
    if (player_id == 1) {
        return false;
    }

    if (flipped[i]) {
        return false;
    }

    // flip the clicked image
    document.getElementById('img-p2-character-'+i).src = './images/closed.jpg';

    // update the progress bar
    num_flipped += 1;
    flipped[i] = true;

    var total_options = document.getElementById('player-board').children.length - 1;
    var progress = Math.round((num_flipped/total_options) * 100);
    document.getElementById('player-progress').value = progress;
};

var update_computer_board = function()
{
    var state = eval(document.getElementById("output-hidden-state").value);
    console.log(state);
    for (var prop in state) {
        if (!p.hasOwnProperty(prop)) {
            //The current property is not a direct property of p
            continue;
        }
        if (!state[prop]) {
            document.getElementById('img-p1-character-'+prop).src = './images/closed.jpg';
        }
    }
}

document.body.addEventListener('load', function() {
    document.getElementById("output-hidden-state").addEventListener("change", update_computer_board);
})
