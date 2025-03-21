import pygame
from config import WINDOW_SIZE, FULLSCREEN, FPS
from menu import MainMenu
from game_logic import Game
from scene import Scene

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN * FULLSCREEN)
        pygame.display.set_caption("Platformer Adventure game")
        self.clock = pygame.time.Clock()
        self.current_scene: Scene = MainMenu(self)

    def return_to_menu(self, *args, **kwargs):
        self.current_scene = MainMenu(self, *args, **kwargs)
        
    def start_level(self, *args, **kwargs):
        self.current_scene = Game(self, *args, **kwargs)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.current_scene.handle_event(event)
            
            self.current_scene.update()
            self.current_scene.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    manager = GameManager()
    manager.run()