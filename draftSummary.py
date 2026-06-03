# modules/draft_summary.py
from collections import defaultdict
import json
from espn_api.baseball.league import League as lg
from leagueManager import LeagueManager

def get_draft_summary(league_id=393414923, year=2026):
    manager = LeagueManager(league_id=league_id, year=year)
    d = lg(league_id=league_id, year=year, espn_s2=manager.espn_s2, swid=manager.swid)

    # Player ID → Name
    player_map = {}
    for team in d.teams:
        for player in team.roster:
            player_map[player.playerId] = player.name
    for player in d.free_agents(size=500):
        player_map[player.playerId] = player.name

    # Team ID → Name
    team_map = {team.team_id: team.team_name for team in d.teams}

    # Load draft data
    raw_draft = d.espn_request.get_league_draft()
    if isinstance(raw_draft, str):
        raw_draft = json.loads(raw_draft)

    picks = raw_draft.get("draftDetail", {}).get("picks", [])
    draft_by_team = defaultdict(lambda: defaultdict(list))

    for pick in picks:
        team_id = pick.get("teamId")
        round_id = pick.get("roundId")
        draft_by_team[team_id][round_id].append(pick)

    # Format for Streamlit
    summary = {}
    for team_id, rounds in draft_by_team.items():
        team_name = team_map.get(team_id, f"Team {team_id}")
        summary[team_name] = {}
        for round_id, picks in rounds.items():
            summary[team_name][round_id] = [
                pick.get("playerName") or player_map.get(pick["playerId"], f"Player {pick['playerId']}")
                for pick in picks
            ]
    return summary
