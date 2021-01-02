var socket = io.connect();
var lastupdate;
var grid;

$(document).ready(function (){
    grid = document.getElementById("container")

    socket.on('connect', function () {
        socket.emit('recieved', {});
    });

    socket.on("states_update", function (json) { //json is an object containing all game updates
        lastupdate = json;
        updateGames(json, $('#selected_filter').text());
        updateLeagues(json);
    });
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
    var newBox = document.createElement("DIV");
    newBox.className = "emptyslot";
    grid.appendChild(newBox);
}

const insertGame = (gridboxnum, game) => {
    var thisBox = grid.children[gridboxnum];
    thisBox.innerHTML = game.html;
    thisBox.className = "game";
    thisBox.timestamp = game.timestamp;
};

const updateLeagues = (games) => {
    //get all leagues
    var leagues = []
    for (var game of games) {
        if (game.league != "" && !leagues.includes(game.league)) {
            leagues.push(game.league)
        }
    }

     //remove leagues no longer present
    $('#filters .filter').each(function(index) {
        if (!leagues.includes($(this).text())) {
            if (this.id != 'selected_filter' && $(this).text() != "All") { //don't remove the currently selected filter or the "all" filter
                $(this).remove();
            }
        } else {
            leagues.splice(leagues.indexOf($(this).text()), 1);
        }
    })

    // add leagues not already present
    for (var league of leagues) { // we removed the entries that are already there in the loop above
        var btn = document.createElement("BUTTON");
        btn.className = "filter"
        btn.innerHTML = league
        $('#filters').append(btn);
    }

    //add click handlers to each filter
    $('#filters .filter').each(function(index) {
        this.onclick = function() {
            if ($('#filters #selected_filter').text() == 'All') {
                updateGames([], ""); // clear grid when switching off of All, to make games collapse to top
            }
            $('#filters #selected_filter').attr('id', '');
            this.id = 'selected_filter';

            var search = new URLSearchParams();
            search.append("name", this.textContent);
            history.pushState({}, "", (this.textContent != 'All' ? "/league?" + search.toString() : "/"));
            updateGames(lastupdate, this.textContent);
        }
    })
}

window.onpopstate = function(e) {
    var searchparams = new URLSearchParams(window.location.search)
    updateLeagues(lastupdate);
    $('#filters #selected_filter').attr('id', '');
    if (searchparams.has('name')) {
        $('#filters .filter').each(function(i) { if (this.textContent == searchparams.get('name')) { this.id = 'selected_filter' }})
        updateGames(lastupdate, searchparams.get('name'));
    } else {
        $('#filters .filter').each(function(i) { if (this.textContent == 'All') { this.id = 'selected_filter' }})
        updateGames(lastupdate, "All");
    }
}