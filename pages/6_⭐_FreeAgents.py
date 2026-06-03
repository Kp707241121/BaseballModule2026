
import streamlit as st
import pandas as pd
import plotly.express as px
from leagueManager import LeagueManager
from free_agents import FreeAgents

# --- Constants ---
PITCHING_STATS = ['K', 'W', 'SV', 'ERA', 'WHIP']
HITTING_STATS = ['R', 'HR', 'RBI', 'OBP', 'SB']
INVERT_STATS = {'ERA', 'WHIP'}
HITTER_GROUPS = ["OF", "IF", "DH"]
PITCHER_GROUPS = ["SP", "RP"]
SPLIT_OPTIONS = {
    "Season": 0,
    "Last 7 Days": 1,
    "Last 15 Days": 2,
    "Last 30 Days": 3
}

# --- Load Free Agents ---
@st.cache_data
def load_agents(stat_split_type):
    manager = LeagueManager(league_id=393414923, year=2026)
    return FreeAgents(manager).get_free_agents(size=50, stat_split_type=stat_split_type)

# --- Normalize for Heatmap Color ---
def normalize(df, stat_keys):
    norm_df = df.copy()
    for stat in stat_keys:
        min_val, max_val = df[stat].min(), df[stat].max()
        norm_df[stat] = (df[stat] - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        if stat in INVERT_STATS:
            norm_df[stat] = 1 - norm_df[stat]
    return norm_df

# --- Flatten by Group ---
def flatten_group(data, pos_label, stat_keys):
    if pos_label not in data:
        return pd.DataFrame(), pd.DataFrame()
    rows = []
    for player, info in data[pos_label].items():
        row = {"Player": player}
        row.update({stat: info["stats"].get(stat, 0) for stat in stat_keys})
        rows.append(row)

    if not rows:
        print(f"⚠️ No rows found for {pos_label}. Check agent data or filters.")
    
    raw_df = pd.DataFrame(rows)

    if "Player" not in raw_df.columns:
        
        print(f"⚠️ 'Player' column missing. Data: {raw_df}")
    raw_df = raw_df.set_index("Player")
    norm_df = normalize(raw_df, stat_keys)
    return raw_df, norm_df

# --- UI ---
st.title("🧊 Free Agent Heatmap Comparison")

split_label = st.selectbox("Choose Stat Range", list(SPLIT_OPTIONS.keys()))
split_type = SPLIT_OPTIONS[split_label]
agents = load_agents(split_type)

# --- Hitters ---
st.subheader("📌 Hitters")
selected_hitter_group = st.selectbox("Select Hitter Group", HITTER_GROUPS)
selected_hitter_sort = st.selectbox("Sort Hitters By", HITTING_STATS, key="hitter_sort")

raw_hit, norm_hit = flatten_group(agents, selected_hitter_group, HITTING_STATS)
if not raw_hit.empty:
    raw_hit = raw_hit.sort_values(by=selected_hitter_sort, ascending=False)
    norm_hit = norm_hit.loc[raw_hit.index]  # keep same order

    fig_hit = px.imshow(
        norm_hit,
        color_continuous_scale="RdBu_r",
        aspect="auto",
        labels=dict(color="Normalized"),
        title=f"{selected_hitter_group} Heatmap (Sorted by {selected_hitter_sort})",
        zmin=0, zmax=1
    )

    st.plotly_chart(fig_hit, use_container_width=True)
else:
    st.info("No hitter data available.")

# --- Pitchers ---
st.subheader("📌 Pitchers")
selected_pitcher_group = st.selectbox("Select Pitcher Group", PITCHER_GROUPS)
selected_pitcher_sort = st.selectbox("Sort Pitchers By", PITCHING_STATS, key="pitcher_sort")

raw_pitch, norm_pitch = flatten_group(agents, selected_pitcher_group, PITCHING_STATS)
if not raw_pitch.empty:
    ascending = selected_pitcher_sort in INVERT_STATS
    raw_pitch = raw_pitch.sort_values(by=selected_pitcher_sort, ascending=ascending)
    norm_pitch = norm_pitch.loc[raw_pitch.index]

    fig_pitch = px.imshow(
        norm_pitch,
        color_continuous_scale="RdBu_r",
        aspect="auto",
        labels=dict(color="Normalized"),
        title=f"{selected_pitcher_group} Heatmap (Sorted by {selected_pitcher_sort})",
        zmin=0, zmax=1
    )
    st.plotly_chart(fig_pitch, use_container_width=True)
else:
    st.info("No pitcher data available.")
