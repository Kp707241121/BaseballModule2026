# season.py
from common_stats   import compute_team_stats
from leagueManager  import LeagueManager

STAT_ORDER    = ['R','HR','RBI','OBP','SB','K','W','SV','ERA','WHIP']
AVERAGE_STATS = {'OBP'}

def compute_season_stats():
    manager    = LeagueManager(league_id=121531, year=2025)
    league     = manager.get_league()
    max_period = league.currentMatchupPeriod

    return compute_team_stats(
        league=league,
        periods=list(range(1, max_period + 1)),
        stat_order=STAT_ORDER,
        avg_stats=AVERAGE_STATS
    )
