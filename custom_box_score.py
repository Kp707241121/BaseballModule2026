
from espn_api.baseball.box_score import H2HCategoryBoxScore as BaseH2HCategoryBoxScore

# Extended stat mapping
STATS_MAP = {
    20: 'R',
    5: 'HR',
    21: 'RBI',
    17: 'OBP',
    18: 'OPS',
    23: 'SB',
    48: 'K',
    63: 'QS', # Quality Starts
    57: 'SV',
    47: 'ERA',
    41: 'WHIP',
    45: 'ER',     # Needed for ERA
    39: 'P_BB',   # Needed for WHIP
    37: 'P_H',    # Needed for WHIP
    34: 'OUTS'    # Needed for ERA (to calculate IP)
}

class H2HCategoryBoxScore(BaseH2HCategoryBoxScore):
    def __init__(self, data, pro_schedule, year, scoring_period=0):
        print("Using custom H2HCategoryBoxScore")
        super().__init__(data, pro_schedule, year, scoring_period)

    def _process_team(self, team_data, is_home_team):
        super()._process_team(team_data, is_home_team)

        team_stats = {}

        if team_data:
            score_by_stat = team_data.get("cumulativeScore", {}).get("scoreByStat", {})
            for stat_id_str, result in score_by_stat.items():
                stat_id = int(stat_id_str)
                stat_name = STATS_MAP.get(stat_id)
                if stat_name:
                    team_stats[stat_name] = {
                        "value": result.get("score"),
                        "result": result.get("result")
                    }

            # Derived stats: ERA and WHIP based on raw components
            try:
                er = float(score_by_stat.get("45", {}).get("score", 0))
                outs = float(score_by_stat.get("34", {}).get("score", 0))
                ip = outs / 3 if outs > 0 else 0
                era = round((er * 9) / ip, 3) if ip else 0
                team_stats['ERA'] = {"value": era, "result": team_stats.get('ERA', {}).get('result')}
            except Exception:
                team_stats['ERA'] = {"value": 0, "result": 'N/A'}

            try:
                walks = float(score_by_stat.get("39", {}).get("score", 0))
                hits = float(score_by_stat.get("37", {}).get("score", 0))
                whip = round((walks + hits) / ip, 3) if ip else 0
                team_stats['WHIP'] = {"value": whip, "result": team_stats.get('WHIP', {}).get('result')}
            except Exception:
                team_stats['WHIP'] = {"value": 0, "result": 'N/A'}

        if is_home_team:
            self.home_stats = team_stats
        else:
            self.away_stats = team_stats
