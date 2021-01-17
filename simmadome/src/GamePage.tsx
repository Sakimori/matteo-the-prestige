import React, {useState, useRef, useLayoutEffect} from 'react';
import twemoji from 'twemoji';
import ReactRouter from 'react-router';
import {GameState, useListener} from './GamesUtil';
import './GamePage.css';
import Game from './Game';
import {getUID} from './util';

function GamePage(props: ReactRouter.RouteComponentProps<{id: string}>) {
	let [game, setGame] = useState<[string, GameState]|undefined>(undefined);
	let history = useRef<[number, string, string][]>([]);

	useListener((newGames) => {
		let newGame = newGames.find((gamePair) => gamePair[0] === props.match.params.id);
		setGame(newGame);
		console.log(newGame);
		if (newGame !== undefined && newGame[1].start_delay < 0 && newGame[1].end_delay > 8) {
			history.current.unshift([getUID(), newGame[1].update_emoji, newGame[1].update_text]);
			if (history.current.length > 8) {
				history.current.pop();
			}
		}
	});

	if (game === undefined) {
		return <div id="game_container">The game you're looking for either doesn't exist or has already ended.</div>
	}

	return (
		<div id="game_container">
	        <Game gameId={game[0]} state={game[1]}/>
	        { history.current.length > 0 ?
	        	<GameHistory history={history.current}/> :
	        	null
	        }
	    </div>
    );
}

function GameHistory(props: {history: [number, string, string][]}) {
	let self = useRef<HTMLDivElement>(null);

	useLayoutEffect(() => {
		if (self.current) {
			twemoji.parse(self.current);
		}
	})

	return (
		<div className="history_box" ref={self}>
			<div className="history_title">History</div>
			{props.history.map((update) => (
				<div className="update history_update" key={update[0]}>
			        <div className="update_emoji">{update[1]}</div>
			        <div className="update_text">{update[2]}</div>
			    </div>
			))}
		</div>
	);
}

export default GamePage;