SELECT name, team_name,
	outs_pitched,
	ROUND(runs_allowed*27.0/(outs_pitched*1.0),3) as era,
	ROUND((walks_allowed+hits_allowed)*3.0/(outs_pitched*1.0),3) as whip,
	ROUND(walks_allowed*27.0/(outs_pitched*1.0),3) as bbper9,
	ROUND(strikeouts_given*27.0/(outs_pitched*1.0),3) as kper9,
	ROUND(strikeouts_given*1.0/walks_allowed*1.0,3) as kperbb
FROM stats WHERE outs_pitched > 150
ORDER BY kperbb ASC;