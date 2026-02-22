import sqlite3

class GameStatistics:
    def __init__(self, db_name='game_stats.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS players (
                                    player_id INTEGER PRIMARY KEY,
                                    player_name TEXT NOT NULL
                                )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS matches (
                                    match_id INTEGER PRIMARY KEY,
                                    match_date TEXT NOT NULL
                                )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS match_players (
                                    match_player_id INTEGER PRIMARY KEY,
                                    match_id INTEGER,
                                    player_id INTEGER,
                                    FOREIGN KEY (match_id) REFERENCES matches (match_id),
                                    FOREIGN KEY (player_id) REFERENCES players (player_id)
                                )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS action_logs (
                                    log_id INTEGER PRIMARY KEY,
                                    match_player_id INTEGER,
                                    action TEXT NOT NULL,
                                    action_time TEXT NOT NULL,
                                    FOREIGN KEY (match_player_id) REFERENCES match_players (match_player_id)
                                )''')

    def add_player(self, player_name):
        with self.conn:
            self.conn.execute('INSERT INTO players (player_name) VALUES (?)', (player_name,))

    def record_match(self, match_date):
        with self.conn:
            self.conn.execute('INSERT INTO matches (match_date) VALUES (?)', (match_date,))

    def add_match_player(self, match_id, player_id):
        with self.conn:
            self.conn.execute('INSERT INTO match_players (match_id, player_id) VALUES (?, ?)', (match_id, player_id))

    def log_action(self, match_player_id, action):
        action_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        with self.conn:
            self.conn.execute('INSERT INTO action_logs (match_player_id, action, action_time) VALUES (?, ?, ?)', (match_player_id, action, action_time))

    def close(self):
        self.conn.close()

# Example usage:
# stats = GameStatistics()
# stats.add_player('John Doe')
# stats.record_match('2026-02-22')
# stats.add_match_player(1, 1)
# stats.log_action(1, 'Player scored')
# stats.close()