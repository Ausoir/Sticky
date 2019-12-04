from pyglet.graphics import Batch
from pyglet.graphics import OrderedGroup


class DrawGroup:
    def __init__(self):
        self.fade = 0
        self.batch = Batch()
        self.background = OrderedGroup(0)
        self.tiles = OrderedGroup(1)
        self.objects = OrderedGroup(2)
        self.units = OrderedGroup(3)
        self.effects = OrderedGroup(4)
        self.other = []

    def colorize(self, index, color, fade=0):
        pass

    def draw(self):
        self.batch.draw()
        # for i in self.other:
        #     i.draw()
