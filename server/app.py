import os
import sys
import json
import hashlib
import random
import sqlite3
from datetime import datetime

# Добавляем текущую папку в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

from database import Database
from models import Player, Match, Skin, Pack
from matchmaking import Matchmaking

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app, origins=['*'])
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

# Инициализация БД
db = Database()
matchmaking = Matchmaking()

# ==================== API ЭНДПОИНТЫ ====================

@app.route('/api/register', methods=['POST'])
def register():
    """Регистрация нового игрока"""
    data = request.json
    name = data.get('name', '').strip()
    password = data.get('password', '').strip()
    
    if not name or not password:
        return jsonify({'error': 'Имя и пароль обязательны'}), 400
    
    if len(name) < 2:
        return jsonify({'error': 'Имя должно быть минимум 2 символа'}), 400
    
    if len(password) < 4:
        return jsonify({'error': 'Пароль должен быть минимум 4 символа'}), 400
    
    existing = db.get_player_by_name(name)
    if existing:
        return jsonify({'error': 'Игрок с таким именем уже существует'}), 400
    
    player = Player(name, password)
    db.create_player(player)
    
    return jsonify({
        'success': True,
        'player': player.to_dict()
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Вход в аккаунт"""
    data = request.json
    name = data.get('name', '').strip()
    password = data.get('password', '').strip()
    
    player = db.get_player_by_name(name)
    if not player:
        return jsonify({'error': 'Игрок не найден'}), 404
    
    if player.password_hash != hashlib.md5(password.encode()).hexdigest():
        return jsonify({'error': 'Неверный пароль'}), 401
    
    return jsonify({
        'success': True,
        'player': player.to_dict()
    })

@app.route('/api/profile/<name>', methods=['GET'])
def get_profile(name):
    """Получение профиля игрока"""
    player = db.get_player_by_name(name)
    if not player:
        return jsonify({'error': 'Игрок не найден'}), 404
    
    stats = db.get_player_stats(player.id)
    inventory = db.get_player_inventory(player.id)
    achievements = db.get_player_achievements(player.id)
    
    return jsonify({
        'player': player.to_dict(),
        'stats': stats,
        'inventory': inventory,
        'achievements': achievements
    })

@app.route('/api/update_stats', methods=['POST'])
def update_stats():
    """Обновление статистики после матча"""
    data = request.json
    player_name = data.get('player_name')
    match_result = data.get('match_result')
    score = data.get('score')
    goals_scored = data.get('goals_scored', 0)
    goals_conceded = data.get('goals_conceded', 0)
    crystals_earned = data.get('crystals_earned', 0)
    rating_change = data.get('rating_change', 0)
    
    player = db.get_player_by_name(player_name)
    if not player:
        return jsonify({'error': 'Игрок не найден'}), 404
    
    db.update_stats(player.id, {
        'matches': 1,
        'wins': 1 if match_result == 'win' else 0,
        'losses': 1 if match_result == 'loss' else 0,
        'draws': 1 if match_result == 'draw' else 0,
        'goals_scored': goals_scored,
        'goals_conceded': goals_conceded,
        'crystals': crystals_earned,
        'rating': rating_change
    })
    
    return jsonify({'success': True})

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получение таблицы рейтингов"""
    limit = request.args.get('limit', 100, type=int)
    leaderboard = db.get_leaderboard(limit)
    return jsonify(leaderboard)

@app.route('/api/buy_pack', methods=['POST'])
def buy_pack():
    """Покупка пака"""
    data = request.json
    player_name = data.get('player_name')
    pack_type = data.get('pack_type')
    
    player = db.get_player_by_name(player_name)
    if not player:
        return jsonify({'error': 'Игрок не найден'}), 404
    
    pack_prices = {
        'common': 100,
        'rare': 300,
        'epic': 800,
        'legendary': 2000
    }
    
    price = pack_prices.get(pack_type, 0)
    if price == 0:
        return jsonify({'error': 'Неверный тип пака'}), 400
    
    stats = db.get_player_stats(player.id)
    if stats['crystals'] < price:
        return jsonify({'error': 'Недостаточно кристаллов'}), 400
    
    pack = Pack(pack_type, player.id)
    db.create_pack(pack)
    db.update_crystals(player.id, -price)
    
    return jsonify({
        'success': True,
        'pack': pack.to_dict(),
        'crystals_left': stats['crystals'] - price
    })

@app.route('/api/open_pack', methods=['POST'])
def open_pack():
    """Открытие пака"""
    data = request.json
    player_name = data.get('player_name')
    pack_id = data.get('pack_id')
    
    player = db.get_player_by_name(player_name)
    if not player:
        return jsonify({'error': 'Игрок не найден'}), 404
    
    pack = db.get_pack(pack_id)
    if not pack or pack['player_id'] != player.id:
        return jsonify({'error': 'Пак не найден'}), 404
    
    if pack['opened']:
        return jsonify({'error': 'Пак уже открыт'}), 400
    
    skin = pack.open()
    db.open_pack(pack_id)
    db.add_skin_to_inventory(player.id, skin)
    
    rating_bonus = skin.get('rating_bonus', 0)
    if rating_bonus > 0:
        db.update_rating(player.id, rating_bonus)
    
    return jsonify({
        'success': True,
        'skin': skin,
        'rating_bonus': rating_bonus
    })

@app.route('/api/equip_skin', methods=['POST'])
def equip_skin():
    """Экипировка скина"""
    data = request.json
    player_name = data.get('player_name')
    slot_id = data.get('slot_id')
    skin_name = data.get('skin_name')
    
    player = db.get_player_by_name(player_name)
    if not player:
        return jsonify({'error': 'Игрок не найден'}), 404
    
    if not db.has_skin(player.id, skin_name):
        return jsonify({'error': 'Скин не найден в инвентаре'}), 404
    
    db.equip_skin(player.id, slot_id, skin_name)
    total_rating = db.calculate_total_rating(player.id)
    db.update_total_rating(player.id, total_rating)
    
    return jsonify({
        'success': True,
        'total_rating': total_rating
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

# ==================== WebSocket ====================

@socketio.on('connect')
def handle_connect():
    print(f'Player connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Player disconnected: {request.sid}')
    matchmaking.remove_player(request.sid)

@socketio.on('find_match')
def handle_find_match(data):
    player_name = data.get('player_name')
    mode = data.get('mode', 'ranked')
    
    player = db.get_player_by_name(player_name)
    if not player:
        emit('match_found', {'error': 'Игрок не найден'})
        return
    
    match_id = matchmaking.add_player(request.sid, {
        'id': player.id,
        'name': player_name,
        'rating': player.total_rating,
        'mode': mode
    })
    
    if match_id:
        match_data = matchmaking.get_match(match_id)
        emit('match_found', {
            'match_id': match_id,
            'opponent': match_data['opponent'],
            'mode': mode,
            'players': match_data['players']
        })
        join_room(match_id)
    else:
        emit('waiting', {'message': 'Ищем соперника...'})

@socketio.on('game_action')
def handle_game_action(data):
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    action = data.get('action')
    
    match_state = matchmaking.update_match(match_id, player_id, action)
    if match_state:
        emit('game_update', match_state, room=match_id)

@socketio.on('match_finished')
def handle_match_finished(data):
    match_id = data.get('match_id')
    result = data.get('result')
    
    match_data = matchmaking.finish_match(match_id, result)
    if match_data:
        emit('match_result', match_data, room=match_id)
        leave_room(match_id)

# ==================== ЗАПУСК ====================

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
