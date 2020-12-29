$(document).ready(function (){
    var socket = io.connect();
    var gameslist = [];
    var maxslot = 3;
    var grid = document.getElementById("container");
    

    socket.on('connect', function () {
        socket.emit('recieved', { data: 'I\'m connected!' });
    });

    socket.on("states_update", function (json) { //json is an object containing all game updates
        for (const timestamp in json) {
            if (!gameslist.includes(timestamp)) { //adds game to list if not there already
                gameslist.push(timestamp)
                var gridBoxes = grid.children;
                for (var slotnum = 3; slotnum <= maxslot; slotnum++) {
                    if (gridBoxes[slotnum].className == "emptyslot") {
                        insertGame(slotnum, json[timestamp], timestamp);
                        maxslot += 1;
                        break;
                    };
                };
            };

            for (var slotnum = 3; slotnum <= maxslot; slotnum++) {
                if (grid.children[slotnum].timestamp == timestamp) {
                    console.log(json[timestamp].update_text)
                    grid.children[slotnum].textContent = json[timestamp].update_text;
                };
            };
        };
    });

    const insertGame = (gridboxnum, gamestate, timestamp) => {
        var thisBox = grid.children[gridboxnum];
        thisBox.className = "game";
        thisBox.timestamp = timestamp
        thisBox.textContent = gamestate.update_text;
    };
});