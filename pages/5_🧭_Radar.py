
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

# --- Constants ---
STAT_ORDER = ['R', 'HR', 'RBI', 'OBP', 'SB', 'K', 'QS', 'SV', 'ERA', 'WHIP']
INVERT_STATS = {'ERA', 'WHIP'}

from week   import compute_week_stats
from season import compute_season_stats

mode = st.radio("Stats for…", ["Season","Week"], horizontal=True)
compute_fn = compute_week_stats if mode=="Week" else compute_season_stats

# --- Page Title ---
st.title("🧭 Team Stat Radar Charts")

# --- Load and Normalize Cached Stats ---
@st.cache_data
def load_team_df(selected_mode: str) -> pd.DataFrame:
    """
    Pulls from week.py or season.py based on selected_mode,
    returns a DataFrame indexed by Team, with columns STAT_ORDER.
    """
    fn   = compute_week_stats if selected_mode=="Week" else compute_season_stats
    data = fn()
    df   = pd.DataFrame.from_dict(data, orient="index")
    df.index.name = "Team"
    # reorder columns
    return df[STAT_ORDER]

# load data
df_stats = load_team_df(mode)

# --- Display Data Table ---
scaler = MinMaxScaler()
df_normalized = pd.DataFrame(
    scaler.fit_transform(df_stats),
    columns=STAT_ORDER,
    index=df_stats.index
)

# Invert ERA & WHIP
for stat in INVERT_STATS:
    if stat in df_normalized.columns:
        df_normalized[stat] = 1 - df_normalized[stat]

# --- Multi-Team Radar ---
st.subheader("📡 Multi-Team Radar")

teams_selected = st.multiselect("Select Teams", df_normalized.index, default=[df_normalized.index[0]])

if teams_selected:
    df_long = df_normalized.loc[teams_selected].reset_index().melt(
        id_vars='Team', var_name='Stat', value_name='Value'
    )

    fig_multi = px.line_polar(
        df_long,
        r='Value',
        theta='Stat',
        color='Team',
        line_close=True,
        title="Team Comparison Radar (Normalized)",
        color_discrete_sequence=px.colors.qualitative.D3,
        
    )

    fig_multi.update_traces(
        fill='toself'
    )
    
    st.plotly_chart(fig_multi)

else:
    st.warning("Please select at least one team to display the radar chart.")

# --- Single-Team Radar ---
st.subheader("🎯 Single-Team Radar")

team_selected = st.selectbox("Select Team", df_normalized.index)

fig_single = px.line_polar(
    r=df_normalized.loc[team_selected][STAT_ORDER],
    theta=STAT_ORDER,
    line_close=True,
    title=f"{team_selected} Stat Radar (Normalized)",
    color_discrete_sequence=px.colors.qualitative.D3
)

fig_single.update_traces(
    fill='toself'
)
st.plotly_chart(fig_single)