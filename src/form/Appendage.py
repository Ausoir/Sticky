from src.entity.Object import Object
from src.entity.Space import Space
from src.form.Sprite import Sprite
from src.game.Group import Group


class Appendage(Sprite):
    def __init__(self, vec, texture_name, resize=1):
        super().__init__(Group.unit, vec=vec, texture_name=texture_name)
        self.offset = Space()
        self.resize = resize
        self.edge = Space()
        self.pivot = Space(self.size.x / 2, 4)
        self.orig_pos = vec

    def __str__(self):
        return self.offset.__str__() + ',' + self.edge.__str__()

    def update(self):
        if self.resize:
            self.size.y = int((self.edge - self.offset).distance() * 1.5)
        self.vec = self.offset + self.orig_pos
        self.rotation = (self.edge - self.offset).atan() - 90

    def set_parent(self, parent, tip):
        if tip:
            self.offset = parent.edge
        else:
            self.offset = parent.offset
