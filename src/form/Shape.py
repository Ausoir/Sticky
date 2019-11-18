from pyglet.gl import *

from src.entity.Space import Space
from src.form.Line import Line


class Shape:
    def __init__(self, x=0, y=0, width=40, height=40, color=(0, 0, 0, 0), border=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.border = border

    def draw(self, surface):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glBegin(GL_TRIANGLES)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + surface.width, self.y)
        glVertex2f(self.x + surface.width, self.y + surface.height)
        glVertex2f(self.x, self.y + surface.height)
        glEnd()

    def collide(self, point):
        pt = Space(point)
        if self.x <= pt.x <= self.x + self.width:
            if self.y <= pt.y <= self.y + self.height:
                return True
