import pygame
import sys
import os
from game import Game
from ui import UI
from save_manager import SaveManager
from online_manager import OnlineManager

class FootballGame:
    def __init__(self):
        pygame.init()
        
        # Устанавливаем иконку
        try:
            icon = pygame.image.load('assets/images/logo.png')
            pygame.display.set_icon(icon)
        except:
            pass
        
        self.screen = pygame.display.set_mode((1200, 700))
        pygame.display.set_caption("⚽ STREET FOOTBALL LEGENDS")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Загрузка звуков
        self.sounds = {}
        try:
            self.sounds['goal'] = pygame.mixer.Sound('assets/sounds/goal.wav')
            self.sounds['kick'] = pygame.mixer.Sound('assets/sounds/kick.wav')
            self.sounds['whistle'] = pygame.mixer.Sound('assets/sounds/whistle.wav')
            self.sounds['click'] = pygame.mixer.Sound('assets/sounds/menu_click.wav')
        except:
            # Если звуков нет - создаем пустые
            pass
        
        # Менеджеры
        self.save_manager = SaveManager()
        self.player_data = self.save_manager.load()
        
        # UI
        self.ui = UI(self.screen, self.player_data, self.sounds)
        
        # Состояние
        self.state = 'menu'
        self.game = None
        self.online_manager = None
        self.leaderboard_data = None
    
    def run(self):
        while self.running:
            self.handle_events()
            
            if self.state == 'menu':
                self.ui.draw_menu()
            elif self.state == 'game':
                if self.game:
                    self.game.update()
                    self.game.draw()
            elif self.state == 'online':
                self.ui.draw_online_menu()
            elif self.state == 'profile':
                self.ui.draw_profile()
            elif self.state == 'leaderboard':
                if self.leaderboard_data:
                    self.ui.draw_leaderboard(self.leaderboard_data)
                else:
                    self.load_leaderboard()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_manager.save(self.player_data)
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    self.handle_menu_keys(event.key)
                elif self.state == 'game':
                    self.handle_game_keys(event.key)
                elif self.state == 'online':
                    self.handle_online_keys(event.key)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == 'menu':
                    self.handle_menu_click(event.pos)
                elif self.state == 'online':
                    self.handle_online_click(event.pos)
                elif self.state == 'profile':
                    self.handle_profile_click(event.pos)
    
    def handle_menu_keys(self, key):
        """Обработка клавиш в меню"""
        if key == pygame.K_1:
            self.start_offline_game(mode='2x2')
        elif key == pygame.K_2:
            self.start_offline_game(mode='3x3')
        elif key == pygame.K_3:
            self.start_offline_game(mode='training')
        elif key == pygame.K_4:
            self.state = 'online'
        elif key == pygame.K_5:
            self.state = 'profile'
        elif key == pygame.K_6:
            self.ui.show_leaderboard()
        elif key == pygame.K_ESCAPE:
            self.save_manager.save(self.player_data)
            self.running = False
    
    def handle_menu_click(self, pos):
        """Обработка кликов в меню"""
        x, y = pos
        
        # Кнопки меню
        buttons = [
            {'rect': (100, 100, 200, 60), 'action': lambda: self.start_offline_game('2x2')},
            {'rect': (100, 180, 200, 60), 'action': lambda: self.start_offline_game('3x3')},
            {'rect': (100, 260, 200, 60), 'action': lambda: self.start_offline_game('training')},
            {'rect': (100, 340, 200, 60), 'action': lambda: setattr(self, 'state', 'online')},
            {'rect': (100, 420, 200, 60), 'action': lambda: setattr(self, 'state', 'profile')},
            {'rect': (100, 500, 200, 60), 'action': self.ui.show_leaderboard},
        ]
        
        for btn in buttons:
            if btn['rect'][0] < x < btn['rect'][0] + btn['rect'][2] and \
               btn['rect'][1] < y < btn['rect'][1] + btn['rect'][3]:
                btn['action']()
    
    def handle_game_keys(self, key):
        """Обработка клавиш в игре"""
        if self.game:
            self.game.handle_key_down(key)
    
    def start_offline_game(self, mode='2x2'):
        """Запуск оффлайн игры"""
        difficulty = self.ui.get_selected_difficulty()
        character = self.ui.get_selected_character()
        
        self.game = Game(self.screen, mode, difficulty, character, self.player_data)
        self.game.start()
        self.state = 'game'
    
    def start_online_game(self, mode='ranked'):
        """Запуск онлайн игры"""
        # Подключаемся к серверу
        if self.online_manager.connect():
            # Ищем соперника
            match_data = self.online_manager.find_match(
                self.player_data['player_name'],  # ✅ ПРАВИЛЬНО
                mode
            )
            if match_data:
                self.game = Game(self.screen, mode, 'online', 
                               self.player_data, match_data)
                self.game.start()
                self.state = 'game'
            else:
                self.ui.show_message('Соперник не найден')
        else:
            self.ui.show_message('Ошибка подключения к серверу')

if __name__ == '__main__':
    game = FootballGame()
    game.run()
