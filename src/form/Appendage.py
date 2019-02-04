from src.entity.Space import Space
from src.form.Sprite import Sprite


class Appendage(Sprite):
    def __init__(self, texture_name, resize=1, part=0):
        super().__init__(texture_name=texture_name)
        self.upper_joint = Space()
        self.resize = resize
        self.lower_joint = Space()
        self.part = part

    def __str__(self):
        return self.upper_joint.__str__() + ',' + self.lower_joint.__str__()

    def set(self, texture_name='Error'):
        super().set(texture_name)
        self.pivot = Space(self.size.x / 2, 0)

    def update(self):
        if self.resize:
            self.size.y = int((self.lower_joint - self.upper_joint).distance() * 1.5)
        self.rotation = (self.lower_joint - self.upper_joint).get_atan() - 90

    def draw(self, surface, x, y):
        super().draw(surface, x + self.upper_joint.x, y + self.upper_joint.y)

    def set_parent(self, parent, tip):
        if tip:
            self.upper_joint = parent.lower_joint
        else:
            self.upper_joint = parent.upper_joint
