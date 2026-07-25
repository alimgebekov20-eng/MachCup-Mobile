import pygame
import math
import random
from player import Player, Bot, Goalkeeper
from ball import Ball
from ui import GameUI
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
        
        # UI
        self.ui = GameUI(screen)
        
        # Флаги
        self.goal_scored = False
        self.goal_timer = 0
        self.match_finished = False
        
        self.init_teams()
    
    def init_teams(self):
        """Инициализация команд"""
        # Персонажи
        characters = {
            'Азиз': {'speed': 8, 'power': 9, 'accuracy': 7, 'defense': 4},
            'Хабиб': {'speed': 7, 'power': 7, 'accuracy': 7, 'defense': 7},
            'Абдул': {'speed': 6, 'power': 5, 'accuracy': 7, 'defense': 9},
            'Шамиль Рб': {'speed': 9, 'power': 6, 'accuracy': 6, 'defense': 5},
            'Шамиль Jr.': {'speed': 7, 'power': 8, 'accuracy': 8, 'defense': 6},
            'Салаудин': {'speed': 5, 'power': 9, 'accuracy': 8, 'defense': 8}
        }
        
        # Выбор состава в зависимости от режима
        if self.mode == '2x2':
            home_team = ['Азиз', 'Хабиб']
            away_team = ['Шамиль Рб', 'Шамиль Jr.']
        else:  # '3x3' или 'training'
            home_team = ['Азиз', 'Хабиб', 'Абдул']
            away_team = ['Шамиль Рб', 'Шамиль Jr.', 'Салаудин']
        
        # Позиции на поле
        home_positions = [(150, 350), (250, 250), (250, 450)]  # защитник, полузащитник, нападающий
        away_positions = [(900, 350), (800, 250), (800, 450)]
        goal_positions = [(50, 350), (1050, 350)]
        
        # Создаем игроков домашней команды
        for i, name in enumerate(home_team):
            pos = home_positions[i % len(home_positions)]
            stats = characters.get(name, {'speed': 7, 'power': 7, 'accuracy': 7, 'defense': 7})
            
            # Проверяем, это игрок или бот
            if name == self.character and not self.match_data:
                # Игрок
                player = Player(pos[0], pos[1], (0, 0, 255), name, stats, is_player=True)
            else:
                # Бот
                player = Bot(pos[0], pos[1], (100, 100, 255), name, stats, 'home', self.difficulty)
            
            player.team = 'home'
            self.players.append(player)
        
        # Создаем игроков гостевой команды
        for i, name in enumerate(away_team):
            pos = away_positions[i % len(away_positions)]
            stats = characters.get(name, {'speed': 7, 'power': 7, 'accuracy': 7, 'defense': 7})
            
            player = Bot(pos[0], pos[1], (255, 0, 0), name, stats, 'away', self.difficulty)
            player.team = 'away'
            self.players.append(player)
        
        # Вратари
        self.goalkeepers = [
            Goalkeeper(70, 350, (0, 0, 200), 'ГК', 'home'),
            Goalkeeper(1030, 350, (200, 0, 0), 'ГК', 'away')
        ]
        
        # Ворота
        self.goals = [
            {'x': 50, 'y': 300, 'width': 10, 'height': 100, 'team': 'home'},
            {'x': 1050, 'y': 300, 'width': 10, 'height': 100, 'team': 'away'}
        ]
    
    def start(self):
        """Начало матча"""
        self.running = True
        self.time = 0
        self.score = {'home': 0, 'away': 0}
        
        # Центральный удар
        self.ball.x = 600
        self.ball.y = 350
        self.ball.vx = random.uniform(-2, 2)
        self.ball.vy = random.uniform(-2, 2)
    
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
                continue  # Игрок управляется пользователем
            player.update(self.ball, self.players, self.goalkeepers, self.goals)
        
        # Обновление вратарей
        for gk in self.goalkeepers:
            gk.update(self.ball, self.goals)
        
        # Проверка столкновений
        self.check_collisions()
        
        # Обновление UI
        self.ui.update(self.time, self.score, self.mode)
    
    def check_collisions(self):
        """Проверка столкновений игроков с мячом"""
        for player in self.players:
            if player.distance_to(self.ball) < player.radius + self.ball.radius:
                # Отталкивание мяча
                angle = math.atan2(self.ball.y - player.y, self.ball.x - player.x)
                power = 3 + random.random() * 2
                self.ball.vx = power * math.cos(angle)
                self.ball.vy = power * math.sin(angle)
                
                # Если игрок владеет мячом
                player.has_ball = True
                for other in self.players:
                    if other != player:
                        other.has_ball = False
    
    def check_goals(self):
        """Проверка гола"""
        for goal in self.goals:
            # Проверка пересечения линии ворот
            if goal['team'] == 'home':
                if self.ball.x < goal['x'] + goal['width'] and \
                   goal['y'] < self.ball.y < goal['y'] + goal['height']:
                    # Гол в домашние ворота (автогол или гол гостей)
                    self.score['away'] += 1
                    self.goal_scored = True
                    self.goal_timer = 60
                    self.reset_ball()
                    self.check_achievements('away')
            else:  # away goal
                if self.ball.x + self.ball.radius > goal['x'] and \
                   goal['y'] < self.ball.y < goal['y'] + goal['height']:
                    self.score['home'] += 1
                    self.goal_scored = True
                    self.goal_timer = 60
                    self.reset_ball()
                    self.check_achievements('home')
    
    def reset_ball(self):
        """Сброс мяча после гола"""
        self.ball.x = 600
        self.ball.y = 350
        self.ball.vx = 0
        self.ball.vy = 0
        self.goal_timer = 60
    
    def check_achievements(self, team):
        """Проверка достижений"""
        if team == 'home':
            # Проверка хет-трика
            if self.score['home'] >= 3:
                self.save_manager.unlock_achievement(self.player_data, 'hat_trick')
            
            # Проверка сухой победы
            if self.score['away'] == 0 and self.score['home'] >= 3:
                self.save_manager.unlock_achievement(self.player_data, 'clean_sheet')
    
    def end_match(self):
        """Завершение матча"""
        self.match_finished = True
        
        # Расчет наград
        if self.score['home'] > self.score['away']:
            result = 'win'
            stars_earned = 0.5 + (self.score['home'] - self.score['away']) * 0.1
            crystals_earned = 50
            
            if self.score['away'] == 0:
                stars_earned += 0.3
                crystals_earned += 30
            
            if self.score['home'] >= 3:
                stars_earned += 0.2
                crystals_earned += 25
            
            # Бонус за сложность
            difficulty_bonus = {'easy': 1, 'medium': 1.5, 'hard': 2}
            crystals_earned *= difficulty_bonus.get(self.difficulty, 1)
            
            # Обновление статистики
            self.player_data['global_stats']['wins'] += 1
            self.player_data['global_stats']['streak'] += 1
            self.player_data['global_stats']['best_streak'] = max(
                self.player_data['global_stats']['best_streak'],
                self.player_data['global_stats']['streak']
            )
            
        elif self.score['home'] < self.score['away']:
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
        self.player_data['global_stats']['goals_scored'] += self.score['home']
        self.player_data['global_stats']['goals_conceded'] += self.score['away']
        self.player_data['global_stats']['crystals'] += int(crystals_earned)
        
        # Сохранение
        self.save_manager.save(self.player_data)
        
        # Отображение результата
        self.ui.show_result(result, self.score, stars_earned, crystals_earned)
    
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
            player.shoot(self.ball, 600, 350)  # Удар по воротам
        elif key == pygame.K_e:
            player.pass_ball(self.ball, self.players)  # Пас
        elif key == pygame.K_q:
            player.tackle(self.ball)  # Отбор
        elif key == pygame.K_p:
            self.paused = not self.paused
    
    def draw(self):
        """Отрисовка игры"""
        self.screen.fill((34, 177, 76))  # Зеленое поле
        
        # Отрисовка поля
        self.draw_field()
        
        # Отрисовка ворот
        for goal in self.goals:
            pygame.draw.rect(self.screen, (255, 255, 255), 
                           (goal['x'], goal['y'], goal['width'], goal['height']))
        
        # Отрисовка игроков
        for player in self.players:
            player.draw(self.screen)
        
        # Отрисовка вратарей
        for gk in self.goalkeepers:
            gk.draw(self.screen)
        
        # Отрисовка мяча
        self.ball.draw(self.screen)
        
        # Отрисовка UI
        self.ui.draw(self.screen)
        
        # Информация о сложности
        if self.mode != 'online':
            difficulty_names = {'easy': 'ЛЕГКО', 'medium': 'СРЕДНЕ', 'hard': 'СЛОЖНО'}
            font = pygame.font.Font(None, 24)
            text = font.render(f'Сложность: {difficulty_names.get(self.difficulty, "СРЕДНЕ")}', True, (255, 255, 255))
            self.screen.blit(text, (10, 10))
    
    def draw_field(self):
        """Отрисовка футбольного поля"""
        # Центральный круг
        pygame.draw.circle(self.screen, (255, 255, 255), (600, 350), 80, 2)
        
        # Центральная линия
        pygame.draw.line(self.screen, (255, 255, 255), (600, 50), (600, 650), 2)
        
        # Штрафные площади
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 250, 120, 200), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (1050-120, 250, 120, 200), 2)
        
        # Вратарские площади
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 300, 70, 100), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (1050-70, 300, 70, 100), 2)
