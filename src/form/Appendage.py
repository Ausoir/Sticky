from src.entity.Space import Space
from src.game import Global


class Limb:
    def __init__(self):
        self.form = Global.blank_form
        self.upper_joint = Space()
        self.lower_joint = Space()

    def __str__(self):
        return self.upper_joint.__str__() + ',' + self.lower_joint.__str__()

    def set(self, sprite):
        pass

    def place(self, x, y):
        diff = self.lower_joint - self.upper_joint
        self.form.rotation = diff.get_atan() - 90

    def set_parent(self, parent, joint):
        if joint == 'u':
            self.upper_joint = parent.lower_joint
        elif joint == 'd':
            self.upper_joint = parent.upper_joint


class Appendage(Limb):
    def __init__(self, sprite, meta):
        super().__init__()
        self.meta = meta  # resize, flip x, flip y
        self.set(sprite)

    def set(self, sprite):
        self.form = sprite
        self.form.flip(self.meta[1], self.meta[2])
        if self.meta[2]:
            self.form.image.anchor_y = 4
        else:
            self.form.image.anchor_y = self.form.image.height

    def place(self, x, y):
        diff = self.lower_joint - self.upper_joint
        self.form.rotation = diff.get_atan() - 90
        if self.meta[0]:
            length = int(diff.distance() * 1.2)
            if length > 0:
                length = max(length, 1)
            else:
                length = min(length, -1)
            self.form.resize(y=length)
        self.form.place(x + self.upper_joint.x, y + self.upper_joint.y)
