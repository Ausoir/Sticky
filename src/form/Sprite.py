import math

import pygame

from src.entity.Space import Space
from src.tools.Data import Data


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group, vec=Space(), texture_name='Error'):
        super().__init__()
        self.visible = 1
        group.append(self)
        self.vec = vec
        self.image = Data.get_image(texture_name, 1)
        self.orig_image = self.image
        self.rotation = 0
        self.direction = 1
        self.size = Space(self.image.get_size())
        self.rect = self.size.to_list()
        self.pivot = Space(self.size.x / 2, self.size.y / 2)

    def draw(self, surface):
        if self.size.x != 0 and self.size.y != 0:
            self.image = self.orig_image
            if self.size.x < 0:
                self.image = pygame.transform.flip(self.orig_image, 1, 0)
            if self.size.y < 0:
                self.image = pygame.transform.flip(self.orig_image, 0, 1)
            self.image = pygame.transform.smoothscale(self.image, self.size.abs().to_list())
            self.image = pygame.transform.rotate(self.image, self.rotation)
            pp = self.pivot - (self.size * .5)
            aa = math.atan2(-pp.y, -pp.x)
            piv = pp.distance()
            ax = math.cos(math.radians(-self.rotation) + aa) * piv
            ay = math.sin(math.radians(-self.rotation) + aa) * piv
            self.rect = self.image.get_rect(center=[self.vec.x+ax, self.vec.y+ay])
            surface.blit(self.image, self.rect)

    def face(self, direction):
        if self.direction != direction:
            self.direction = direction
            self.orig_image = pygame.transform.flip(self.orig_image, 1, 0)
