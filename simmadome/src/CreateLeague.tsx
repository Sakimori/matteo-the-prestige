import React, {useState, useRef, useLayoutEffect, useReducer} from 'react';
import './CreateLeague.css';
import twemoji from 'twemoji';

interface LeagueStructureState {
	subleagues: SubleagueState[]
}

interface SubleagueState {
	name: string
	id: string|number
	divisions: DivisionState[]
}

interface DivisionState {
	name: string
	id: string|number
	teams: TeamState[]
}

interface TeamState {
	name: string
	id: string|number
}

type LeagueReducerActions = 
	{type: 'remove_subleague', subleague_index: number} |
	{type: 'add_subleague'} |
	{type: 'rename_subleague', subleague_index: number, name: string} |
	{type: 'remove_divisions', division_index: number} |
	{type: 'add_divisions'} |
	{type: 'rename_division', subleague_index: number, division_index: number, name: string} |
	{type: 'remove_team', subleague_index: number, division_index: number, name:string} |
	{type: 'add_team', subleague_index:number, division_index:number, name:string}

type DistributiveOmit<T, K extends keyof any> = T extends any ? Omit<T, K> : never;

let getUID = function() { // does NOT generate UUIDs. Meant to create list keys ONLY
	let id = 0;
	return function() { return id++}
}()

function leagueStructureReducer(state: LeagueStructureState, action: LeagueReducerActions): LeagueStructureState {
	switch (action.type) {
	case 'remove_subleague':
		return {subleagues: removeIndex(state.subleagues, action.subleague_index)};
	case 'add_subleague':
		return {subleagues: state.subleagues.concat([{
			name: "", 
			id: getUID(),
			divisions: arrayOf(state.subleagues[0].divisions.length, i => ({
				name: "",
				id: getUID(),
				teams: []
			}))
		}])};
	case 'rename_subleague':
		return replaceSubleague(state, action.subleague_index, subleague => ({
			name: action.name, 
			id: subleague.id,
			divisions: subleague.divisions
		}));
	case 'remove_divisions':
		return {subleagues: state.subleagues.map(subleague => ({
			name: subleague.name, 
			id: subleague.id,
			divisions: removeIndex(subleague.divisions, action.division_index)
		}))};
	case 'add_divisions':
		return {subleagues: state.subleagues.map(subleague => ({
			name: subleague.name,
			id: subleague.id,
			divisions: subleague.divisions.concat([{
				name: "", 
				id: getUID(),
				teams: []
			}])
		}))};
	case 'rename_division':
		return replaceDivision(state, action.subleague_index, action.division_index, division => ({
			name: action.name,
			id: division.id,
			teams: division.teams
		}));
	case 'remove_team':
		return replaceDivision(state, action.subleague_index, action.division_index, division => ({
			name: division.name,
			id: division.id,
			teams: removeIndex(division.teams, division.teams.findIndex(val => val.name === action.name))
		}));
	case 'add_team':
		return replaceDivision(state, action.subleague_index, action.division_index, division => ({
			name: division.name,
			id: division.id,
			teams: division.teams.concat([{
				name: action.name,
				id: getUID()
			}])
		}));
	}
}

function replaceSubleague(state: LeagueStructureState, si: number, func: (val: SubleagueState) => SubleagueState) {
	return {subleagues: replaceIndex(state.subleagues, si, func(state.subleagues[si]))}
}

function replaceDivision(state: LeagueStructureState, si: number, di: number, func:(val: DivisionState) => DivisionState) {
	return replaceSubleague(state, si, subleague => ({
		name: subleague.name,
		id: subleague.id,
		divisions: replaceIndex(subleague.divisions, di, func(subleague.divisions[di]))
	}))
}

function removeIndex(arr: any[], index: number) {
	return arr.slice(0, index).concat(arr.slice(index+1));
}

function replaceIndex<T>(arr: T[], index: number, val: T) {
	return arr.slice(0, index).concat([val]).concat(arr.slice(index+1));
}

function append<T>(arr: T[], val: T) {
	return arr.concat([val]);
} 

function arrayOf<T>(length: number, func: (i: number) => T): T[] {
	var out: T[] = [];
	for (var i = 0; i < length; i++) {
		out.push(func(i));
	}
	return out;
}

let initLeagueStructure = {
	subleagues: [0, 1].map((val) => ({
		name: "",
		id: getUID(),
		divisions: [0, 1].map((val) => ({
			name: "",
			id: getUID(),
			teams: []
		}))
	}))
}

function CreateLeague() {
	let [name, setName] = useState("");
	let [structure, dispatch] = useReducer(leagueStructureReducer, initLeagueStructure);

	let self = useRef<HTMLDivElement | null>(null)

	useLayoutEffect(() => {
		if (self.current) {
			twemoji.parse(self.current)
		}
	})

	return (
		<div className="cl_league_main" ref={self}>
			<input type="text" className="cl_league_name" placeholder="League Name" value={name} onChange={(e) => setName(e.target.value)}/>
			<LeagueStructre state={structure} dispatch={dispatch}/>
			<LeagueOptions />
		</div>
	);
}

function LeagueStructre(props: {state: LeagueStructureState, dispatch: React.Dispatch<LeagueReducerActions>}) {
	return (
		<div className="cl_league_structure">
			<div className="cl_league_structure_scrollbox">
				<div className="cl_subleague_add_align">
					<div className="cl_league_structure_table">
						<SubleagueHeaders subleagues={props.state.subleagues} dispatch={props.dispatch} />
						<Divisions subleagues={props.state.subleagues} dispatch={props.dispatch} />
					</div>
					<button className="cl_subleague_add" onClick={e => props.dispatch({type: 'add_subleague'})}>➕</button>
				</div>
			</div>
			<button className="cl_division_add" onClick={e => props.dispatch({type: 'add_divisions'})}>➕</button>
		</div>
	);
}

function SubleagueHeaders(props: {subleagues: SubleagueState[], dispatch: React.Dispatch<LeagueReducerActions>}) {
	return (
		<div className="cl_headers">
			<div key="filler" className="cl_delete_filler"/> 
			{props.subleagues.map((subleague, i) => (
				<div key={subleague.id} className="cl_table_header">
					<div className="cl_subleague_bg">
						<SubleageHeader state={subleague} canDelete={props.subleagues.length > 1} dispatch={action => 
							props.dispatch(Object.assign({subleague_index: i}, action))
						}/>
					</div>
				</div>
			))}
		</div>
	);
}

function SubleageHeader(props: {state: SubleagueState, canDelete: boolean, dispatch:(action: DistributiveOmit<LeagueReducerActions, 'subleague_index'>) => void}) {
	return (
		<div className="cl_subleague_header">
			<input type="text" className="cl_subleague_name" placeholder="Subleague Name" value={props.state.name} onChange={e => 
				props.dispatch({type: 'rename_subleague', name: e.target.value})
			}/>
			{props.canDelete ? <button className="cl_subleague_delete" onClick={e => props.dispatch({type: 'remove_subleague'})}>➖</button> : null}
		</div>
	);
}

function Divisions(props: {subleagues: SubleagueState[], dispatch: React.Dispatch<LeagueReducerActions>}) {
	return (<>
		{props.subleagues[0].divisions.map((val, di) => (
			<div key={val.id} className="cl_table_row">
				<div key="delete" className="cl_delete_box">
					{props.subleagues[0].divisions.length > 1 ?
						<button className="cl_division_delete" onClick={e => props.dispatch({type: 'remove_divisions', division_index: di})}>➖</button> :
						null
					}
				</div>
				{props.subleagues.map((subleague, si) => (
					<div key={subleague.id} className="cl_division_cell">
						<div className="cl_subleague_bg">
							<Division state={subleague.divisions[di]} dispatch={action =>
								props.dispatch(Object.assign({subleague_index: si, division_index: di}, action))
							}/>
						</div>
					</div>
				))}
			</div>
		))}
	</>);
}

function Division(props: {state: DivisionState, dispatch:(action: DistributiveOmit<LeagueReducerActions, 'subleague_index'|'division_index'>) => void}) {
	let [newName, setNewName] = useState("");
	let [searchResults, setSearchResults] = useState<string[]>([]);
	let newNameInput = useRef<HTMLInputElement>(null);
	let resultList = useRef<HTMLDivElement>(null);

	useLayoutEffect(() => {
		if (resultList.current) {
			twemoji.parse(resultList.current)
		}
	})

	return (
		<div className="cl_division">
			<div>
				<input type="text" className="cl_division_name" placeholder="Division Name" key="input" value={props.state.name} onChange={e => 
					props.dispatch({type: 'rename_division', name: e.target.value})
				}/>
			</div>
			{props.state.teams.map((team, i) => (
				<div className="cl_team" key={team.id}>
					<div className="cl_team_name">{team.name}</div>
					<button className="cl_team_delete" onClick={e => props.dispatch({type:'remove_team', name: team.name})}>➖</button>
				</div>
			))}
			<div className="cl_team_add">
				<input type="text" className="cl_newteam_name" placeholder="Add team..." value={newName} ref={newNameInput}
					onChange={e => {
						let params = new URLSearchParams({query: e.target.value, page_len: '5', page_num: '0'});
						fetch("/api/teams/search?" + params.toString())
							.then(response => response.json())
							.then(data => setSearchResults(data));
						setNewName(e.target.value);
					}}/>
			</div>
			{searchResults.length > 0 && newName.length > 0 ? 
				(<div className="cl_search_list" ref={resultList}>
					{searchResults.map(result => 
						<div className="cl_search_result" key={result} onClick={e => {
							props.dispatch({type:'add_team', name: result});
							setNewName("");
							if (newNameInput.current) {
								newNameInput.current.focus();
							}
						}}>{result}</div>
					)}
				</div>): 
				<div/>
			}
		</div>
	);
}

function LeagueOptions() {
	return (
		<div className="cl_league_options">

		</div>
	);
}

export default CreateLeague;