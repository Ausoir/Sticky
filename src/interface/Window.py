import pygame

from src.Group import Group
from src.entity.Object import Object
from src.form.Shape import Shape


class Window(Object):
    fore_color1 = (68, 102, 120, 240)
    fore_color2 = (95, 112, 120, 255)
    font_color1 = (205, 209, 227, 255)
    font_color2 = (120, 180, 140, 200)

    def __init__(self, size):
        super().__init__(size)
        Group.interface.append(self)
        Group.gui.append(self)
        self.visible = -1
        self.hover = None
        self.click = None
        self.font = pygame.font.SysFont('Helvetica', 20)

    def display(self):
        self.visible = self.visible * -1
        self.form.visible = self.visible

    def make_form(self, size):
        if isinstance(self.form, Shape):
            self.remove()
        boundary = ((self.pos.x, self.pos.y),
                    (self.pos.x + size[0], self.pos.y),
                    (self.pos.x + size[0], self.pos.y + size[1]),
                    (self.pos.x, self.pos.y + size[1]))
        self.form = Shape(Group.gui, self.pos, color=Window.fore_color1, vertices=boundary)
        self.form.visible = -1

    def input(self, event):
        if self.visible != 1:
            return
        if event.type == pygame.MOUSEMOTION:
            mouse = pygame.mouse.get_pos()
            if self.hover is not None:
                if self.form.collide(mouse):
                    self.hover(0)

    def draw(self, surface):
        surface.blit(self.font.render('Something', 1, Window.font_color1), [self.pos.x+8, self.pos.y+8])
