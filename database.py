import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

dataclass
class PlayerStats:
    """Player statistics data class"""
    user_id: int
    username: str
    total_score: float = 0.0
    total_games: int = 0
    wins: int = 0
    civilian_score: float = 0.0
    doctor_score: float = 0.0
    detective_score: float = 0.0
    mafia_score: float = 0.0
    detective_mafia_found: int = 0
    detective_mafia_killed: int = 0
    doctor_saves: int = 0
    mafia_kills: int = 0

class Database:
    """Database manager for Mafia game"""
    
    def __init__(self, db_name: str = 'mafia_game.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Players stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                total_score REAL DEFAULT 0.0,
                total_games INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                civilian_score REAL DEFAULT 0.0,
                doctor_score REAL DEFAULT 0.0,
                detective_score REAL DEFAULT 0.0,
                mafia_score REAL DEFAULT 0.0,
                detective_mafia_found INTEGER DEFAULT 0,
                detective_mafia_killed INTEGER DEFAULT 0,
                doctor_saves INTEGER DEFAULT 0,
                mafia_kills INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Match history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_history (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                winning_team TEXT NOT NULL,
                players_data TEXT NOT NULL,
                game_log TEXT NOT NULL
            )
        ''')
        
        # Game actions log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_actions (
                action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                target_id INTEGER,
                action_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES match_history(match_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_or_create_player(self, user_id: int, username: str) -> PlayerStats:
        """Get or create player stats"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM player_stats WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            player = PlayerStats(
                user_id=row[0], username=row[1], total_score=row[2],
                total_games=row[3], wins=row[4], civilian_score=row[5],
                doctor_score=row[6], detective_score=row[7], mafia_score=row[8],
                detective_mafia_found=row[9], detective_mafia_killed=row[10],
                doctor_saves=row[11], mafia_kills=row[12]
            )
        else:
            cursor.execute(
                'INSERT INTO player_stats (user_id, username) VALUES (?, ?)',
                (user_id, username)
            )
            conn.commit()
            player = PlayerStats(user_id=user_id, username=username)
        
        conn.close()
        return player
    
    def update_player_stats(self, player_stats: PlayerStats):
        """Update player statistics"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE player_stats SET
                username = ?, total_score = ?, total_games = ?, wins = ?,
                civilian_score = ?, doctor_score = ?, detective_score = ?,
                mafia_score = ?, detective_mafia_found = ?,
                detective_mafia_killed = ?, doctor_saves = ?, mafia_kills = ?
            WHERE user_id = ?
        ''', (
            player_stats.username, player_stats.total_score, player_stats.total_games,
            player_stats.wins, player_stats.civilian_score, player_stats.doctor_score,
            player_stats.detective_score, player_stats.mafia_score,
            player_stats.detective_mafia_found, player_stats.detective_mafia_killed,
            player_stats.doctor_saves, player_stats.mafia_kills,
            player_stats.user_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_leaderboard(self, limit: int = 10) -> List[PlayerStats]:
        """Get top players by total score"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM player_stats
            ORDER BY total_score DESC
            LIMIT ?
        ''', (limit,))
        
        players = []
        for row in cursor.fetchall():
            players.append(PlayerStats(
                user_id=row[0], username=row[1], total_score=row[2],
                total_games=row[3], wins=row[4], civilian_score=row[5],
                doctor_score=row[6], detective_score=row[7], mafia_score=row[8],
                detective_mafia_found=row[9], detective_mafia_killed=row[10],
                doctor_saves=row[11], mafia_kills=row[12]
            ))
        
        conn.close()
        return players
    
    def save_match(self, server_id: int, players_data: Dict, game_log: List[str], winning_team: str) -> int:
        """Save match to history"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO match_history (server_id, winning_team, players_data, game_log, end_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            server_id,
            winning_team,
            json.dumps(players_data),
            json.dumps(game_log),
            datetime.now().isoformat()
        ))
        
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return match_id
    
    def log_action(self, match_id: int, user_id: int, action_type: str, target_id: Optional[int] = None, action_data: Optional[str] = None):
        """Log game action"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO game_actions (match_id, user_id, action_type, target_id, action_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (match_id, user_id, action_type, target_id, action_data))
        
        conn.commit()
        conn.close()
    
    def get_match_history(self, server_id: int, limit: int = 10) -> List[Dict]:
        """Get recent matches for server"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT match_id, start_time, end_time, winning_team, players_data, game_log
            FROM match_history
            WHERE server_id = ?
            ORDER BY start_time DESC
            LIMIT ?
        ''', (server_id, limit))
        
        matches = []
        for row in cursor.fetchall():
            matches.append({
                'match_id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'winning_team': row[3],
                'players': json.loads(row[4]),
                'log': json.loads(row[5])
            })
        
        conn.close()
        return matches
    
    def get_action_log(self, match_id: int) -> List[Dict]:
        """Get all actions for a match"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, action_type, target_id, action_data, timestamp
            FROM game_actions
            WHERE match_id = ?
            ORDER BY timestamp
        ''', (match_id,))
        
        actions = []
        for row in cursor.fetchall():
            actions.append({
                'user_id': row[0],
                'action_type': row[1],
                'target_id': row[2],
                'action_data': row[3],
                'timestamp': row[4]
            })
        
        conn.close()
        return actions