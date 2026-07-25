import hashlib
import random
import sqlite3
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

class Pack:
    def __init__(self, pack_type, player_id, id=None):
        self.id = id
        self.pack_type = pack_type
        self.player_id = player_id
        self.opened = False
        
        self.drop_rates = {
            'common': {'common': 60, 'uncommon': 30, 'rare': 10},
            'rare': {'uncommon': 40, 'rare': 35, 'epic': 25},
            'epic': {'rare': 30, 'epic': 45, 'legendary': 25},
            'legendary': {'epic': 30, 'legendary': 50, 'mythic': 20}
        }
    
    def open(self):
        self.opened = True
        
        rates = self.drop_rates.get(self.pack_type, {})
        rarity = self._weighted_random(rates)
        
        skins = {
            'common': ['Повязка', 'Майка', 'Шорты', 'Кеды', 'Нарукавник'],
            'uncommon': ['Бандана', 'Футболка', 'Наголенники', 'Кроссовки', 'Перчатки'],
            'rare': ['Шлем', 'Броня', 'Щитки', 'Бутсы', 'Напульсник'],
            'epic': ['Корона', 'Латы', 'Поножи', 'Молнии', 'Амулет'],
            'legendary': ['Золотой шлем', 'Золотая броня', 'Золотые поножи', 'Золотые бутсы', 'Золотой амулет'],
            'mythic': ['Нимб бога', 'Доспехи бога', 'Ноги бога', 'Ботинки бога', 'Артефакт бога']
        }
        
        skin_name = random.choice(skins.get(rarity, ['Повязка']))
        
        conn = sqlite3.connect('football.db')
        c = conn.cursor()
        c.execute('SELECT name, slot_id, rarity, rating_bonus, speed_bonus, power_bonus, accuracy_bonus, defense_bonus FROM skins WHERE name = ?',
                 (skin_name,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {'name': row[0], 'slot_id': row[1], 'rarity': row[2], 'rating_bonus': row[3],
                    'speed_bonus': row[4], 'power_bonus': row[5], 'accuracy_bonus': row[6], 'defense_bonus': row[7]}
        return {'name': skin_name, 'rarity': rarity}
    
    def _weighted_random(self, weights):
        total = sum(weights.values())
        r = random.random() * total
        for key, weight in weights.items():
            r -= weight
            if r <= 0:
                return key
        return list(weights.keys())[0]
    
    def to_dict(self):
        return {'id': self.id, 'pack_type': self.pack_type, 'opened': self.opened}
