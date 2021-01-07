import React, {useState, useRef, useEffect, useLayoutEffect} from 'react';
import io from 'socket.io-client';
import './App.css';
import Game from './Game';

interface GameState {
  bases: (string | null)[];
  outs: number;
  display_top_of_inning: boolean
  display_inning: number
  max_innings: number
  title: string
  weather_emoji: string
  weather_text: string
  away_name: string
  away_score: number
  home_name: string
  home_score: number
  pitcher: string
  batter: string
  update_emoji: string
  update_text: string
  is_league: boolean
  leagueoruser: string
}

type GameList = ([id: string, game: GameState] | null)[];

function App(props: {filter: string | null, gameId: string | null}) {

  let [games, setGames] = useState(new Array<[string, GameState]>());
  let [filter, setFilter] = useState("");
  useListener(setGames);

  let filters: string[] = [];
  games.forEach((game, id) => { if (game[1].is_league && !filters.includes(game[1].leagueoruser)) { filters.push(game[1].leagueoruser) }});

  let gameList = useRef(new Array<(string | null)>());
  let filterGames = games.filter((game, i) => filter === "" || game[1].leagueoruser === filter);
  updateList(gameList.current, filterGames);

  return (
    <div className="App">
      <Filters filterList={filters} selectedFilter={filter} onSelectNewFilter={(filter: string) => {gameList.current = []; setFilter(filter)}}/>
      <Grid gameList={gameList.current.map((val) => val !== null ? filterGames.find((game) => game[0] === val) as [string, GameState] : null )}/>
      <Footer has_games={filterGames.length > 0}/>
    </div>
  );
}

// App Utils

// connects to the given url (or host if none) and waits for state updates
const useListener = (onUpdate: (update: [string, GameState][]) => void, url: string | null = null) => {
  useEffect(() => {
    let socket = url ? io(url) : io();
    socket.on('connect', () => socket.emit('recieved', {}));
    socket.on('states_update', onUpdate);
    return () => {socket.disconnect()};
  }, [url])
}

// adds and removes games from list to keep it up to date, without relocating games already in place
function updateList(gameList: (string | null)[], games: [string, GameState][]) {

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

function Filters (props: {filterList: string[], selectedFilter: string, onSelectNewFilter: (newFilter: string) => void}) {
  function Filter(innerprops: {title: string, filter:string} ) {
    return (
      <button className="filter"
              id={innerprops.filter === props.selectedFilter ? "selected_filter" : ""}
              onClick={() => props.onSelectNewFilter(innerprops.filter)}>
        {innerprops.title}
      </button>
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

  useLayoutEffect(() => {
    setNumcols(getCols());
  }, [])

  useEffect(() => {
    window.addEventListener('resize', (event) => {
      setNumcols(getCols());
    })
  })


  let slots = newList.map((game) => {
    if (game) {
      return <Game gameId={game[0]} state={game[1]} key={game[0]}/>
    } else {
      return <div className="emptyslot"/>
    }
  })

  return (
    <section className="container" id="container" ref={self}>
      {slots.map((elem) => <div className="slot_container">{elem}</div>)}
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

export default App;
export type { GameState };