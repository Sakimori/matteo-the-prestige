$(document).ready(function (){
    var socket = io.connect();

    socket.on('connect', function () {
        console.log("connected")
        socket.emit('recieved', {});
    });

    socket.on("states_update", function (json) { //json is an object containing all game updates
        var searchparams = new URLSearchParams(window.location.search);
        var exists = false;
        for (game of json) {
            if (searchparams.get('timestamp') == game.timestamp) {
                $('.game').html(game.html);
                exists = true;
            }
        }
        if (!exists) {
            $('game').remove()
            $('#game_container').text("The game you're looking for either doesn't exist or has already ended.")
        }

        twemoji.parse(document.body);
    });
});