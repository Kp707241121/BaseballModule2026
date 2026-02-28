# common_stats.py

from collections import OrderedDict

def compute_team_stats(league, *, periods, stat_order, avg_stats):
    """
    Compute cumulative team stats for the given league and periods.

    :param league:      League object
    :param periods:     iterable of matchup_period ints
    :param stat_order:  list of stats to include in final output
    :param avg_stats:   set of stats to average rather than sum
    :return:            OrderedDict { team_name: {stat: value, …}, … }
    """
    # 1) Raw accumulators
    team_stats     = {}
    matchup_counts = {}

    # 2) Fetch & accumulate each period’s box scores
    for period in periods:
        box_scores = league.box_scores(matchup_period=period)
        for box in box_scores:
            for team_obj, stats in [(box.home_team, box.home_stats),
                                     (box.away_team, box.away_stats)]:
                if not team_obj or not stats:
                    continue

                name = team_obj.team_name
                if name not in team_stats:
                    # initialize all requested stats to zero
                    team_stats[name] = {st: 0 for st in stat_order}
                    # buckets for ERA/WHIP intermediates
                    team_stats[name].update({'ER':0, 'P_BB':0, 'P_H':0, 'OUTS':0})
                    matchup_counts[name] = 0

                matchup_counts[name] += 1

                for stat, data in stats.items():
                    value = data['value']
                    if value is None:
                        continue
                    try:
                        value = float(value)
                    except (TypeError, ValueError):
                        print(f"⚠️ Skipping non-numeric stat '{stat}' with value: {value} for {name}")
                        continue

                    if stat in team_stats[name]:
                        team_stats[name][stat] += value
                    elif stat in {'ER', 'P_BB', 'P_H', 'OUTS'}:
                        team_stats[name][stat] += value

    # Format and normalize
    ordered_output = OrderedDict()
    for team, stats in sorted(team_stats.items()):
        count = matchup_counts[team]
        updated_stats = {}

        ip = stats['OUTS'] / 3 if stats['OUTS'] else 0
        era = round((stats['ER'] * 9 / ip), 3) if ip else 0
        whip = round(((stats['P_BB'] + stats['P_H']) / ip), 3) if ip else 0

        for stat in stat_order:
            if stat == 'ERA':
                updated_stats['ERA'] = era
            elif stat == 'WHIP':
                updated_stats['WHIP'] = whip
            elif stat in avg_stats:
                updated_stats[stat] = round(stats[stat] / count, 3) if count else 0
            else:
                updated_stats[stat] = int(stats.get(stat, 0))

        ordered_output[team] = updated_stats

    return ordered_output                        