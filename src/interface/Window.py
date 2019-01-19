import pygame

from src.entity.Space import Space
from src.form.Shape import Shape
from src.game.Group import Group


class Window(Shape):
    fore_color1 = (68, 102, 120, 200)
    fore_color2 = (95, 112, 120, 220)
    fore_color3 = (210, 220, 240, 80)
    font_color1 = (205, 209, 227, 255)
    font_color2 = (120, 180, 140, 200)

    def __init__(self, depth, size, vec=(0, 0), color=fore_color1):
        self.color = color
        self.size = size
        self.depth = depth
        self.vec = Space(vec)
        super().__init__(Group.gui, self.depth - 1, self.vec, color=self.color, vertices=Shape.make_rect(size))

        Group.interface.append(self)
        self.children = []
        self.visible = -1
        self.text = []
        self.on_click = None
        self.margin = Space(8, 8)
        self.font = pygame.font.SysFont('Helvetica', 20)
        self.font_color = Window.font_color1
        self.spacing = 40
        self.next_y = self.vec.y + self.margin.y

    def display(self, visible):
        self.visible = visible
        for i in self.children:
            i.display(visible)

    def flush(self):
        self.next_y = self.vec.y + self.margin.y
        for i in self.children:
            i.flush()
        self.children = []

    def input(self, event):
        if self.visible != 1:
            return 0
        if event.type == pygame.MOUSEMOTION:
            mouse = pygame.mouse.get_pos()
            if self.text:
                if self.collide(mouse):
                    self.font_color = Window.font_color2
                else:
                    self.font_color = Window.font_color1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            if self.collide(mouse):
                if event.button == 1 and self.on_click is not None:
                    self.on_click()
                    return 1

    def draw(self, surface):
        super().draw(surface)
        position = [self.vec.x + self.margin.x, self.vec.y + self.margin.y]
        for i in self.text:
            surface.blit(self.font.render(i, 1, self.font_color), position)
            position[1] += self.spacing

    def set_text(self, text):
        self.text = text
        self.size[1] = self.spacing * len(text)
        self.vertices = Shape.make_rect(self.size)
        self.redraw()

    def add_child(self, child):
        self.children.append(child)
        child.vec.load(child.vec.x + self.margin.x + self.vec.x, child.vec.y + self.next_y)
        self.next_y += child.size[1] + self.margin.y
