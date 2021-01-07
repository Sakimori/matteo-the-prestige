import React from 'react';
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

interface AppProps { 
  filter: string | null
  gameId: string | null
}

interface AppState { 
  filter: string
  games: [string, GameState][] 
}

class App extends React.Component<AppProps, AppState> {
  gameList: GameList;

  constructor(props: AppProps) {
    super(props);

    let socket = io();
    socket.on('connect', () => socket.emit('recieved', {}));
    socket.on('states_update', (update: [string, GameState][]) => this.onStatesUpdate(update));

    this.gameList = [];
    this.state = {
      filter: props.filter ?? "",
      games: []
    };
    this.onSelectNewFilter = this.onSelectNewFilter.bind(this);
  }

  onStatesUpdate(newStates: [string, GameState][]) {
    console.log(newStates);
    this.setState({ games: newStates });
  }

  onSelectNewFilter(newFilter: string) {
    this.setState({ filter: newFilter });
    this.gameList = [];
  }

  updateGameList() {
    let filterGames = this.state.games.filter((game, i) => this.state.filter === "" || game[1].leagueoruser === this.state.filter)

    //remove games no longer present, update games with new info
    for (let i = 0; i < this.gameList.length; i ++) {
      if (this.gameList[i] !== null) {
        let newState = filterGames.find((val) => val[0] === this.gameList[i]![0]);
        if (newState !== undefined) {
          this.gameList[i] = newState;
        } else {
          this.gameList[i] = null;
        }
      }
    }

    // add games not present
    for (let game of filterGames) {
      if (!this.gameList.find((val) => val !== null && val[0] === game[0])) {
        let firstEmpty = this.gameList.indexOf(null);
        if (firstEmpty < 0) {
          this.gameList.push(game)
        } else {
          this.gameList[firstEmpty] = game;
        }
      }
    }

    //remove trailing empty cells
    while (this.gameList[this.gameList.length-1] === null) {
      this.gameList.pop();
    }
  }

  render() {
    this.updateGameList();

    let filters: string[] = [];
    this.state.games.forEach((game, id) => { if (game[1].is_league && !filters.includes(game[1].leagueoruser)) { filters.push(game[1].leagueoruser) }});
    return (
      <div className="App">
        <Filters filterList={filters} selectedFilter={this.state.filter} onSelectNewFilter={this.onSelectNewFilter}/>
        <Grid gameList={this.gameList}/>
        <Footer has_games={this.gameList.length > 0}/>
      </div>
    );
  }
}

function Filters (props: {filterList: string[], selectedFilter: string, onSelectNewFilter: (newFilter: string) => void}) {
  let filters = props.filterList.map((filter: string) => 
    <button className="filter"
            id={filter === props.selectedFilter ? "selected_filter" : ""}
            onClick={() => props.onSelectNewFilter(filter)}>
      {filter}
    </button>
  )

  return (
    <div id="filters">
        <div>Filter:</div>
        <button className="filter" 
                id={"" === props.selectedFilter ? "selected_filter" : ""} 
                onClick={() => props.onSelectNewFilter("")}>
          All
        </button>
        {filters}
    </div>
  );
}


function Grid(props: { gameList: GameList }) {
   return (
    <section className="container" id="container">
      {props.gameList.map((game) => {if (game) {
        return <Game gameId={game[0]} state={game[1]}/>
      } else {
        return <div className="emptyslot"/>
      }})}
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