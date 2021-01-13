import {useLayoutEffect} from 'react';
import io from 'socket.io-client';

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


// connects to the given url (or host if none) and waits for state updates
const useListener = (onUpdate: (update: [string, GameState][]) => void, url: string | null = null) => {
  useLayoutEffect(() => {
    let socket = url ? io(url) : io();
    socket.on('connect', () => socket.emit('recieved', {}));
    socket.on('states_update', onUpdate);
    return () => {socket.disconnect()};
  }, [url])
}

export { useListener };
export type { GameState, GameList };