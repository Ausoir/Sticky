import math

import pygame

from src.entity.Space import Space
from src.game.Camera import Camera
from src.tools.Data import Data


class Sprite(pygame.sprite.Sprite):
    def __init__(self, texture_name):
        super().__init__()
        self.visible = 1
        self.rotation = 0
        self.direction = 1
        self.image = None
        self.orig_image = None
        self.size = None
        self.rect = None
        self.pivot = None
        self.offset = [0, 0]
        self.set(texture_name)
        self.flipped = 0

    def set(self, texture_name='Error'):
        self.image = Data.get_image(texture_name, 1)
        self.orig_image = self.image
        self.size = Space(self.image.get_size())
        self.rect = self.size.to_list()
        self.pivot = Space(self.size.x / 2, self.size.y / 2)

    def draw(self, surface, x, y):
        if self.size.x != 0 and self.size.y != 0:
            self.image = self.orig_image
            if self.size.x < 0:
                self.image = pygame.transform.flip(self.orig_image, 1, 0)
            if self.size.y < 0:
                self.image = pygame.transform.flip(self.orig_image, 0, 1)
            self.image = pygame.transform.smoothscale(self.image, self.size.abs().to_list())
            if self.rotation:
                self.image = pygame.transform.rotozoom(self.image, self.rotation, 1)
            pp = self.pivot - (self.size * (.5, .5))
            aa = math.atan2(-pp.y, -pp.x)
            piv = pp.distance()
            ax = math.cos(math.radians(-self.rotation) + aa) * piv
            ay = math.sin(math.radians(-self.rotation) + aa) * piv
            rect = [x + ax + Camera.pos[0] + self.offset[0], y + ay + Camera.pos[1] + self.offset[1]]
            self.rect = self.image.get_rect(center=rect)
            surface.blit(self.image, self.rect)

    def face(self, direction):
        if self.direction != direction:
            self.direction = direction
            self.orig_image = pygame.transform.flip(self.orig_image, 1, 0)

    def flip(self, flip):
        if flip == 1 and not self.flipped:
            self.orig_image = pygame.transform.flip(self.orig_image, 0, 1)
            self.rotation += 180
            self.flipped = 1
        elif flip == -1 and self.flipped:
            self.orig_image = pygame.transform.flip(self.orig_image, 0, 1)
            self.rotation -= 180
            self.flipped = 0
