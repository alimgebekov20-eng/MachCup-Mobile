import pygame
import math

class UI:
    def __init__(self, screen, player_data, sounds=None):
        self.screen = screen
        self.player_data = player_data
        self.sounds = sounds or {}
        
        # Шрифты
        try:
            self.font_large = pygame.font.Font('assets/fonts/default.ttf', 72)
            self.font_medium = pygame.font.Font('assets/fonts/default.ttf', 48)
            self.font_small = pygame.font.Font('assets/fonts/default.ttf', 32)
            self.font_tiny = pygame.font.Font('assets/fonts/default.ttf', 24)
        except:
            self.font_large = pygame.font.Font(None, 72)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 32)
            self.font_tiny = pygame.font.Font(None, 24)
        
        # Загрузка аватарок
        self.avatars = {}
        players = ['aziz', 'khabib', 'abdul', 'shamil_rb', 'shamil_jr', 'salaudin']
        player_names = ['Азиз', 'Хабиб', 'Абдул', 'Шамиль Рб', 'Шамиль Jr.', 'Салаудин']
        
        for i, player in enumerate(players):
            try:
                img = pygame.image.load(f'assets/images/players/{player}.png')
                self.avatars[player_names[i]] = pygame.transform.scale(img, (60, 60))
            except:
                self.avatars[player_names[i]] = None
        
        # Настройки
        self.selected_difficulty = 'medium'
        self.selected_character = 'Азиз'
        self.message = None
        self.message_timer = 0
        self.message_color = (255, 255, 0)
        
        # Кнопки
        self.buttons = []
    
    def draw_menu(self):
        """Отрисовка главного меню"""
        # Фон
        self.screen.fill((34, 177, 76))
        
        # Логотип
        try:
            logo = pygame.image.load('assets/images/logo.png')
            logo = pygame.transform.scale(logo, (400, 150))
            logo_rect = logo.get_rect(center=(600, 100))
            self.screen.blit(logo, logo_rect)
        except:
            # Лого текстом
            title = self.font_large.render('⚽ STREET FOOTBALL LEGENDS', True, (255, 255, 255))
            title_rect = title.get_rect(center=(600, 100))
            self.screen.blit(title, title_rect)
        
        # Информация об игроке
        rating = self.player_data.get('rating', 50)
        crystals = self.player_data.get('crystals', 100)
        player_name = self.player_data.get('player_name', 'Игрок')
        
        info_text = f'👤 {player_name}  ⭐ {rating}/99  💎 {crystals}'
        info = self.font_medium.render(info_text, True, (255, 255, 255))
        info_rect = info.get_rect(center=(600, 180))
        self.screen.blit(info, info_rect)
        
        # Кнопки меню
        menu_items = [
            ('⚔️ БЫСТРЫЙ МАТЧ (2x2)', self.start_2x2),
            ('⚔️ БЫСТРЫЙ МАТЧ (3x3)', self.start_3x3),
            ('🎯 ТРЕНИРОВКА', self.start_training),
            ('🌐 ОНЛАЙН', self.go_online),
            ('👤 ПРОФИЛЬ', self.go_profile),
            ('📊 ТАБЛИЦА РЕЙТИНГОВ', self.show_leaderboard),
        ]
        
        self.buttons = []
        for i, (text, action) in enumerate(menu_items):
            y = 220 + i * 55
            rect = pygame.Rect(300, y, 600, 50)
            
            # Фон кнопки
            color = (0, 100, 0) if i % 2 == 0 else (0, 120, 0)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=10)
            
            # Текст
            label = self.font_medium.render(text, True, (255, 255, 255))
            label_rect = label.get_rect(center=(600, y + 25))
            self.screen.blit(label, label_rect)
            
            self.buttons.append({'rect': rect, 'action': action})
        
        # Нижняя панель
        bottom_text = f'Выбран персонаж: {self.selected_character}  |  Сложность: {self.get_difficulty_name()}'
        bottom = self.font_small.render(bottom_text, True, (255, 255, 255))
        bottom_rect = bottom.get_rect(center=(600, 660))
        self.screen.blit(bottom, bottom_rect)
        
        # Сообщение
        if self.message and self.message_timer > 0:
            msg_text = self.font_medium.render(self.message, True, self.message_color)
            msg_rect = msg_text.get_rect(center=(600, 350))
            
            # Фон для сообщения
            msg_bg = pygame.Surface((msg_rect.width + 40, msg_rect.height + 20))
            msg_bg.set_alpha(200)
            msg_bg.fill((0, 0, 0))
            bg_rect = msg_bg.get_rect(center=(600, 350))
            self.screen.blit(msg_bg, bg_rect)
            
            self.screen.blit(msg_text, msg_rect)
            self.message_timer -= 1
    
    def get_difficulty_name(self):
        """Получение названия сложности"""
        names = {'easy': '🟢 ЛЕГКО', 'medium': '🟡 СРЕДНЕ', 'hard': '🔴 СЛОЖНО'}
        return names.get(self.selected_difficulty, 'СРЕДНЕ')
    
    def draw_online_menu(self):
        """Отрисовка онлайн меню"""
        self.screen.fill((34, 177, 76))
        
        title = self.font_large.render('🌐 ОНЛАЙН РЕЖИМ', True, (255, 255, 255))
        title_rect = title.get_rect(center=(600, 100))
        self.screen.blit(title, title_rect)
        
        # Информация
        info = self.font_medium.render('Играй против реальных игроков!', True, (200, 200, 200))
        info_rect = info.get_rect(center=(600, 170))
        self.screen.blit(info, info_rect)
        
        online_items = [
            ('🔍 РЕЙТИНГОВЫЙ МАТЧ', self.find_ranked),
            ('🔍 ОБЫЧНЫЙ МАТЧ', self.find_casual),
            ('🏆 ТУРНИРНАЯ СЕТКА', self.find_tournament),
            ('↩️ НАЗАД', self.go_back)
        ]
        
        self.buttons = []
        for i, (text, action) in enumerate(online_items):
            y = 220 + i * 65
            rect = pygame.Rect(300, y, 600, 55)
            
            color = (0, 100, 0) if i % 2 == 0 else (0, 120, 0)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=10)
            
            label = self.font_medium.render(text, True, (255, 255, 255))
            label_rect = label.get_rect(center=(600, y + 27))
            self.screen.blit(label, label_rect)
            
            self.buttons.append({'rect': rect, 'action': action})
        
        # Статус подключения
        status = '🟢 Онлайн'  # Временно
        status_text = self.font_small.render(status, True, (0, 255, 0))
        status_rect = status_text.get_rect(center=(600, 640))
        self.screen.blit(status_text, status_rect)
    
    def draw_profile(self):
        """Отрисовка профиля"""
        self.screen.fill((34, 177, 76))
        
        # Заголовок
        title = self.font_large.render('👤 ПРОФИЛЬ', True, (255, 255, 255))
        title_rect = title.get_rect(center=(600, 60))
        self.screen.blit(title, title_rect)
        
        # Информация
        stats = self.player_data.get('global_stats', {})
        rating = self.player_data.get('rating', 50)
        crystals = self.player_data.get('crystals', 100)
        player_name = self.player_data.get('player_name', 'Игрок')
        
        wins = stats.get('wins', 0)
        matches = stats.get('matches', 0)
        win_rate = (wins / max(1, matches) * 100)
        
        # Аватарка
        avatar = self.avatars.get(self.selected_character)
        if avatar:
            self.screen.blit(avatar, (100, 130))
        
        info_lines = [
            f'Игрок: {player_name}',
            f'Персонаж: {self.selected_character}',
            f'Рейтинг: ⭐ {rating}/99',
            f'Кристаллы: 💎 {crystals}',
            '',
            f'📊 СТАТИСТИКА:',
            f'Матчей: {matches}',
            f'Побед: {wins} ({win_rate:.1f}%)',
            f'Голов забито: {stats.get("goals_scored", 0)}',
            f'Голов пропущено: {stats.get("goals_conceded", 0)}',
            f'Лучший стрик: {stats.get("best_streak", 0)}'
        ]
        
        for i, line in enumerate(info_lines):
            y = 130 + i * 40
            color = (255, 255, 0) if 'Рейтинг' in line else (255, 255, 255)
            if 'СТАТИСТИКА' in line:
                color = (200, 200, 200)
            text = self.font_small.render(line, True, color)
            self.screen.blit(text, (200, y))
        
        # Прогресс до 99 рейтинга
        progress = min(rating / 99, 1)
        bar_x, bar_y = 200, 530
        bar_width, bar_height = 600, 30
        
        # Фон прогресс-бара
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=15)
        # Заполнение
        pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=15)
        
        # Текст прогресса
        progress_text = self.font_small.render(f'{int(progress * 100)}% к 99 рейтингу', True, (255, 255, 255))
        progress_rect = progress_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        self.screen.blit(progress_text, progress_rect)
        
        # Кнопка назад
        back_rect = pygame.Rect(450, 600, 300, 50)
        pygame.draw.rect(self.screen, (0, 100, 0), back_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), back_rect, 2, border_radius=10)
        back_text = self.font_medium.render('↩️ НАЗАД', True, (255, 255, 255))
        back_rect_text = back_text.get_rect(center=(600, 625))
        self.screen.blit(back_text, back_rect_text)
        
        self.buttons = [{'rect': back_rect, 'action': self.go_back}]
    
    def draw_leaderboard(self, data):
        """Отрисовка таблицы рейтингов"""
        self.screen.fill((34, 177, 76))
        
        title = self.font_large.render('📊 ТАБЛИЦА РЕЙТИНГОВ', True, (255, 255, 255))
        title_rect = title.get_rect(center=(600, 50))
        self.screen.blit(title, title_rect)
        
        # Заголовки
        headers = ['#', 'Игрок', '⭐', 'Побед', 'Голов']
        colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
        
        for i, header in enumerate(headers):
            x = 150 + i * 170
            text = self.font_small.render(header, True, (255, 255, 255))
            self.screen.blit(text, (x, 100))
        
        # Разделительная линия
        pygame.draw.line(self.screen, (100, 100, 100), (100, 125), (1100, 125), 2)
        
        # Данные
        if isinstance(data, list):
            for rank, player in enumerate(data[:20], 1):
                y = 140 + rank * 35
                color = (255, 255, 255)
                if rank <= 3:
                    color = colors[rank-1]
                
                # Ранг
                rank_text = self.font_small.render(f'{rank}', True, color)
                self.screen.blit(rank_text, (150, y))
                
                # Имя
                name_text = self.font_small.render(player.get('name', 'Unknown')[:15], True, color)
                self.screen.blit(name_text, (220, y))
                
                # Рейтинг
                rating_text = self.font_small.render(f'⭐ {player.get("rating", 50)}', True, color)
                self.screen.blit(rating_text, (390, y))
                
                # Победы
                wins_text = self.font_small.render(f'{player.get("wins", 0)}', True, color)
                self.screen.blit(wins_text, (560, y))
                
                # Голы
                goals_text = self.font_small.render(f'{player.get("goals", 0)}', True, color)
                self.screen.blit(goals_text, (730, y))
                
                # Подсветка текущего игрока
                if player.get('name') == self.player_data.get('player_name'):
                    pygame.draw.rect(self.screen, (255, 255, 0), (140, y-5, 600, 30), 2)
        
        # Кнопка назад
        back_rect = pygame.Rect(450, 620, 300, 50)
        pygame.draw.rect(self.screen, (0, 100, 0), back_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), back_rect, 2, border_radius=10)
        back_text = self.font_medium.render('↩️ НАЗАД', True, (255, 255, 255))
        back_rect_text = back_text.get_rect(center=(600, 645))
        self.screen.blit(back_text, back_rect_text)
        
        self.buttons = [{'rect': back_rect, 'action': self.go_back}]
    
    def show_leaderboard(self):
        """Показать таблицу рейтингов (заглушка)"""
        data = [
            {'name': 'GOD', 'rating': 99, 'wins': 1250, 'goals': 5678},
            {'name': 'PRO', 'rating': 95, 'wins': 980, 'goals': 4321},
            {'name': 'LEGEND', 'rating': 90, 'wins': 890, 'goals': 3987},
            {'name': 'STAR', 'rating': 85, 'wins': 760, 'goals': 3456},
            {'name': 'ACE', 'rating': 80, 'wins': 670, 'goals': 2987},
            {'name': self.player_data.get('player_name', 'Игрок'), 
             'rating': self.player_data.get('rating', 50),
             'wins': self.player_data.get('global_stats', {}).get('wins', 0),
             'goals': self.player_data.get('global_stats', {}).get('goals_scored', 0)}
        ]
        self.draw_leaderboard(data)
    
    def show_message(self, text, color=(255, 255, 0)):
        """Показать сообщение"""
        self.message = text
        self.message_color = color
        self.message_timer = 180  # 3 секунды
        
        # Звук клика
        try:
            if self.sounds.get('click'):
                self.sounds['click'].play()
        except:
            pass
    
    # ===== КНОПКИ МЕНЮ =====
    
    def start_2x2(self):
        from main import FootballGame
        game = FootballGame()
        game.start_offline_game('2x2')
    
    def start_3x3(self):
        from main import FootballGame
        game = FootballGame()
        game.start_offline_game('3x3')
    
    def start_training(self):
        from main import FootballGame
        game = FootballGame()
        game.start_offline_game('training')
    
    def go_online(self):
        from main import FootballGame
        game = FootballGame()
        game.start_online_game('ranked')
    
    def go_profile(self):
        from main import FootballGame
        game = FootballGame()
        game.state = 'profile'
    
    def go_back(self):
        from main import FootballGame
        game = FootballGame()
        game.state = 'menu'
    
    def find_ranked(self):
        from main import FootballGame
        game = FootballGame()
        game.start_online_game('ranked')
    
    def find_casual(self):
        from main import FootballGame
        game = FootballGame()
        game.start_online_game('casual')
    
    def find_tournament(self):
        self.show_message('🏆 Турнирная сетка будет в следующем обновлении!', (255, 215, 0))
    
    def get_selected_difficulty(self):
        return self.selected_difficulty
    
    def get_selected_character(self):
        return self.selected_character
