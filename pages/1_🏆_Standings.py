import streamlit as st
import pandas as pd

from leagueManager import LeagueManager
from manualmatchup import Scores
from espn_api.baseball import League


# Force ESPN matchups to use your patched Scores class
League._matchup_class = Scores


# -----------------------------
# League Config
# -----------------------------
CURRENT_LEAGUE_ID = 393414923
CURRENT_YEAR = 2026

HISTORICAL_LEAGUE_ID = 121531
HISTORICAL_YEARS = [2025, 2024, 2023]


# -----------------------------
# Initialize Current League
# -----------------------------
manager = LeagueManager(league_id=CURRENT_LEAGUE_ID, year=CURRENT_YEAR)
league = manager.get_league()


# -----------------------------
# Current Standings
# -----------------------------
st.header("🏆 League Standings")

standings = league.standings()

if standings:
    records = [(team.wins + team.ties / 2) for team in standings]
    max_record = max(records)

    df_standings = pd.DataFrame([
        {
            "Overall": idx + 1,
            "Team": team.team_name.strip(),
            "Wins": team.wins,
            "Losses": team.losses,
            "Ties": team.ties,
            "GB": round(max_record - (team.wins + team.ties / 2), 1)
        }
        for idx, team in enumerate(standings)
    ])

    st.dataframe(
        df_standings,
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("No standings data returned.")


# -----------------------------
# Historical Final Standings
# -----------------------------
def get_top3_for_year(league_id: int, year: int):
    manager = LeagueManager(league_id=league_id, year=year)
    historical_league = manager.get_league()

    top3 = sorted(
        [team for team in historical_league.teams if team.final_standing > 0],
        key=lambda t: t.final_standing
    )[:3]

    return {
        "📆 Year": year,
        "🏅 1st Place": top3[0].team_name.strip() if len(top3) > 0 else None,
        "🥈 2nd Place": top3[1].team_name.strip() if len(top3) > 1 else None,
        "🥉 3rd Place": top3[2].team_name.strip() if len(top3) > 2 else None,
    }


st.header("👑 Final Standings")

standings_summary = [
    get_top3_for_year(league_id=HISTORICAL_LEAGUE_ID, year=year)
    for year in HISTORICAL_YEARS
]

df_summary = pd.DataFrame(standings_summary)

st.dataframe(
    df_summary,
    use_container_width=True,
    hide_index=True
)


# -----------------------------
# Schedule Viewer
# -----------------------------
st.header("📅 Team Schedule Viewer")

team_names = [team.team_name.strip() for team in league.teams]

selected_team_name = st.selectbox(
    "Select a team to view schedule:",
    team_names
)

selected_team = next(
    team for team in league.teams
    if team.team_name.strip() == selected_team_name
)

schedule_data = []

for week_number, matchup in enumerate(selected_team.schedule, start=1):
    if matchup.home_team == selected_team:
        opponent = matchup.away_team
        location = "Home"
        score = matchup.home_team_live_score
        opponent_score = matchup.away_team_live_score
    else:
        opponent = matchup.home_team
        location = "Away"
        score = matchup.away_team_live_score
        opponent_score = matchup.home_team_live_score

    opponent_name = opponent.team_name.strip() if opponent else "BYE"

    schedule_data.append({
        "Week": week_number,
        "Location": location,
        "Opponent": opponent_name,
        "Score": score,
        "Opponent Score": opponent_score
    })


df_schedule = pd.DataFrame(schedule_data).sort_values(by="Week")


def get_result(row):
    score = row["Score"]
    opponent_score = row["Opponent Score"]

    if pd.isna(score) or pd.isna(opponent_score):
        return "Pending"

    if score > opponent_score:
        return "W"

    if score < opponent_score:
        return "L"

    return "T"


df_schedule["Result"] = df_schedule.apply(get_result, axis=1)

st.dataframe(
    df_schedule,
    use_container_width=True,
    hide_index=True
)