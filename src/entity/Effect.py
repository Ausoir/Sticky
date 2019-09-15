import random

from src.entity.Space import Space
from src.game.Camera import Camera
from src.game.Group import Group
from src.game.Turn import Turn
from src.tools.Data import Data


class Effect:
    @classmethod
    def make(cls, arg, pos, lifetime=10, offset=16):
        r = cls(arg)
        r.lifetime = lifetime
        r.at = pos
        r.offset = [random.randint(-offset, offset), random.randint(-offset, offset)]
        return r.add()

    def __init__(self, animation):
        self.visible = 1
        self.form = Data.run_cache(animation)
        self.at = Space()
        self.lifetime = 2
        self.offset = Space()
        self.depth = 4

    def add(self):
        Group.effects.add(self)
        Turn.add(self.turn)
        return self

    def remove(self):
        Group.remove(self)
        Turn.remove(self.turn)

    def turn(self):
        if self.lifetime == 0:
            self.remove()
        self.lifetime -= 1

    def draw(self, surface):
        pos = self.at + self.offset
        if Camera.in_camera(pos.x, pos.y):
            self.form.draw(surface, pos.x, pos.y)
