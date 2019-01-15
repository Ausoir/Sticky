from src.Group import Group
from src.entity.Object import Object
from src.entity.Space import Space
from src.form.Sprite import Sprite


class Appendage(Object):
    def __init__(self, pos, texture_name, resize=1):
        super().__init__(texture_name)
        self.pos = pos
        self.resize = resize
        self.edge = Space()
        self.form.pivot = Space(self.form.size.x / 2, 4)

    def __str__(self):
        return self.pos.__str__() + ',' + self.edge.__str__()

    def make_form(self, arg):
        if isinstance(self.form, Sprite):
            self.form.remove()
        self.form = Sprite(Group.unit, self.pos, texture_name=arg)

    def update(self):
        if self.resize:
            self.form.size.y = int((self.edge - self.pos).distance()*1.5)
        self.form.pos = self.pos
        self.form.rotation = (self.edge - self.pos).atan() - 90

    def set_parent(self, parent, tip):
        if tip:
            self.pos = parent.edge
        else:
            self.pos = parent.pos
