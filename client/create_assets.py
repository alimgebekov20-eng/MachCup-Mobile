"""
Скрипт для создания всех ассетов игры программно
Запусти один раз перед игрой
"""

import pygame
import os
import wave
import struct
import math

def create_folders():
    """Создание папок"""
    folders = [
        'assets/fonts',
        'assets/sounds',
        'assets/images',
        'assets/images/players'
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print('✅ Папки созданы')

def create_font():
    """Создание шрифта (используем системный)"""
    # Просто создаем пустой файл-заглушку
    font_path = 'assets/fonts/default.ttf'
    if not os.path.exists(font_path):
        # Создаем пустой файл (будет использован системный шрифт)
        with open(font_path, 'w') as f:
            f.write('')  # Пустой файл, но Pygame будет использовать системный
    print('✅ Шрифт создан')

def create_sound(filename, duration=0.5, freq=440):
    """Создание звукового файла WAV программно"""
    path = f'assets/sounds/{filename}'
    if os.path.exists(path):
        return
    
    # Параметры звука
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    # Создаем звук (синусоида)
    sound_data = []
    for i in range(num_samples):
        t = i / sample_rate
        value = math.sin(2 * math.pi * freq * t)
        # Затухание
        value *= (1 - t / duration)
        sound_data.append(int(value * 32767))
    
    # Записываем в WAV
    with wave.open(path, 'w') as wav:
        wav.setnchannels(1)  # Моно
        wav.setsampwidth(2)  # 2 байта на сэмпл
        wav.setframerate(sample_rate)
        
        # Конвертируем в байты
        bytes_data = b''.join(struct.pack('<h', s) for s in sound_data)
        wav.writeframes(bytes_data)
    
    print(f'✅ Звук создан: {filename}')

def create_images():
    """Создание изображений для игры"""
    
    # 1. Логотип
    create_logo()
    
    # 2. Фон поля
    create_field_bg()
    
    # 3. Мяч
    create_ball_image()
    
    # 4. Аватарки игроков
    create_player_avatars()

def create_logo():
    """Создание логотипа"""
    path = 'assets/images/logo.png'
    if os.path.exists(path):
        return
    
    # Создаем поверхность для логотипа
    surf = pygame.Surface((400, 150), pygame.SRCALPHA)
    
    # Фон
    pygame.draw.rect(surf, (34, 177, 76), (0, 0, 400, 150), border_radius=20)
    pygame.draw.rect(surf, (255, 255, 255), (0, 0, 400, 150), 3, border_radius=20)
    
    # Текст
    font = pygame.font.Font(None, 60)
    text = font.render('⚽ STREET', True, (255, 255, 255))
    surf.blit(text, (50, 20))
    
    text2 = font.render('FOOTBALL', True, (255, 255, 255))
    surf.blit(text2, (70, 80))
    
    # Сохраняем
    pygame.image.save(surf, path)
    print('✅ Логотип создан')

def create_field_bg():
    """Создание фона поля"""
    path = 'assets/images/field.png'
    if os.path.exists(path):
        return
    
    # Создаем поле
    surf = pygame.Surface((1200, 700))
    
    # Зеленый фон
    surf.fill((34, 177, 76))
    
    # Разметка
    white = (255, 255, 255)
    
    # Границы
    pygame.draw.rect(surf, white, (50, 50, 1100, 600), 3)
    
    # Центр
    pygame.draw.circle(surf, white, (600, 350), 80, 2)
    pygame.draw.line(surf, white, (600, 50), (600, 650), 2)
    
    # Штрафные
    pygame.draw.rect(surf, white, (50, 250, 150, 200), 2)
    pygame.draw.rect(surf, white, (1050-150, 250, 150, 200), 2)
    
    # Вратарские
    pygame.draw.rect(surf, white, (50, 300, 80, 100), 2)
    pygame.draw.rect(surf, white, (1050-80, 300, 80, 100), 2)
    
    # Угловые
    pygame.draw.circle(surf, white, (50, 50), 15, 2)
    pygame.draw.circle(surf, white, (1150, 50), 15, 2)
    pygame.draw.circle(surf, white, (50, 650), 15, 2)
    pygame.draw.circle(surf, white, (1150, 650), 15, 2)
    
    pygame.image.save(surf, path)
    print('✅ Фон поля создан')

def create_ball_image():
    """Создание текстуры мяча"""
    path = 'assets/images/ball.png'
    if os.path.exists(path):
        return
    
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    
    # Мяч
    pygame.draw.circle(surf, (255, 255, 255), (20, 20), 18)
    pygame.draw.circle(surf, (50, 50, 50), (20, 20), 18, 2)
    
    # Пятиугольники (упрощенно)
    for i in range(5):
        angle = i * 2 * math.pi / 5 - math.pi / 2
        x = 20 + 10 * math.cos(angle)
        y = 20 + 10 * math.sin(angle)
        pygame.draw.circle(surf, (200, 200, 200), (int(x), int(y)), 4)
    
    pygame.image.save(surf, path)
    print('✅ Текстура мяча создана')

def create_player_avatars():
    """Создание аватарок игроков"""
    players = [
        ('aziz', (255, 107, 53), 'Азиз'),
        ('khabib', (0, 180, 216), 'Хабиб'),
        ('abdul', (45, 106, 79), 'Абдул'),
        ('shamil_rb', (230, 57, 70), 'Шамиль Рб'),
        ('shamil_jr', (155, 93, 229), 'Шамиль Jr.'),
        ('salaudin', (247, 127, 0), 'Салаудин')
    ]
    
    for name, color, label in players:
        path = f'assets/images/players/{name}.png'
        if os.path.exists(path):
            continue
        
        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        
        # Круг
        pygame.draw.circle(surf, color, (40, 40), 35)
        pygame.draw.circle(surf, (255, 255, 255), (40, 40), 35, 3)
        
        # Инициалы
        font = pygame.font.Font(None, 30)
        initials = ''.join([w[0] for w in label.split()])
        if not initials:
            initials = label[0]
        text = font.render(initials, True, (255, 255, 255))
        text_rect = text.get_rect(center=(40, 40))
        surf.blit(text, text_rect)
        
        pygame.image.save(surf, path)
        print(f'✅ Аватарка {label} создана')

def create_all_sounds():
    """Создание всех звуков"""
    sounds = [
        ('goal.wav', 1.0, 880),      # Гол - высокая нота
        ('kick.wav', 0.3, 440),       # Удар - средняя нота
        ('whistle.wav', 0.8, 660),    # Свисток - высокая нота
        ('menu_click.wav', 0.2, 330), # Клик - низкая нота
        ('crowd_cheer.wav', 2.0, 550) # Аплодисменты
    ]
    
    for filename, duration, freq in sounds:
        create_sound(filename, duration, freq)
    
    print('✅ Все звуки созданы')

def main():
    """Главная функция"""
    print('🎨 СОЗДАНИЕ ASSETS ДЛЯ ИГРЫ...')
    print('=' * 40)
    
    # Инициализация Pygame
    pygame.init()
    
    # Создание папок
    create_folders()
    
    # Создание шрифта
    create_font()
    
    # Создание изображений
    create_images()
    
    # Создание звуков
    create_all_sounds()
    
    print('=' * 40)
    print('✅ ВСЕ ASSETS СОЗДАНЫ!')
    print('🎮 МОЖНО ЗАПУСКАТЬ ИГРУ!')

if __name__ == '__main__':
    main()
