from leagueManager import LeagueManager
from free_agents import FreeAgents

manager = LeagueManager(league_id=393414923, year=2026)
fa = FreeAgents(manager)

free_agents = fa.get_free_agents(size=5)

PITCHING_STATS = ['K', 'W', 'SV', 'ERA', 'WHIP']
HITTING_STATS = ['R', 'HR', 'RBI', 'OBP', 'SB']

for position, players in free_agents.items():
    print(f"\nPosition: {position}")
    for name, stats in players.items():
        print(f"  Name: {name}")
        relevant_stats = PITCHING_STATS if position in {"SP", "RP", "SP/RP"} else HITTING_STATS
        for stat in relevant_stats:
            print(f"    {stat}: {stats.get(stat, 0)}")
