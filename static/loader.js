$(document).ready(function (){
    var socket = io.connect();
    var gameslist = [];
    var maxSlot = 1;
    var grid = document.getElementById("container");
    

    socket.on('connect', function () {
        socket.emit('recieved', { data: 'I\'m connected!' });
    });

    socket.on("states_update", function (json) { //json is an object containing all game updates
        for (const timestamp in json) {
            if (!gameslist.includes(timestamp)) { //adds game to list if not there already
                gameslist.push(timestamp)
                for (var slotnum = 1; true; slotnum++) { //this is really a while loop but don't tell anyone
                    if (slotnum >= grid.children.length) {
                        for (var i = 0; i < 3; i ++) {
                            newBox = document.createElement("DIV");
                            newBox.className = "emptyslot";
                            grid.appendChild(newBox);
                        }
                    }
                    if (grid.children[slotnum].className == "emptyslot") {
                        insertGame(slotnum, json[timestamp], timestamp);
                        maxSlot = Math.max(maxSlot, slotnum);
                        break;
                    };
                };
            };

            for (var slotnum = 1; slotnum <= maxSlot; slotnum++) {
                if (grid.children[slotnum].timestamp == timestamp) {
                    updateGame(grid.children[slotnum], json[timestamp]);
                };
            };
        };
    });

    const insertGame = (gridboxnum, gamestate, timestamp) => {
        var thisBox = grid.children[gridboxnum];
        thisBox.className = "game";
        thisBox.timestamp = timestamp;
        fetch("/static/game.html").then(x=>x.text()).then(gamehtml => {
            thisBox.innerHTML = gamehtml;
            updateGame(thisBox, gamestate);
        });
    };

    const BASE_EMPTY = "/static/img/base_empty.png"
    const BASE_FILLED = "/static/img/base_filled.png"
    const OUT_OUT = "/static/img/out_out.png"
    const OUT_IN = "/static/img/out_in.png"

    const updateGame = (gamediv, gamestate) => {
        gamediv.id = "updateTarget";
        $('#updateTarget .inning').html("Inning: " + (gamestate.display_top_of_inning ? "🔼" : "🔽") + " " + gamestate.display_inning + "/" + gamestate.max_innings);
        $('#updateTarget .weather').html(gamestate.weather_emoji + " " + gamestate.weather_text);

        $('#updateTarget .away_name').html(gamestate.away_name);
        $('#updateTarget .home_name').html(gamestate.home_name);
        $('#updateTarget .away_score').html("" + gamestate.away_score);
        $('#updateTarget .home_score').html("" + gamestate.home_score);

        for (var i = 1; i <= 3; i++) {
            $('#updateTarget .base_' + i).attr('src', (gamestate.bases[i] == null ? BASE_EMPTY : BASE_FILLED));
        }

        $('#updateTarget .outs_count').children().each(function(index) {
            $(this).attr('src', index < gamestate.outs ? OUT_OUT : OUT_IN);
        });

        $('#updateTarget .pitcher_name').html(gamestate.pitcher);
        $('#updateTarget .batter_name').html(gamestate.batter);

        $('#updateTarget .update_emoji').html(gamestate.update_emoji);
        $('#updateTarget .update_text').html(gamestate.update_text);

        $('#updateTarget .batting').html((gamestate.top_of_inning ? gamestate.away_name : gamestate.home_name) + " batting.");

        gamediv.id = "";
    };
});