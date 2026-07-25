import hashlib
import random
from datetime import datetime

class Player:
    def __init__(self, name, password=None, password_hash=None, created_at=None, id=None):
        self.id = id
        self.name = name
        self.password_hash = password_hash if password_hash else hashlib.md5(password.encode()).hexdigest()
        self.created_at = created_at or datetime.now()
        self.total_rating = 50
        self.crystals = 100
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': str(self.created_at),
            'total_rating': self.total_rating
        }

class Skin:
    def __init__(self, name, slot_id, rarity, rating_bonus, speed_bonus=0, power_bonus=0, accuracy_bonus=0, defense_bonus=0):
        self.name = name
        self.slot_id = slot_id
        self.rarity = rarity
        self.rating_bonus = rating_bonus
        self.speed_bonus = speed_bonus
        self.power_bonus = power_bonus
        self.accuracy_bonus = accuracy_bonus
        self.defense_bonus = defense_bonus
    
    def to_dict(self):
        return {
            'name': self.name,
            'slot_id': self.slot_id,
            'rarity': self.rarity,
            'rating_bonus': self.rating_bonus,
            'speed_bonus': self.speed_bonus,
            'power_bonus': self.power_bonus,
            'accuracy_bonus': self.accuracy_bonus,
            'defense_bonus': self.defense_bonus
        }

class Pack:
    def __init__(self, pack_type, player_id, id=None):
        self.id = id
        self.pack_type = pack_type  # 'common', 'rare', 'epic', 'legendary'
        self.player_id = player_id
        self.opened = False
        
        # Шансы выпадения
        self.drop_rates = {
            'common': {'common': 60, 'uncommon': 30, 'rare': 10},
            'rare': {'uncommon': 40, 'rare': 35, 'epic': 25},
            'epic': {'rare': 30, 'epic': 45, 'legendary': 25},
            'legendary': {'epic': 30, 'legendary': 50, 'mythic': 20}
        }
    
    def open(self):
        """Открытие пака"""
        self.opened = True
        
        # Выбор редкости
        rates = self.drop_rates.get(self.pack_type, {})
        rarity = self._weighted_random(rates)
        
        # Выбор скина из этой редкости
        skins = {
            'common': ['Повязка', 'Майка', 'Шорты', 'Кеды', 'Нарукавник'],
            'uncommon': ['Бандана', 'Футболка', 'Наголенники', 'Кроссовки', 'Перчатки'],
            'rare': ['Шлем', 'Броня', 'Щитки', 'Бутсы', 'Напульсник'],
            'epic': ['Корона', 'Латы', 'Поножи', 'Молнии', 'Амулет'],
            'legendary': ['Золотой шлем', 'Золотая броня', 'Золотые поножи', 'Золотые бутсы', 'Золотой амулет'],
            'mythic': ['Нимб бога', 'Доспехи бога', 'Ноги бога', 'Ботинки бога', 'Артефакт бога']
        }
        
        skin_name = random.choice(skins.get(rarity, ['Повязка']))
        
        # Получаем данные скина
        from database import Database
        db = Database()
        conn = sqlite3.connect(db.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT name, slot_id, rarity, rating_bonus, speed_bonus, power_bonus, accuracy_bonus, defense_bonus
            FROM skins WHERE name = ?
        ''', (skin_name,))
        
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'name': row[0],
                'slot_id': row[1],
                'rarity': row[2],
                'rating_bonus': row[3],
                'speed_bonus': row[4],
                'power_bonus': row[5],
                'accuracy_bonus': row[6],
                'defense_bonus': row[7]
            }
        
        return {'name': skin_name, 'rarity': rarity}
    
    def _weighted_random(self, weights):
        """Взвешенный случайный выбор"""
        total = sum(weights.values())
        r = random.random() * total
        for key, weight in weights.items():
            r -= weight
            if r <= 0:
                return key
        return list(weights.keys())[0]
    
    def to_dict(self):
        return {
            'id': self.id,
            'pack_type': self.pack_type,
            'opened': self.opened
        }

class Match:
    def __init__(self, players, mode='2x2'):
        self.id = None
        self.players = players  # dict {player_id: player_data}
        self.mode = mode  # '1x1', '2x2', '3x3'
        self.state = 'waiting'  # 'waiting', 'playing', 'finished'
        self.ball = {'x': 600, 'y': 350, 'vx': 0, 'vy': 0}
        self.score = {'team_a': 0, 'team_b': 0}
        self.start_time = None
        self.end_time = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'mode': self.mode,
            'state': self.state,
            'players': self.players,
            'ball': self.ball,
            'score': self.score
        }
