from src.entity.Space import Space
from src.game.Camera import Camera
from src.game.Global import DEPTH_EFFECT
from src.game.Group import Group
from src.game.Turn import Turn
from src.tools.Data import Data
from src.tools.Random import Random


class Effect:
    @classmethod
    def make(cls, arg, pos, lifetime=-1, offset=16):
        r = cls(arg)
        r.lifetime = lifetime
        r.at = pos
        r.offset = [Random.rand_int(-offset, offset), Random.rand_int(-offset, offset)]
        return r.add()

    def __init__(self, animation):
        self.visible = 1
        self.delay = 0
        self.form = Data.run_cache(animation)
        self.at = Space()
        self.lifetime = 2
        self.offset = Space()
        self.depth = DEPTH_EFFECT

    def add(self):
        Group.objects.add(self)
        Turn.add(self)
        return self

    def remove(self):
        Group.remove(self)
        Turn.remove(self)

    def turn(self):
        if self.lifetime == 0:
            self.remove()
        self.lifetime -= 1

    def draw(self, surface):
        pos = self.at + self.offset
        if Camera.in_camera(pos.x, pos.y):
            self.form.draw(surface, pos.x, pos.y)
            if self.form.ended:
                self.remove()
