import React, {useState} from 'react';
import {GameState, useListener} from './GamesUtil';
import './GamePage.css';
import Game from './Game';

function GamePage() {
	let searchparams = new URLSearchParams(window.location.search);
	let gameId = searchparams.get('id');

	let [games, setGames] = useState<[string, GameState][]>([]);
	useListener((newGames) => setGames(newGames));

	let game = games.find((game) => game[0] === gameId)
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