# week.py
from common_stats   import compute_team_stats
from leagueManager  import LeagueManager

STAT_ORDER    = ['R','HR','RBI','OBP','SB','K','W','SV','ERA','WHIP']
AVERAGE_STATS = {'OBP'}

def compute_week_stats():
    manager    = LeagueManager(league_id=121531, year=2025)
    league     = manager.get_league()
    max_period = league.currentMatchupPeriod

    # league is the one positional arg; the rest are keyword-only:
    return compute_team_stats(
        league=league,
        periods=[max_period],
        stat_order=STAT_ORDER,
        avg_stats=AVERAGE_STATS
    )
