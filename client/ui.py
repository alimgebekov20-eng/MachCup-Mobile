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
            f'Игрок: {self.player_data["player_name"]}',
            f'Рейтинг: ★ {self.player_data["rating"]}/99',
            f'Кристаллы: 💎 {self.player_data["crystals"]}',
            f'Матчей: {stats["matches"]}',
            f'Побед: {stats["wins"]} ({win_rate:.1f}%)',
            f'Голов забито: {stats["goals_scored"]}',
            f'Голов пропущено: {stats["goals_conceded"]}',
            f'Лучший стрик: {stats["best_streak"]}',
            f'Персонаж: {self.selected_character}'
        ]
        
        for i, line in enumerate(info_lines):
            y = 130 + i * 45
            text = self.font_small.render(line, True, (255, 255, 255))
            self.screen.blit(text, (200, y))
        
        # Кнопка назад
        back_rect = pygame.Rect(450, 600, 300, 50)
        pygame.draw.rect(self.screen, (0, 100, 0), back_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), back_rect, 2, border_radius=10)
        back_text = self.font_medium.render('↩️ НАЗАД', True, (255, 255, 255))
        back_rect_text = back_text.get_rect(center=(600, 625))
        self.screen.blit(back_text, back_rect_text)
    
    def draw_leaderboard(self, data):
        """Отрисовка таблицы рейтингов"""
        self.screen.fill((34, 177, 76))
        
        title = self.font_large.render('📊 ТАБЛИЦА РЕЙТИНГОВ', True, (255, 255, 255))
        title_rect = title.get_rect(center=(600, 50))
        self.screen.blit(title, title_rect)
        
        # Заголовки
        headers = ['#', 'Игрок', 'Рейтинг', 'Побед', 'Голов']
        colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
        
        for i, header in enumerate(headers):
            x = 150 + i * 180
            text = self.font_small.render(header, True, (255, 255, 255))
            self.screen.blit(text, (x, 100))
        
        # Данные
        if isinstance(data, list):
            for rank, player in enumerate(data[:20], 1):
                y = 140 + rank * 35
                color = (255, 255, 255)
                if rank <= 3:
                    color = colors[rank-1]
                
                # Игрок
                name_text = self.font_small.render(f'{rank}. {player["name"]}', True, color)
                self.screen.blit(name_text, (150, y))
                
                # Рейтинг
                rating_text = self.font_small.render(f'★ {player["rating"]}', True, color)
                self.screen.blit(rating_text, (330, y))
                
                # Победы
                wins_text = self.font_small.render(f'{player["wins"]}', True, color)
                self.screen.blit(wins_text, (510, y))
                
                # Голы
                goals_text = self.font_small.render(f'{player["goals"]}', True, color)
                self.screen.blit(goals_text, (690, y))
                
                # Подсветка текущего игрока
                if player['name'] == self.player_data['player_name']:
                    pygame.draw.rect(self.screen, (255, 255, 0), (140, y-5, 550, 30), 2)
        
        # Кнопка назад
        back_rect = pygame.Rect(450, 620, 300, 50)
        pygame.draw.rect(self.screen, (0, 100, 0), back_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), back_rect, 2, border_radius=10)
        back_text = self.font_medium.render('↩️ НАЗАД', True, (255, 255, 255))
        back_rect_text = back_text.get_rect(center=(600, 645))
        self.screen.blit(back_text, back_rect_text)
    
    def show_leaderboard(self):
        """Показать таблицу рейтингов"""
        # Имитация данных
        data = [
            {'name': 'GOD', 'rating': 99, 'wins': 1250, 'goals': 5678},
            {'name': 'PRO', 'rating': 95, 'wins': 980, 'goals': 4321},
            {'name': 'LEGEND', 'rating': 90, 'wins': 890, 'goals': 3987},
            {'name': 'STAR', 'rating': 85, 'wins': 760, 'goals': 3456},
            {'name': 'ACE', 'rating': 80, 'wins': 670, 'goals': 2987},
            {'name': self.player_data['player_name'], 'rating': self.player_data['rating'], 
             'wins': self.player_data['global_stats']['wins'], 
             'goals': self.player_data['global_stats']['goals_scored']}
        ]
        self.draw_leaderboard(data)
    
    def show_message(self, text):
        """Показать сообщение"""
        self.message = text
        self.message_timer = 120  # 2 секунды
    
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
        self.draw_profile()
    
    def go_back(self):
        self.draw_menu()
    
    def find_ranked(self):
        from main import FootballGame
        game = FootballGame()
        game.start_online_game('ranked')
    
    def find_casual(self):
        from main import FootballGame
        game = FootballGame()
        game.start_online_game('casual')
    
    def find_tournament(self):
        self.show_message('Турнирная сетка будет доступна в следующем обновлении!')
    
    def show_settings(self):
        self.show_message('Настройки будут доступны в следующем обновлении!')
    
    def get_selected_difficulty(self):
        return self.selected_difficulty
    
    def get_selected_character(self):
        return self.selected_character

class GameUI:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        self.time = 0
        self.score = {'home': 0, 'away': 0}
        self.mode = '2x2'
        self.result = None
        self.result_timer = 0
    
    def update(self, time, score, mode):
        self.time = time
        self.score = score
        self.mode = mode
    
    def draw(self, screen):
        """Отрисовка игрового UI"""
        # Счет
        score_text = self.font_large.render(f'{self.score["home"]} : {self.score["away"]}', True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(600, 40))
        screen.blit(score_text, score_rect)
        
        # Время
        minutes = int(self.time // 60)
        seconds = int(self.time % 60)
        time_text = self.font_medium.render(f'⏱️ {minutes:02d}:{seconds:02d}', True, (255, 255, 255))
        time_rect = time_text.get_rect(center=(100, 40))
        screen.blit(time_text, time_rect)
        
        # Режим
        mode_names = {'2x2': '2x2', '3x3': '3x3', 'training': 'Тренировка'}
        mode_text = self.font_small.render(mode_names.get(self.mode, '2x2'), True, (255, 255, 255))
        mode_rect = mode_text.get_rect(center=(1100, 40))
        screen.blit(mode_text, mode_rect)
        
        # Управление (подсказка)
        controls = self.font_tiny.render('WASD - движение  |  SPACE - удар  |  E - пас  |  Q - отбор', True, (200, 200, 200))
        controls_rect = controls.get_rect(center=(600, 670))
        screen.blit(controls, controls_rect)
        
        # Результат матча
        if self.result:
            self.result_timer += 1
            result_text = self.font_large.render(self.result['text'], True, self.result['color'])
            result_rect = result_text.get_rect(center=(600, 350))
            screen.blit(result_text, result_rect)
            
            stats_text = self.font_medium.render(
                f'Счет: {self.result["score"]["home"]}:{self.result["score"]["away"]}  '
                f'⭐ {self.result["stars"]}  💎 {self.result["crystals"]}',
                True, (255, 255, 255)
            )
            stats_rect = stats_text.get_rect(center=(600, 420))
            screen.blit(stats_text, stats_rect)
            
            if self.result_timer > 180:  # 3 секунды
                self.result = None
                self.result_timer = 0
    
    def show_result(self, result, score, stars, crystals):
        """Показать результат матча"""
        if result == 'win':
            text = '🏆 ПОБЕДА!'
            color = (0, 255, 0)
        elif result == 'loss':
            text = '💔 ПОРАЖЕНИЕ'
            color = (255, 0, 0)
        else:
            text = '🤝 НИЧЬЯ'
            color = (255, 255, 0)
        
        self.result = {
            'text': text,
            'color': color,
            'score': score,
            'stars': f'+{stars}' if stars >= 0 else str(stars),
            'crystals': f'+{int(crystals)}'
        }
        self.result_timer = 0
