from src.tools.Space import Space
from src.game import Global


class Limb:
    def __init__(self):
        self.index = -1
        self.form = Global.blank_form
        self.texture_num = -1
        self.upper_joint = Space()
        self.lower_joint = Space()
        self.child = None

    def __str__(self):
        return self.upper_joint.__str__() + ',' + self.lower_joint.__str__()

    def place(self, x, y):
        pass

    def set_parent(self, parent, joint):
        parent.child = self
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
        if self.flip_x > 0:
            self.form.scale_x *= -1
        if self.flip_y > 0:
            self.form.scale_y *= -1
        self.form.image.anchor_x = self.form.width / 2
        if self.flip_y:
            self.form.image.anchor_y = 3
        else:
            self.form.image.anchor_y = self.form.height - 3

    def place(self, x, y):
        diff = self.lower_joint - self.upper_joint
        rotation = diff.get_atan() - 90
        if self.resize:
            length = diff.distance()
            if abs(length) > 2:
                scale_y = length / (self.form.height / self.form.scale_y)
                self.form.place(x + self.upper_joint.x, y - self.upper_joint.y, rotation=rotation, scale_y=scale_y)
                return
        self.form.place(x + self.upper_joint.x, y - self.upper_joint.y, rotation=rotation)

    def flip(self, side, direction):
        if side <= 0:
            self.form.scale_x *= -1
        if self.flip_x == -1 and direction % 2 == 0:
            self.form.scale_x *= -1
