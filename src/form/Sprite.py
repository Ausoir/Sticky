import math

import pygame

from src.entity.Space import Space
from src.game.Camera import Camera
from src.tools.Math import Math


class Sprite:
    def __init__(self, args):
        self.rotation = 0
        self.image = None
        self.orig_image = None
        self.size = Space()
        self.pivot = None
        self.rot_pos = [0, 0]
        self.direction = [1, 0]
        self.set(args[0])

    def clone(self):
        new = Sprite([self.orig_image])
        return new

    def set(self, image):
        self.image = image
        self.orig_image = self.image
        self.resize(self.image.get_size())

    def resize(self, arg=None):
        if arg:
            self.size.load(arg)
            self.pivot = Space(self.size.x / 2, self.size.y / 2)
        x_flip = self.direction[0] != 1
        y_flip = self.direction[1] != 0
        if x_flip or y_flip:
            dir_x = 1 if x_flip else 0
            dir_y = 1 if y_flip else 0
            self.image = pygame.transform.flip(self.orig_image, dir_x, dir_y)
        else:
            self.image = self.orig_image
        scale = [max(1, self.size.x), max(1, self.size.y)]
        self.image = pygame.transform.smoothscale(self.image, scale)

    def rotate(self, angle):
        self.rotation = angle
        self.resize()
        self.image = pygame.transform.rotozoom(self.image, self.rotation, 1)
        pp = self.pivot - (self.size * (.5, .5))
        aa = math.degrees(math.atan2(-pp.y, -pp.x))
        piv = pp.distance()
        self.rot_pos[0] = Math.cos(-self.rotation + aa) * piv
        self.rot_pos[1] = Math.sin(-self.rotation + aa) * piv

    def draw(self, surface, x, y):
        if self.size.x > 1 and self.size.y > 1:
            bounds = [x + self.rot_pos[0] + Camera.pos[0], y + self.rot_pos[1] + Camera.pos[1]]
            rect = self.image.get_rect(center=bounds)
            surface.blit(self.image, rect)

    def flip(self, x, y):
        if x or y:
            self.orig_image = pygame.transform.flip(self.orig_image, x, y)
