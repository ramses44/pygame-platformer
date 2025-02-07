import pygame
import json
import itertools
import copy

from config import *
import sprites


class LevelEditor:
    def __init__(self):
        self.platforms = pygame.sprite.Group()
        self.ladders = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.mines = pygame.sprite.Group()
        self.start = pygame.sprite.Group()
        self.finish = pygame.sprite.Group()
        self.selected_object = None

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode(WINDOW_SIZE)
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:  # ЛКМ
                        if self.selected_object:
                            match type(self.selected_object):
                                case sprites.Platform:
                                    self.platforms.add(copy.copy(self.selected_object))
                                case sprites.Ladder:
                                    self.ladders.add(copy.copy(self.selected_object))
                                case sprites.Mine:
                                    self.mines.add(copy.copy(self.selected_object))
                                case sprites.Coin:
                                    self.coins.add(copy.copy(self.selected_object))
                                case sprites.Start:
                                    self.start.add(self.selected_object)
                                    self.selected_object = None
                                case sprites.Finish:
                                    self.finish.add(self.selected_object)
                                    self.selected_object = None
                                
                        else:
                            for sprite in itertools.chain(
                                self.coins, self.mines, self.finish, self.start, self.ladders, self.platforms
                            ):
                                if sprite.rect.collidepoint(pygame.mouse.get_pos()):
                                    sprite.kill()
                                    self.selected_object = sprite
                                    break

                    elif event.button == 3:  # ПКМ
                        self.selected_object = None

                elif event.type == pygame.KEYDOWN:
                    pos = pygame.mouse.get_pos()

                    if event.key == pygame.K_1:
                        self.selected_object = sprites.Platform(0, pos, sprites.Size.SMALL)
                    elif event.key == pygame.K_2:
                        self.selected_object = sprites.Platform(0, pos, sprites.Size.MEDIUM)
                    elif event.key == pygame.K_3:
                        self.selected_object = sprites.Platform(0, pos, sprites.Size.LARGE)
                    elif event.key == pygame.K_4:
                        self.selected_object = sprites.Ladder(0, pos, sprites.Size.SMALL)
                    elif event.key == pygame.K_5:
                        self.selected_object = sprites.Ladder(0, pos, sprites.Size.MEDIUM)
                    elif event.key == pygame.K_6:
                        self.selected_object = sprites.Ladder(0, pos, sprites.Size.LARGE)
                    elif event.key == pygame.K_7:
                        self.selected_object = sprites.Mine(0, pos)
                    elif event.key == pygame.K_8:
                        self.selected_object = sprites.Coin(0, pos)
                    elif event.key == pygame.K_9:
                        self.start.empty()
                        self.selected_object = sprites.Start(pos)
                    elif event.key == pygame.K_0:
                        self.finish.empty()
                        self.selected_object = sprites.Finish(pos)
                    elif event.key == pygame.K_RETURN:
                        self.save_level('levels/level_1.json')
                    elif event.key == pygame.K_RSHIFT:
                        self.load_level('levels/level_1.json')
                  
                elif event.type == pygame.MOUSEWHEEL:
                    if isinstance(self.selected_object, sprites.Platform):
                        self.selected_object.rotate(event.y * 5)

                elif event.type == pygame.MOUSEMOTION:
                    if self.selected_object:
                        self.selected_object.set_pos(pygame.mouse.get_pos())

            screen.fill(BACKGROUND_COLOR)

            self.platforms.draw(screen)
            self.ladders.draw(screen)
            self.start.draw(screen)
            self.finish.draw(screen)
            self.mines.draw(screen)
            self.coins.draw(screen)

            if self.selected_object:
                self.selected_object.draw(screen)

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()

    def save_level(self, filename):
        assert len(self.start) and len(self.finish)
        
        map_data = {
            'id': 1,
            'map': {
                'start': self.start.sprites()[0].get_pos(),
                'finish': self.finish.sprites()[0].get_pos(),
                'platforms': [p.to_dict() | {'id': i} for i, p in enumerate(self.platforms, 1)],
                'ladders': [p.to_dict() | {'id': i} for i, p in enumerate(self.ladders, 1)],
                'mines': [p.to_dict() | {'id': i} for i, p in enumerate(self.mines, 1)],
                'coins': [p.to_dict() | {'id': i} for i, p in enumerate(self.coins, 1)],
            }
        }

        with open(filename, "w") as f:
            json.dump(map_data, f, indent=4)

    def load_level(self, filename):
        with open(filename) as f:
            map_data = json.load(f)

        self.start = pygame.sprite.Group([sprites.Start(map_data['map']['start'])])
        self.finish = pygame.sprite.Group([sprites.Finish(map_data['map']['finish'])])
        self.platforms = pygame.sprite.Group([sprites.Platform.from_dict(d) for d in map_data['map']['platforms']])
        self.ladders = pygame.sprite.Group([sprites.Ladder.from_dict(d) for d in map_data['map']['ladders']])
        self.mines = pygame.sprite.Group([sprites.Mine.from_dict(d) for d in map_data['map']['mines']])
        self.coins = pygame.sprite.Group([sprites.Coin.from_dict(d) for d in map_data['map']['coins']])


if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
