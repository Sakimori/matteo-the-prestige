SELECT name, 
	plate_appearances - (walks_taken + sacrifices) as atbats, 
	ROUND(hits*1.0 / (plate_appearances - (walks_taken + sacrifices)*1.0),3) as average,
	ROUND(total_bases*1.0 / (plate_appearances - (walks_taken + sacrifices)*1.0),3) as slg,
	ROUND((walks_taken + hits)*1.0/plate_appearances*1.0,3) as obp,
	ROUND((walks_taken + hits)*1.0/plate_appearances*1.0,3) + ROUND(total_bases*1.0 / (plate_appearances - (walks_taken + sacrifices)*1.0),3) as ops
FROM stats WHERE plate_appearances > 50
ORDER BY ops DESC;