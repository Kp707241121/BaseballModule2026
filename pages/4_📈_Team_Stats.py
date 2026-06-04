import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from leagueManager import LeagueManager
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

# import both flavors
from week   import compute_week_stats
from season import compute_season_stats
# --- Constants ---
STAT_ORDER     = ['R','HR','RBI','OBP','OPS', 'SB','K','QS','SV','ERA','WHIP']
FORMAT_RED     = {'R','HR','RBI','OBP','OPS', 'SB','K','QS','SV'}
ASCENDING_STATS= {'ERA','WHIP'}
FLOAT_COLS     = {'OBP','OPS', 'ERA','WHIP'}
FORMAT_DICT    = {s:"{:.3f}" if s in FLOAT_COLS else "{:.0f}" 
                  for s in STAT_ORDER}


# --- Highlight Function ---
def highlight_rank(col):
    if col.name not in FORMAT_RED | ASCENDING_STATS:
        return [''] * len(col)

    values = col.astype(float)
    ascending = col.name in ASCENDING_STATS
    ranks = values.rank(ascending=ascending, method='min')

    cmap = cm.get_cmap('RdYlBu')
    norm = mcolors.Normalize(vmin=1, vmax=10)

    styles = []
    for rank in ranks:
        rank = int(rank)
        if rank in [5, 6]:
            hex_color = '#ffffff'
            font_color = 'black'
        else:
            rgba = cmap(norm(rank))
            hex_color = mcolors.to_hex(rgba)
            font_color = 'white' if rank == 3 or (rgba[0]*0.299 + rgba[1]*0.587 + rgba[2]*0.114) < 0.5 else 'black'
        styles.append(f'background-color: {hex_color}; color: {font_color}; border: 1px solid black')
    return styles

# --- Page Title ---
st.title("📈 Accumulated Team Stats")

# allow user to choose “Week” vs “Season”
mode = st.radio("Stats for…", ["Season","Week"], horizontal=True)
compute_fn = compute_week_stats if mode=="Week" else compute_season_stats

# Refresh button
if st.button("🔄 Refresh"):
    with st.spinner("Recomputing team stats..."):
        st.cache_data.clear()
        st.rerun()

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

# --- Table ---
st.subheader(f"📋 {mode}ly Team Stat Table")
st.dataframe(
    df_stats.style
        .format(FORMAT_DICT)
        .apply(highlight_rank, axis=0),
    use_container_width=True
)

# --- Logos (unchanged) ---
manager = LeagueManager(league_id=393414923, year=2026)
league  = manager.get_league()
logo_map= {t.team_name:t.logo_url for t in league.teams}

# --- Bar chart ---
st.subheader("📊 Bar Chart Comparison")
stat_bar    = st.selectbox("Bar:", STAT_ORDER, key="bar")
asc_bar     = stat_bar in ASCENDING_STATS
df_bar      = df_stats.sort_values(stat_bar, ascending=asc_bar)

fig1, ax1 = plt.subplots(figsize=(12,6))
bars     = ax1.bar(df_bar.index, df_bar[stat_bar], color='darkblue')
ax1.set_title(f"{mode} {stat_bar}")
ax1.set_xticklabels(df_bar.index, rotation=45)
for b in bars:
    h    = b.get_height()
    fmt  = FORMAT_DICT[stat_bar].format(h)
    off  = (df_bar[stat_bar].max()-df_bar[stat_bar].min())*0.01 or 0.1
    ax1.text(b.get_x()+b.get_width()/2, h+off, fmt,
             ha='center', va='bottom')
st.pyplot(fig1)

# --- Line Chart ---
st.subheader("📈 Line Chart Comparison")
selected_line_stat = st.selectbox("Choose a stat for line chart", STAT_ORDER, key="line_chart")
line_ascending = selected_line_stat in ASCENDING_STATS
df_sorted_line = df_stats.sort_values(by=selected_line_stat, ascending=line_ascending)

fig_line, ax_line = plt.subplots(figsize=(12, 6))
ax_line.plot(df_sorted_line.index, df_sorted_line[selected_line_stat], marker='o', color='darkblue')
ax_line.set_title(f"{mode} {selected_line_stat}")
ax_line.set_xlabel("Team")
ax_line.set_ylabel(selected_line_stat)
plt.xticks(rotation=45)

st.pyplot(fig_line)

# --- Radar Chart ---
st.subheader("📊 Normalized Stat Comparison (Radar Style)")

scaler = MinMaxScaler()
df_normalized = pd.DataFrame(
    scaler.fit_transform(df_stats),
    columns=df_stats.columns,
    index=df_stats.index
)

for stat in ASCENDING_STATS:
    if stat in df_normalized.columns:
        df_normalized[stat] = 1 - df_normalized[stat]

df_melted = df_normalized.reset_index().melt(id_vars="Team", var_name="Stat", value_name="Value")

fig_radar = px.line(
    df_melted,
    x="Stat",
    y="Value",
    color="Team",
    line_group="Team",
    markers=True,
    title="Normalized Stat Comparison Across Teams"
)
st.plotly_chart(fig_radar)