import os
import json
from leagueManager import LeagueManager
from teams import Team

# Load saved team_id: team_name mapping
with open("teams.json", "r") as f:
    team_dict = json.load(f)

# Create output folder
output_dir = "rosters"
os.makedirs(output_dir, exist_ok=True)

# Connect to league
manager = LeagueManager(league_id=393414923, year=2026)
league = manager.get_league()

# Loop through each team using team_id directly
for team_id_str, team_name in team_dict.items():
    team_id = int(team_id_str)
    try:
        team = Team(league, team_id)
        roster_list = team.get_roster()  # Already returns a list of dicts

        # Clean filename
        safe_name = team_name.replace(" ", "_").replace("/", "_")
        file_path = os.path.join(output_dir, f"{safe_name}.json")

        # Save to JSON
        with open(file_path, "w") as f:
            json.dump(roster_list, f, indent=4)

        print(f"✅ Saved roster for '{team_name}' to {file_path}")

    except Exception as e:
        print(f"❌ Skipping {team_name}: {e}")

print("\n📋 Actual Teams in League:")
for t in league.teams:
    print(f"ID: {t.team_id} → {t.team_name}")

