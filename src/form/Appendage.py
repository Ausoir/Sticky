from src.tools.Space import Space
from src.game import Global


class Limb:
    def __init__(self):
        self.form = Global.blank_form
        self.texture_num = -1
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
    def __init__(self, texture_num, resize, flip_x, flip_y):
        super().__init__()
        self.texture_num = texture_num
        self.resize = resize
        self.flip_x = flip_x
        self.flip_y = flip_y

    def set(self, sprite):
        self.form = sprite
        self.form.flip(self.flip_x, self.flip_y)
        self.form.image.anchor_x = self.form.width / 2
        if self.flip_y:
            self.form.image.anchor_y = 3
        else:
            self.form.image.anchor_y = self.form.height - 3

    def place(self, x, y):
        diff = self.lower_joint - self.upper_joint
        self.form.rotation = diff.get_atan() - 90
        if self.resize:
            length = int(diff.distance() * 1.1)
            if abs(length) > 2:
                self.form.resize(y=length)
        self.form.place(x + self.upper_joint.x, y - self.upper_joint.y)

    def face(self, side, direction):
        self.form.face(x=side)
        if direction == 1 or direction == 3:
            if self.flip_x == 2:
                self.form.scale_x *= -1
