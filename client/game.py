import pygame
import math
import random
from player import Player, Bot, Goalkeeper
from ball import Ball
from save_manager import SaveManager

class Game:
    def __init__(self, screen, mode, difficulty, character, player_data, match_data=None):
        self.screen = screen
        self.mode = mode  # '2x2', '3x3', 'training'
        self.difficulty = difficulty  # 'easy', 'medium', 'hard'
        self.character = character
        self.player_data = player_data
        self.match_data = match_data
        self.save_manager = SaveManager()
        
        # Загрузка текстур
        self.images = {}
        try:
            self.images['field'] = pygame.image.load('assets/images/field.png')
            self.images['ball'] = pygame.image.load('assets/images/ball.png')
        except:
            self.images = {}
        
        # Загрузка звуков
        self.sounds = {}
        try:
            self.sounds['goal'] = pygame.mixer.Sound('assets/sounds/goal.wav')
            self.sounds['kick'] = pygame.mixer.Sound('assets/sounds/kick.wav')
            self.sounds['whistle'] = pygame.mixer.Sound('assets/sounds/whistle.wav')
        except:
            self.sounds = {}
        
        # Игровые объекты
        self.ball = Ball(600, 350)
        self.players = []
        self.goalkeepers = []
        self.goals = []
        
        # Состояние
        self.running = False
        self.paused = False
        self.score = {'home': 0, 'away': 0}
        self.time = 0
        self.max_time = 300  # 5 минут
        self.goal_scored = False
        self.goal_timer = 0
        self.match_finished = False
        self.goal_animation_timer = 0
        self.goal_animation_active = False
        
        # Флаги для статистики
        self.home_goals_scored = 0
        self.away_goals_scored = 0
        
        # UI элементы
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        self.init_teams()
    
    def init_teams(self):
        """Инициализация команд"""
        # Загрузка данных персонажей
        import json
        try:
            with open('data/characters.json', 'r', encoding='utf-8') as f:
                chars_data = json.load(f)
                characters = {c['name']: c for c in chars_data['characters']}
                formations = chars_data.get('formations', {})
        except:
            characters = {}
            formations = {}
        
        # Персонажи по умолчанию
        default_characters = {
            'Азиз': {'base_stats': {'speed': 8, 'power': 9, 'accuracy': 7, 'defense': 4}, 'color': '#FF6B35'},
            'Хабиб': {'base_stats': {'speed': 7, 'power': 7, 'accuracy': 7, 'defense': 7}, 'color': '#00B4D8'},
            'Абдул': {'base_stats': {'speed': 6, 'power': 5, 'accuracy': 7, 'defense': 9}, 'color': '#2D6A4F'},
            'Шамиль Рб': {'base_stats': {'speed': 9, 'power': 6, 'accuracy': 6, 'defense': 5}, 'color': '#E63946'},
            'Шамиль Jr.': {'base_stats': {'speed': 7, 'power': 8, 'accuracy': 8, 'defense': 6}, 'color': '#9B5DE5'},
            'Салаудин': {'base_stats': {'speed': 5, 'power': 9, 'accuracy': 8, 'defense': 8}, 'color': '#F77F00'}
        }
        
        # Выбор состава в зависимости от режима
        if self.mode == '2x2':
            home_team = ['Азиз', 'Хабиб']
            away_team = ['Шамиль Рб', 'Шамиль Jr.']
        elif self.mode == 'training':
            home_team = [self.character]
            away_team = ['Шамиль Рб', 'Шамиль Jr.']
        else:  # '3x3'
            home_team = ['Азиз', 'Хабиб', 'Абдул']
            away_team = ['Шамиль Рб', 'Шамиль Jr.', 'Салаудин']
        
        # Позиции на поле
        home_positions = [(200, 350), (300, 250), (300, 450)]
        away_positions = [(900, 350), (800, 250), (800, 450)]
        goal_positions = [(50, 350), (1050, 350)]
        
        # Создаем игроков домашней команды
        for i, name in enumerate(home_team):
            pos = home_positions[i % len(home_positions)]
            
            # Получаем данные персонажа
            char_data = characters.get(name, default_characters.get(name, {}))
            stats = char_data.get('base_stats', {'speed': 7, 'power': 7, 'accuracy': 7, 'defense': 7})
            color_str = char_data.get('color', '#888888')
            color = self.hex_to_rgb(color_str)
            
            # Проверяем, это игрок или бот
            if name == self.character and not self.match_data:
                # Игрок
                player = Player(pos[0], pos[1], color, name, stats, is_player=True, player_data=self.player_data)
            else:
                # Бот
                player = Bot(pos[0], pos[1], color, name, stats, 'home', self.difficulty, self.player_data)
            
            player.team = 'home'
            player.role = ['defender', 'midfielder', 'forward'][i % 3]
            self.players.append(player)
        
        # Создаем игроков гостевой команды
        for i, name in enumerate(away_team):
            pos = away_positions[i % len(away_positions)]
            
            char_data = characters.get(name, default_characters.get(name, {}))
            stats = char_data.get('base_stats', {'speed': 7, 'power': 7, 'accuracy': 7, 'defense': 7})
            color_str = char_data.get('color', '#888888')
            color = self.hex_to_rgb(color_str)
            
            player = Bot(pos[0], pos[1], color, name, stats, 'away', self.difficulty, self.player_data)
            player.team = 'away'
            player.role = ['defender', 'midfielder', 'forward'][i % 3]
            self.players.append(player)
        
        # Вратари
        self.goalkeepers = [
            Goalkeeper(70, 350, (0, 0, 200), 'ГК', 'home', self.player_data),
            Goalkeeper(1030, 350, (200, 0, 0), 'ГК', 'away', self.player_data)
        ]
        
        # Ворота
        self.goals = [
            {'x': 50, 'y': 300, 'width': 10, 'height': 100, 'team': 'home'},
            {'x': 1050, 'y': 300, 'width': 10, 'height': 100, 'team': 'away'}
        ]
    
    def hex_to_rgb(self, hex_color):
        """Конвертация HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def start(self):
        """Начало матча"""
        self.running = True
        self.time = 0
        self.score = {'home': 0, 'away': 0}
        self.home_goals_scored = 0
        self.away_goals_scored = 0
        
        # Центральный удар
        self.ball.x = 600
        self.ball.y = 350
        self.ball.vx = random.uniform(-2, 2)
        self.ball.vy = random.uniform(-2, 2)
        
        # Свисток
        try:
            self.sounds['whistle'].play()
        except:
            pass
    
    def update(self):
        """Обновление игрового состояния"""
        if not self.running or self.paused or self.match_finished:
            return
        
        # Обновление таймера
        self.time += 1/60
        if self.time >= self.max_time:
            self.match_finished = True
            self.end_match()
            return
        
        # Обновление мяча
        self.ball.update()
        self.check_goals()
        
        # Обновление игроков
        for player in self.players:
            if player.is_player:
                # Игрок управляется пользователем
                player.update()
            else:
                # Боты
                player.update(self.ball, self.players, self.goalkeepers, self.goals)
        
        # Обновление вратарей
        for gk in self.goalkeepers:
            gk.update(self.ball, self.goals)
        
        # Проверка столкновений
        self.check_collisions()
        
        # Анимация гола
        if self.goal_animation_active:
            self.goal_animation_timer += 1
            if self.goal_animation_timer > 120:  # 2 секунды
                self.goal_animation_active = False
                self.goal_animation_timer = 0
                self.reset_ball()
    
    def check_collisions(self):
        """Проверка столкновений игроков с мячом"""
        for player in self.players:
            if player.distance_to(self.ball) < player.radius + self.ball.radius:
                # Если у игрока нет мяча, а он подошел к мячу
                if not player.has_ball and not self.ball_has_owner():
                    # Отталкивание мяча
                    angle = math.atan2(self.ball.y - player.y, self.ball.x - player.x)
                    power = 2 + random.random() * 2
                    self.ball.vx = power * math.cos(angle)
                    self.ball.vy = power * math.sin(angle)
                    player.has_ball = True
    
    def ball_has_owner(self):
        """Проверка есть ли у мяча владелец"""
        for player in self.players:
            if player.has_ball:
                return True
        return False
    
    def check_goals(self):
        """Проверка гола"""
        for goal in self.goals:
            # Проверка пересечения линии ворот
            if goal['team'] == 'home':
                if self.ball.x < goal['x'] + goal['width'] and \
                   goal['y'] < self.ball.y < goal['y'] + goal['height']:
                    # Гол в домашние ворота (гол гостей)
                    self.score['away'] += 1
                    self.away_goals_scored += 1
                    self.goal_scored = True
                    self.goal_animation_active = True
                    self.goal_animation_timer = 0
                    
                    # Звук гола
                    try:
                        self.sounds['goal'].play()
                    except:
                        pass
                    
                    # Проверка достижений
                    self.check_achievements('away')
                    return
            else:  # away goal
                if self.ball.x + self.ball.radius > goal['x'] and \
                   goal['y'] < self.ball.y < goal['y'] + goal['height']:
                    self.score['home'] += 1
                    self.home_goals_scored += 1
                    self.goal_scored = True
                    self.goal_animation_active = True
                    self.goal_animation_timer = 0
                    
                    try:
                        self.sounds['goal'].play()
                    except:
                        pass
                    
                    self.check_achievements('home')
                    return
    
    def reset_ball(self):
        """Сброс мяча после гола"""
        self.ball.x = 600
        self.ball.y = 350
        self.ball.vx = random.uniform(-1, 1)
        self.ball.vy = random.uniform(-1, 1)
        
        # Сброс владения мячом
        for player in self.players:
            player.has_ball = False
        
        self.goal_scored = False
    
    def check_achievements(self, team):
        """Проверка достижений"""
        if team == 'home':
            # Проверка хет-трика
            if self.home_goals_scored >= 3:
                self.save_manager.unlock_achievement(self.player_data, 'hat_trick')
            
            # Проверка сухой победы
            if self.score['away'] == 0 and self.score['home'] >= 3:
                self.save_manager.unlock_achievement(self.player_data, 'clean_sheet')
            
            # Первый гол
            if self.score['home'] == 1 and self.home_goals_scored == 1:
                self.save_manager.unlock_achievement(self.player_data, 'first_goal')
    
    def end_match(self):
        """Завершение матча"""
        self.match_finished = True
        
        # Расчет наград
        home_score = self.score['home']
        away_score = self.score['away']
        
        if home_score > away_score:
            result = 'win'
            stars_earned = 0.5 + (home_score - away_score) * 0.1
            crystals_earned = 50
            
            if away_score == 0:
                stars_earned += 0.3
                crystals_earned += 30
            
            if home_score >= 3:
                stars_earned += 0.2
                crystals_earned += 25
            
            # Бонус за сложность
            difficulty_bonus = {'easy': 1, 'medium': 1.5, 'hard': 2}
            crystals_earned *= difficulty_bonus.get(self.difficulty, 1)
            crystals_earned = int(crystals_earned)
            
            # Обновление статистики
            self.player_data['global_stats']['wins'] += 1
            self.player_data['global_stats']['streak'] += 1
            self.player_data['global_stats']['best_streak'] = max(
                self.player_data['global_stats']['best_streak'],
                self.player_data['global_stats']['streak']
            )
            
        elif home_score < away_score:
            result = 'loss'
            stars_earned = -0.3
            crystals_earned = 10
            self.player_data['global_stats']['streak'] = 0
        else:
            result = 'draw'
            stars_earned = 0
            crystals_earned = 20
        
        # Обновление глобальной статистики
        self.player_data['global_stats']['matches'] += 1
        self.player_data['global_stats']['goals_scored'] += home_score
        self.player_data['global_stats']['goals_conceded'] += away_score
        
        # Обновление кристаллов и рейтинга
        self.player_data['crystals'] += crystals_earned
        self.player_data['rating'] = max(0, self.player_data.get('rating', 50) + stars_earned)
        
        # Сохранение
        self.save_manager.save(self.player_data)
        
        # Звук свистка
        try:
            self.sounds['whistle'].play()
        except:
            pass
    
    def handle_key_down(self, key):
        """Обработка нажатий клавиш"""
        if not self.running:
            return
        
        # Поиск игрока
        player = None
        for p in self.players:
            if p.is_player:
                player = p
                break
        
        if not player:
            return
        
        # Управление
        if key == pygame.K_w:
            player.move_up = True
        elif key == pygame.K_s:
            player.move_down = True
        elif key == pygame.K_a:
            player.move_left = True
        elif key == pygame.K_d:
            player.move_right = True
        elif key == pygame.K_SPACE:
            # Удар по воротам противника
            enemy_goal = self.goals[1] if player.team == 'home' else self.goals[0]
            goal_x = enemy_goal['x'] + enemy_goal['width'] / 2
            goal_y = enemy_goal['y'] + enemy_goal['height'] / 2
            player.shoot(self.ball, goal_x, goal_y)
            try:
                self.sounds['kick'].play()
            except:
                pass
        elif key == pygame.K_e:
            # Пас
            teammates = [p for p in self.players if p.team == player.team and p != player]
            player.pass_ball(self.ball, teammates)
            try:
                self.sounds['kick'].play()
            except:
                pass
        elif key == pygame.K_q:
            # Отбор
            player.tackle(self.ball)
        elif key == pygame.K_p:
            self.paused = not self.paused
    
    def handle_key_up(self, key):
        """Обработка отпускания клавиш"""
        player = None
        for p in self.players:
            if p.is_player:
                player = p
                break
        
        if not player:
            return
        
        if key == pygame.K_w:
            player.move_up = False
        elif key == pygame.K_s:
            player.move_down = False
        elif key == pygame.K_a:
            player.move_left = False
        elif key == pygame.K_d:
            player.move_right = False
    
    def draw(self):
        """Отрисовка игры"""
        # Фон поля
        if 'field' in self.images:
            field_img = pygame.transform.scale(self.images['field'], (1200, 700))
            self.screen.blit(field_img, (0, 0))
        else:
            self.draw_field()
        
        # Ворота
        for goal in self.goals:
            # Стойки ворот
            pygame.draw.rect(self.screen, (255, 255, 255), 
                           (goal['x'], goal['y'], goal['width'], goal['height']))
            # Сетка
            for i in range(0, goal['height'], 8):
                pygame.draw.line(self.screen, (200, 200, 200),
                               (goal['x'], goal['y'] + i),
                               (goal['x'] + goal['width'], goal['y'] + i), 1)
            for i in range(0, goal['width'], 8):
                pygame.draw.line(self.screen, (200, 200, 200),
                               (goal['x'] + i, goal['y']),
                               (goal['x'] + i, goal['y'] + goal['height']), 1)
        
        # Игроки
        for player in self.players:
            player.draw(self.screen)
        
        # Вратари
        for gk in self.goalkeepers:
            gk.draw(self.screen)
        
        # Мяч
        if 'ball' in self.images:
            ball_img = pygame.transform.scale(self.images['ball'], (24, 24))
            self.screen.blit(ball_img, (self.ball.x - 12, self.ball.y - 12))
        else:
            self.ball.draw(self.screen)
        
        # Анимация гола
        if self.goal_animation_active:
            # Большая надпись ГОЛ!!!
            font = pygame.font.Font(None, 120)
            text = font.render('⚽ ГОЛ!', True, (255, 255, 0))
            text_rect = text.get_rect(center=(600, 350))
            
            # Пульсирующий эффект
            scale = 1 + 0.1 * math.sin(self.goal_animation_timer * 0.1)
            scaled_text = pygame.transform.scale(text, 
                (int(text_rect.width * scale), int(text_rect.height * scale)))
            scaled_rect = scaled_text.get_rect(center=(600, 350))
            self.screen.blit(scaled_text, scaled_rect)
        
        # UI
        self.draw_ui()
    
    def draw_field(self):
        """Отрисовка футбольного поля (без картинок)"""
        # Зеленый фон
        self.screen.fill((34, 177, 76))
        
        # Трава с полосками
        for i in range(0, 700, 40):
            color = (34, 177, 76) if i % 80 == 0 else (30, 160, 70)
            pygame.draw.rect(self.screen, color, (0, i, 1200, 40))
        
        # Разметка
        white = (255, 255, 255)
        
        # Границы
        pygame.draw.rect(self.screen, white, (50, 50, 1100, 600), 3)
        
        # Центральный круг
        pygame.draw.circle(self.screen, white, (600, 350), 80, 2)
        pygame.draw.circle(self.screen, white, (600, 350), 5)
        
        # Центральная линия
        pygame.draw.line(self.screen, white, (600, 50), (600, 650), 2)
        
        # Штрафные
        pygame.draw.rect(self.screen, white, (50, 250, 150, 200), 2)
        pygame.draw.rect(self.screen, white, (1050-150, 250, 150, 200), 2)
        
        # Вратарские
        pygame.draw.rect(self.screen, white, (50, 300, 80, 100), 2)
        pygame.draw.rect(self.screen, white, (1050-80, 300, 80, 100), 2)
        
        # Угловые
        pygame.draw.circle(self.screen, white, (50, 50), 15, 2)
        pygame.draw.circle(self.screen, white, (1150, 50), 15, 2)
        pygame.draw.circle(self.screen, white, (50, 650), 15, 2)
        pygame.draw.circle(self.screen, white, (1150, 650), 15, 2)
    
    def draw_ui(self):
        """Отрисовка UI"""
        # Счет
        score_text = self.font_large.render(f'{self.score["home"]} : {self.score["away"]}', True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(600, 40))
        
        # Тень для счета
        shadow = self.font_large.render(f'{self.score["home"]} : {self.score["away"]}', True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(603, 43))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(score_text, score_rect)
        
        # Время
        minutes = int(self.time // 60)
        seconds = int(self.time % 60)
        time_text = self.font_medium.render(f'⏱️ {minutes:02d}:{seconds:02d}', True, (255, 255, 255))
        time_rect = time_text.get_rect(topleft=(20, 20))
        self.screen.blit(time_text, time_rect)
        
        # Режим
        mode_names = {'2x2': '2x2', '3x3': '3x3', 'training': '🏋️ Тренировка'}
        mode_text = self.font_small.render(mode_names.get(self.mode, '2x2'), True, (255, 255, 255))
        mode_rect = mode_text.get_rect(topright=(1180, 20))
        self.screen.blit(mode_text, mode_rect)
        
        # Информация о сложности
        if self.mode != 'online':
            diff_names = {'easy': '🟢 ЛЕГКО', 'medium': '🟡 СРЕДНЕ', 'hard': '🔴 СЛОЖНО'}
            diff_text = self.font_small.render(diff_names.get(self.difficulty, 'СРЕДНЕ'), True, (255, 255, 255))
            diff_rect = diff_text.get_rect(topleft=(20, 60))
            self.screen.blit(diff_text, diff_rect)
        
        # Управление
        controls = self.font_small.render('WASD - движение | SPACE - удар | E - пас | Q - отбор | P - пауза', 
                                         True, (200, 200, 200))
        controls_rect = controls.get_rect(center=(600, 670))
        self.screen.blit(controls, controls_rect)
        
        # Пауза
        if self.paused:
            pause_text = self.font_large.render('⏸️ ПАУЗА', True, (255, 255, 0))
            pause_rect = pause_text.get_rect(center=(600, 350))
            self.screen.blit(pause_text, pause_rect)
        
        # Результат матча (если завершен)
        if self.match_finished:
            overlay = pygame.Surface((1200, 700))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Результат
            if self.score['home'] > self.score['away']:
                result_text = '🏆 ПОБЕДА!'
                result_color = (0, 255, 0)
            elif self.score['home'] < self.score['away']:
                result_text = '💔 ПОРАЖЕНИЕ'
                result_color = (255, 0, 0)
            else:
                result_text = '🤝 НИЧЬЯ'
                result_color = (255, 255, 0)
            
            text = self.font_large.render(result_text, True, result_color)
            text_rect = text.get_rect(center=(600, 280))
            self.screen.blit(text, text_rect)
            
            # Счет
            score_text = self.font_large.render(f'{self.score["home"]} : {self.score["away"]}', True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(600, 370))
            self.screen.blit(score_text, score_rect)
            
            # Награды
            reward_text = self.font_medium.render('Нажми ESC для выхода', True, (200, 200, 200))
            reward_rect = reward_text.get_rect(center=(600, 450))
            self.screen.blit(reward_text, reward_rect)
