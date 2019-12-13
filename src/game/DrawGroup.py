from pyglet.graphics import Batch, OrderedGroup


class DrawGroup:
    def __init__(self):
        self.fade = 0
        self.batch = [Batch(), Batch(), Batch(), Batch()]  # tiles, objects, units
        self.group = []
        self.tile_group = OrderedGroup(-99)
        self.other = []

    def add_group(self, group):
        self.group.append(OrderedGroup(group))

    def colorize(self, index, color, fade=0):
        pass

    def draw(self):
        for i in self.batch:
            i.draw()
