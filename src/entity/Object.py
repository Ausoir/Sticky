from src.entity.Space import Space
from src.form.Sprite import Sprite
from src.game.Group import Group


class Object:
    BLOCK = 40

    def __init__(self, form, map):
        self.id = -1
        self.seed = -1
        self.vec = Space()
        self.form = None
        self.make_form(form)
        self.map = map
        self.pos = map.get_tile(0, 0)

    def load(self, p):
        self.id = p[0]
        self.seed = p[1]
        self.pos.load(p[2])
        return 3

    def remove(self):
        Group.remove(self.form)

    def make_form(self, arg):
        if isinstance(self.form, Sprite):
            self.remove()
        self.form = Sprite(Group.object, self.vec, texture_name=arg)

    def update(self):
        self.vec.load(self.pos * Object.BLOCK)

    def move(self, x, y):
        self.pos = self.map.get_tile(self.pos + (x, y))
