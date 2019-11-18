from pyglet.sprite import Sprite

from src.game import Global
from src.game.Camera import Camera


class Picture(Sprite):
    def __init__(self, texture, **kwargs):
        super().__init__(texture, **kwargs, batch=Global.draw_group.batch)
        self.image.anchor_x = self.width / 2
        self.image.anchor_y = self.height / 2
        self.direction = 1
        self.direction_y = 1
        self.enabled = False
        self.visible = False
        self.remove = 0

    def set(self, arg):
        super()._set_texture(arg)
        self.image.anchor_x = self.width / 2
        self.image.anchor_y = self.height / 2

    def enable(self, arg):
        self.enabled = arg

    def clone(self):
        r = Picture(self.image)
        return r

    def face(self, x=0, y=0):
        if x and self.direction != x:
            self.direction = x
            self.flip(x=1)
        if y and self.direction_y != y:
            self.direction_y = y
            self.flip(y=1)

    def resize(self, x=1, y=1):
        if x != 1 and self.width:
            self.scale_x = x / (self.width / self.scale_x)
        if y != 1 and self.height:
            self.scale_y = y / (self.height / self.scale_y)

    def place(self, x, y):
        bound_x = x + Camera.pos[0]
        bound_y = Global.DISPLAY[1] - (y + Camera.pos[1])
        self.update(x=bound_x, y=bound_y)
        if self.enabled and 0 < bound_x < Global.DISPLAY[0] and 0 < bound_y < Global.DISPLAY[1]:
            self.visible = True
        else:
            self.visible = False

    def flip(self, x=0, y=0):
        if x:
            self.scale_x *= -1
        if y:
            self.scale_y *= -1
