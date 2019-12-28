from pyglet.graphics import Batch


class DrawGroup:
    def __init__(self):
        self.fade = 0
        self.batch = Batch()
        self.other = []

    def colorize(self, index, color, fade=0):
        pass

    def draw(self):
        self.batch.draw()
