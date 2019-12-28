from pyglet.sprite import Sprite, pyglet

from src.game import Global
from src.game.Camera import Camera
from src.tools import Direction


class Picture(Sprite):
    def __init__(self, texture, **kwargs):
        super().__init__(texture, **kwargs, batch=Global.draw_group.batch)
        self.side = 1
        self.side_y = 1
        self.inbound = False
        self.display = False

    def set(self, arg):
        super()._set_texture(arg)

    def reset(self):
        self.set_anchor(self.width / 2, self.height / 2)
        self.side = 1
        self.side_y = 1
        self.scale = 1
        self.scale_x = 1
        self.scale_y = 1

    def set_anchor(self, x, y):
        if isinstance(self.image, pyglet.image.Animation):
            for f in self.image.frames:
                f.image.anchor_x = x
                f.image.anchor_y = y
        else:
            self.image.anchor_x = x
            self.image.anchor_y = y

    def show(self, visible):
        self.display = visible
        self.visible = self.inbound and self.display

    def bound(self, visible):
        self.inbound = visible
        self.visible = self.inbound and self.display

    def clone(self):
        r = Picture(self.image)
        return r

    def face(self, x=0, y=0):
        if x and self.side != x:
            self.side = x
            self.flip(x=1)
        if y and self.side_y != y:
            self.side_y = y
            self.flip(y=1)

    def face_cardinal(self, direction):
        coord = Direction.coord[direction]
        self.face(x=coord[0])

    def resize(self, x=1, y=1):
        if x != 1 and self.width:
            self.scale_x = x / (self.width / self.scale_x)
        if y != 1 and self.height:
            self.scale_y = y / (self.height / self.scale_y)

    def place(self, x, y):
        bound_x = x + Camera.pos[0]
        bound_y = Global.DISPLAY[1] - (y + Camera.pos[1])
        self.update(x=bound_x, y=bound_y)

    def flip(self, x=0, y=0):
        if x:
            self.scale_x *= -1
        if y:
            self.scale_y *= -1

    def switch(self, index):
        pass
