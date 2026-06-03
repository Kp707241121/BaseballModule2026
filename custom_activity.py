from leagueManager import LeagueManager


# --- Init league ---
manager = LeagueManager(league_id=393414923, year=2026)
league = manager.get_league()

ACTIVITY_MAP = {
    "DROP": 239,
    "ADD": 178,
    "ADD2": 180,
    "TRADED": 244,
}

class Activity:
    def __init__(self, data, player_map, get_team_data):
        self.actions = []  # List of tuples: (Team, Action, Player)
        self.date = data['date']

        for msg in data['messages']:
            msg_id = msg.get('messageTypeId')
            if msg_id is None:
                continue

            if msg_id == 244:
                team = get_team_data(msg.get('from'))
            elif msg_id == 239:
                team = get_team_data(msg.get('for'))
            else:
                team = get_team_data(msg.get('to'))

            action = ACTIVITY_MAP.get(msg_id, "UNKNOWN")

            target_id = msg.get('targetId')
            player = player_map.get(target_id, "")

            if action != "UNKNOWN" and player:
                self.actions.append((team, action, player))

    def __repr__(self):
        return 'Activity(' + ' '.join("(%s, %s, %s)" % tup for tup in self.actions) + ')'
    

log = Activity()
print(log)

#date="2025-06-22", messages=[{"messageTypeId": 178, "messageTypeId": 180, "messageTypeId": 239, "messageTypeId": 244}])
