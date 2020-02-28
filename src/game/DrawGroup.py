from pyglet.graphics import Batch, OrderedGroup


class DrawGroup:
    def __init__(self):
        self.fade = 0
        self.batch = Batch()
        self.group_tile = OrderedGroup(0)
        self.group_shade = OrderedGroup(1)
        self.group_object = OrderedGroup(2)
        self.group_overlay = OrderedGroup(3)
        self.group_gui = OrderedGroup(4)

    def draw(self):
        self.batch.draw()
