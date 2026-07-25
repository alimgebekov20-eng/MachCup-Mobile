import pygame
import math
import random

class Player:
    def __init__(self, x, y, color, name, stats, is_player=False):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.stats = stats  # {'speed': 7, 'power': 7, 'accuracy': 7, 'defense': 7}
        self.is_player = is_player
        self.radius = 18
        
        # Движение
        self.vx = 0
        self.vy = 0
        self.speed = 3.5
        self.move_up = False        self.move_down = False
        self.move_left = False
        self.move_right = False
        
        # Состояние
        self.has_ball = False
        self.target_x = x
        self.target_y = y
        self.team = None  # 'home' or 'away'
        
        # Применяем скины
        self.apply_skins()
    
    def apply_skins(self):
        """Применение бонусов от скинов"""
        # Загрузка скинов из данных игрока
        if hasattr(self, 'player_data') and self.player_data:
            equipped = self.player_data.get('equipped_skins', {})
            for slot_id, skin_name in equipped.items():
                # Получаем бонусы скина
                skin_bonus = self.get_skin_bonus(skin_name)
                if skin_bonus:
                    self.stats['speed'] += skin_bonus.get('speed', 0)
                    self.stats['power'] += skin_bonus.get('power', 0)
                    self.stats['accuracy'] += skin_bonus.get('accuracy', 0)
                    self.stats['defense'] += skin_bonus.get('defense', 0)
    
    def get_skin_bonus(self, skin_name):
        """Получение бонусов скина"""
        skin_bonuses = {
            'Бандана': {'speed': 3},
            'Шлем': {'speed': 5, 'defense': 2},
            'Корона': {'speed': 8, 'accuracy': 5},
            'Золотой шлем': {'speed': 12, 'defense': 8},
            'Нимб бога': {'speed': 20, 'accuracy': 10},
            # ... остальные скины
        }
        return skin_bonuses.get(skin_name, {})
    
    def update(self):
        """Обновление позиции"""
        if self.is_player:
            # Управление игроком
            self.vx = 0
            self.vy = 0
            if self.move_up:
                self.vy = -self.speed
            if self.move_down:
                self.vy = self.speed
            if self.move_left:
                self.vx = -self.speed
            if self.move_right:
                self.vx = self.speed
            
            # Нормализация
            if self.vx != 0 and self.vy != 0:
                self.vx *= 0.707
                self.vy *= 0.707
        
        # Движение
        self.x += self.vx
        self.y += self.vy
        
        # Границы поля
        self.x = max(80, min(1120, self.x))
        self.y = max(80, min(620, self.y))
    
    def shoot(self, ball, target_x, target_y):
        """Удар по воротам"""
        if not self.has_ball:
            return
        
        distance = math.hypot(target_x - self.x, target_y - self.y)
        power = self.stats.get('power', 7) * 0.8
        
        # Точность
        accuracy = self.stats.get('accuracy', 7) * 0.7
        angle_offset = (1 - accuracy / 10) * random.uniform(-0.5, 0.5)
        angle = math.atan2(target_y - self.y, target_x - self.x) + angle_offset
        
        # Сила в зависимости от расстояния
        if distance < 200:
            power *= 0.6
        elif distance < 400:
            power *= 0.8
        else:
            power *= 1.0
        
        ball.vx = power * math.cos(angle)
        ball.vy = power * math.sin(angle)
        self.has_ball = False
    
    def pass_ball(self, ball, teammates):
        """Пас партнеру"""
        if not self.has_ball:
            return
        
        # Находим ближайшего партнера
        nearest = None
        min_dist = float('inf')
        
        for teammate in teammates:
            if teammate == self or teammate.team != self.team:
                continue
            dist = math.hypot(teammate.x - self.x, teammate.y - self.y)
            if dist < min_dist:
                min_dist = dist
                nearest = teammate
        
        if nearest and min_dist < 500:
            angle = math.atan2(nearest.y - self.y, nearest.x - self.x)
            power = min(10, min_dist / 50)
            ball.vx = power * math.cos(angle)
            ball.vy = power * math.sin(angle)
            self.has_ball = False
    
    def tackle(self, ball):
        """Отбор мяча"""
        if self.distance_to(ball) < self.radius + ball.radius + 10:
            # Отбор
            ball.vx = random.uniform(-3, 3)
            ball.vy = random.uniform(-3, 3)
            self.has_ball = True
    
    def distance_to(self, obj):
        return math.hypot(self.x - obj.x, self.y - obj.y)
    
    def draw(self, screen):
        # Круг игрока
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)
        
        # Имя
        font = pygame.font.Font(None, 14)
        text = font.render(self.name[:10], True, (255, 255, 255))
        screen.blit(text, (self.x - 20, self.y - self.radius - 20))
        
        # Номер
        if self.has_ball:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 6)

class Bot(Player):
    def __init__(self, x, y, color, name, stats, team, difficulty='medium'):
        super().__init__(x, y, color, name, stats, is_player=False)
        self.team = team
        self.difficulty = difficulty
        self.target_x = x
        self.target_y = y
        self.decision_timer = 0
        self.action_timer = 0
        self.pass_cooldown = 0
        
        # Настройка сложности
        difficulty_settings = {
            'easy': {'speed': 0.5, 'accuracy': 0.4, 'aggression': 0.2},
            'medium': {'speed': 0.75, 'accuracy': 0.7, 'aggression': 0.5},
            'hard': {'speed': 0.95, 'accuracy': 0.9, 'aggression': 0.8}
        }
        self.diff = difficulty_settings.get(difficulty, difficulty_settings['medium'])
        
        # Позиционные роли
        self.role = self.determine_role()
    
    def determine_role(self):
        """Определение роли на поле"""
        if self.x < 300:
            return 'defender'
        elif self.x > 700:
            return 'forward'
        else:
            return 'midfielder'
    
    def update(self, ball, players, goalkeepers, goals):
        """Обновление ИИ бота"""
        self.action_timer += 1
        
        # Поиск цели
        if self.role == 'defender':
            # Защитник: держится ближе к своим воротам
            if self.team == 'home':
                self.target_x = 200
                self.target_y = 350
            else:
                self.target_x = 900
                self.target_y = 350
            
            # Если мяч рядом - перехват
            if self.distance_to(ball) < 200:
                self.target_x = ball.x
                self.target_y = ball.y
        
        elif self.role == 'forward':
            # Нападающий: у чужих ворот
            if self.team == 'home':
                self.target_x = 1000
                self.target_y = 350 + random.randint(-50, 50)
            else:
                self.target_x = 150
                self.target_y = 350 + random.randint(-50, 50)
            
            # Если мяч в атаке - бежим к нему
            if ball.x > 400 and self.team == 'home':
                self.target_x = ball.x + 50
                self.target_y = ball.y
            elif ball.x < 600 and self.team == 'away':
                self.target_x = ball.x - 50
                self.target_y = ball.y
        
        else:  # midfielder
            # Полузащитник: центр поля
            self.target_x = 500
            self.target_y = 350 + random.randint(-100, 100)
            
            # Если мяч рядом - перехват
            if self.distance_to(ball) < 250:
                self.target_x = ball.x
                self.target_y = ball.y
        
        # Движение к цели
        self.move_to_target()
        
        # Проверка застревания
        self.check_stuck()
        
        # Принятие решений
        if self.action_timer % 20 == 0:
            self.make_decision(ball, players, goalkeepers, goals)
    
    def move_to_target(self):
        """Движение к цели"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 5:
            speed = self.speed * self.diff['speed']
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
            self.x += self.vx
            self.y += self.vy
    
    def check_stuck(self):
        """Анти-застревание"""
        if not hasattr(self, '_last_x'):
            self._last_x = self.x
            self._last_y = self.y
            self._stuck_counter = 0
        
        # Проверка движения
        if abs(self.x - self._last_x) < 2 and abs(self.y - self._last_y) < 2:
            self._stuck_counter += 1
            if self._stuck_counter > 30:  # 0.5 секунды
                # Смена цели
                self.target_x += random.randint(-100, 100)
                self.target_y += random.randint(-100, 100)
                self._stuck_counter = 0
        else:
            self._stuck_counter = 0
        
        self._last_x = self.x
        self._last_y = self.y
    
    def make_decision(self, ball, players, goalkeepers, goals):
        """Принятие решения"""
        # Если у меня мяч
        if self.has_ball:
            # Проверка удара по воротам
            if self.role == 'forward' and self.distance_to_point(goals[1]['x'], goals[1]['y']) < 400:
                if random.random() < self.diff['accuracy']:
                    # Удар по воротам
                    target = (goals[1]['x'], goals[1]['y'] + random.randint(-30, 30))
                    self.shoot(ball, target[0], target[1])
                    return
            
            # Пас партнеру
            if self.pass_cooldown <= 0 and random.random() < 0.7:
                teammates = [p for p in players if p != self and p.team == self.team]
                if teammates:
                    # Выбираем лучшего партнера для паса
                    best = None
                    best_score = -999
                    
                    for tm in teammates:
                        # Оценка: близко к воротам противника + нет врагов рядом
                        dist_to_goal = tm.distance_to_point(goals[1]['x'], goals[1]['y'])
                        danger = sum(1 for p in players if p.team != self.team and p.distance_to(tm) < 100)
                        score = -dist_to_goal * 0.01 - danger * 2
                        
                        if self.role == 'forward':
                            score += 50
                        
                        if score > best_score:
                            best_score = score
                            best = tm
                    
                    if best:
                        self.pass_ball(ball, [best])
                        self.pass_cooldown = 30
                        return
            
            # Движение к воротам
            if self.team == 'home':
                self.target_x = 1000
            else:
                self.target_x = 150
            self.target_y = 350 + random.randint(-50, 50)
            return
        
        # Мяч у противника - перехват
        enemy_players = [p for p in players if p.team != self.team]
        for enemy in enemy_players:
            if enemy.has_ball and self.distance_to(enemy) < 150:
                # Бежим к противнику с мячом
                self.target_x = enemy.x
                self.target_y = enemy.y
                if self.distance_to(enemy) < 50 and random.random() < self.diff['aggression']:
                    # Отбор
                    self.tackle(ball)
                return
    
    def distance_to_point(self, x, y):
        return math.hypot(self.x - x, self.y - y)

class Goalkeeper(Player):
    def __init__(self, x, y, color, name, team):
        super().__init__(x, y, color, name, {'speed': 5, 'power': 8, 'accuracy': 8, 'defense': 10})
        self.team = team
        self.radius = 22
        self.target_x = x
        self.target_y = y
        self.reaction_timer = 0
    
    def update(self, ball, goals):
        """Обновление вратаря"""
        self.reaction_timer += 1
        
        # Находим свои ворота
        for goal in goals:
            if (self.team == 'home' and goal['team'] == 'home') or \
               (self.team == 'away' and goal['team'] == 'away'):
                goal_x = goal['x']
                goal_y = goal['y'] + goal['height'] / 2
                break
        
        # Реакция на мяч
        if abs(ball.x - goal_x) < 200 and abs(ball.y - goal_y) < 150:
            # Мяч близко к воротам - реакция с задержкой
            if self.reaction_timer > 12:  # 0.2 секунды задержки
                self.target_x = ball.x + random.randint(-20, 20)
                self.target_y = ball.y + random.randint(-20, 20)
                self.reaction_timer = 0
        else:
            # Возврат на линию ворот
            self.target_x = goal_x + 20
            self.target_y = goal_y
        
        # Движение к цели
        self.move_to_target()
        
        # Проверка на выход из штрафной
        if self.team == 'home':
            self.x = max(50, min(120, self.x))
        else:
            self.x = max(1080, min(1150, self.x))
        self.y = max(300, min(400, self.y))
    
    def move_to_target(self):
        """Движение к цели"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 5:
            speed = 4
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
            self.x += self.vx
            self.y += self.vy
