import os
import json
import hashlib
import random
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from database import Database
from models import Player, Match, Skin, Pack
from matchmaking import Matchmaking

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app, origins=['*'])
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')

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
    
    # Проверка на существование игрока
    existing = db.get_player_by_name(name)
    if existing:
        return jsonify({'error': 'Игрок с таким именем уже существует'}), 400
    
    # Создание нового игрока
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
    match_result = data.get('match_result')  # 'win', 'loss', 'draw'
    score = data.get('score')  # [my_score, opp_score]
    goals_scored = data.get('goals_scored', 0)
    goals_conceded = data.get('goals_conceded', 0)
    crystals_earned = data.get('crystals_earned', 0)
    rating_change = data.get('rating_change', 0)
    
    player = db.get_player_by_name(player_name)
    if not player:
        return jsonify({'error': 'Игрок не найден'}), 404
    
    # Обновление статистики
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
    
    # Проверка на достижения
    stats = db.get_player_stats(player.id)
    new_achievements = check_achievements(player.id, stats)
    
    return jsonify({
        'success': True,
        'new_achievements': new_achievements
    })

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
    pack_type = data.get('pack_type')  # 'common', 'rare', 'epic', 'legendary'
    
    player = db.get_player_by_name(player_name)
    if not player:
        return jsonify({'error': 'Игрок не найден'}), 404
    
    # Проверка цены
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
    
    # Создание пака
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
    
    # Открытие пака
    skin = pack.open()
    db.open_pack(pack_id)
    db.add_skin_to_inventory(player.id, skin)
    
    # Обновление рейтинга
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
    slot_id = data.get('slot_id')  # 1-5
    skin_name = data.get('skin_name')
    
    player = db.get_player_by_name(player_name)
    if not player:
        return jsonify({'error': 'Игрок не найден'}), 404
    
    # Проверка наличия скина
    if not db.has_skin(player.id, skin_name):
        return jsonify({'error': 'Скин не найден в инвентаре'}), 404
    
    # Экипировка
    db.equip_skin(player.id, slot_id, skin_name)
    
    # Пересчет рейтинга
    total_rating = db.calculate_total_rating(player.id)
    db.update_total_rating(player.id, total_rating)
    
    return jsonify({
        'success': True,
        'total_rating': total_rating
    })

# ==================== WebSocket (для онлайн игры) ====================

@socketio.on('connect')
def handle_connect():
    """Подключение игрока"""
    print(f'Player connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """Отключение игрока"""
    print(f'Player disconnected: {request.sid}')
    matchmaking.remove_player(request.sid)

@socketio.on('find_match')
def handle_find_match(data):
    """Поиск соперника"""
    player_name = data.get('player_name')
    mode = data.get('mode', 'ranked')  # 'ranked' или 'casual'
    
    player = db.get_player_by_name(player_name)
    if not player:
        emit('match_found', {'error': 'Игрок не найден'})
        return
    
    # Добавление в очередь
    match_id = matchmaking.add_player(request.sid, {
        'id': player.id,
        'name': player_name,
        'rating': player.total_rating,
        'mode': mode
    })
    
    if match_id:
        # Матч найден!
        match_data = matchmaking.get_match(match_id)
        emit('match_found', {
            'match_id': match_id,
            'opponent': match_data['opponent'],
            'mode': mode,
            'players': match_data['players']
        })
        
        # Создаем комнату для матча
        join_room(match_id)
    else:
        # В очереди
        emit('waiting', {'message': 'Ищем соперника...'})

@socketio.on('game_action')
def handle_game_action(data):
    """Обработка действий в игре"""
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    action = data.get('action')  # {'type': 'move', 'x': 100, 'y': 200}
    
    # Обновление состояния матча
    match_state = matchmaking.update_match(match_id, player_id, action)
    
    # Отправка всем игрокам в комнате
    emit('game_update', match_state, room=match_id)

@socketio.on('match_finished')
def handle_match_finished(data):
    """Завершение матча"""
    match_id = data.get('match_id')
    result = data.get('result')
    
    # Обновление статистики
    match_data = matchmaking.finish_match(match_id, result)
    
    # Отправка результатов
    emit('match_result', match_data, room=match_id)
    
    # Очистка
    leave_room(match_id)

# ==================== ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ====================

def check_achievements(player_id, stats):
    """Проверка и разблокировка достижений"""
    new_achievements = []
    
    achievements = db.get_all_achievements()
    unlocked = db.get_player_achievements(player_id)
    unlocked_ids = [a['achievement_id'] for a in unlocked]
    
    for ach in achievements:
        if ach['id'] in unlocked_ids:
            continue
        
        # Проверка условий
        condition = ach['condition']
        if check_condition(stats, condition):
            db.unlock_achievement(player_id, ach['id'])
            new_achievements.append(ach)
            
            # Награда кристаллами
            db.update_crystals(player_id, ach['crystal_reward'])
    
    return new_achievements

def check_condition(stats, condition):
    """Проверка условия достижения"""
    if condition == 'first_goal':
        return stats['goals_scored'] >= 1
    elif condition == 'hat_trick':
        return stats['goals_scored'] >= 3
    elif condition == 'win_streak_5':
        return stats['streak'] >= 5
    elif condition == 'win_streak_10':
        return stats['streak'] >= 10
    elif condition == 'goals_100':
        return stats['goals_scored'] >= 100
    elif condition == 'goals_500':
        return stats['goals_scored'] >= 500
    elif condition == 'rating_60':
        return stats['total_rating'] >= 60
    elif condition == 'rating_70':
        return stats['total_rating'] >= 70
    elif condition == 'rating_80':
        return stats['total_rating'] >= 80
    elif condition == 'rating_90':
        return stats['total_rating'] >= 90
    elif condition == 'tournament_win':
        return stats['tournaments_won'] >= 1
    return False

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
