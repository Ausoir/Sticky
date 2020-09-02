from pyglet.image import Animation

from src.form.Sprite import Sprite
from src.game import Global


class Picture(Sprite):
    def __init__(self, texture, z=0, group=None):
        super().__init__(texture, z=z, group=group or Global.draw_group.group_object, batch=Global.draw_group.batch)
        self.inbound = False
        self.display = False

    def set(self, arg):
        super()._set_texture(arg)

    def reset(self):
        self.set_anchor(self.width / 2, self.height / 2)
        self.scale = 1
        self.scale_x = 1
        self.scale_y = 1

    def set_anchor(self, x, y):
        if isinstance(self.image, Animation):
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

    def face(self, direction):
        self.rotation = 90 * direction

    def place(self, x, y, **kwargs):
        self.update(x=Global.OFFSET[0] + x, y=Global.OFFSET[1] + y, **kwargs)

    def switch(self, index):
        pass

    def colorize(self, color):
        self.color = color

    def delete(self):
        if self._vertex_list is not None:
            super().delete()


class Model(Picture):
    def __init__(self, clips, **kwargs):
        super().__init__(clips[0], **kwargs)
        self.clips = clips

    def switch(self, index):
        self.set(self.clips[index])
