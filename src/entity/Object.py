from src.Group import Group
from src.entity.Space import Space
from src.form.Sprite import Sprite


class Object:
    def __init__(self, form):  # same characteristics across all objects
        self.id = -1
        self.seed = -1
        self.pos = Space()
        self.form = None
        self.make_form(form)

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
        self.form = Sprite(Group.object, self.pos, texture_name=arg)
