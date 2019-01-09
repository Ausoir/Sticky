from src.entity.Entity import Entity
from src.form.Sprite import Sprite


class Appendage(Entity, Sprite):
    image_size = (96, 64)

    def __init__(self, texture_name, texture_subset=0):
        Sprite.__init__(texture_name, (32*texture_subset, 0, 32, 64))

    def draw(self, surface, pos):
        self.form.draw(surface, self.pos)
