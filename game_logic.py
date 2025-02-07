import pygame

from level import Level, Status
from player import Direction
from level_loader import load_level
from sounds import SoundManager
from sprites import load_image, scale_image
from config import BACKGROUND_COLOR, WINDOW_SIZE

class Game:
    def __init__(self, lvl: int):
        pygame.init()
        
        self.level_number = lvl
        self.level_data = load_level(self.level_number)
        self.level = Level(self.level_data)
        self.sound_manager = SoundManager()

    def run(self):
        screen = pygame.display.set_mode(WINDOW_SIZE)
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 48)
        bg_image = load_image('background.png')
        bg_image = scale_image(bg_image, WINDOW_SIZE[0] / bg_image.get_size()[0])

        running = True
        game_over = False
        messagebox = None
        while running:
            for event in pygame.event.get():
                if game_over and event.type != pygame.QUIT:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        running = False
                        
                    continue

                match event.type:
                    case pygame.QUIT:
                        running = False
                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_LEFT:
                                self.level.player.go(Direction.LEFT)
                            case pygame.K_RIGHT:
                                self.level.player.go(Direction.RIGHT)
                            case pygame.K_DOWN:
                                self.level.player.go(Direction.DOWN)
                            case pygame.K_UP:
                                self.level.player.go(Direction.UP)
                            case pygame.K_SPACE:
                                self.level.player.jump(self.level.platforms)
                    case pygame.KEYUP:
                        match event.key:
                            case pygame.K_LEFT:
                                self.level.player.stop(Direction.LEFT)
                            case pygame.K_RIGHT:
                                self.level.player.stop(Direction.RIGHT)
                            case pygame.K_UP:
                                self.level.player.stop(Direction.UP)
                            case pygame.K_DOWN:
                                self.level.player.stop(Direction.DOWN)
            
            if not game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    self.level.player.go(Direction.UP)
                if keys[pygame.K_DOWN]:
                    self.level.player.go(Direction.DOWN)

            self.level.update()

            if self.level.get_status() == Status.FAILED:
                messagebox = InfoBox((WINDOW_SIZE[0] // 5 * 2, WINDOW_SIZE[1] // 5 * 2),
                                     'You lose!', (WINDOW_SIZE[0] // 5, WINDOW_SIZE[1] // 5))
                game_over = True
            elif self.level.get_status() == Status.FINISHED:
                messagebox = InfoBox((WINDOW_SIZE[0] // 5 * 2, WINDOW_SIZE[1] // 5 * 2),
                                     'You won!', (WINDOW_SIZE[0] // 5, WINDOW_SIZE[1] // 5))
                game_over = True

            screen.fill(BACKGROUND_COLOR)
            screen.blit(bg_image, bg_image.get_rect())
            self.level.draw(screen)

            screen.blit(font.render(
                f'Coins collected: {self.level.coins_collected()}',
                True, (0, 0, 0)), (10, 10))

            if game_over:
                messagebox.draw(screen)

            pygame.display.flip()
            clock.tick(60)

            self.sound_manager.play_random_music()

        pygame.quit()


class InfoBox:
    def __init__(
            self,
            pos: tuple[int, int],
            message: str, size: tuple[int, int],
            font_size: int = 30,
            font_color = (0, 0, 0),
            bg_color = (128, 128, 128),
            btn_color = (255, 255, 255)
        ):
        self.pos = pos

        self.surface = pygame.Surface(size)
        self.surface.fill(bg_color)

        font = pygame.font.SysFont(None, font_size)

        message = font.render(message, True, font_color)
        self.surface.blit(message, ((size[0] - message.get_size()[0]) // 2, (size[1] - message.get_size()[1]) // 2))

        # button_size = size[0] // 4, size[1] // 4
        # button = pygame.Surface(button_size)
        # button.fill(btn_color)
        # button_text = font.render('OK', True, font_color)
        # button.blit(button_text, [(button_size[i] - button_text.get_size()[i]) // 2 for i in range(2)])

        # self.surface.blit(button, ((size[0] - button_size[0]) // 2, (size[1] - button_size[1]) // 4 * 3))

        # self.button = button

    # def get_button(self):
    #     return self.button
    
    def draw(self, screen):
        rect = self.surface.get_rect()
        rect.x, rect.y = self.pos
        screen.blit(self.surface, rect)
        