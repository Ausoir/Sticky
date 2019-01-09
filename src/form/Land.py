import pygame
from src.other import Data


class Land:
    def __init__(self, texture_name='Error'):
        image = Data.get_texture(texture_name)
        self.canvas = pygame.Surface(image.get_size())
        self.canvas.blit(image, (0, 0))

    def draw(self, surface, pos):
        surface.blit(self.canvas, pos)
