# -*- coding: utf-8 -*-
import pygame
import json
from scene import Scene
from config import BACKGROUND_COLOR, WINDOW_SIZE
from level import Level, Status
from player import Direction
from sounds import SoundManager
from sprites import load_image
from database import level_win

class Game(Scene):
    def __init__(self, game_manager, level):
        super().__init__()

        self.font = pygame.font.Font(None, 36)
        self.sound_manager = SoundManager()
        self.game_manager = game_manager

        with open(level['map_filepath']) as f:
            self.level_data = json.load(f)

        self.level_id = level['id']
        self.bg_image = load_image('background.png')
        self.pause_btn_rect = None
        self.restart_btn_rect = None
        self.menu_btn_rect = None
        self.reset()
        
    def reset(self):
        self.level = Level(self.level_id, self.level_data)
        self.game_over = False
        self.messagebox = None
        self.start_time = pygame.time.get_ticks()
        self.paused = False
        self.elapsed_time = 0

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.level.get_status() == Status.FAILED:
                    self.reset()
                else:
                    self.sound_manager.stop()
                    self.game_manager.return_to_menu()
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_btn_rect.collidepoint(event.pos):
                self.sound_manager.stop()
                self.game_manager.return_to_menu()
            elif self.pause_btn_rect.collidepoint(event.pos):
                self.toggle_pause()
            elif self.restart_btn_rect.collidepoint(event.pos):
                self.reset()

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if self.paused:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.level.player.go(Direction.LEFT)
            elif event.key == pygame.K_RIGHT:
                self.level.player.go(Direction.RIGHT)
            elif event.key == pygame.K_DOWN:
                self.level.player.go(Direction.DOWN)
            elif event.key == pygame.K_UP:
                self.level.player.go(Direction.UP)
            elif event.key == pygame.K_SPACE:
                self.level.player.jump(self.level.platforms)
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.level.player.stop(Direction.LEFT)
            elif event.key == pygame.K_RIGHT:
                self.level.player.stop(Direction.RIGHT)
            elif event.key == pygame.K_UP:
                self.level.player.stop(Direction.UP)
            elif event.key == pygame.K_DOWN:
                self.level.player.stop(Direction.DOWN)

    def update(self):
        if self.paused:
            return

        self.level.update()

        if self.game_over:
            return
        
        self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000  # time inc
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.level.player.go(Direction.UP)
        if keys[pygame.K_DOWN]:
            self.level.player.go(Direction.DOWN)
        
        status = self.level.get_status()
        if status == Status.FAILED:
            self.lose()
        elif status == Status.FINISHED:
            self.win()

        self.sound_manager.play_random_music()

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        screen.blit(self.bg_image, (0, 0))
        self.level.draw(screen)
        
        self.draw_ui(screen)
        
        if self.game_over or self.paused:
            self.messagebox.draw(screen)

    def draw_ui(self, screen):
        # Кнопки
        self.draw_menu_button(screen)
        self.draw_pause_button(screen)
        self.draw_restart_button(screen)

        # Статистика
        coins_text = f"Монет собрано: {self.level.coins_collected()} "
        time_text = f"Время: {self.format_time(self.elapsed_time)}"
        
        # Отрисовка монет
        coin_pos = (WINDOW_SIZE[0]//20 * 6, 20)
        screen.blit(self.font.render(coins_text, True, (255,255,255)), 
                   (coin_pos[0], coin_pos[1]))
        
        # Отрисовка времени
        time_pos = (WINDOW_SIZE[0]//20 * 11, 20)
        screen.blit(self.font.render(time_text, True, (255,255,255)), time_pos)

    def draw_menu_button(self, screen, padding=20):
        menu_icon = pygame.image.load('assets/icons/back.png').convert_alpha()
        
        menu_text = self.font.render("В меню", True, (255, 255, 255))
        
        icon_spacing = 10
        btn_width = menu_icon.get_width() + menu_text.get_width() + icon_spacing + 30
        btn_height = max(menu_icon.get_height(), menu_text.get_height()) + 20
        btn_topleft = (padding, padding)
        
        surface = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (140, 140, 140), (0, 0, btn_width, btn_height), border_radius=4)
        
        icon_y = btn_height//2 - menu_icon.get_height()//2
        text_y = btn_height//2 - menu_text.get_height()//2
        
        surface.blit(menu_icon, (15, icon_y))
        surface.blit(menu_text, (15 + menu_icon.get_width() + icon_spacing, text_y))

        surface.set_alpha(150)
        self.menu_btn_rect = surface.get_rect(topleft=btn_topleft)
        screen.blit(surface, btn_topleft)

    def draw_pause_button(self, screen, padding=20):
        pause_icon = pygame.image.load('assets/icons/pause.png').convert_alpha()
        play_icon = pygame.image.load('assets/icons/unpause.png').convert_alpha()
        current_icon = play_icon if self.paused else pause_icon
        
        btn_width = current_icon.get_width() + 30
        btn_height = current_icon.get_height() + 20
        btn_topleft = (WINDOW_SIZE[0] - btn_width - padding, padding)

        surface = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (140, 140, 140), (0, 0, btn_width, btn_height), border_radius=3)

        surface.blit(current_icon, (15, btn_height//2 - current_icon.get_height()//2))
        
        surface.set_alpha(128)
        self.pause_btn_rect = surface.get_rect(topleft=btn_topleft)
        screen.blit(surface, btn_topleft)

    def draw_restart_button(self, screen, padding = 20):
        restart_icon = pygame.image.load('assets/icons/restart.png').convert_alpha()
        
        btn_width = restart_icon.get_width() + 30
        btn_height = restart_icon.get_height() + 20
        btn_topleft = (self.pause_btn_rect.left - btn_width - padding, padding)

        surface = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (140, 140, 140), (0, 0, btn_width, btn_height), border_radius=3)

        surface.blit(restart_icon, (15, btn_height//2 - restart_icon.get_height()//2))
        
        surface.set_alpha(128)
        self.restart_btn_rect = surface.get_rect(topleft=btn_topleft)
        screen.blit(surface, btn_topleft)

    def win(self):
        level_win(self.level_id, 
                  coins_collected=self.level.coins_collected(),
                  time_spent=self.elapsed_time)
        self.messagebox = InfoBox(
            (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2),
            "Победа! Нажмите чтобы вернуться в меню",
            (500, 100),
            bg_color=(50, 200, 50)
        )
        self.game_over = True
        
    def lose(self):
        self.game_over = True
        self.messagebox = InfoBox(
            (WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2),
            "Поражение! Нажмите чтобы повторить",
            (500, 100),
            bg_color=(200, 50, 50)
        )

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_time = pygame.time.get_ticks()
            self.messagebox = InfoBox(
                (WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2),
                "Игра на паузе!",
                (300, 100),
                bg_color=(150, 150, 150)
            )
        else:
            self.start_time += pygame.time.get_ticks() - self.pause_time

class InfoBox:
    def __init__(self, center_pos, text, size, bg_color=(80, 80, 80), text_color=(255, 255, 255)):
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.surface.get_rect(center=center_pos)
        
        # Фон с закругленными углами
        pygame.draw.rect(self.surface, (*bg_color, 200), (0, 0, *size), border_radius=15)
        
        # Текст
        font = pygame.font.Font(None, 32)
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(size[0]//2, size[1]//2))
        self.surface.blit(text_surf, text_rect)

    def draw(self, screen):
        screen.blit(self.surface, self.rect)