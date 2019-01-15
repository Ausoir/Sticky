import pygame

from src.entity.Space import Space
from src.form.Line import Line


class Shape:
    def __init__(self, group, pos, color, vertices):
        group.append(self)
        self.visible = 1
        self.pos = pos
        self.lines = []
        prev_pt = None
        high_x = 0
        high_y = 0
        for i in vertices:
            if prev_pt is not None:
                self.lines.append(Line(Space(prev_pt), Space(i)))
            prev_pt = i
            high_x = max(high_x, i[0])
            high_y = max(high_y, i[1])
        self.lines.append(Line(Space(prev_pt), Space(vertices[0])))
        self.canvas = pygame.Surface((high_x, high_y), pygame.SRCALPHA, 32)
        pygame.draw.polygon(self.canvas, color, vertices)

    def draw(self, surface):
        surface.blit(self.canvas, self.pos.to_list())

    def collide(self, point):
        mouse = Line(Space(-self.pos), Space(point) - self.pos)
        r = 0
        for line in self.lines:
            r += (1 if line.cross_line(mouse) else 0)
        return r % 2 == 1
