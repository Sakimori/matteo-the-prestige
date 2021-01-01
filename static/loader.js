$(document).ready(function (){
    var socket = io.connect();
    var lastupdate;
    var grid = document.getElementById("container");
    

    socket.on('connect', function () {
        socket.emit('recieved', { data: 'I\'m connected!' });
    });

    socket.on("states_update", function (json) { //json is an object containing all game updates
        lastupdate = json;
        updateGames(json, $('#selected_filter').text());

        //get all leagues
        leagues = []
        for (var game of json) {
            if (game.league != "" && !leagues.includes(game.league)) {
                leagues.push(game.league)
            }
        }

        //remove leagues no longer present
        $('#filters .filter').each(function(index) {
            if (!leagues.includes($(this).text())) {
                if ($(this).attr('id') != 'selected_filter' && $(this).text() != "All") { //don't remove the currently selected filter or the "all" filter
                    $(this).remove();
                }
            } else {
                leagues.splice(leagues.indexOf($(this).text()), 1);
            }
        })

        // add leagues not already present
        for (var league of leagues) { // we removed the entries that are already there in the loop above
            $('#filters').append("<button class='filter'>"+league+"</button>");
        }

        //add click handlers to each filter
        $('#filters .filter').each(function(index) {
            $(this).click(function() {
                if ($('#filters #selected_filter').text() == 'All') {
                    updateGames([], ""); // clear grid when switching off of All, to make games collapse to top
                }
                $('#filters #selected_filter').attr('id', '');
                $(this).attr('id', 'selected_filter');
                updateGames(lastupdate, $(this).text());
            })
        })
    });

    const updateGames = (json, filter) => {

        filterjson = [];
        for (var game of json) {
            if (game.league == filter || filter == "All") {
                filterjson.push(game);
            }
        }

        if (filterjson.length == 0) {
            $('#footer div').html("No games right now. Why not head over to Discord and start one?");
        } else {
            $('#footer div').html("");
        }

        //replace games that have ended with empty slots
        for (var slotnum = 0; slotnum < grid.children.length; slotnum++) {
            if (grid.children[slotnum].className == "game" && !filterjson.some((x) => x.timestamp == grid.children[slotnum].timestamp)) {
                grid.children[slotnum].className = "emptyslot";
                grid.children[slotnum].timestamp = null;
                grid.children[slotnum].innerHTML = "";
            }
        }

        for (var game of filterjson) {
            //updates game in list
            for (var slotnum = 0; slotnum < grid.children.length; slotnum++) {
                if (grid.children[slotnum].timestamp == game.timestamp) {
                    insertGame(slotnum, game);
                };
            };

            //adds game to list if not there already
            if (!Array.prototype.slice.call(grid.children).some((x) => x.timestamp == game.timestamp)) {
                for (var slotnum = 0; true; slotnum++) { //this is really a while loop but shh don't tell anyone
                    if (slotnum >= grid.children.length) {
                        for (var i = 0; i < 3; i ++) {
                            insertEmpty(grid);
                        }
                    }
                    if (grid.children[slotnum].className == "emptyslot") {
                        insertGame(slotnum, game);
                        break;
                    };
                };
            }
        };

        //remove last rows if not needed
        while (grid.children[grid.children.length-1].className == "emptyslot" &&
               grid.children[grid.children.length-2].className == "emptyslot" &&
               grid.children[grid.children.length-3].className == "emptyslot" &&
               grid.children.length > 3) {
            for (var i = 0; i < 3; i++) {
                grid.removeChild(grid.children[grid.children.length-1]);
            }
        }
    }

    const insertEmpty = (grid) => {
        newBox = document.createElement("DIV");
        newBox.className = "emptyslot";
        grid.appendChild(newBox);
    }

    const insertGame = (gridboxnum, game) => {
        var thisBox = grid.children[gridboxnum];
        thisBox.innerHTML = game.html;
        thisBox.className = "game";
        thisBox.timestamp = game.timestamp;
    };
});