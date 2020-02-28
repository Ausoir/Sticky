from pyglet.gl import *

from src.game import Global


class Shape:
    def __init__(self, x, y, z, group=None, width=40, height=40, color=(0, 0, 0, 0), border=0):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.color = color + color + color + color
        self.border = border
        self.group = group
        self.submission = None
        self.removed = False
        self.visible = True

    def add_batch(self):
        if self.submission:
            self.update()
        else:
            self.removed = False
            self.submission = Global.draw_group.batch.add(4, gl.GL_QUADS, self.group,
                                                          ('v3i', self.get_vertices()),
                                                          ('c4B', self.color)
                                                          )

    def remove_batch(self):
        if self.submission:
            self.removed = True
            self.submission.delete()
            self.submission = None

    def show(self, visible):
        self.visible = visible

    def get_vertices(self):
        left = self.x + Global.OFFSET[0]
        right = left + self.width
        up = Global.DISPLAY[1] - self.y + Global.OFFSET[1]
        down = up - self.height
        return (left, up, self.z,
                right, up, self.z,
                right, down, self.z,
                left, down, self.z)

    def update(self, x=None, y=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if self.visible:
            self.submission.vertices = self.get_vertices()
            self.submission.colors = self.color
        else:
            self.submission.vertices = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    def set_solid_color(self, color):
        self.color = color + color + color + color

    def set_gradient(self, color1, color2, color3, color4):
        self.color = color1 + color2 + color3 + color4

    def collide(self, point_x, point_y):
        if self.x <= point_x <= self.x + self.width:
            if self.y <= point_y <= self.y + self.height:
                return True
