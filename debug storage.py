def large_scale_debug(): #massive debug, goes in games.py
    average_player = player('{"id" : "average", "name" : "average", "batting_stars" : 2.5, "pitching_stars" : 2.5, "defense_stars" : 2.5, "baserunning_stars" : 2.5}')
    max_player = player('{"id" : "max", "name" : "max", "batting_stars" : 5, "pitching_stars" : 5, "defense_stars" : 5, "baserunning_stars" : 5}')
    min_player = player('{"id" : "min", "name" : "min", "batting_stars" : 1, "pitching_stars" : 1, "defense_stars" : 1, "baserunning_stars" : 1}')
    team_avg = team()
    team_avg.add_lineup(average_player)
    team_avg.set_pitcher(average_player)
    team_avg.finalize()
    team_max = team()
    team_max.add_lineup(max_player)
    team_max.set_pitcher(max_player)
    team_max.finalize()
    team_min = team()
    team_min.add_lineup(min_player)
    team_min.set_pitcher(min_player)
    team_min.finalize()

    average_game = game(team_avg, team_avg)
    slugging_game = game(team_max, team_min)
    shutout_game = game(team_min, team_max)

    hit_count_avg = 0
    walk_count_avg = 0
    home_run_avg = 0
    so_avg = 0
    fo_avg = 0
    go_avg = 0
    for i in range(0,10000):
        ab = average_game.at_bat()
        if ab["ishit"]:
            hit_count_avg += 1
            if ab["text"] == appearance_outcomes.homerun:
                home_run_avg += 1
        elif ab["text"] == appearance_outcomes.walk:
            walk_count_avg += 1
        elif ab["text"] == appearance_outcomes.strikeoutlooking or ab["text"] == appearance_outcomes.strikeoutswinging:
            so_avg += 1
        elif ab["text"] == appearance_outcomes.groundout:
            go_avg += 1
        elif ab["text"] == appearance_outcomes.flyout:
            fo_avg += 1
    
    hit_count_slg = 0
    walk_count_slg = 0
    home_run_slg = 0
    fo_slg = 0
    go_slg = 0
    so_slg = 0
    for i in range(0,10000):
        ab = slugging_game.at_bat()
        if ab["ishit"]:
            hit_count_slg += 1
            if ab["text"] == appearance_outcomes.homerun:
                home_run_slg += 1
        elif ab["text"] == appearance_outcomes.walk:
            walk_count_slg += 1
        elif ab["text"] == appearance_outcomes.strikeoutlooking or ab["text"] == appearance_outcomes.strikeoutswinging:
            so_slg += 1
        elif ab["text"] == appearance_outcomes.groundout:
            go_slg += 1
        elif ab["text"] == appearance_outcomes.flyout:
            fo_slg += 1

    hit_count_sht = 0
    walk_count_sht = 0
    home_run_sht = 0
    go_sht = 0
    fo_sht = 0
    so_sht = 0
    for i in range(0,10000):
        ab = shutout_game.at_bat()
        if ab["ishit"]:
            hit_count_sht += 1
            if ab["text"] == appearance_outcomes.homerun:
                home_run_sht += 1
        elif ab["text"] == appearance_outcomes.walk:
            walk_count_sht += 1
        elif ab["text"] == appearance_outcomes.strikeoutlooking or ab["text"] == appearance_outcomes.strikeoutswinging:
            so_sht += 1
        elif ab["text"] == appearance_outcomes.groundout:
            go_sht += 1
        elif ab["text"] == appearance_outcomes.flyout:
            fo_sht += 1
    
            
    return (hit_count_avg, walk_count_avg, hit_count_slg, walk_count_slg, hit_count_sht, walk_count_sht, home_run_avg, home_run_slg, home_run_sht, so_avg, so_slg, so_sht, go_avg, go_slg, go_sht, fo_avg, fo_slg, fo_sht)


#    massive debug function, companion to above. goes in the_prestige
#    elif command == "testabs":
#        result = games.large_scale_debug()
#        await msg.channel.send(f"over 10000 atbats, average player vs average pitcher achieved avg {(result[0]/(10000-result[1]))} and walk rate {result[1]/10000}.")
#        await msg.channel.send(f"over 10000 atbats, max player vs min pitcher achieved avg {(result[2]/(10000-result[3]))} and walk rate {result[3]/10000}.")
#        await msg.channel.send(f"over 10000 atbats, min player vs max pitcher achieved avg {(result[4]/(10000-result[5]))} and walk rate {result[5]/10000}.")
#        await msg.channel.send(f"""there were {result[6]}, {result[7]}, and {result[8]} home runs, respectively.
#        there were {result[9]}, {result[10]}, and {result[11]} strikeouts, respectively.
#        there were {result[12]}, {result[13]}, and {result[14]} groundouts, respectively.
#        there were {result[15]}, {result[16]}, and {result[17]} flyouts, respectively.""")
