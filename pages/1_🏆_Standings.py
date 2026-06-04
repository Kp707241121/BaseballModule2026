import streamlit as st
import pandas as pd
from leagueManager import LeagueManager
from teams import Team
from manualmatchup import Scores# ✅ Use your custom Matchup subclass
# Inject your patched Scores logic into ESPN League
from espn_api.baseball import League
League._matchup_class = Scores  # ✅ Force all matchups to use your patched class

# --- Init league ---

manager = LeagueManager(league_id=393414923, year=2026)
league = manager.get_league()

# --- Standings ---
st.header("🏆 League Standings")
standings = league.standings()
records = [(team.wins + team.ties / 2) for team in standings]
max_record = max(records)

logo_map = {
    team.team_name.strip(): team.logo_url
    for team in league.teams
}

df_standings = pd.DataFrame([{
    "Overall": idx + 1,
    "Logo": logo_map.get(team.team_name.strip(), team.logo_url),
    "Team": team.team_name.strip(),
    "Wins": team.wins,
    "Losses": team.losses,
    "Ties": team.ties,
    "GB": round(max_record - (team.wins + team.ties / 2), 1)
} for idx, team in enumerate(standings)])

st.dataframe(
    df_standings,
    column_config={
        "Logo": st.column_config.ImageColumn("Team Logo", width="small")
        },
    hide_index=True,
    use_container_width=True)

# --- final Standings ---
def get_top3_for_year(league_id: int, year: int):
    manager = LeagueManager(league_id=league_id, year=year)
    league = manager.get_league()
    top3 = sorted(
        [team for team in league.teams if team.final_standing > 0],
        key=lambda t: t.final_standing
    )[:3]
    return {
        "📆 Year": year,
        "🏅 1st Place": top3[0].team_name if len(top3) > 0 else None,
        "🥈 2nd Place": top3[1].team_name if len(top3) > 1 else None,
        "🥉 3rd Place": top3[2].team_name if len(top3) > 2 else None,
    }

# Collect data for multiple years
standings_summary = [
    get_top3_for_year(league_id=121531, year=2025),
    get_top3_for_year(league_id=121531, year=2024),
    get_top3_for_year(league_id=121531, year=2023)
]

# Create a DataFrame
df_summary = pd.DataFrame(standings_summary)

# Display in Streamlit
st.header("👑 Final Standings")
st.dataframe(df_summary, use_container_width=True, hide_index=True)


# --- Schedule ---

st.header("📅 Team Schedule Viewer")
schedule_data = []

team_names = [team.team_name.strip() for team in league.teams]
selected_team_name = st.selectbox("Select a team to view schedule:", team_names)
selected_team = next(team for team in league.teams if team.team_name.strip() == selected_team_name)

for week_number, matchup in enumerate(selected_team.schedule, start=1):
    if matchup.home_team == selected_team:
        opponent = matchup.away_team
        location = "Home"
        score = matchup.home_team_live_score
        opp_score = matchup.away_team_live_score
    else:
        opponent = matchup.home_team
        location = "Away"
        score = matchup.away_team_live_score
        opp_score = matchup.home_team_live_score

    opponent_name = opponent.team_name.strip() if opponent else "BYE"

    schedule_data.append({
        "Week": week_number,
        "Location": location,
        "Opponent": opponent_name,
        "Score": score,
        "OpponentScore": opp_score
    })

df = pd.DataFrame(schedule_data).sort_values(by="Week")

def get_result(row):
    if pd.isna(row["Score"]) or pd.isna(row["OpponentScore"]):
        return "Pending"
    if row["Score"] > row["OpponentScore"]:
        return "W"
    if row["Score"] < row["OpponentScore"]:
        return "L"
    return "T"

df["Result"] = df.apply(get_result, axis=1)

st.dataframe(df, use_container_width=True, hide_index=True)
