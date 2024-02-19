import pygame
from dataclasses import dataclass

class Colors:
    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (128, 128, 128)
    light_gray = (192, 192, 192)
    dark_gray = (64, 64, 64)
    red = (255, 0, 0)
    blue = (85, 171, 255)
    bg_blue = (64, 84, 128)
    green = (85, 255, 171)
    purple = (255, 64, 255)
    yellow = (255,255,0)
    blue_black = (6, 8, 32)
    light_blue_black = (24, 32, 64)


class Sprite:
    def __init__(self, image, x: int, y: int, rotation: float):
        self.x = x
        self.y = y
        self.ogimage = image
        self.rotation = rotation
        self.last_rotation = rotation
        self.target_rotation = rotation
        self.image = pygame.transform.rotate(self.ogimage, self.rotation)
        self.centered = False

    def draw(self, window):
        if self.rotation != self.last_rotation:
            self.image = pygame.transform.rotate(self.ogimage, self.rotation)
            self.last_rotation = self.rotation
        if self.centered:
            window.blit(self.image, (self.x-self.image.get_width()/2, self.y-self.image.get_height()/2))
        else:
            x_offset = (self.image.get_width()-self.ogimage.get_width())/2
            y_offset = (self.image.get_height()-self.ogimage.get_height())/2
            window.blit(self.image, (self.x-x_offset, self.y-y_offset))

    def set_centered(self, centered):
        self.centered = centered


@dataclass
class Scale:
    x: float
    y: float
    autoscroll_offset_x: float
    autoscroll_offset_y: float


class Drawable:
    def __init__(self, scale: Scale, x: int, y: int, width: int, height: int, rotation: float) -> None:
        self.scale = scale
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.sprite = None

    def make_sprite(self, image, centered=False):
        img = pygame.transform.smoothscale(image, (round(self.width*self.scale.x), round(self.height*self.scale.y)))
        self.sprite = Sprite(img, self.x*self.scale.x, self.y*self.scale.y, self.rotation)
        self.sprite.set_centered(centered)

    def update_sprite(self):
        self.sprite.x = (self.x-self.scale.autoscroll_offset_x)*self.scale.x
        self.sprite.y = (self.y-self.scale.autoscroll_offset_y)*self.scale.y
        self.sprite.width = self.width*self.scale.x
        self.sprite.height = self.height*self.scale.y
        self.sprite.rotation = self.rotation

    def draw(self, window):
        self.update_sprite()
        self.sprite.draw(window)
