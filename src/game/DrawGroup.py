from pyglet.graphics import Batch
from pyglet.graphics import OrderedGroup

from src.game import Global
from src.tools.Data import Data


class DrawGroup:
    def __init__(self):
        self.fade = 0
        self.background_image = None
        self.batch = Batch()
        self.background = OrderedGroup(0)
        self.tiles = OrderedGroup(1)
        self.objects = OrderedGroup(2)
        self.units = OrderedGroup(3)
        self.effects = OrderedGroup(4)
        self.other = []

    def colorize(self, index, color, fade=0):
        pass

    def set_background(self, arg):
        self.background_image = Data.get_form(arg, group=self.background)
        # self.background_image.visible = True
        self.on_resize()

    def on_resize(self):
        self.background_image.update(x=Global.CENTER[0], y=Global.CENTER[1])
        self.background_image.resize(x=Global.DISPLAY[0], y=Global.DISPLAY[1])

    def draw(self):
        self.batch.draw()
        # for i in self.other:
        #     i.draw()
