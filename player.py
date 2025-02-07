import pygame
import math
import itertools

from config import GRAVITY, PLAYER_SPEED, JUMP_STRENGTH, LADDER_CLIMBING_SPEED
from sprites import load_image, scale_image


class Direction:
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

    @staticmethod
    def directions():
        return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]


class Player(pygame.sprite.Sprite):
    RUNNING_SPRITE_FILENAMES = ["character_1.png", "character_2.png"]
    CLIMBING_SPRITE_FILENAMES = ["character_1.png", "character_2.png"]
    FRAME_RATE_COEF = 7
    SPRITE_SCALE_COEF = 1 / 3

    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)

        self.sprite_num = 0

        self.running_images = list(itertools.chain(*(
            [scale_image(load_image(fname), self.SPRITE_SCALE_COEF)] * self.FRAME_RATE_COEF
            for fname in self.RUNNING_SPRITE_FILENAMES
        )))
        self.climbing_images = list(itertools.chain(*(
            [scale_image(load_image(fname), self.SPRITE_SCALE_COEF)] * self.FRAME_RATE_COEF
            for fname in self.CLIMBING_SPRITE_FILENAMES
        )))

        self.image = self.running_images[self.sprite_num]
        self.rect = self.image.get_rect(midbottom=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.climbing_ladder = None
        self.rotation = Direction.RIGHT

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def rotate(self, direction):
        if (self.rotation != direction):
            self.rotation = direction
            self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pygame.mask.from_surface(self.image)

    def switch_frame(self):
        self.sprite_num = (self.sprite_num + 1) % len(self.running_images)
        direction = self.rotation
        self.image = self.running_images[self.sprite_num]
        self.rotation = Direction.RIGHT
        self.rotate(direction)

    def jump(self, platforms):
        if self.is_on_ground(platforms) or self.climbing_ladder and self.climbing_ladder.rect.top > self.rect.center[1]:
            self.velocity_y -= JUMP_STRENGTH

    def go(self, direction):
        if direction == Direction.LEFT:
            self.rotate(direction)
            self.velocity_x = -PLAYER_SPEED
        elif direction == Direction.RIGHT:
            self.rotate(direction)
            self.velocity_x = PLAYER_SPEED
        elif direction == Direction.UP and self.climbing_ladder:
            self.velocity_y = -LADDER_CLIMBING_SPEED
        elif direction == Direction.DOWN and self.climbing_ladder:
            self.velocity_y = LADDER_CLIMBING_SPEED

    def stop(self, direction):
        if direction in (Direction.LEFT, Direction.RIGHT):
            self.velocity_x = 0
        elif direction in (Direction.UP, Direction.DOWN) and self.climbing_ladder:
            self.velocity_y == 0
        
    def force_move(self, direction, delta = 1):
        match direction:
            case Direction.UP:
                self.rect.y -= delta
            case Direction.DOWN:
                self.rect.y += delta
            case Direction.LEFT:
                self.rect.x -= delta
            case Direction.RIGHT:
                self.rect.x += delta

    def push_out(self, platform):
        if not pygame.sprite.collide_mask(self, platform):
            return

        for delta in range(max(platform.mask.get_size()) + max(self.mask.get_size())):
            for direction in Direction.directions():
                self.force_move(direction, delta)

                if pygame.sprite.collide_mask(self, platform):
                    self.force_move(direction, -delta)
                else:
                    return
            
    def check_handle_collisions(self, platforms) -> bool:
        pushed = False
        for _ in range(len(platforms)):
            for platform in platforms:
                if pygame.sprite.collide_mask(self, platform):
                    self.push_out(platform)
                    pushed = True
                    break
            else:
                break
        
        return pushed
    
    def is_on_ground(self, platforms) -> bool:
        self.force_move(Direction.DOWN)
        res = any(map(lambda x: pygame.sprite.collide_mask(self, x), platforms))
        self.force_move(Direction.UP)
        return res

    def update(self, platforms, ladders, mines, coins):
        # Применяем гравитацию
        if not self.climbing_ladder and not self.is_on_ground(platforms):
            self.velocity_y += GRAVITY
            # self.velocity_y = min(self.velocity_y, MAX_FALL_SPEED)  # Ограничиваем скорость падения

        if self.velocity_x:
            self.switch_frame()

        x_steps = int(abs(self.velocity_x))
        y_steps = int(abs(self.velocity_y))

        for _ in range(x_steps):
            self.rect.x += self.velocity_x / x_steps
            if self.check_handle_collisions(platforms):
                break

        for _ in range(y_steps):
            self.rect.y += self.velocity_y / y_steps
            if self.check_handle_collisions(platforms):
                self.velocity_y = 0
                break

        # Логика для лестниц
        self.climbing_ladder = None
        for ladder in ladders:
            if pygame.sprite.collide_mask(self, ladder):
                if not self.climbing_ladder or self.climbing_ladder.rect.top > ladder.rect.top:
                    self.climbing_ladder = ladder

        if self.climbing_ladder:
            self.velocity_y = 0  # Останавливаем падение на лестнице

        # Логика для мин
        for mine in mines:
            if pygame.sprite.collide_mask(self, mine):
                mine.explode_update()

        # Логика для монет
        for coin in coins:
            if pygame.sprite.collide_mask(self, coin):
                coin.on_pick_up()
