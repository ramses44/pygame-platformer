import pygame
from config import (
    NOTIFICATION_SUCCESS_CLR,
    NOTIFICATION_ERROR_CLR,
    NOTIFICATION_INFO_CLR,
    NOTIFICATION_FADE_IN_TIME,
    NOTIFICATION_FADE_OUT_TIME,
    NOTIFICATION_DISPLAY_TIME
)

class NotificationManager:
    def __init__(self):
        self.current_notification = None
        self.start_time = 0
        self.alpha = 0
        self.state = "hidden"  # hidden, fading_in, visible, fading_out

    def show(self, text, notification_type="info", duration=NOTIFICATION_DISPLAY_TIME):
        self.current_notification = {
            "text": text,
            "type": notification_type,
            "duration": duration
        }
        self.state = "fading_in"
        self.start_time = pygame.time.get_ticks()
        self.alpha = 0

    def update(self):
        if self.state == "hidden":
            return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time

        if self.state == "fading_in":
            progress = min(elapsed / NOTIFICATION_FADE_IN_TIME, 1.0)
            self.alpha = int(255 * progress)
            if progress >= 1.0:
                self.state = "visible"
                self.start_time = current_time

        elif self.state == "visible":
            if elapsed >= self.current_notification["duration"]:
                self.state = "fading_out"
                self.start_time = current_time

        elif self.state == "fading_out":
            progress = min(elapsed / NOTIFICATION_FADE_OUT_TIME, 1.0)
            self.alpha = 255 - int(255 * progress)
            if progress >= 1.0:
                self.state = "hidden"

    def draw(self, screen):
        if self.state == "hidden" or not self.current_notification:
            return

        text_color = (255, 255, 255)
        bg_color = {
            "success": NOTIFICATION_SUCCESS_CLR,
            "error": NOTIFICATION_ERROR_CLR,
            "info": NOTIFICATION_INFO_CLR
        }.get(self.current_notification["type"], NOTIFICATION_INFO_CLR)

        # Создаем поверхность с прозрачностью
        font = pygame.font.Font(None, 28)
        text_surf = font.render(self.current_notification["text"], True, text_color)
        padding = 20
        width = text_surf.get_width() + padding * 2
        height = text_surf.get_height() + padding * 2
        
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (*bg_color, self.alpha), (0, 0, width, height), border_radius=10)
        surface.blit(text_surf, (padding, padding))
        surface.set_alpha(self.alpha)
        
        screen.blit(surface, (screen.get_width() - width - 20, 20))