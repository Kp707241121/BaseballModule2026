# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from leagueManager import LeagueManager
from week import compute_week_stats
import json

# --- Constants ---
STAT_ORDER     = ['R','HR','RBI','OBP','SB','K','QS','SV','ERA','WHIP']
FLOAT_COLS     = {'OBP','ERA','WHIP'}
FORMAT_DICT    = {s:"{:.3f}" if s in FLOAT_COLS else "{:.0f}" 
                  for s in STAT_ORDER}

# --- Your Team ID & Name Map ---
MY_TEAM_ID = 2
with open("teams.json","r") as f:
    TEAM_NAME_BY_ID = json.load(f)

# --- Connect to League once ---
manager = LeagueManager(league_id=121531, year=2025)
league  = manager.get_league()

# --- Find this week's opponent for your team ---
def get_matchup_pair(league, team_id):
    period = league.currentMatchupPeriod
    for box in league.box_scores(matchup_period=period):
        ht, at = box.home_team, box.away_team
        if ht and ht.team_id == team_id:
            return ht.team_name, at.team_name
        if at and at.team_id == team_id:
            return at.team_name, ht.team_name
    raise RuntimeError(f"No matchup found for team_id {team_id} in period {period}")

# --- Streamlit App ---
st.title("📈 This Week’s Head-to-Head Stats")

if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.experimental_rerun()

@st.cache_data
def load_my_matchup_df():
    # 1) Get the full-week stats
    data = compute_week_stats()             # note the ()!
    df   = pd.DataFrame.from_dict(data, orient="index")
    df.index.name = "Team"
    df   = df[STAT_ORDER]

    # 2) Determine which two teams to show
    my_name, opp_name = get_matchup_pair(league, MY_TEAM_ID)

    # 3) Filter to only those two rows
    df = df.loc[[my_name, opp_name]]
    return df, my_name, opp_name

# --- Load & Display ---
df_stats, my_name, opp_name = load_my_matchup_df()
st.dataframe(df_stats.style.format(FORMAT_DICT), use_container_width=True)

ip_values = [i/10 for i in range(1, 51)]  # 0.1 to 5.0 innings

# look up your ERA and WHIP from the two‐team df
my_era  = df_stats.loc[my_name, 'ERA']
my_whip = df_stats.loc[my_name, 'WHIP']



ip_values = list(range(1, 10))

# Compute fractional thresholds
df_thresholds = pd.DataFrame({
    'Innings Pitched': ip_values,
    'Max Runs Allowed (ERA < yours)': (pd.Series(ip_values) * my_era / 9).round(3),
    'Max (H + BB) Allowed (WHIP < yours)': (pd.Series(ip_values) * my_whip).round(3),
})



st.subheader("📊 Opponent Thresholds")
st.table(df_thresholds)

