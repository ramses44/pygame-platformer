import pygame
from scene import Scene
from database import get_all_levels, get_balance, unlock_level, purchase_level
from config import (
    BACKGROUND_COLOR,
    WINDOW_SIZE,
    DIFFICULTY_EASY_CLR,
    DIFFICULTY_MEDIUM_CLR,
    DIFFICULTY_HARD_CLR,
    DIFFICULTY_UNKNOWN_CLR,
    FPS
)
from notification import NotificationManager

class MainMenu(Scene):
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.levels = get_all_levels()
        self.notifications = NotificationManager()
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Графические ресурсы
        self.font_title = pygame.font.Font('assets/fonts/Title-font.ttf', 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.lock_icon = pygame.transform.scale(
            pygame.image.load('assets/icons/lock.png').convert_alpha(), 
            (40, 40)
        )
        self.coin_icon = pygame.transform.scale(
            pygame.image.load('assets/icons/coin.png').convert_alpha(),
            (32, 32)
        )
        
        # Цвета сложности
        self.difficulty_colors = {
            'EASY': DIFFICULTY_EASY_CLR,
            'MEDIUM': DIFFICULTY_MEDIUM_CLR,
            'HARD': DIFFICULTY_HARD_CLR,
            'UNKNOWN': DIFFICULTY_UNKNOWN_CLR
        }
        
        # Параметры сетки уровней
        self.button_width = 220
        self.button_height = 160
        self.buttons_per_row = WINDOW_SIZE[0] // (self.button_width + 30)
        self.rows = (len(self.levels) + self.buttons_per_row - 1) // self.buttons_per_row
        self.max_scroll = max(0, self.rows * (self.button_height + 30) - WINDOW_SIZE[1] + 250)

    def get_level_button_rect(self, index):
        start_y = 200 + self.scroll_offset
        row = index // self.buttons_per_row
        col = index % self.buttons_per_row
        padding = (WINDOW_SIZE[0] - (self.button_width + 30) * self.buttons_per_row + 30) // 2
        x = padding + col * (self.button_width + 30)
        y = start_y + row * (self.button_height + 30)
        return pygame.Rect(x, y, self.button_width, self.button_height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверка клика по кнопке выхода
            if self.exit_btn_rect.collidepoint(mouse_pos):
                pygame.quit()
                exit()
            
            # Проверка кликов по уровням
            for i, level in enumerate(self.levels):
                btn_rect = self.get_level_button_rect(i)
                if btn_rect.collidepoint(mouse_pos):
                    self.handle_level_click(level)

        elif event.type == pygame.MOUSEWHEEL:
            if event.y == 1:  # Скролл вверх
                self.scroll_offset = min(self.scroll_offset + 20, 0)
            elif event.y == -1:  # Скролл вниз
                self.scroll_offset = max(self.scroll_offset - 20, -self.max_scroll)

    def handle_level_click(self, level):
        if level['unlocked']:
            self.game_manager.start_level(level)
        else:
            if level['cost'] is None:
                if self.check_previous_level_completed(level['id']):
                    unlock_level(level['id'])
                    self.levels = get_all_levels()
                else:
                    self.notifications.show("Пройдите предыдущий уровень!", "error")
            else:
                if purchase_level(level['id']):
                    self.levels = get_all_levels()
                    self.notifications.show("Уровень куплен!", "success")
                else:
                    self.notifications.show("Недостаточно монет!", "error")

    def check_previous_level_completed(self, level_id):
        prev_level = next((l for l in self.levels if l['id'] == level_id - 1), None)
        return prev_level and prev_level['unlocked'] and prev_level['coins_collected'] is not None

    def update(self):
        self.notifications.update()

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)

        # Отрисовка уровней
        self.draw_level_buttons(screen)

        pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(0, 0, WINDOW_SIZE[0], 200))
        
        # Заголовок
        title = self.font_title.render("Platformer Adventure", True, (255, 255, 255))
        screen.blit(title, (WINDOW_SIZE[0]//2 - title.get_width()//2, 20))
        
        # Верхняя панель
        self.draw_top_panel(screen)
        
        # Уведомления
        self.notifications.draw(screen)
        
        pygame.display.flip()

    def draw_top_panel(self, screen):
        panel_y = 120
        padding = 15
        
        # Баланс
        balance = get_balance()
        coin_text = f"Баланс: {balance}"
        text_surf = self.font_medium.render(coin_text, True, (255, 215, 0))
        
        # Вертикальное центрирование
        total_height = max(self.coin_icon.get_height(), text_surf.get_height())
        icon_y = panel_y + (total_height - self.coin_icon.get_height()) // 2
        text_y = panel_y + (total_height - text_surf.get_height()) // 2
        
        screen.blit(self.coin_icon, (50, icon_y))
        screen.blit(text_surf, (50 + self.coin_icon.get_width() + padding, text_y))
        
        # Легенда сложности
        self.draw_difficulty_legend(screen, panel_y)
        
        # Кнопка выхода
        self.draw_exit_button(screen, panel_y, total_height)

    def draw_difficulty_legend(self, screen, y_pos):
        items = [
            ('EASY', 'Легко'),
            ('MEDIUM', 'Средне'),
            ('HARD', 'Сложно'),
            ('UNKNOWN', 'Неизвестно')
        ]
        
        total_width = sum(140 for _ in items)
        start_x = WINDOW_SIZE[0]//2 - total_width//2
        
        for i, (diff, label) in enumerate(items):
            x = start_x + i * 140
            pygame.draw.circle(screen, self.difficulty_colors[diff], (x, y_pos + 25), 10)
            text = self.font_small.render(label, True, (200, 200, 200))
            screen.blit(text, (x + 20, y_pos + 18))

    def draw_exit_button(self, screen, panel_y, element_height):
        exit_text = self.font_medium.render("Выход", True, (255, 255, 255))
        btn_width = exit_text.get_width() + 40
        btn_height = exit_text.get_height() + 20
        
        # Позиционирование
        btn_y = panel_y + (element_height - btn_height) // 2
        self.exit_btn_rect = pygame.Rect(
            WINDOW_SIZE[0] - btn_width - 50,
            btn_y,
            btn_width,
            btn_height
        )
        
        # Отрисовка кнопки
        pygame.draw.rect(screen, (200, 50, 50), self.exit_btn_rect, border_radius=8)
        pygame.draw.rect(screen, (150, 30, 30), self.exit_btn_rect, 3, border_radius=8)
        
        # Текст кнопки
        text_x = self.exit_btn_rect.x + (btn_width - exit_text.get_width()) // 2
        text_y = self.exit_btn_rect.y + (btn_height - exit_text.get_height()) // 2
        screen.blit(exit_text, (text_x, text_y))

    def draw_level_buttons(self, screen):
        for i, level in enumerate(self.levels):
            btn_rect = self.get_level_button_rect(i)
            color = self.difficulty_colors.get(level['difficulty'], DIFFICULTY_UNKNOWN_CLR)
            
            # Затемнение для заблокированных
            if not level['unlocked']:
                color = tuple(c // 2 for c in color)
            
            # Отрисовка кнопки уровня
            pygame.draw.rect(screen, color, btn_rect, border_radius=12)
            
            # Текст уровня
            if level['unlocked']:
                level_text = f"Уровень {level['id']}" if level['cost'] is None else "Бонусный"
                text_color = (255, 255, 255)
            else:
                level_text = f"{level['cost']} монет" if level['cost'] else "Заблокирован"
                text_color = (150, 150, 150)
            
            text_surf = self.font_medium.render(level_text, True, text_color)
            screen.blit(text_surf, (btn_rect.x + 20, btn_rect.y + 15))
            
            # Прогресс
            if level['unlocked']:
                coins_text = f"Монет собрано: {level['coins_collected'] or 0}/{level['max_coins']}"
                time_text = f"Лучшее время: {self.format_time(level['time_spent'])}"
                
                # Отрисовка прогресса
                self.draw_centered_text(screen, coins_text, btn_rect.x + 10, btn_rect.bottom - 50, self.button_width - 20)
                self.draw_centered_text(screen, time_text, btn_rect.x + 10, btn_rect.bottom - 30, self.button_width - 20)
            
            # Иконка замка
            if not level['unlocked']:
                lock_pos = btn_rect.center
                screen.blit(self.lock_icon, self.lock_icon.get_rect(center=lock_pos))

    def draw_centered_text(self, screen, text, x, y, width):
        text_surf = self.font_small.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (x + (width - text_surf.get_width()) // 2, y))