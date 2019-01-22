from src.entity.Space import Space
from src.form.Sprite import Sprite


class Appendage(Sprite):
    def __init__(self, texture_name, resize=1):
        super().__init__(texture_name=texture_name)
        self.offset = Space()
        self.resize = resize
        self.edge = Space()
        self.pivot = Space(self.size.x / 2, 4)

    def __str__(self):
        return self.offset.__str__() + ',' + self.edge.__str__()

    def update(self):
        if self.resize:
            self.size.y = int((self.edge - self.offset).distance() * 1.5)
        self.rotation = (self.edge - self.offset).get_atan() - 90

    def draw(self, surface, pos):
        super().draw(surface, [pos[0] + self.offset.x, pos[1] + self.offset.y])

    def set_parent(self, parent, tip):
        if tip:
            self.offset = parent.edge
        else:
            self.offset = parent.offset
