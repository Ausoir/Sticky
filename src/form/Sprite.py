import pygame
from src.other import Data
from src.entity.Entity import Entity


class Sprite(Entity):
    def __init__(self, texture_name='Error', subset=None):
        super().__init__()
        self.form = Data.get_cache_image(texture_name)
        if subset is None:
            self.canvas = pygame.Surface(self.form.get_size())
            self.canvas.blit(self.form, (0, 0))
        else:
            self.canvas = pygame.Surface((subset[2], subset[3]))
            self.canvas.blit(self.form, (0, 0), subset)

    def load(self, p):
        super().load(p)
        self.resize(self.size)

    def resize(self, size):
        if size is None:
            self.canvas = pygame.transform.scale(self.canvas, self.canvas.get_size())
        else:
            self.canvas = pygame.transform.scale(self.canvas, size)

    def draw(self, surface):
        surface.blit(self.canvas, self.pos)
