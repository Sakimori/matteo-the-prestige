import { GameState } from './App';
import './Game.css';
import base_filled from './img/base_filled.png';
import base_empty from './img/base_empty.png';
import out_filled from './img/out_out.png';
import out_empty from './img/out_in.png';

function Game(props: {gameId: string, state : GameState}) {
	let state = props.state;
	return (
		<div className="game">
			<div className="header">
			    <div className="inning">Inning: {state.display_top_of_inning ? "🔼" : "🔽"} {state.display_inning}/{state.max_innings}</div>
			    <div className="title">{state.title}</div>
			    <div className="weather">{state.weather_emoji} {state.weather_text}</div>
			</div>
			<div className="body">
			    <div className="teams">
			        <Team name={state.away_name} score={state.away_score}/>
			        <Team name={state.home_name} score={state.home_score}/>
			    </div>
			    <div className="info">
			        <div className="field">
			            <Base name={state.bases[2]} />
			            <div style={{display: "flex"}}>
			            	<Base name={state.bases[3]} />
			            	<Base name={state.bases[1]} />
			            </div>
			        </div>
			        <div className="outs">
			            <div className="outs_title">OUTS</div>
			            <div className="outs_count">
			            	{[1, 2].map((out) => <Out thisOut={out} totalOuts={state.outs} key={out} />)}
			            </div>
			        </div>
			    </div>
			    <div className="players">
			        <div className="player_type">PITCHER</div>
			        <div className="player_name">{state.pitcher}</div>
			        <div className="player_type">BATTER</div>
			        <div className="player_name batter_name">{state.batter}</div>
			    </div>
			    <div className="update">
			        <div className="update_emoji">{state.update_emoji}</div>
			        <div className="update_text">{state.update_text}</div>
			    </div>
			</div>
			<div className="footer">
			    <div className="batting">{state.display_top_of_inning ? state.away_name : state.home_name} batting.</div>
			    <div className="leagueoruser">{state.leagueoruser} (<a href={"/game?id=" + props.gameId}>share</a>)</div>
			</div>
		</div>
	);
}

function Team(props: {name: string, score: number}) {
	return (
		<div className="team">
        	<div className="team_name">{ props.name }</div>
        	<div className="score">{ props.score }</div>
    	</div>
    );
}

function Base(props: {name: string | null}) {
	return (
		<img className="base" alt={ props.name ?? "" } src={ props.name ? base_filled : base_empty }/>
	);
}

function Out(props: {thisOut: number, totalOuts: number}) {
	return <img className="out" alt="" src={props.thisOut <= props.totalOuts ? out_filled : out_empty}/>;
}

export default Game;