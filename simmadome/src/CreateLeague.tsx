import React, {useState, useRef, useLayoutEffect, useReducer} from 'react';
import {removeIndex, replaceIndex, append, arrayOf, shallowClone, getUID, DistributiveOmit} from './util';
import './CreateLeague.css';
import twemoji from 'twemoji';

// CONSTS

const MAX_SUBLEAGUE_DIVISION_TOTAL = 22;
const MAX_TEAMS_PER_DIVISION = 12;

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

// OPTIONS REDUCER

class LeagueOptionsState {
	games_series = "3"
	intra_division_series = "8"
	inter_division_series = "16"
	inter_league_series = "8"
	top_postseason = "1"
	wildcards = "0"
}

type OptionsReducerActions =
	{type: 'set_games_series', value: string} |
	{type: 'set_intra_division_series', value: string} |
	{type: 'set_inter_division_series', value: string} |
	{type: 'set_inter_league_series', value: string} |
	{type: 'set_top_postseason', value: string} |
	{type: 'set_wildcards', value: string}

function LeagueOptionsReducer(state: LeagueOptionsState, action: OptionsReducerActions) {
	let newState = shallowClone(state);
	switch (action.type) {
	case 'set_games_series':
		newState.games_series = action.value;
		break;
	case 'set_intra_division_series':
		newState.intra_division_series = action.value;
		break;
	case 'set_inter_division_series':
		newState.inter_division_series = action.value;
		break;
	case 'set_inter_league_series':
		newState.inter_league_series = action.value;
		break;
	case 'set_top_postseason':
		newState.top_postseason = action.value;
		break;
	case 'set_wildcards':
		newState.wildcards = action.value;
		break;
	}
	return newState
}

// CREATE LEAGUE

let initLeagueStructure = {
	subleagues: [0, 1].map((val) => 
		new SubleagueState([0, 1].map((val) => 
			new DivisionState()
		))
	)
};

function CreateLeague() {
	let [name, setName] = useState("");
	let [showError, setShowError] = useState(false);
	let [nameExists, setNameExists] = useState(false);
	let [deletedTeams, setDeletedTeams] = useState<string[]>([]);
	let [createSuccess, setCreateSuccess] = useState(false);
	let [structure, structureDispatch] = useReducer(leagueStructureReducer, initLeagueStructure);
	let [options, optionsDispatch] = useReducer(LeagueOptionsReducer, new LeagueOptionsState());

	let self = useRef<HTMLDivElement | null>(null)

	useLayoutEffect(() => {
		if (self.current) {
			twemoji.parse(self.current)
		}
	})

	if (createSuccess) {
		return( 
			<div className="cl_league_main" ref={self}>
				<div className="cl_confirm_box">
					League created succesfully!
				</div>
			</div>
		);
	}

	return (
		<div className="cl_league_main" ref={self}>
			<input type="text" className="cl_league_name" placeholder="League Name" value={name} onChange={(e) => {
				setName(e.target.value);
				setNameExists(false);
			}}/>
			<div className="cl_structure_err">{
				name === "" && showError ? "A name is required." : 
				nameExists && showError ? "A league by that name already exists" : 
				""
			}</div>
			<LeagueStructre state={structure} dispatch={structureDispatch} deletedTeams={deletedTeams} showError={showError}/>
			<div className="cl_league_options">
				<LeagueOptions state={options} dispatch={optionsDispatch} showError={showError}/>
				<div className="cl_option_submit_box">
					<button className="cl_option_submit" onClick={e => {
						if (!validRequest(name, structure, options)) {
							setShowError(true);
						} else {
							let req = new XMLHttpRequest();
							let data = makeRequest(name, structure, options);
							req.open("POST", "/api/leagues", true);
							req.setRequestHeader("Content-type", "application/json");
							req.onreadystatechange = () => {
								if(req.readyState === 4) {
									if (req.status === 200) {
										setCreateSuccess(true);
									}
									if (req.status === 400) {
										let err = JSON.parse(req.response);
										switch (err.status) {
										case 'err_league_exists':
											setNameExists(true);
											break;
										case 'err_no_such_team':
											setDeletedTeams(err.cause);
											break;
										}
										setShowError(true);
									}
								}
							}
							req.send(data);
						}
					}}>Submit</button>
					<div className="cl_option_err">{
						!validRequest(name, structure, options) && showError ?
						"Cannot create league. Some information is missing or invalid." : ""
					}</div>
				</div>
			</div>
		</div>
	);
}

function makeRequest(name:string, structure: LeagueStructureState, options:LeagueOptionsState) {
	return JSON.stringify({
		name: name,
		structure: {
			subleagues: structure.subleagues.map(subleague => ({
				name: subleague.name,
				divisions: subleague.divisions.map(division => ({
					name: division.name,
					teams: division.teams.map(team => team.name)
				}))
			}))
		},
		games_per_series: Number(options.games_series),
		division_series: Number(options.intra_division_series),
		inter_division_series: Number(options.inter_division_series),
		inter_league_series: Number(options.inter_league_series),
		top_postseason: Number(options.top_postseason),
		wildcards: Number(options.wildcards)
	});
}

function validRequest(name:string, structure: LeagueStructureState, options:LeagueOptionsState) {


	return (
		name !== "" && 

		validNumber(options.games_series) && 
		validNumber(options.intra_division_series) && 
		validNumber(options.inter_division_series) && 
		validNumber(options.inter_league_series) &&
		validNumber(options.top_postseason) &&
		validNumber(options.wildcards, 0) &&

		structure.subleagues.length % 2 === 0 &&

		structure.subleagues.every((subleague, si) => 
			subleague.name !== "" &&
			!structure.subleagues.slice(0, si).some(val => val.name === subleague.name) &&
			subleague.divisions.every((division, di) => 
				division.name !== "" &&
				division.teams.length >= 2 &&
				division.teams.length <= MAX_TEAMS_PER_DIVISION &&
				!subleague.divisions.slice(0, di).some(val => val.name === division.name)
			)
		)
	)
}

function validNumber(value: string, min = 1) {
	return !isNaN(Number(value)) && Number(value) >= min;
}

// LEAGUE STRUCUTRE

function LeagueStructre(props: {state: LeagueStructureState, dispatch: React.Dispatch<StructureReducerActions>, deletedTeams: string[], showError: boolean}) {
	let nSubleagues = props.state.subleagues.length;
	let nDivisions = props.state.subleagues[0].divisions.length;
	return (
		<div className="cl_league_structure">
			<div className="cl_league_structure_scrollbox">
				<div className="cl_subleague_add_align">
					<div className="cl_league_structure_table">
						<SubleagueHeaders subleagues={props.state.subleagues} dispatch={props.dispatch} showError={props.showError}/>
						<Divisions subleagues={props.state.subleagues} dispatch={props.dispatch} deletedTeams={props.deletedTeams} showError={props.showError}/>
					</div>
					{ (nSubleagues+1) * (nDivisions+1) < MAX_SUBLEAGUE_DIVISION_TOTAL ?
						<button className="cl_subleague_add" onClick={e => props.dispatch({type: 'add_subleague'})}>➕</button> :
						<div className="cl_subleague_add_filler"/>
					}
				</div>
			</div>
			<div className="cl_structure_err">{props.state.subleagues.length % 2 !== 0 && props.showError ? "Must have an even number of subleagues." : ""}</div>
			{ nSubleagues * (nDivisions+2) < MAX_SUBLEAGUE_DIVISION_TOTAL ?
				<button className="cl_division_add" onClick={e => props.dispatch({type: 'add_divisions'})}>➕</button>:
				<div className="cl_division_add_filler"/>
			}
		</div>
	);
}

function SubleagueHeaders(props: {subleagues: SubleagueState[], dispatch: React.Dispatch<StructureReducerActions>, showError:boolean}) {
	return (
		<div className="cl_headers">
			<div key="filler" className="cl_delete_filler"/> 
			{props.subleagues.map((subleague, i) => {
				let err = 
					subleague.name === "" ?
						"A name is required." :
					props.subleagues.slice(0, i).some(val => val.name === subleague.name) ?
						"Each subleague must have a different name." :
					"";

				return (
					<div key={subleague.id} className="cl_table_header">
						<div className="cl_subleague_bg">
							<SubleageHeader state={subleague} canDelete={props.subleagues.length > 1} dispatch={action => 
								props.dispatch(Object.assign({subleague_index: i}, action))
							}/>
							<div className="cl_structure_err">{props.showError ? err : ""}</div>
						</div>
					</div>
				)
			})}
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

function Divisions(props: {subleagues: SubleagueState[], dispatch: React.Dispatch<StructureReducerActions>, deletedTeams: string[], showError: boolean}) {
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
							} 
							isDuplicate={subleague.divisions.slice(0, di).some(val => val.name === subleague.divisions[di].name)}
							deletedTeams={props.deletedTeams} showError={props.showError} />
						</div>
					</div>
				))}
			</div>
		))}
	</>);
}

function Division(props: {
		state: DivisionState, 
		dispatch: (action: DistributiveOmit<StructureReducerActions, 'subleague_index'|'division_index'>) => void, 
		isDuplicate: boolean,
		deletedTeams: string[],
		showError: boolean
	}) {

	let [newName, setNewName] = useState("");
	let [searchResults, setSearchResults] = useState<string[]>([]);
	let newNameInput = useRef<HTMLInputElement>(null);
	let resultList = useRef<HTMLDivElement>(null);

	useLayoutEffect(() => {
		if (resultList.current) {
			twemoji.parse(resultList.current)
		}
	})

	let divisionErr = 
		props.state.name === "" ? 
			"A name is required." :
		props.isDuplicate ?
			"Each division in a subleague must have a different name." :
		""

	let teamsErr = props.state.teams.length < 2 ? "Must have at least 2 teams." : "";

	return (
		<div className="cl_division">
			<div className="cl_division_name_box">
				<input type="text" className="cl_division_name" placeholder="Division Name" key="input" value={props.state.name} onChange={e => 
					props.dispatch({type: 'rename_division', name: e.target.value})
				}/>
				<div className="cl_structure_err cl_structure_err_div">{props.showError ? divisionErr : ""}</div>
			</div>
			{props.state.teams.map((team, i) => {
				let showDeleted = props.showError && props.deletedTeams.includes(team.name)
				return (<>
					<div className="cl_team" key={team.id}>
						<div className={"cl_team_name" + (showDeleted ? " cl_team_name_err" : "")}>{team.name}</div>
						<button className="cl_team_delete" onClick={e => props.dispatch({type:'remove_team', name: team.name})}>➖</button>
					</div>
					<div className="cl_structure_err cl_structure_err_team">{showDeleted ? "This team was deleted" : ""}</div>
				</>)
			})}
			{ props.state.teams.length < MAX_TEAMS_PER_DIVISION ? <>
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
					null
				}</> :
				null
			}
			
			<div className="cl_structure_err cl_structure_err_teams">{props.showError ? teamsErr : ""}</div>
		</div>
	);
}

// LEAGUE OPTIONS

function LeagueOptions(props: {state: LeagueOptionsState, dispatch: React.Dispatch<OptionsReducerActions>, showError: boolean}) {
	return (
		<div className="cl_option_main">
			<div className="cl_option_column">
				<NumberInput title="Number of games per series" value={props.state.games_series} setValue={(value: string) => 
					props.dispatch({type: 'set_games_series', value: value})} showError={props.showError}/>
				<NumberInput title="Number of teams from top of division to postseason" value={props.state.top_postseason} setValue={(value: string) => 
					props.dispatch({type: 'set_top_postseason', value: value})} showError={props.showError}/>
				<NumberInput title="Number of wildcards" value={props.state.wildcards} minValue={0} setValue={(value: string) => 
					props.dispatch({type: 'set_wildcards', value: value})} showError={props.showError}/>
			</div>
			<div className="cl_option_column">
				<NumberInput title="Number of series with each division opponent" value={props.state.intra_division_series} setValue={(value: string) => 
					props.dispatch({type: 'set_intra_division_series', value: value})} showError={props.showError}/>
				<NumberInput title="Number of inter-divisional series" value={props.state.inter_division_series} setValue={(value: string) => 
					props.dispatch({type: 'set_inter_division_series', value: value})} showError={props.showError}/>
				<NumberInput title="Number of inter-league series" value={props.state.inter_league_series} setValue={(value: string) => 
					props.dispatch({type: 'set_inter_league_series', value: value})} showError={props.showError}/>
			</div>
		</div>
	);
}

function NumberInput(props: {title: string, value: string, setValue: (newVal: string) => void, showError: boolean, minValue? : number}) {
	let minValue = 1;
	if (props.minValue !== undefined) { 
		minValue = props.minValue
	}
	return (
		<div className="cl_option_box">
			<div className="cl_option_label">{props.title}</div>
			<input className="cl_option_input" type="number" min={minValue} value={props.value} onChange={e => props.setValue(e.target.value)}/>
			<div className="cl_option_err">{(isNaN(Number(props.value)) || Number(props.value) < minValue) && props.showError ? "Must be a number greater than " + minValue : ""}</div>
		</div>
	);
}

export default CreateLeague;