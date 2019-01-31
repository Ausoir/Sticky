import pygame

from src.entity.Space import Space
from src.form.Line import Line
from src.game.Camera import Camera


class Shape:
    def __init__(self, depth, vec, color, vertices, border=0):
        self.depth = depth
        self.vec = vec
        self.vertices = vertices
        self.color = color
        self.lines = []
        self.canvas = None
        self.border = border
        self.redraw()

    @staticmethod
    def make_rect(size):
        return ((0, 0),
                (size[0]-1, 0),
                (size[0]-1, size[1]-1),
                (0, size[1]-1))

    def redraw(self):
        self.lines = []
        prev_pt = None
        high_x = 0
        high_y = 0
        for i in self.vertices:
            if prev_pt is not None:
                self.lines.append(Line(Space(prev_pt), Space(i)))
            prev_pt = i
            high_x = max(high_x, i[0])
            high_y = max(high_y, i[1])
        self.lines.append(Line(Space(prev_pt), Space(self.vertices[0])))
        self.canvas = pygame.Surface((high_x+1, high_y+1), pygame.SRCALPHA, 32)
        pygame.draw.polygon(self.canvas, self.color, self.vertices)
        if self.border:
            pygame.draw.polygon(self.canvas, (0, 0, 0), self.vertices, self.border)

    def draw(self, surface):
        surface.blit(self.canvas, [self.vec.x + Camera.pos[0], self.vec.y + Camera.pos[1]])

    def collide(self, point):
        mouse = Line(Space(-self.vec), Space(point) - self.vec)
        r = 0
        for line in self.lines:
            r += (1 if line.cross_line(mouse) else 0)
        return r % 2 == 1
