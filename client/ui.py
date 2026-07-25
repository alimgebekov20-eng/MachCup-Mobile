import pygame
import math

class UI:
    def __init__(self, screen, player_data):
        self.screen = screen
        self.player_data = player_data
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        self.selected_difficulty = 'medium'
        self.selected_character = 'Азиз'
        self.message = None
        self.message_timer = 0
    
    def draw_menu(self):
        """Отрисовка главного меню"""
        # Фон
        self.screen.fill((34, 177, 76))
        
        # Заголовок
        title = self.font_large.render('⚽ STREET FOOTBALL LEGENDS', True, (255, 255, 255))
        title_rect = title.get_rect(center=(600, 100))
        self.screen.blit(title, title_rect)
        
        # Информация об игроке
        player_info = f'👤 {self.player_data["player_name"]}  ★ {self.player_data["rating"]}  💎 {self.player_data["crystals"]}'
        info_text = self.font_medium.render(player_info, True, (255, 255, 255))
        info_rect = info_text.get_rect(center=(600, 160))
        self.screen.blit(info_text, info_rect)
        
        # Кнопки меню
        menu_items = [
            ('▶️ БЫСТРЫЙ МАТЧ (2x2)', self.start_2x2),
            ('▶️ БЫСТРЫЙ МАТЧ (3x3)', self.start_3x3),
            ('🎯 ТРЕНИРОВКА', self.start_training),
            ('🌐 ОНЛАЙН', self.go_online),
            ('👤 ПРОФИЛЬ', self.go_profile),
            ('📊 ТАБЛИЦА РЕЙТИНГОВ', self.show_leaderboard),
            ('⚙️ НАСТРОЙКИ', self.show_settings),
        ]
        
        for i, (text, _) in enumerate(menu_items):
            y = 220 + i * 55
            color = (255, 255, 255)
            rect = pygame.Rect(300, y, 600, 45)
            pygame.draw.rect(self.screen, (0, 100, 0), rect, border_radius=10)
            pygame.draw.rect(self.screen, color, rect, 2, border_radius=10)
            
            label = self.font_medium.render(text, True, color)
            label_rect = label.get_rect(center=(600, y + 22))
            self.screen.blit(label, label_rect)
        
        # Нижняя панель
        bottom_text = f'Выбран персонаж: {self.selected_character}  |  Сложность: {self.selected_difficulty.upper()}'
        bottom = self.font_small.render(bottom_text, True, (255, 255, 255))
        bottom_rect = bottom.get_rect(center=(600, 660))
        self.screen.blit(bottom, bottom_rect)
        
        # Сообщение
        if self.message and self.message_timer > 0:
            msg_text = self.font_medium.render(self.message, True, (255, 255, 0))
            msg_rect = msg_text.get_rect(center=(600, 350))
            self.screen.blit(msg_text, msg_rect)
            self.message_timer -= 1
    
    def draw_online_menu(self):
        """Отрисовка онлайн меню"""
        self.screen.fill((34, 177, 76))
        
        title = self.font_large.render('🌐 ОНЛАЙН РЕЖИМ', True, (255, 255, 255))
        title_rect = title.get_rect(center=(600, 100))
        self.screen.blit(title, title_rect)
        
        online_items = [
            ('🔍 ПОИСК СОПЕРНИКА (РЕЙТИНГОВЫЙ)', self.find_ranked),
            ('🔍 ПОИСК СОПЕРНИКА (ОБЫЧНЫЙ)', self.find_casual),
            ('🏆 ТУРНИРНАЯ СЕТКА (4 ИГРОКА)', self.find_tournament),
            ('↩️ НАЗАД', self.go_back)
        ]
        
        for i, (text, _) in enumerate(online_items):
            y = 200 + i * 65
            rect = pygame.Rect(300, y, 600, 55)
            pygame.draw.rect(self.screen, (0, 100, 0), rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=10)
            
            label = self.font_medium.render(text, True, (255, 255, 255))
            label_rect = label.get_rect(center=(600, y + 27))
            self.screen.blit(label, label_rect)
    
    def draw_profile(self):
        """Отрисовка профиля"""
        self.screen.fill((34, 177, 76))
        
        # Заголовок
        title = self.font_large.render('👤 ПРОФИЛЬ', True, (255, 255, 255))
        title_rect = title.get_rect(center=(600, 60))
        self.screen.blit(title, title_rect)
        
        # Информация
        stats = self.player_data['global_stats']
        win_rate = (stats['wins'] / max(1, stats['matches']) * 100)
        
        info_lines = [
            f'Иг
