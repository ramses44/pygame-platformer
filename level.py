import pygame

import sprites
from player import Player
from config import WINDOW_SIZE


class Status:
    IN_PROGRESS = 1
    FAILED = 2
    FINISHED = 3


class Level:
    def __init__(self, level_id, level_data):
        self.id = level_id

        self.platforms = pygame.sprite.Group([sprites.Platform.from_dict(d) for d in level_data['map']['platforms']])
        self.ladders = pygame.sprite.Group([sprites.Ladder.from_dict(d) for d in level_data['map']['ladders']])
        self.mines = pygame.sprite.Group([sprites.Mine.from_dict(d) for d in level_data['map']['mines']])
        self.coins = pygame.sprite.Group([sprites.Coin.from_dict(d) for d in level_data['map']['coins']])

        self.start = sprites.Start(level_data['map']['start'])
        self.finish = sprites.Finish(level_data['map']['finish'])
        self.player = Player(self.start.get_pos())

        self.max_coins = len(self.coins)
        self.status = Status.IN_PROGRESS
        
    def update(self):
        self.mines.update()

        if self.status == Status.IN_PROGRESS:
            self.player.update(self.platforms, self.ladders, self.mines, self.coins)

            if self.check_finish():
                self.status = Status.FINISHED
            elif self.check_fail():
                self.status = Status.FAILED

    def draw(self, screen):
        self.platforms.draw(screen)
        self.ladders.draw(screen)
        self.coins.draw(screen)
        self.start.draw(screen)
        self.finish.draw(screen)
        self.mines.draw(screen)

        if self.status == Status.IN_PROGRESS:
            self.player.draw(screen)

    def get_status(self):
        return self.status

    def check_finish(self):
        return pygame.sprite.collide_mask(self.player, self.finish)
    
    def check_fail(self):
        return self.player.rect.bottom > WINDOW_SIZE[1] * 2 or \
            any(map(lambda x: x.is_exploding(), self.mines))
    
    def coins_collected(self):
        return self.max_coins - len(self.coins)