import uuid
import time
from datetime import datetime

class Matchmaking:
    def __init__(self):
        self.queue = []  # Очередь игроков
        self.matches = {}  # Активные матчи
        self.match_timers = {}  # Таймеры матчей
    
    def add_player(self, player_sid, player_data):
        """Добавление игрока в очередь"""
        # Проверяем не в очереди ли уже
        for q in self.queue:
            if q['sid'] == player_sid:
                return None
        
        # Добавляем в очередь
        self.queue.append({
            'sid': player_sid,
            'data': player_data,
            'joined_at': time.time()
        })
        
        # Пытаемся найти матч
        return self._try_match()
    
    def _try_match(self):
        """Попытка найти матч для игроков"""
        if len(self.queue) < 2:
            return None
        
        # Сортируем по рейтингу
        self.queue.sort(key=lambda x: x['data']['rating'])
        
        # Ищем пару с близким рейтингом
        for i in range(len(self.queue) - 1):
            for j in range(i + 1, len(self.queue)):
                p1 = self.queue[i]
                p2 = self.queue[j]
                
                # Проверяем разницу в рейтинге (максимум 200)
                rating_diff = abs(p1['data']['rating'] - p2['data']['rating'])
                if rating_diff <= 200 or p1['data']['mode'] == 'casual':
                    # Создаем матч
                    match_id = self._create_match(p1, p2)
                    # Удаляем игроков из очереди
                    self.queue.remove(p1)
                    self.queue.remove(p2)
                    return match_id
        
        return None
    
    def _create_match(self, p1, p2):
        """Создание матча между двумя игроками"""
        match_id = str(uuid.uuid4())[:8]
        
        players = {
            'player1': {
                'sid': p1['sid'],
                'name': p1['data']['name'],
                'rating': p1['data']['rating'],
                'team': 'A'
            },
            'player2': {
                'sid': p2['sid'],
                'name': p2['data']['name'],
                'rating': p2['data']['rating'],
                'team': 'B'
            }
        }
        
        self.matches[match_id] = {
            'id': match_id,
            'players': players,
            'state': 'playing',
            'mode': p1['data']['mode'],
            'score': {'A': 0, 'B': 0},
            'start_time': time.time(),
            'updates': {},
            'opponent': p2['data']['name']
        }
        
        return match_id
    
    def get_match(self, match_id):
        """Получение данных матча"""
        return self.matches.get(match_id)
    
    def update_match(self, match_id, player_id, action):
        """Обновление состояния матча"""
        if match_id not in self.matches:
            return None
        
        match = self.matches[match_id]
        
        # Сохраняем действие игрока
        if player_id not in match['updates']:
            match['updates'][player_id] = []
        match['updates'][player_id].append({
            'action': action,
            'timestamp': time.time()
        })
        
        # Ограничиваем историю
        if len(match['updates'][player_id]) > 100:
            match['updates'][player_id] = match['updates'][player_id][-100:]
        
        return match
    
    def finish_match(self, match_id, result):
        """Завершение матча"""
        if match_id not in self.matches:
            return None
        
        match = self.matches[match_id]
        match['state'] = 'finished'
        match['end_time'] = time.time()
        match['result'] = result
        
        result_data = {
            'match_id': match_id,
            'result': result,
            'players': match['players'],
            'score': match['score']
        }
        
        del self.matches[match_id]
        return result_data
    
    def remove_player(self, player_sid):
        """Удаление игрока из очереди"""
        for i, q in enumerate(self.queue):
            if q['sid'] == player_sid:
                del self.queue[i]
                return True
        return False
    
    def get_queue_size(self):
        """Размер очереди"""
        return len(self.queue)
