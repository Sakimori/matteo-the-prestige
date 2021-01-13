import React, {useState} from 'react';
import ReactRouter from 'react-router';
import {GameState, useListener} from './GamesUtil';
import './GamePage.css';
import Game from './Game';

function GamePage(props: ReactRouter.RouteComponentProps<{id: string}>) {
	let [games, setGames] = useState<[string, GameState][]>([]);
	useListener((newGames) => setGames(newGames));

	let game = games.find((game) => game[0] === props.match.params.id)
	return (
		<div id="game_container">
	        { game ? 
	        	<Game gameId={game[0]} state={game[1]}/> : 
	        	"The game you're looking for either doesn't exist or has already ended."
	        }
	    </div>
    );
}

export default GamePage;