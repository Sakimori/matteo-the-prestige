import React, {useState, useRef, useEffect, useLayoutEffect} from 'react';
import {GameState, GameList, useListener} from './GamesUtil';
import {Link} from 'react-router-dom';
import './GamesPage.css';
import Game from './Game';

function GamesPage() {
  let gameList = useRef<(string | null)[]>([]);

  let [search, setSearch] = useState(window.location.search);
  useEffect(() => {
    setSearch(window.location.search);
    gameList.current = [];
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [window.location.search])

  // get filter term
  let searchparams = new URLSearchParams(search);
  let filter = searchparams.get('league') ?? ""

  // set up socket listener
  let [games, setGames] = useState<[string, GameState][]>([]);
  useListener(setGames);

  // build filter list
  let filters = useRef(filter !== "" ? [filter] : []); 
  games.forEach((game) => { if (game[1].is_league && !filters.current.includes(game[1].leagueoruser)) { filters.current.push(game[1].leagueoruser) }});
  filters.current = filters.current.filter((f) => games.find((game) => game && game[1].is_league && game[1].leagueoruser === f) || f === filter);

  // update game list
  let filterGames = games.filter((game, i) => filter === "" || game[1].leagueoruser === filter);
  updateList(gameList.current, filterGames, searchparams.get('game'));

  return (
    <>
      <Filters filterList={filters.current} selectedFilter={filter} />
      <Grid gameList={gameList.current.map((val) => val !== null ? filterGames.find((game) => game[0] === val) as [string, GameState] : null )}/>
      <Footer has_games={filterGames.length > 0}/>
    </>
  );
}

// adds and removes games from list to keep it up to date, without relocating games already in place
function updateList(gameList: (string | null)[], games: [string, GameState][], firstGame: string | null) {
  // insert firstGame into first slot, if necessary 
  if (firstGame !== null && games.find((game) => game[0] === firstGame)) {
    if (gameList.includes(firstGame)) {
      gameList[gameList.indexOf(firstGame)] = null;
    }
    gameList[0] = firstGame;
  }

  //remove games no longer present
  for (let i = 0; i < gameList.length; i ++) {
    if (gameList[i] !== null && games.findIndex((val) => val[0] === gameList[i]) < 0) {
        gameList[i] = null;
    }
  }

  // add games not present
  for (let game of games) {
    if (!gameList.find((val) => val !== null && val === game[0])) {
      let firstEmpty = gameList.indexOf(null);
      if (firstEmpty < 0) {
        gameList.push(game[0])
      } else {
        gameList[firstEmpty] = game[0];
      }
    }
  }

  //remove trailing empty cells
  while (gameList[gameList.length-1] === null) {
    gameList.pop();
  }
}

function Filters (props: {filterList: string[], selectedFilter: string}) {
  function Filter(innerprops: {title: string, filter:string} ) {
    let search = new URLSearchParams();
    search.append('league', innerprops.filter);

    return (
      <Link to={innerprops.filter !== "" ? "/?" + search.toString() : "/"} className="filter" id={innerprops.filter === props.selectedFilter ? "selected_filter" : ""}>
          {innerprops.title}
      </Link>
    );
  }

  return (
    <div id="filters">
      <div>Filter:</div>
      <Filter title="All" filter="" key="" />
      {props.filterList.map((filter: string) => 
        <Filter title={filter} filter={filter} key={filter} />
      )}
    </div>
  );
}

function Grid(props: { gameList: GameList }) {
  let self: React.RefObject<HTMLElement> = useRef(null);
  let [numcols, setNumcols] = useState(3);
  let newList = [...props.gameList];

  while (newList.length === 0 || newList.length % numcols !== 0) {
    newList.push(null);
  }

  function getCols() {
    if (self.current !== null) {
      //this is a hack, but there's weirdly no "real" way to get the number of columns
      return window.getComputedStyle(self.current).getPropertyValue('grid-template-columns').split(' ').length;
    } else {
      return 3;
    }
  }
  
  //set num cols after page loads, then add listener to update if window resizes
  useLayoutEffect(() => {
    setNumcols(getCols());
    window.addEventListener('resize', (event) => {
      setNumcols(getCols());
    })
  }, [])

  let emptyKey = 0;
  return (
    <section className="container" id="container" ref={self}>
      {newList.map((game) => (
        <div className="slot_container" key={game ? game[0] : emptyKey++}>
          {game ? <Game gameId={game[0]} state={game[1]}/> : <div className="emptyslot"/>}
        </div>
      ))}
    </section>
  );
}

function Footer(props: { has_games: boolean }) {
  let text = props.has_games ? "" : "No games right now. Why not head over to Discord and start one?";
  return (
    <div id="footer">
      <div>{text}</div>
    </div>
  );
}

export default GamesPage;