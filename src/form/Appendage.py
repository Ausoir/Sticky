from src.entity.Space import Space


class Appendage:
    def __init__(self, sprite, resize=1, part=0):
        self.form = sprite
        self.upper_joint = Space()
        self.resize = resize
        self.lower_joint = Space()
        self.part = part
        self.length = None
        self.rotation = 0
        self.set(sprite)

    def __str__(self):
        return self.upper_joint.__str__() + ',' + self.lower_joint.__str__()

    def set(self, sprite):
        self.form = sprite
        self.form.pivot = Space(self.form.size.x / 2, 0)
        self.length = self.form.size.y

    def update(self):
        diff = self.lower_joint - self.upper_joint
        self.rotation = -diff.get_atan() + 90
        if self.resize:
            self.length = int(diff.distance() * 1.5)
            self.form.size.y = self.length
        self.form.rotate(self.rotation)

    def draw(self, surface, x, y):
        self.form.draw(surface, x + self.upper_joint.x, y + self.upper_joint.y)

    def set_parent(self, parent, tip):
        if tip:
            self.upper_joint = parent.lower_joint
        else:
            self.upper_joint = parent.upper_joint
