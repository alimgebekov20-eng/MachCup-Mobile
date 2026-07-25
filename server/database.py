    import sqlite3
import json
import hashlib
from datetime import datetime

class Database:
    def __init__(self, db_path='football.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Таблица игроков
        c.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_online DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица статистики
        c.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                player_id INTEGER PRIMARY KEY,
                matches INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                goals_scored INTEGER DEFAULT 0,
                goals_conceded INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                total_rating INTEGER DEFAULT 50,
                base_rating INTEGER DEFAULT 50,
                crystals INTEGER DEFAULT 100,
                tournaments_won INTEGER DEFAULT 0,
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
        ''')
        
        # Таблица инвентаря скинов
        c.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                skin_name TEXT NOT NULL,
                slot_id INTEGER,  -- 1-5 для экипированных
                rarity TEXT NOT NULL,
                equipped BOOLEAN DEFAULT 0,
                unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
        ''')
        
        # Таблица паков
        c.execute('''
            CREATE TABLE IF NOT EXISTS packs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                pack_type TEXT NOT NULL,
                opened BOOLEAN DEFAULT 0,
                bought_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
        ''')
        
        # Таблица достижений
        c.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
        ''')
        
        # Таблица истории матчей
        c.execute('''
            CREATE TABLE IF NOT EXISTS match_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1_id INTEGER NOT NULL,
                player2_id INTEGER NOT NULL,
                player1_score INTEGER NOT NULL,
                player2_score INTEGER NOT NULL,
                result TEXT NOT NULL,
                stars_change INTEGER,
                match_type TEXT NOT NULL,
                played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player1_id) REFERENCES players(id),
                FOREIGN KEY(player2_id) REFERENCES players(id)
            )
        ''')
        
        # Таблица всех доступных скинов
        c.execute('''
            CREATE TABLE IF NOT EXISTS skins (
                name TEXT PRIMARY KEY,
                slot_id INTEGER NOT NULL,
                rarity TEXT NOT NULL,
                rating_bonus INTEGER DEFAULT 0,
                speed_bonus INTEGER DEFAULT 0,
                power_bonus INTEGER DEFAULT 0,
                accuracy_bonus INTEGER DEFAULT 0,
                defense_bonus INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Добавляем скины если их нет
        self.init_skins()
    
    def init_skins(self):
        """Инициализация таблицы скинов"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Проверяем есть ли скины
        c.execute('SELECT COUNT(*) FROM skins')
        count = c.fetchone()[0]
        
        if count == 0:
            skins = [
                # Слот 1: Голова
                ('Повязка', 1, 'common', 0, 1, 0, 0, 0),
                ('Бандана', 1, 'uncommon', 1, 3, 0, 0, 0),
                ('Шлем', 1, 'rare', 2, 5, 0, 0, 2),
                ('Корона', 1, 'epic', 5, 8, 0, 5, 0),
                ('Золотой шлем', 1, 'legendary', 8, 12, 0, 0, 8),
                ('Нимб бога', 1, 'mythic', 10, 20, 0, 10, 0),
                # Слот 2: Торс
                ('Майка', 2, 'common', 0, 0, 1, 0, 0),
                ('Футболка', 2, 'uncommon', 1, 0, 3, 0, 0),
                ('Броня', 2, 'rare', 2, 0, 5, 0, 2),
                ('Латы', 2, 'epic', 5, 0, 8, 0, 5),
                ('Золотая броня', 2, 'legendary', 8, 0, 12, 0, 8),
                ('Доспехи бога', 2, 'mythic', 10, 0, 20, 0, 10),
                # Слот 3: Ноги
                ('Шорты', 3, 'common', 0, 0, 0, 1, 0),
                ('Наголенники', 3, 'uncommon', 1, 0, 0, 3, 0),
                ('Щитки', 3, 'rare', 2, 2, 0, 5, 0),
                ('Поножи', 3, 'epic', 5, 0, 0, 8, 0),
                ('Золотые поножи', 3, 'legendary', 8, 0, 0, 12, 0),
                ('Ноги бога', 3, 'mythic', 10, 0, 0, 20, 0),
                # Слот 4: Ботинки
                ('Кеды', 4, 'common', 0, 1, 0, 0, 0),
                ('Кроссовки', 4, 'uncommon', 1, 3, 0, 1, 0),
                ('Бутсы', 4, 'rare', 2, 5, 0, 3, 0),
                ('Молнии', 4, 'epic', 5, 8, 0, 5, 0),
                ('Золотые бутсы', 4, 'legendary', 8, 12, 0, 8, 0),
                ('Ботинки бога', 4, 'mythic', 10, 20, 0, 10, 0),
                # Слот 5: Аксессуар
                ('Нарукавник', 5, 'common', 0, 0, 0, 0, 1),
                ('Перчатки', 5, 'uncommon', 1, 0, 1, 0, 3),
                ('Напульсник', 5, 'rare', 2, 0, 3, 0, 5),
                ('Амулет', 5, 'epic', 4, 0, 5, 0, 8),
                ('Золотой амулет', 5, 'legendary', 7, 0, 8, 0, 12),
                ('Артефакт бога', 5, 'mythic', 9, 0, 10, 0, 20),
            ]
            
            for skin in skins:
                c.execute('''
                    INSERT INTO skins (name, slot_id, rarity, rating_bonus, 
                                     speed_bonus, power_bonus, accuracy_bonus, defense_bonus)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', skin)
            
            conn.commit()
        
        conn.close()
    
    def create_player(self, player):
        """Создание нового игрока"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO players (name, password_hash)
            VALUES (?, ?)
        ''', (player.name, player.password_hash))
        
        player_id = c.lastrowid
        
        # Создаем запись статистики
        c.execute('''
            INSERT INTO stats (player_id, total_rating, base_rating, crystals)
            VALUES (?, 50, 50, 100)
        ''', (player_id,))
        
        # Добавляем стартовый скин
        c.execute('''
            INSERT INTO inventory (player_id, skin_name, rarity, equipped)
            VALUES (?, 'Повязка', 'common', 1)
        ''', (player_id,))
        
        conn.commit()
        conn.close()
        
        player.id = player_id
        return player
    
    def get_player_by_name(self, name):
        """Получение игрока по имени"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT id, name, password_hash, created_at FROM players WHERE name = ?', (name,))
        row = c.fetchone()
        conn.close()
        
        if row:
            from models import Player
            return Player(row[0], row[1], row[2], row[3])
        return None
    
    def get_player_stats(self, player_id):
        """Получение статистики игрока"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT matches, wins, losses, draws, goals_scored, goals_conceded,
                   streak, best_streak, total_rating, base_rating, crystals, tournaments_won
            FROM stats WHERE player_id = ?
        ''', (player_id,))
        
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'matches': row[0],
                'wins': row[1],
                'losses': row[2],
                'draws': row[3],
                'goals_scored': row[4],
                'goals_conceded': row[5],
                'streak': row[6],
                'best_streak': row[7],
                'total_rating': row[8],
                'base_rating': row[9],
                'crystals': row[10],
                'tournaments_won': row[11]
            }
        return {}
    
    def update_stats(self, player_id, stats_update):
        """Обновление статистики"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Получаем текущую статистику
        current = self.get_player_stats(player_id)
        
        # Обновляем
        new_matches = current['matches'] + stats_update.get('matches', 0)
        new_wins = current['wins'] + stats_update.get('wins', 0)
        new_losses = current['losses'] + stats_update.get('losses', 0)
        new_draws = current['draws'] + stats_update.get('draws', 0)
        new_goals_scored = current['goals_scored'] + stats_update.get('goals_scored', 0)
        new_goals_conceded = current['goals_conceded'] + stats_update.get('goals_conceded', 0)
        new_crystals = current['crystals'] + stats_update.get('crystals', 0)
        new_rating = current['total_rating'] + stats_update.get('rating', 0)
        
        # Обновляем стрик
        if stats_update.get('wins', 0) > 0:
            new_streak = current['streak'] + 1
            new_best_streak = max(current['best_streak'], new_streak)
        elif stats_update.get('losses', 0) > 0:
            new_streak = 0
            new_best_streak = current['best_streak']
        else:
            new_streak = current['streak']
            new_best_streak = current['best_streak']
        
        c.execute('''
            UPDATE stats SET
                matches = ?,
                wins = ?,
                losses = ?,
                draws = ?,
                goals_scored = ?,
                goals_conceded = ?,
                streak = ?,
                best_streak = ?,
                crystals = ?,
                total_rating = ?
            WHERE player_id = ?
        ''', (new_matches, new_wins, new_losses, new_draws, new_goals_scored,
              new_goals_conceded, new_streak, new_best_streak, new_crystals,
              new_rating, player_id))
        
        conn.commit()
        conn.close()
    
    def get_player_inventory(self, player_id):
        """Получение инвентаря игрока"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT skin_name, slot_id, rarity, equipped, unlocked_at
            FROM inventory WHERE player_id = ?
        ''', (player_id,))
        
        rows = c.fetchall()
        conn.close()
        
        inventory = []
        for row in rows:
            inventory.append({
                'skin_name': row[0],
                'slot_id': row[1],
                'rarity': row[2],
                'equipped': bool(row[3]),
                'unlocked_at': row[4]
            })
        
        return inventory
    
    def add_skin_to_inventory(self, player_id, skin):
        """Добавление скина в инвентарь"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO inventory (player_id, skin_name, slot_id, rarity, equipped)
            VALUES (?, ?, ?, ?, 0)
        ''', (player_id, skin['name'], skin['slot_id'], skin['rarity']))
        
        conn.commit()
        conn.close()
    
    def equip_skin(self, player_id, slot_id, skin_name):
        """Экипировка скина"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Снимаем все скины с этого слота
        c.execute('''
            UPDATE inventory SET equipped = 0
            WHERE player_id = ? AND slot_id = ?
        ''', (player_id, slot_id))
        
        # Экипируем новый скин
        c.execute('''
            UPDATE inventory SET equipped = 1
            WHERE player_id = ? AND skin_name = ?
        ''', (player_id, skin_name))
        
        conn.commit()
        conn.close()
    
    def has_skin(self, player_id, skin_name):
        """Проверка наличия скина"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT COUNT(*) FROM inventory
            WHERE player_id = ? AND skin_name = ?
        ''', (player_id, skin_name))
        
        count = c.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def calculate_total_rating(self, player_id):
        """Расчет общего рейтинга"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Получаем базовый рейтинг
        c.execute('SELECT base_rating FROM stats WHERE player_id = ?', (player_id,))
        base = c.fetchone()[0]
        
        # Получаем все экипированные скины
        c.execute('''
            SELECT s.rating_bonus FROM inventory i
            JOIN skins s ON i.skin_name = s.name
            WHERE i.player_id = ? AND i.equipped = 1
        ''', (player_id,))
        
        rows = c.fetchall()
        conn.close()
        
        total = base
        for row in rows:
            total += row[0]
        
        return min(total, 99)
    
    def update_total_rating(self, player_id, total_rating):
        """Обновление общего рейтинга"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE stats SET total_rating = ?
            WHERE player_id = ?
        ''', (total_rating, player_id))
        
        conn.commit()
        conn.close()
    
    def get_leaderboard(self, limit=100):
        """Получение таблицы рейтингов"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT p.name, s.total_rating, s.wins, s.matches, s.goals_scored,
                   s.crystals, p.last_online
            FROM players p
            JOIN stats s ON p.id = s.player_id
            ORDER BY s.total_rating DESC, s.wins DESC
            LIMIT ?
        ''', (limit,))
        
        rows = c.fetchall()
        conn.close()
        
        leaderboard = []
        for rank, row in enumerate(rows, 1):
            leaderboard.append({
                'rank': rank,
                'name': row[0],
                'rating': row[1],
                'wins': row[2],
                'matches': row[3],
                'goals': row[4],
                'crystals': row[5],
                'last_online': row[6]
            })
        
        return leaderboard
    
    def create_pack(self, pack):
        """Создание пака"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO packs (player_id, pack_type, opened)
            VALUES (?, ?, 0)
        ''', (pack.player_id, pack.pack_type))
        
        pack_id = c.lastrowid
        conn.commit()
        conn.close()
        
        pack.id = pack_id
        return pack
    
    def get_pack(self, pack_id):
        """Получение пака"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, player_id, pack_type, opened, bought_at
            FROM packs WHERE id = ?
        ''', (pack_id,))
        
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'player_id': row[1],
                'pack_type': row[2],
                'opened': bool(row[3]),
                'bought_at': row[4]
            }
        return None
    
    def open_pack(self, pack_id):
        """Открытие пака"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE packs SET opened = 1
            WHERE id = ?
        ''', (pack_id,))
        
        conn.commit()
        conn.close()
    
    def update_crystals(self, player_id, amount):
        """Обновление кристаллов"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE stats SET crystals = crystals + ?
            WHERE player_id = ?
        ''', (amount, player_id))
        
        conn.commit()
        conn.close()
    
    def get_player_achievements(self, player_id):
        """Получение достижений игрока"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT achievement_id, unlocked_at
            FROM achievements WHERE player_id = ?
        ''', (player_id,))
        
        rows = c.fetchall()
        conn.close()
        
        return [{'achievement_id': row[0], 'unlocked_at': row[1]} for row in rows]
    
    def unlock_achievement(self, player_id, achievement_id):
        """Разблокировка достижения"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO achievements (player_id, achievement_id)
            VALUES (?, ?)
        ''', (player_id, achievement_id))
        
        conn.commit()
        conn.close()
    
    def get_all_achievements(self):
        """Получение всех достижений"""
        return [
            {'id': 'first_goal', 'name': 'Первый гол', 'condition': 'first_goal', 'crystal_reward': 50},
            {'id': 'hat_trick', 'name': 'Хет-трик', 'condition': 'hat_trick', 'crystal_reward': 100},
            {'id': 'win_streak_5', 'name': '5 побед подряд', 'condition': 'win_streak_5', 'crystal_reward': 150},
            {'id': 'win_streak_10', 'name': '10 побед подряд', 'condition': 'win_streak_10', 'crystal_reward': 300},
            {'id': 'goals_100', 'name': '100 голов', 'condition': 'goals_100', 'crystal_reward': 200},
            {'id': 'goals_500', 'name': '500 голов', 'condition': 'goals_500', 'crystal_reward': 500},
            {'id': 'rating_60', 'name': 'Рейтинг 60', 'condition': 'rating_60', 'crystal_reward': 200},
            {'id': 'rating_70', 'name': 'Рейтинг 70', 'condition': 'rating_70', 'crystal_reward': 400},
            {'id': 'rating_80', 'name': 'Рейтинг 80', 'condition': 'rating_80', 'crystal_reward': 600},
            {'id': 'rating_90', 'name': 'Рейтинг 90', 'condition': 'rating_90', 'crystal_reward': 1000},
            {'id': 'tournament_win', 'name': 'Победитель турнира', 'condition': 'tournament_win', 'crystal_reward': 200}
        ]
