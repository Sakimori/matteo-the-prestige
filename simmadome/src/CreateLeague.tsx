import React, {useState, useRef, useLayoutEffect, useReducer} from 'react';
import './CreateLeague.css';
import twemoji from 'twemoji';

// STATE CLASSES

class LeagueStructureState {
	subleagues: SubleagueState[]

	constructor(subleagues: SubleagueState[] = []) {
		this.subleagues = subleagues;
	}
}

class SubleagueState {
	name: string
	divisions: DivisionState[]
	id: string|number

	constructor(divisions: DivisionState[] = []) {
		this.name = "";
		this.divisions = divisions;
		this.id = getUID();
	}
}

class DivisionState {
	name: string
	teams: TeamState[]
	id: string|number

	constructor() {
		this.name = "";
		this.teams = [];
		this.id = getUID();
	}
}

class TeamState {
	name: string
	id: string|number

	constructor(name: string = "") {
		this.name = name;
		this.id = getUID();
	}
}

let getUID = function() { // does NOT generate UUIDs. Meant to create list keys ONLY
	let id = 0;
	return function() { return id++ }
}()

let initLeagueStructure = {
	subleagues: [0, 1].map((val) => 
		new SubleagueState([0, 1].map((val) => 
			new DivisionState()
		))
	)
};

// STRUCTURE REDUCER

type StructureReducerActions = 
	{type: 'remove_subleague', subleague_index: number} |
	{type: 'add_subleague'} |
	{type: 'rename_subleague', subleague_index: number, name: string} |
	{type: 'remove_divisions', division_index: number} |
	{type: 'add_divisions'} |
	{type: 'rename_division', subleague_index: number, division_index: number, name: string} |
	{type: 'remove_team', subleague_index: number, division_index: number, name:string} |
	{type: 'add_team', subleague_index:number, division_index:number, name:string}

function leagueStructureReducer(state: LeagueStructureState, action: StructureReducerActions): LeagueStructureState {
	switch (action.type) {
	case 'remove_subleague':
		return {subleagues: removeIndex(state.subleagues, action.subleague_index)};
	case 'add_subleague':
		return {subleagues: append(state.subleagues, new SubleagueState(
			arrayOf(state.subleagues[0].divisions.length, i => 
				new DivisionState()
			)
		))}
	case 'rename_subleague':
		return replaceSubleague(state, action.subleague_index, subleague => {
			let nSubleague = shallowClone(subleague);
			nSubleague.name = action.name;
			return nSubleague;
		});
	case 'remove_divisions':
		return {subleagues: state.subleagues.map(subleague => {
			let nSubleague = shallowClone(subleague);
			nSubleague.divisions = removeIndex(subleague.divisions, action.division_index)
			return nSubleague;
		})};
	case 'add_divisions':
		return {subleagues: state.subleagues.map(subleague => {
			let nSubleague = shallowClone(subleague);
			nSubleague.divisions = append(subleague.divisions, new DivisionState())
			return nSubleague;
		})};
	case 'rename_division':
		return replaceDivision(state, action.subleague_index, action.division_index, division => {
			let nDivision = shallowClone(division);
			nDivision.name = action.name;
			return nDivision; 
		});
	case 'remove_team':
		return replaceDivision(state, action.subleague_index, action.division_index, division => {
			let nDivision = shallowClone(division);
			nDivision.teams = removeIndex(division.teams, division.teams.findIndex(val => val.name === action.name));
			return nDivision; 
		});
	case 'add_team':
		return replaceDivision(state, action.subleague_index, action.division_index, division => {
			let nDivision = shallowClone(division);
			nDivision.teams = append(division.teams, new TeamState(action.name));
			return nDivision;
		});
	}
}

function replaceSubleague(state: LeagueStructureState, si: number, func: (val: SubleagueState) => SubleagueState) {
	return {subleagues: replaceIndex(state.subleagues, si, func(state.subleagues[si]))}
}

function replaceDivision(state: LeagueStructureState, si: number, di: number, func:(val: DivisionState) => DivisionState) {
	return replaceSubleague(state, si, subleague => {
		let nSubleague = shallowClone(subleague);
		nSubleague.divisions = replaceIndex(subleague.divisions, di, func(subleague.divisions[di]));
		return nSubleague;
	});
}

// UTIL

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

function shallowClone<T>(obj: T): T {
	return Object.assign({}, obj);
}

type DistributiveOmit<T, K extends keyof any> = T extends any ? Omit<T, K> : never;

// CREATE LEAGUE

function CreateLeague() {
	let [name, setName] = useState("");
	let [showError, setShowError] = useState(false);
	let [structure, dispatch] = useReducer(leagueStructureReducer, initLeagueStructure);
	let gamesSeries = useState('3');
	let seriesDivisionOpp = useState('8');
	let seriesInterDivision = useState('16');
	let seriesInterLeague = useState('8');

	let self = useRef<HTMLDivElement | null>(null)

	useLayoutEffect(() => {
		if (self.current) {
			twemoji.parse(self.current)
		}
	})

	return (
		<div className="cl_league_main" ref={self}>
			<input type="text" className="cl_league_name" placeholder="League Name" value={name} onChange={(e) => setName(e.target.value)}/>
			<div className="cl_structure_err">{name === "" && showError ? "A name is required." : ""}</div>
			<LeagueStructre state={structure} dispatch={dispatch} showError={showError}/>
			<div className="cl_league_options">
				<LeagueOptions 
					gamesSeries={gamesSeries} 
					seriesDivisionOpp={seriesDivisionOpp} 
					seriesInterDivision={seriesInterDivision} 
					seriesInterLeague={seriesInterLeague}
					showError={showError}
				/>
				<div className="cl_option_submit_box">
					<button className="cl_option_submit" onClick={e => {
						//make network call, once leagues are merged
						if (!validRequest(name, structure, gamesSeries[0], seriesDivisionOpp[0], seriesInterDivision[0], seriesInterLeague[0])) {
							setShowError(true);
						}
					}}>Submit</button>
					<div className="cl_option_err">{
						!validRequest(name, structure, gamesSeries[0], seriesDivisionOpp[0], seriesInterDivision[0], seriesInterLeague[0]) && showError ?
						"Cannot create league. Some information is invalid." : ""
					}</div>
				</div>
			</div>
		</div>
	);
}

function makeRequest(
		name:string, 
		structure: LeagueStructureState, 
		gamesPerSeries: string, 
		divisionSeries: string, 
		interDivisionSeries: string, 
		interLeagueSeries: string
	) {

	if (!validRequest(name, structure, gamesPerSeries, divisionSeries, interDivisionSeries, interLeagueSeries)) { 
		return null 
	}
	
	return ({
		structure: {
			name: name,
			subleagues: structure.subleagues.map(subleague => ({
				name: subleague.name,
				divisions: subleague.divisions.map(division => ({
					name: division.name,
					teams: division.teams
				}))
			}))
		},
		games_per_series: Number(gamesPerSeries),
		division_series: Number(divisionSeries),
		inter_division_series: Number(interDivisionSeries),
		inter_league_series: Number(interLeagueSeries) 
	});
}

function validRequest(
		name:string, 
		structure: LeagueStructureState, 
		gamesPerSeries: string, 
		divisionSeries: string, 
		interDivisionSeries: string, 
		interLeagueSeries: string
	) {

	return (
		name !== "" && 
		validNumber(gamesPerSeries) && 
		validNumber(divisionSeries) && 
		validNumber(interDivisionSeries) && 
		validNumber(interLeagueSeries) &&
		structure.subleagues.length % 2 === 0 &&
		structure.subleagues.every(subleague => 
			subleague.name !== "" &&
			subleague.divisions.every(division => 
				division.name !== "" &&
				division.teams.length >= 2
			)
		)
	)
}

function validNumber(value: string) {
	return Number(value) !== NaN && Number(value) > 0
}

// LEAGUE STRUCUTRE

function LeagueStructre(props: {state: LeagueStructureState, dispatch: React.Dispatch<StructureReducerActions>, showError: boolean}) {
	return (
		<div className="cl_league_structure">
			<div className="cl_league_structure_scrollbox">
				<div className="cl_subleague_add_align">
					<div className="cl_league_structure_table">
						<SubleagueHeaders subleagues={props.state.subleagues} dispatch={props.dispatch} showError={props.showError}/>
						<Divisions subleagues={props.state.subleagues} dispatch={props.dispatch} showError={props.showError}/>
					</div>
					<button className="cl_subleague_add" onClick={e => props.dispatch({type: 'add_subleague'})}>➕</button>
				</div>
			</div>
			<div className="cl_structure_err">{props.state.subleagues.length % 2 !== 0 && props.showError ? "Must have an even number of subleagues." : ""}</div>
			<button className="cl_division_add" onClick={e => props.dispatch({type: 'add_divisions'})}>➕</button>
		</div>
	);
}

function SubleagueHeaders(props: {subleagues: SubleagueState[], dispatch: React.Dispatch<StructureReducerActions>, showError:boolean}) {
	return (
		<div className="cl_headers">
			<div key="filler" className="cl_delete_filler"/> 
			{props.subleagues.map((subleague, i) => (
				<div key={subleague.id} className="cl_table_header">
					<div className="cl_subleague_bg">
						<SubleageHeader state={subleague} canDelete={props.subleagues.length > 1} dispatch={action => 
							props.dispatch(Object.assign({subleague_index: i}, action))
						}/>
						<div className="cl_structure_err">{subleague.name === "" && props.showError ? "A name is required." : ""}</div>
					</div>
				</div>
			))}
		</div>
	);
}

function SubleageHeader(props: {state: SubleagueState, canDelete: boolean, dispatch:(action: DistributiveOmit<StructureReducerActions, 'subleague_index'>) => void}) {
	return (
		<div className="cl_subleague_header">
			<input type="text" className="cl_subleague_name" placeholder="Subleague Name" value={props.state.name} onChange={e => 
				props.dispatch({type: 'rename_subleague', name: e.target.value})
			}/>
			{props.canDelete ? <button className="cl_subleague_delete" onClick={e => props.dispatch({type: 'remove_subleague'})}>➖</button> : null}
		</div>
	);
}

function Divisions(props: {subleagues: SubleagueState[], dispatch: React.Dispatch<StructureReducerActions>, showError: boolean}) {
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
							} showError={props.showError}/>
						</div>
					</div>
				))}
			</div>
		))}
	</>);
}

function Division(props: {state: DivisionState, dispatch:(action: DistributiveOmit<StructureReducerActions, 'subleague_index'|'division_index'>) => void, showError:boolean}) {
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
			<div className="cl_division_name_box">
				<input type="text" className="cl_division_name" placeholder="Division Name" key="input" value={props.state.name} onChange={e => 
					props.dispatch({type: 'rename_division', name: e.target.value})
				}/>
				<div className="cl_structure_err cl_structure_err_div">{props.state.name === "" && props.showError ? "A name is required." : ""}</div>
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
			<div className="cl_structure_err cl_structure_err_teams">{props.state.teams.length < 2 && props.showError ? "Must have at least 2 teams." : ""}</div>
		</div>
	);
}

// LEAGUE OPTIONS

type StateBundle<T> = [T, React.Dispatch<React.SetStateAction<T>>]

function LeagueOptions(props: {
		gamesSeries: StateBundle<string>, 
		seriesDivisionOpp: StateBundle<string>, 
		seriesInterDivision: StateBundle<string>, 
		seriesInterLeague: StateBundle<string>,
		showError: boolean
	}) {

	let [nGamesSeries, setGamesSeries] = props.gamesSeries;
	let [nSeriesDivisionOpp, setSeriesDivisionOpp] = props.seriesDivisionOpp;
	let [nSeriesInterDivision, setSeriesInterDivision] = props.seriesInterDivision;
	let [nSeriesInterLeague, setSeriesInterLeague] = props.seriesInterLeague;

	return (
		<div className="cl_option_main">
			<div className="cl_option_column">
				<NumberInput title="Number of games per series" value={nGamesSeries} setValue={setGamesSeries} showError={props.showError}/>
				<NumberInput title="Number of series with each division opponent" value={nSeriesDivisionOpp} setValue={setSeriesDivisionOpp} showError={props.showError}/>
			</div>
			<div className="cl_option_column">
				<NumberInput title="Number of inter-divisional series" value={nSeriesInterDivision} setValue={setSeriesInterDivision} showError={props.showError}/>
				<NumberInput title="Number of inter-league series" value={nSeriesInterLeague} setValue={setSeriesInterLeague} showError={props.showError}/>
			</div>
		</div>
	);
}

function NumberInput(props: {title: string, value: string, setValue: (newVal: string) => void, showError: boolean}) {
	return (
		<div className="cl_option_box">
			<div className="cl_option_label">{props.title}</div>
			<input className="cl_option_input" type="number" min="0" value={props.value} onChange={e => props.setValue(e.target.value)}/>
			<div className="cl_option_err">{(Number(props.value) === NaN || Number(props.value) < 0) && props.showError ? "Must be a number greater than 0" : ""}</div>
		</div>
	);
}

export default CreateLeague;