from pyglet.gl import *

from src.game import Global


class Shape:
    def __init__(self, x, y, width=40, height=40, color=(0, 0, 0, 0), border=0):
        self.x = x
        self.y = y
        self.z = 1
        self.width = width
        self.height = height
        self.color = color
        self.border = border

    @staticmethod
    def draw_rect(x, y, z, width, height, color):
        right = x + width
        up = Global.DISPLAY[1] - y
        down = up - height
        vertices = [x, up, z,
                    right, up, z,
                    right, down, z,
                    x, down, z]
        color = color + color + color + color
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v3i', vertices), ('c4B', color))

    def draw(self):
        Shape.draw_rect(self.x, self.y, self.z, self.width, self.height, self.color)

    def collide(self, point_x, point_y):
        if self.x <= point_x <= self.x + self.width:
            if self.y <= point_y <= self.y + self.height:
                return True
