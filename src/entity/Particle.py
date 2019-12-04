import random

from src.entity.Prop import Prop
from src.game.Turn import Turn


class Particle(Prop):
    @classmethod
    def make(cls, arg, pos, glow=-1, lifetime=10, offset=16, direction=1):
        from src.entity.Stock import Stock
        r = cls(Stock.location)
        r.set_form(arg)
        r.lifetime = lifetime
        r.pos = Stock.location.get_tile_from_vec(pos.x, pos.y)
        r.vec = pos
        r.offset = [random.randint(-offset, offset), random.randint(-offset, offset)]
        r.form.face(direction)
        if glow >= 0:
            r.glow(glow)
        return r.add()

    def __init__(self, loc):
        super().__init__(loc)
        self.lifetime = 4
        self.collision_type = 0
        self.offset = None

    def add(self):
        self.removed = 0
        Turn.add(self.turn)
        self.relocate(self.pos.x, self.pos.y, force=1)
        return self

    def remove(self):
        self.removed = 1
        Turn.remove(self.turn)
        self.pos.things.remove(self)

    def turn(self):
        if self.lifetime == 0:
            self.remove()
        self.lifetime -= 1

    def hit(self, damage, accuracy=None, hitter=None):
        pass

    def draw(self, surface):
        self.form.draw(surface, self.vec.x + self.offset[0], self.vec.y + self.offset[1])

    def update_vec(self):
        pass
