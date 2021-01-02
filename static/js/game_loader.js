$(document).ready(function (){
    var socket = io.connect();

    socket.on('connect', function () {
        console.log("connected")
        socket.emit('recieved', {});
    });

    socket.on("states_update", function (json) { //json is an object containing all game updates
        console.log(json)
        var searchparams = new URLSearchParams(window.location.search);
        var exists = false;
        for (game of json) {
            if (searchparams.get('timestamp') == game.timestamp) {
                $('.game').html(game.html);
                exists = true;
            }
        }
        if (!exists) {
            // inform the user the game has ended
        }
    });
});