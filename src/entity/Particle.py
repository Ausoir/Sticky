import random

from src.entity.Image import Image
from src.game.Camera import Camera
from src.game.Turn import Turn


class Particle(Image):
    @classmethod
    def make(cls, arg, pos, glow=-1, lifetime=6, offset=0, direction=4):
        r = cls(pos.location)
        r.name = arg
        r.set_form(arg)
        r.lifetime = lifetime
        r.pos = pos
        r.vec = pos.get_center()
        r.offset = [offset, offset]
        r.form.face(direction % 4)
        if glow >= 0:
            r.pos.glow(glow)
        return r.add()

    def __init__(self, location):
        super().__init__(location)
        self.pos = None
        self.lifetime = 4
        self.obstruct_type = 0
        self.offset = None

    def add(self):
        self.offset[0] = random.randint(-self.offset[0], self.offset[0])
        self.offset[1] = random.randint(-self.offset[1], self.offset[1])
        self.form.show(True)
        Turn.add(self.turn)
        self.pos.others.append(self)
        return self

    def remove(self):
        self.form.show(False)
        Turn.remove(self.turn)
        self.pos.others.remove(self)

    def turn(self):
        if self.lifetime == 0:
            self.remove()
        else:
            self.lifetime -= 1

    def relocate(self, to=None, x=None, y=None, force=False):
        if to is None:
            to = self.pos.location.get_tile(x, y, limit=True)
        if force or to != self.pos:
            self.pos.others.remove(self)
            to.others.append(self)
            self.pos = to
            self.vec = to.get_center()
            return True

    def set_form(self, arg):
        super().set_form(arg)
        self.form.z = 800

    def bound(self, arg):
        pass

    def update(self):
        bound_x, bound_y = Camera.get_relative_pos(self.vec.x, self.vec.y)
        self.form.place(bound_x + self.offset[0], bound_y + self.offset[1])
