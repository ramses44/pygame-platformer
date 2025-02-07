import pygame
import os
from PIL import Image


def load_image(name):
    fullname = os.path.join('assets', 'sprites', name)
    image = pygame.image.load(fullname)

    return image


def load_GIF(filename):
    filename = os.path.join('assets', 'sprites', filename)
    pil_image = Image.open(filename)

    frames = []

    try:
        while True:
            frame = pil_image.copy()
            frame = frame.convert("RGBA")
            frame_data = frame.tobytes()

            pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
            frames.append(pygame_surface)

            pil_image.seek(pil_image.tell() + 1)
    except EOFError:
        pass

    return frames


def scale_image(image: pygame.Surface, scale_coef: float):
    scaled_size = [image.get_size()[i] * scale_coef for i in range(2)]
    return pygame.transform.scale(image, scaled_size)


class Size:
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'

    @staticmethod
    def sizes():
        return [Size.SMALL, Size.MEDIUM, Size.LARGE]


class SpriteBase(pygame.sprite.Sprite):
    id: int
    image: pygame.Surface
    rect: pygame.Rect

    def __copy__(self):
        return type(self).from_dict(self.to_dict())

    def to_dict(self):
        return {'id': self.id, 'pos': self.get_pos()}

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(**dct)
    
    def set_pos(self, pos):
        self.rect.center = pos

    def get_pos(self):
        return self.rect.center
    
    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def setup_image(self, pos: tuple[int, int], filename: str, scale_coef = 1):
        self.image = load_image(filename)
        self.image = scale_image(self.image, scale_coef)

        self.rect = self.image.get_rect()
        self.set_pos(pos)

        self.mask = pygame.mask.from_surface(self.image)


class Platform(SpriteBase):
    SPRITE_FILENAME_TEMPLATE = 'platform-%s.png'
    SPRITE_SCALE_COEF = 1 / 3

    def __init__(self, id: int, pos: tuple[int, int], size: str, angle: float = 0, **kwargs):
        super().__init__(**kwargs)

        if size not in Size.sizes():
            raise ValueError(f'Invalid size {size}, expected one of {Size.sizes()}')

        self.id = id
        self.size = size
        self.angle = .0

        self.setup_image(pos, self.SPRITE_FILENAME_TEMPLATE % size, self.SPRITE_SCALE_COEF)

        self.base_image = self.image
        self.rotate(angle)

    def to_dict(self):
        return super().to_dict() | {'size': self.size, 'angle': self.angle}

    def rotate(self, angle):
        self.angle = (self.angle + angle) % 360
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def get_surface_height(self, x):
        local_x = x - self.rect.x
        for y in range(self.rect.height):
            if self.mask.get_at((local_x, y)):
                return y
        return self.rect.height


class Ladder(SpriteBase):
    SPRITE_FILENAME_TEMPLATE = 'ladder-%s.png'
    SPRITE_SCALE_COEF = 1 / 2

    def __init__(self, id: int, pos: tuple[int, int], size: str, **kwargs):
        super().__init__(**kwargs)

        if size not in Size.sizes():
            raise ValueError(f'Invalid size {size}, expected one of {Size.sizes()}')

        self.id = id
        self.size = size

        self.setup_image(pos, self.SPRITE_FILENAME_TEMPLATE % size, self.SPRITE_SCALE_COEF)

    def to_dict(self):
        return super().to_dict() | {'size': self.size}
        

class Mine(SpriteBase):
    SPRITE_FILENAME = 'mine.png'
    SPRITE_SCALE_COEF = 1 / 6
    BOOM_ANIMATION_FILENAME = 'boom.gif'
    BOOM_ANIMATION_SCALE_COEF = 2 / 3
    BOOM_ANIMATION_OFFSET = (-0.25,) * 2

    def __init__(self, id: int, pos: tuple[int, int], **kwargs):
        super().__init__(**kwargs)

        self.id = id
        self.setup_image(pos, self.SPRITE_FILENAME, self.SPRITE_SCALE_COEF)
        self.boom_images = [scale_image(frame, self.BOOM_ANIMATION_SCALE_COEF) 
                            for frame in load_GIF(self.BOOM_ANIMATION_FILENAME)]
        self.explosion_frame = -1

    def update(self):
        if self.is_exploding():
            self.explode_update()

    def explode_update(self):
        if not self.is_exploding():
            self.set_pos((
                self.get_pos()[0] + self.BOOM_ANIMATION_OFFSET[0],
                self.get_pos()[1] + self.BOOM_ANIMATION_OFFSET[1]
            ))

        self.explosion_frame += 1
        if self.explosion_frame >= len(self.boom_images):
            self.image = pygame.Surface((0, 0))
            self.rect = self.image.get_rect()
            self.kill()
        else:
            self.image = self.boom_images[self.explosion_frame]
            self.rect = self.image.get_rect(center=self.get_pos())

    def is_exploding(self):
        return self.explosion_frame != -1


class Coin(SpriteBase):
    SPRITE_FILENAME = 'coin.png'
    SPRITE_SCALE_COEF = 1 / 25

    def __init__(self, id: int, pos: tuple[int, int], **kwargs):
        super().__init__(**kwargs)

        self.id = id
        self.setup_image(pos, self.SPRITE_FILENAME, self.SPRITE_SCALE_COEF)

    def on_pick_up(self):
        self.kill()


class Start(SpriteBase):
    SPRITE_FILENAME = 'start.png'
    SPRITE_SCALE_COEF = 1 / 10

    def __init__(self, pos: tuple[int, int], **kwargs):
        super().__init__(**kwargs)

        self.setup_image(pos, self.SPRITE_FILENAME, self.SPRITE_SCALE_COEF)

    def to_dict(self):
        return {'pos': self.get_pos()}
     

class Finish(SpriteBase):
    SPRITE_FILENAME = 'finish.png'
    SPRITE_SCALE_COEF = 1 / 10

    def __init__(self, pos: tuple[int, int], **kwargs):
        super().__init__(**kwargs)

        self.setup_image(pos, self.SPRITE_FILENAME, self.SPRITE_SCALE_COEF)   

    def to_dict(self):
        return {'pos': self.get_pos()}
