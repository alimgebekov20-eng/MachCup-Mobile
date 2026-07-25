import pygame
import math
import random

class Player:
    """Базовый класс игрока"""
    def __init__(self, x, y, color, name, stats, is_player=False, player_data=None):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.stats = stats  # {'speed': 7, 'power': 7, 'accuracy': 7, 'defense': 7}
        self.is_player = is_player
        self.player_data = player_data
        self.radius = 18
        
        # Движение
        self.vx = 0
        self.vy = 0
        self.speed = 3.5
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False
        
        # Состояние
        self.has_ball = False
        self.target_x = x
        self.target_y = y
        self.team = None  # 'home' or 'away'
        self.role = 'forward'
        
        # Характеристики (с учетом скинов)
        self.final_stats = stats.copy()
        
        # Применяем скины если есть данные
        if player_data:
            self.apply_skins()
    
    def apply_skins(self):
        """Применение бонусов от скинов"""
        if not self.player_data:
            return
        
        # Получаем экипированные скины для текущего персонажа
        character = self.player_data.get('selected_character', 'Азиз')
        equipped = self.player_data.get('characters', {}).get(character, {}).get('skin_equipped', {})
        
        for slot_id, skin_name in equipped.items():
            bonuses = self.get_skin_bonus(skin_name)
            if bonuses:
                for stat, bonus in bonuses.items():
                    if stat in self.final_stats:
                        self.final_stats[stat] += bonus // 10  # Преобразуем проценты в очки
    
    def get_skin_bonus(self, skin_name):
        """Получение бонусов скина из JSON"""
        # Загружаем данные скинов
        import json
        import os
        
        try:
            with open('data/skins.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for skin in data['skins']:
                    if skin['name'] == skin_name:
                        return skin.get('bonuses', {})
        except:
            pass
        
        # Если файл не найден - возвращаем дефолтные бонусы
        default_bonuses = {
            'Повязка': {'speed': 1},
            'Бандана': {'speed': 3},
            'Шлем': {'speed': 5, 'defense': 2},
            'Корона': {'speed': 8, 'accuracy': 5},
            'Золотой шлем': {'speed': 12, 'defense': 8},
            'Нимб бога': {'speed': 20, 'accuracy': 10},
            'Майка': {'power': 1},
            'Футболка': {'power': 3},
            'Броня': {'power': 5, 'defense': 2},
            'Латы': {'power': 8, 'defense': 5},
            'Золотая броня': {'power': 12, 'defense': 8},
            'Доспехи бога': {'power': 20, 'defense': 10},
            'Шорты': {'accuracy': 1},
            'Наголенники': {'accuracy': 3},
            'Щитки': {'speed': 2, 'accuracy': 5},
            'Поножи': {'accuracy': 8},
            'Золотые поножи': {'accuracy': 12},
            'Ноги бога': {'accuracy': 20},
            'Кеды': {'speed': 1},
            'Кроссовки': {'speed': 3, 'accuracy': 1},
            'Бутсы': {'speed': 5, 'accuracy': 3},
            'Молнии': {'speed': 8, 'accuracy': 5},
            'Золотые бутсы': {'speed': 12, 'accuracy': 8},
            'Ботинки бога': {'speed': 20, 'accuracy': 10},
            'Нарукавник': {'defense': 1},
            'Перчатки': {'power': 1, 'defense': 3},
            'Напульсник': {'power': 3, 'defense': 5},
            'Амулет': {'power': 5, 'defense': 8},
            'Золотой амулет': {'power': 8, 'defense': 12},
            'Артефакт бога': {'power': 10, 'defense': 20}
        }
        return default_bonuses.get(skin_name, {})
    
    def update(self):
        """Обновление позиции игрока"""
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
            
            # Нормализация диагонального движения
            if self.vx != 0 and self.vy != 0:
                self.vx *= 0.707
                self.vy *= 0.707
        else:
            # Боты двигаются по ИИ
            pass
        
        # Применение скорости с учетом характеристик
        speed_multiplier = self.final_stats.get('speed', 7) / 7
        self.x += self.vx * speed_multiplier
        self.y += self.vy * speed_multiplier
        
        # Границы поля
        self.x = max(60, min(1140, self.x))
        self.y = max(60, min(640, self.y))
    
    def shoot(self, ball, target_x, target_y):
        """Удар по воротам"""
        if not self.has_ball:
            return
        
        distance = math.hypot(target_x - self.x, target_y - self.y)
        power_base = self.final_stats.get('power', 7) * 0.8
        
        # Сила зависит от расстояния
        if distance < 150:
            power = power_base * 0.5
        elif distance < 300:
            power = power_base * 0.7
        elif distance < 500:
            power = power_base * 0.9
        else:
            power = power_base * 1.0
        
        # Точность
        accuracy = self.final_stats.get('accuracy', 7) * 0.7
        angle_offset = (1 - accuracy / 10) * random.uniform(-0.4, 0.4)
        angle = math.atan2(target_y - self.y, target_x - self.x) + angle_offset
        
        # Добавляем случайность
        power *= random.uniform(0.85, 1.15)
        
        ball.vx = power * math.cos(angle)
        ball.vy = power * math.sin(angle)
        self.has_ball = False
        
        # Звук удара (если есть)
        try:
            kick_sound = pygame.mixer.Sound('assets/sounds/kick.wav')
            kick_sound.play()
        except:
            pass
    
    def pass_ball(self, ball, teammates):
        """Пас партнеру"""
        if not self.has_ball:
            return
        
        # Находим лучшего партнера для паса
        best_teammate = None
        best_score = -999
        
        for teammate in teammates:
            if teammate == self or teammate.team != self.team:
                continue
            
            # Оценка: близость к воротам противника + свободное пространство
            dist_to_goal = teammate.distance_to_point(1050 if teammate.team == 'home' else 50, 350)
            danger = sum(1 for p in teammates if p.team != self.team and p.distance_to(teammate) < 100)
            score = -dist_to_goal * 0.01 - danger * 2
            
            # Атакующие игроки имеют приоритет
            if teammate.role == 'forward':
                score += 30
            
            if score > best_score:
                best_score = score
                best_teammate = teammate
        
        if best_teammate and self.distance_to(best_teammate) < 500:
            angle = math.atan2(best_teammate.y - self.y, best_teammate.x - self.x)
            distance = self.distance_to(best_teammate)
            power = min(8, distance / 50)
            
            # Точность паса
            accuracy = self.final_stats.get('accuracy', 7) * 0.5
            angle_offset = (1 - accuracy / 10) * random.uniform(-0.2, 0.2)
            angle += angle_offset
            
            ball.vx = power * math.cos(angle)
            ball.vy = power * math.sin(angle)
            self.has_ball = False
    
    def tackle(self, ball):
        """Отбор мяча"""
        if self.distance_to(ball) < self.radius + ball.radius + 15:
            # Сила отбора зависит от защиты
            defense = self.final_stats.get('defense', 7) / 10
            power = 3 + random.random() * 3 * defense
            
            angle = math.atan2(ball.y - self.y, ball.x - self.x)
            ball.vx = power * math.cos(angle + random.uniform(-0.3, 0.3))
            ball.vy = power * math.sin(angle + random.uniform(-0.3, 0.3))
            self.has_ball = True
            return True
        return False
    
    def distance_to(self, obj):
        return math.hypot(self.x - obj.x, self.y - obj.y)
    
    def distance_to_point(self, x, y):
        return math.hypot(self.x - x, self.y - y)
    
    def draw(self, screen):
        """Отрисовка игрока"""
        # Тень
        pygame.draw.circle(screen, (50, 50, 50), (int(self.x + 3), int(self.y + 3)), self.radius)
        
        # Основной круг
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)
        
        # Имя игрока
        font = pygame.font.Font(None, 14)
        text = font.render(self.name[:12], True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y - self.radius - 15))
        screen.blit(text, text_rect)
        
        # Индикатор владения мячом
        if self.has_ball:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 6)
        
        # Роль
        role_icons = {
            'forward': '⚡',
            'defender': '🛡️',
            'midfielder': '🎯',
            'goalkeeper': '🧤'
        }
        role_text = font.render(role_icons.get(self.role, ''), True, (255, 255, 255))
        screen.blit(role_text, (self.x + self.radius + 5, self.y - 10))
        
        # Если игрок - показывает стрелки управления
        if self.is_player:
            # Рамка вокруг игрока
            pygame.draw.circle(screen, (0, 255, 255), (int(self.x), int(self.y)), self.radius + 4, 2)

class Bot(Player):
    """Бот с искусственным интеллектом"""
    def __init__(self, x, y, color, name, stats, team, difficulty='medium', player_data=None):
        super().__init__(x, y, color, name, stats, is_player=False, player_data=player_data)
        self.team = team
        self.difficulty = difficulty
        self.target_x = x
        self.target_y = y
        self.decision_timer = 0
        self.action_timer = 0
        self.pass_cooldown = 0
        self.stuck_counter = 0
        self._last_x = x
        self._last_y = y
        
        # Настройка сложности
        difficulty_settings = {
            'easy': {'speed': 0.5, 'accuracy': 0.4, 'aggression': 0.2, 'reaction': 30},
            'medium': {'speed': 0.75, 'accuracy': 0.7, 'aggression': 0.5, 'reaction': 20},
            'hard': {'speed': 0.95, 'accuracy': 0.9, 'aggression': 0.8, 'reaction': 10}
        }
        self.diff = difficulty_settings.get(difficulty, difficulty_settings['medium'])
        
        # Определяем роль по позиции
        self.role = self.determine_role()
    
    def determine_role(self):
        """Определение роли на поле"""
        if self.x < 250:
            return 'defender'
        elif self.x > 750:
            return 'forward'
        else:
            return 'midfielder'
    
    def update(self, ball, players, goalkeepers, goals):
        """Обновление ИИ бота"""
        self.action_timer += 1
        
        # Обновляем роль каждые 5 секунд
        if self.action_timer % 300 == 0:
            self.role = self.determine_role()
        
        # Поиск цели в зависимости от роли
        if self.role == 'defender':
            # Защитник: держится ближе к своим воротам
            if self.team == 'home':
                self.target_x = 200 + random.randint(-30, 30)
                self.target_y = 350 + random.randint(-50, 50)
            else:
                self.target_x = 900 + random.randint(-30, 30)
                self.target_y = 350 + random.randint(-50, 50)
            
            # Если мяч рядом - перехват
            if self.distance_to(ball) < 150:
                self.target_x = ball.x
                self.target_y = ball.y
        
        elif self.role == 'forward':
            # Нападающий: у чужих ворот
            if self.team == 'home':
                self.target_x = 1000 + random.randint(-50, 0)
                self.target_y = 350 + random.randint(-80, 80)
            else:
                self.target_x = 150 + random.randint(0, 50)
                self.target_y = 350 + random.randint(-80, 80)
            
            # Если мяч в атаке - бежим за ним
            if self.team == 'home' and ball.x > 400:
                self.target_x = ball.x + 30
                self.target_y = ball.y
            elif self.team == 'away' and ball.x < 600:
                self.target_x = ball.x - 30
                self.target_y = ball.y
        
        else:  # midfielder
            # Полузащитник: центр поля
            self.target_x = 500 + random.randint(-100, 100)
            self.target_y = 350 + random.randint(-100, 100)
            
            # Если мяч рядом - перехват
            if self.distance_to(ball) < 200:
                self.target_x = ball.x
                self.target_y = ball.y
        
        # Движение к цели
        self.move_to_target()
        
        # Проверка застревания
        self.check_stuck()
        
        # Принятие решений
        if self.action_timer % max(1, int(self.diff['reaction'])) == 0:
            self.make_decision(ball, players, goalkeepers, goals)
        
        # Обновление пас-кулдауна
        if self.pass_cooldown > 0:
            self.pass_cooldown -= 1
    
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
        # Проверка движения
        if abs(self.x - self._last_x) < 2 and abs(self.y - self._last_y) < 2:
            self.stuck_counter += 1
            if self.stuck_counter > 30:  # 0.5 секунды
                # Смена цели со случайным смещением
                self.target_x += random.randint(-150, 150)
                self.target_y += random.randint(-150, 150)
                
                # Если бот застрял у границы - разворачиваем
                if self.x < 100:
                    self.target_x = 600 + random.randint(0, 200)
                elif self.x > 1100:
                    self.target_x = 600 - random.randint(0, 200)
                if self.y < 100:
                    self.target_y = 350 + random.randint(0, 200)
                elif self.y > 600:
                    self.target_y = 350 - random.randint(0, 200)
                
                self.stuck_counter = 0
        else:
            self.stuck_counter = max(0, self.stuck_counter - 1)
        
        self._last_x = self.x
        self._last_y = self.y
    
    def make_decision(self, ball, players, goalkeepers, goals):
        """Принятие решения"""
        # Если у меня мяч
        if self.has_ball:
            # Проверка удара по воротам
            if self.role in ['forward', 'midfielder']:
                # Находим ворота противника
                enemy_goal = goals[1] if self.team == 'home' else goals[0]
                goal_x = enemy_goal['x'] + enemy_goal['width'] / 2
                goal_y = enemy_goal['y'] + enemy_goal['height'] / 2
                
                # Если близко к воротам
                if self.distance_to_point(goal_x, goal_y) < 400:
                    # Шанс удара зависит от сложности и роли
                    shoot_chance = 0.3 * self.diff['accuracy']
                    if self.role == 'forward':
                        shoot_chance *= 1.5
                    
                    if random.random() < shoot_chance:
                        # Удар с учетом точности
                        goal_offset_y = random.randint(-40, 40)
                        self.shoot(ball, goal_x, goal_y + goal_offset_y)
                        return
            
            # Пас партнеру
            if self.pass_cooldown <= 0 and random.random() < 0.6 * self.diff['accuracy']:
                teammates = [p for p in players if p != self and p.team == self.team and not p.has_ball]
                if teammates:
                    # Выбираем лучшего партнера
                    best = None
                    best_score = -999
                    
                    for tm in teammates:
                        # Оценка: близко к воротам противника + нет врагов рядом
                        enemy_goal = goals[1] if self.team == 'home' else goals[0]
                        goal_x = enemy_goal['x'] + enemy_goal['width'] / 2
                        goal_y = enemy_goal['y'] + enemy_goal['height'] / 2
                        
                        dist_to_goal = tm.distance_to_point(goal_x, goal_y)
                        danger = sum(1 for p in players if p.team != self.team and p.distance_to(tm) < 100)
                        score = -dist_to_goal * 0.01 - danger * 2
                        
                        if tm.role == 'forward':
                            score += 40
                        
                        if score > best_score:
                            best_score = score
                            best = tm
                    
                    if best and self.distance_to(best) < 500:
                        self.pass_ball(ball, [best])
                        self.pass_cooldown = 20
                        return
            
            # Движение к воротам
            enemy_goal = goals[1] if self.team == 'home' else goals[0]
            self.target_x = enemy_goal['x'] + enemy_goal['width'] / 2 + random.randint(-50, 50)
            self.target_y = enemy_goal['y'] + enemy_goal['height'] / 2 + random.randint(-50, 50)
            return
        
        # Мяч у противника - перехват
        enemy_with_ball = None
        for enemy in players:
            if enemy.team != self.team and enemy.has_ball:
                enemy_with_ball = enemy
                break
        
        if enemy_with_ball:
            # Бежим к противнику с мячом
            self.target_x = enemy_with_ball.x
            self.target_y = enemy_with_ball.y
            
            # Попытка отбора
            if self.distance_to(enemy_with_ball) < 60 and random.random() < self.diff['aggression']:
                self.tackle(ball)
                return
        
        # Если мяч свободен - бежим к нему
        if not any(p.has_ball for p in players):
            # Проверяем, кто ближе к мячу
            if self.distance_to(ball) < 200:
                self.target_x = ball.x
                self.target_y = ball.y
    
    def draw(self, screen):
        """Отрисовка бота"""
        # Тень
        pygame.draw.circle(screen, (50, 50, 50), (int(self.x + 3), int(self.y + 3)), self.radius)
        
        # Основной круг с градиентом
        color = self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)
        
        # Имя
        font = pygame.font.Font(None, 13)
        text = font.render(self.name[:12], True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y - self.radius - 15))
        screen.blit(text, text_rect)
        
        # Индикатор мяча
        if self.has_ball:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 5)
        
        # Роль иконка
        role_icons = {
            'forward': '⚡',
            'defender': '🛡️',
            'midfielder': '🎯'
        }
        role_text = font.render(role_icons.get(self.role, ''), True, (255, 255, 255))
        screen.blit(role_text, (self.x + self.radius + 5, self.y - 10))
        
        # Индикатор сложности
        if self.difficulty == 'hard':
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x - self.radius - 5), int(self.y - self.radius - 5)), 3)
        elif self.difficulty == 'medium':
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x - self.radius - 5), int(self.y - self.radius - 5)), 3)
        else:
            pygame.draw.circle(screen, (0, 255, 0), (int(self.x - self.radius - 5), int(self.y - self.radius - 5)), 3)

class Goalkeeper(Player):
    """Вратарь"""
    def __init__(self, x, y, color, name, team, player_data=None):
        stats = {'speed': 5, 'power': 8, 'accuracy': 8, 'defense': 10}
        super().__init__(x, y, color, name, stats, is_player=False, player_data=player_data)
        self.team = team
        self.radius = 24
        self.target_x = x
        self.target_y = y
        self.reaction_timer = 0
        self.role = 'goalkeeper'
        
        # Настройка вратаря
        self.reaction_speed = 15  # чем меньше, тем быстрее реакция
        self.max_speed = 4.5
    
    def update(self, ball, goals):
        """Обновление вратаря"""
        self.reaction_timer += 1
        
        # Находим свои ворота
        my_goal = None
        for goal in goals:
            if (self.team == 'home' and goal['team'] == 'home') or \
               (self.team == 'away' and goal['team'] == 'away'):
                my_goal = goal
                break
        
        if not my_goal:
            return
        
        goal_x = my_goal['x'] + my_goal['width'] / 2
        goal_y = my_goal['y'] + my_goal['height'] / 2
        
        # Реакция на мяч
        dist_to_ball = self.distance_to(ball)
        dist_to_goal = math.hypot(ball.x - goal_x, ball.y - goal_y)
        
        if dist_to_goal < 250 and dist_to_ball < 300:
            # Мяч близко к воротам - реакция
            if self.reaction_timer > self.reaction_speed:
                # Предсказываем движение мяча
                predict_x = ball.x + ball.vx * 10
                predict_y = ball.y + ball.vy * 10
                
                # Добавляем небольшой разброс для реалистичности
                noise_x = random.randint(-10, 10)
                noise_y = random.randint(-10, 10)
                
                self.target_x = predict_x + noise_x
                self.target_y = predict_y + noise_y
                self.reaction_timer = 0
        else:
            # Возврат на линию ворот
            self.target_x = goal_x + 20
            self.target_y = goal_y
        
        # Движение к цели (с ограничением скорости)
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 5:
            speed = min(self.max_speed, dist / 10)
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
            self.x += self.vx
            self.y += self.vy
        
        # Ограничение в штрафной площади
        if self.team == 'home':
            self.x = max(50, min(150, self.x))
        else:
            self.x = max(1050, min(1150, self.x))
        self.y = max(290, min(410, self.y))
        
        # Проверка на застревание
        if not hasattr(self, '_last_x'):
            self._last_x = self.x
            self._last_y = self.y
            self._stuck_counter = 0
        
        if abs(self.x - self._last_x) < 1 and abs(self.y - self._last_y) < 1:
            self._stuck_counter += 1
            if self._stuck_counter > 60:
                self.target_x = goal_x + 20 + random.randint(-20, 20)
                self.target_y = goal_y + random.randint(-20, 20)
                self._stuck_counter = 0
        else:
            self._stuck_counter = 0
        
        self._last_x = self.x
        self._last_y = self.y
        
        # Попытка поймать мяч
        if self.distance_to(ball) < self.radius + ball.radius + 10:
            if abs(ball.vx) > 0.5 or abs(ball.vy) > 0.5:
                # Ловим мяч с вероятностью от защиты
                catch_chance = 0.7 + (self.final_stats.get('defense', 10) / 100)
                if random.random() < catch_chance:
                    ball.vx = 0
                    ball.vy = 0
                    self.has_ball = True
                    
                    # Выбиваем мяч после ловли
                    if self.reaction_timer > 10:
                        self.kick_ball(ball)
                        self.reaction_timer = 0
    
    def kick_ball(self, ball):
        """Выбить мяч после ловли"""
        if not self.has_ball:
            return
        
        # Выбиваем в центр поля или на нападающего
        if self.team == 'home':
            target_x = 600 + random.randint(-100, 100)
        else:
            target_x = 600 + random.randint(-100, 100)
        target_y = 350 + random.randint(-100, 100)
        
        angle = math.atan2(target_y - self.y, target_x - self.x)
        power = 5 + random.random() * 5
        
        ball.vx = power * math.cos(angle)
        ball.vy = power * math.sin(angle)
        self.has_ball = False
    
    def draw(self, screen):
        """Отрисовка вратаря"""
        # Тень
        pygame.draw.circle(screen, (50, 50, 50), (int(self.x + 3), int(self.y + 3)), self.radius)
        
        # Вратарь
        color = self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 3)
        
        # Имя
        font = pygame.font.Font(None, 14)
        text = font.render('🧤 ' + self.name[:8], True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y - self.radius - 18))
        screen.blit(text, text_rect)
        
        # Индикатор владения мячом
        if self.has_ball:
            pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), 8, 2)
        
        # Линия штрафной (для наглядности)
        if self.team == 'home':
            pygame.draw.rect(screen, (255, 255, 255, 50), (50, 280, 120, 140), 1)
        else:
            pygame.draw.rect(screen, (255, 255, 255, 50), (1050-120, 280, 120, 140), 1)
