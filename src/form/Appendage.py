from src.entity.Space import Space


class Appendage:
    def __init__(self, sprite, meta):
        self.form = sprite
        self.upper_joint = Space()
        self.lower_joint = Space()
        self.length = None
        self.rotation = 0
        self.meta = meta  # resize, flip x, flip y
        self.set(sprite)

    def __str__(self):
        return self.upper_joint.__str__() + ',' + self.lower_joint.__str__()

    def set(self, sprite):
        self.form = sprite
        self.form.pivot = Space(self.form.size.x / 2, 0)
        self.length = self.form.size.y
        self.form.flip(self.meta[1], self.meta[2])

    def update(self):
        diff = self.lower_joint - self.upper_joint
        self.rotation = -diff.get_atan() + 90
        if self.meta[0]:
            self.length = int(diff.distance() * 1.5)
            self.form.size.y = self.length
        self.form.rotate(self.rotation)

    def draw(self, surface, x, y):
        self.form.draw(surface, x + self.upper_joint.x, y + self.upper_joint.y)

    def set_parent(self, parent, type):
        if type == 'u':
            self.upper_joint = parent.lower_joint
        elif type == 'd':
            self.upper_joint = parent.upper_joint
