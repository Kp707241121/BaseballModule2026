import streamlit as st
from leagueManager import LeagueManager
from teams import Team
import json
import datetime
import pandas as pd
    
# --- Load team ID → Name mapping ---
with open("teams.json", "r") as f:
    team_dict = json.load(f)

# --- Connect to League ---
manager = LeagueManager(league_id=393414923, year=2026)
league = manager.get_league()

# --- Helper: Map team_id to team_index ---
def get_team_index_by_id(league, team_id):
    for i, team in enumerate(league.teams):
        if team.team_id == team_id:
            return i
    raise ValueError(f"Team ID '{team_id}' not found in league.")

# --- Build team rosters ---
team_rosters = {}
for team_id_str, team_name in team_dict.items():
    try:
        team_id = int(team_id_str)
        team_index = get_team_index_by_id(league, team_id)
        team = Team(league, team_index)
        players = team.get_roster()
        team_rosters[team_name] = [
            {"Player": p["name"], "Position": p.get("position", "")}
            for p in players
        ]
    except Exception as e:
        st.warning(f"⚠️ Skipping {team_name}: {e}")

# --- UI: Select team ---
selected_team = st.selectbox("Select a team", sorted(team_rosters))

# --- Display Roster ---
if selected_team:
    df_roster = pd.DataFrame(team_rosters[selected_team])
    st.subheader(f"📋 Roster for {selected_team}")
    st.dataframe(df_roster[["Player", "Position"]], use_container_width=True, hide_index=True)

# --- Recent League Activity ---
activities = league.recent_activity(size=100)

# --- Normalize action types ---
ACTION_MAP = {
    "FA ADDED": "Add",
    "WAIVER ADDED": "Add",
    "DROPPED": "Drop"
}

seen = set()
activity_rows = []

for activity in activities:
    try:
        timestamp = int(str(activity.date)[:13])
        date_str = datetime.datetime.fromtimestamp(timestamp / 1000.0).strftime("%m-%d-%Y")
    except:
        date_str = "Unknown"

    for team, action, player in activity.actions:
        team_name = getattr(team, "team_name", str(team)).replace("Team(", "").replace(")", "")
        if team_name != selected_team:
            continue

        player_name = getattr(player, "name", str(player))
        simplified_action = ACTION_MAP.get(action)
        if not simplified_action:
            continue

        key = (date_str, simplified_action, player_name)
        if key not in seen:
            seen.add(key)
            activity_rows.append({
                "Date": date_str,
                "Team": team_name,
                "Action": simplified_action,
                "Player": player_name
            })

# --- Display Activity Tables ---
df_activity = pd.DataFrame(activity_rows)

st.subheader("🟢 Added Players")
df_add = df_activity[df_activity["Action"] == "Add"]
if not df_add.empty:
    st.dataframe(df_add[["Date", "Team", "Player"]].sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("No recent players added.")

st.subheader("🔴 Dropped Players")
df_drop = df_activity[df_activity["Action"] == "Drop"]
if not df_drop.empty:
    st.dataframe(df_drop[["Date", "Team", "Player"]].sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("No recent players dropped.")
