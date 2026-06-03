import json
from leagueManager import LeagueManager

manager = LeagueManager(league_id=393414923, year=2026)
league = manager.get_league()

# Create correct mapping of current team IDs to team names
current_teams = {str(team.team_id): team.team_name for team in league.teams}

with open("teams.json", "w") as f:
    json.dump(current_teams, f, indent=4)

print("✅ Rebuilt teams.json with current team IDs:")
for tid, name in current_teams.items():
    print(f"ID: {tid} → {name}")
