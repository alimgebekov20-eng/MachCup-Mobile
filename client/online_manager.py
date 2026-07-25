import requests
import json
import socketio
import threading
import time

class OnlineManager:
    def __init__(self, server_url='http://localhost:5000'):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected = False
        self.token = None
        self.player_name = None
        
        # Настройка событий
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('match_found', self.on_match_found)
        self.sio.on('game_update', self.on_game_update)
        self.sio.on('match_result', self.on_match_result)
        self.sio.on('waiting', self.on_waiting)
        
        self.match_data = None
        self.game_update_callback = None
        self.match_result_callback = None
        self.waiting_callback = None
    
    def connect(self):
        """Подключение к серверу"""
        try:
            self.sio.connect(self.server_url)
            self.connected = True
            return True
        except:
            self.connected = False
            return False
    
    def disconnect(self):
        """Отключение от сервера"""
        if self.connected:
            self.sio.disconnect()
            self.connected = False
    
    def register(self, name, password):
        """Регистрация"""
        try:
            response = requests.post(f'{self.server_url}/api/register', json={
                'name': name,
                'password': password
            })
            return response.json()
        except:
            return {'error': 'Ошибка подключения к серверу'}
    
    def login(self, name, password):
        """Вход"""
        try:
            response = requests.post(f'{self.server_url}/api/login', json={
                'name': name,
                'password': password
            })
            data = response.json()
            if data.get('success'):
                self.player_name = name
                self.token = data.get('token')
            return data
        except:
            return {'error': 'Ошибка подключения к серверу'}
    
    def get_profile(self, name):
        """Получение профиля"""
        try:
            response = requests.get(f'{self.server_url}/api/profile/{name}')
            return response.json()
        except:
            return {'error': 'Ошибка подключения к серверу'}
    
    def get_leaderboard(self, limit=100):
        """Получение таблицы рейтингов"""
        try:
            response = requests.get(f'{self.server_url}/api/leaderboard?limit={limit}')
            return response.json()
        except:
            return {'error': 'Ошибка подключения к серверу'}
    
    def update_stats(self, stats):
        """Обновление статистики"""
        try:
            response = requests.post(f'{self.server_url}/api/update_stats', json={
                'player_name': self.player_name,
                **stats
            })
            return response.json()
        except:
            return {'error': 'Ошибка подключения к серверу'}
    
    def buy_pack(self, pack_type):
        """Покупка пака"""
        try:
            response = requests.post(f'{self.server_url}/api/buy_pack', json={
                'player_name': self.player_name,
                'pack_type': pack_type
            })
            return response.json()
        except:
            return {'error': 'Ошибка подключения к серверу'}
    
    def open_pack(self, pack_id):
        """Открытие пака"""
        try:
            response = requests.post(f'{self.server_url}/api/open_pack', json={
                'player_name': self.player_name,
                'pack_id': pack_id
            })
            return response.json()
        except:
            return {'error': 'Ошибка подключения к серверу'}
    
    def find_match(self, mode='ranked'):
        """Поиск соперника"""
        if not self.connected:
            return None
        
        self.sio.emit('find_match', {
            'player_name': self.player_name,
            'mode': mode
        })
        
        # Ждем ответа
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 секунд таймаут
            if self.match_data:
                data = self.match_data
                self.match_data = None
                return data
            time.sleep(0.1)
        
        return None
    
    def send_game_action(self, match_id, action):
        """Отправка действия в игре"""
        if self.connected:
            self.sio.emit('game_action', {
                'match_id': match_id,
                'player_id': self.player_name,
                'action': action
            })
    
    def finish_match(self, match_id, result):
        """Завершение матча"""
        if self.connected:
            self.sio.emit('match_finished', {
                'match_id': match_id,
                'result': result
            })
    
    # ===== EVENTS =====
    
    def on_connect(self):
        print('Подключено к серверу')
        self.connected = True
    
    def on_disconnect(self):
        print('Отключено от сервера')
        self.connected = False
    
    def on_match_found(self, data):
        self.match_data = data
        if self.match_found_callback:
            self.match_found_callback(data)
    
    def on_game_update(self, data):
        if self.game_update_callback:
            self.game_update_callback(data)
    
    def on_match_result(self, data):
        if self.match_result_callback:
            self.match_result_callback(data)
    
    def on_waiting(self, data):
        if self.waiting_callback:
            self.waiting_callback(data['message'])
    
    # ===== CALLBACKS =====
    
    def set_callbacks(self, match_found=None, game_update=None, match_result=None, waiting=None):
        self.match_found_callback = match_found
        self.game_update_callback = game_update
        self.match_result_callback = match_result
        self.waiting_callback = waiting
