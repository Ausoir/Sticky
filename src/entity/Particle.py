import random

from src.entity.Prop import Prop
from src.game.Turn import Turn


class Particle(Prop):
    @classmethod
    def make(cls, arg, pos, glow=-1, lifetime=10, offset=16, direction=1):
        from src.game import Global
        r = cls()
        r.set_form(arg)
        r.lifetime = lifetime
        r.pos = Global.location.get_tile_from_vec(pos.x, pos.y)
        r.vec = pos + 0
        r.offset = [offset, offset]
        r.form.face(direction)
        if glow >= 0:
            r.pos.glow(glow)
        return r.add()

    def __init__(self):
        super().__init__()
        self.lifetime = 4
        self.obstruct_type = 0
        self.offset = None

    def add(self):
        self.offset[0] = random.randint(-self.offset[0], self.offset[0])
        self.offset[1] = random.randint(-self.offset[1], self.offset[1])
        self.removed = 0
        self.form.show(True)
        Turn.add(self.turn)
        self.relocate(self.pos.x, self.pos.y, force=1)
        return self

    def remove(self):
        self.removed = 1
        self.form.show(False)
        Turn.remove(self.turn)
        self.pos.things.remove(self)

    def turn(self):
        if self.lifetime == 0:
            self.remove()
        self.lifetime -= 1

    def set_form(self, arg):
        super().set_form(arg)
        self.form.z = 800

    def set_row(self, row):
        pass

    def hit(self, damage, accuracy=None, hitter=None):
        return 0

    def update(self):
        diff = self.pos.get_center() - self.vec
        self.vec += diff * .07
        self.form.place(self.vec.x + self.offset[0], self.vec.y + self.offset[1])
