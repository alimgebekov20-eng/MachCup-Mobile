import json
import os
from datetime import datetime

class SaveManager:
    def __init__(self, save_file='save.json'):
        self.save_file = save_file
        self.default_data = {
            'player_name': 'Игрок',
            'selected_character': 'Азиз',
            'rating': 50,
            'crystals': 100,
            'characters': {
                'Азиз': {
                    'level': 1,
                    'xp': 0,
                    'base_stats': {'speed': 8, 'power': 9, 'accuracy': 7, 'defense': 4},
                    'skin_equipped': {},
                    'skins_owned': {}
                },
                'Хабиб': {
                    'level': 1,
                    'xp': 0,
                    'base_stats': {'speed': 7, 'power': 7, 'accuracy': 7, 'defense': 7},
                    'skin_equipped': {},
                    'skins_owned': {}
                },
                'Абдул': {
                    'level': 1,
                    'xp': 0,
                    'base_stats': {'speed': 6, 'power': 5, 'accuracy': 7, 'defense': 9},
                    'skin_equipped': {},
                    'skins_owned': {}
                },
                'Шамиль Рб': {
                    'level': 1,
                    'xp': 0,
                    'base_stats': {'speed': 9, 'power': 6, 'accuracy': 6, 'defense': 5},
                    'skin_equipped': {},
                    'skins_owned': {}
                },
                'Шамиль Jr.': {
                    'level': 1,
                    'xp': 0,
                    'base_stats': {'speed': 7, 'power': 8, 'accuracy': 8, 'defense': 6},
                    'skin_equipped': {},
                    'skins_owned': {}
                },
                'Салаудин': {
                    'level': 1,
                    'xp': 0,
                    'base_stats': {'speed': 5, 'power': 9, 'accuracy': 8, 'defense': 8},
                    'skin_equipped': {},
                    'skins_owned': {}
                }
            },
            'global_stats': {
                'matches': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'goals_scored': 0,
                'goals_conceded': 0,
                'streak': 0,
                'best_streak': 0,
                'rating_history': [50],
                'total_crystals_earned': 100,
                'total_crystals_spent': 0
            },
            'inventory': {
                'skins': {},
                'packs': []
            },
            'achievements': [],
            'last_sync': None
        }
    
    def load(self):
        """Загрузка сохранения"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Проверка на наличие всех ключей
                    return self._merge_with_default(data)
            except:
                return self.default_data
        return self.default_data
    
    def save(self, data):
        """Сохранение"""
        data['last_sync'] = datetime.now().isoformat()
        with open(self.save_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _merge_with_default(self, data):
        """Слияние с дефолтными данными"""
        merged = self.default_data.copy()
        for key, value in data.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key].update(value)
                else:
                    merged[key] = value
        return merged
    
    def unlock_achievement(self, player_data, achievement_id):
        """Разблокировка достижения"""
        if achievement_id not in player_data['achievements']:
            player_data['achievements'].append(achievement_id)
            self.save(player_data)
            return True
        return False
    
    def add_skin(self, player_data, character, skin_name, slot_id, rarity):
        """Добавление скина"""
        if 'skins_owned' not in player_data['characters'][character]:
            player_data['characters'][character]['skins_owned'] = {}
        
        if slot_id not in player_data['characters'][character]['skins_owned']:
            player_data['characters'][character]['skins_owned'][slot_id] = []
        
        if skin_name not in player_data['characters'][character]['skins_owned'][slot_id]:
            player_data['characters'][character]['skins_owned'][slot_id].append({
                'name': skin_name,
                'rarity': rarity,
                'equipped': False
            })
            self.save(player_data)
            return True
        return False
    
    def equip_skin(self, player_data, character, slot_id, skin_name):
        """Экипировка скина"""
        # Снимаем все скины в этом слоте
        for slot in player_data['characters'][character]['skins_owned'].get(slot_id, []):
            slot['equipped'] = False
        
        # Экипируем новый
        for slot in player_data['characters'][character]['skins_owned'].get(slot_id, []):
            if slot['name'] == skin_name:
                slot['equipped'] = True
                player_data['characters'][character]['skin_equipped'][slot_id] = skin_name
                self.save(player_data)
                return True
        return False
