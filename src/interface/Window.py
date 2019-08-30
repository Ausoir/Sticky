import pygame

from src.entity.Space import Space
from src.form.Shape import Shape
from src.game import Global
from src.game.Camera import Camera


class Window(Shape):
    fore_color0 = (0, 0, 0, 0)
    fore_color1 = (68, 102, 120, 160)
    fore_color2 = (95, 112, 120, 220)
    fore_color3 = (210, 220, 240, 60)
    font_color1 = (205, 209, 227, 255)
    font_color2 = (120, 180, 140, 200)
    font_color3 = (60, 80, 80, 220)

    def __init__(self, size, vec=(0, 0), name=0, color=fore_color1):
        self.name = name
        self.color = color
        self.size = Space(size)
        self.vec = Space(vec)
        super().__init__(self.vec, color=self.color, vertices=Shape.make_rect(size))

        self.children = []
        self.visible = -1
        self.text = []
        self.on_click = None
        self.on_r_click = None
        self.margin = Space(8, 8)
        self.normal_font_color = Window.font_color1
        self.hover_font_color = Window.font_color2
        self.font_color = self.normal_font_color
        self.text_spacing = 40
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
        for i in self.children:
            if i.input(event):
                return 1
        if event.type == pygame.MOUSEMOTION:
            mouse = pygame.mouse.get_pos()
            if self.text:
                self.glow(self.collide(mouse))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            if self.collide(mouse):
                if event.button == 1 and self.on_click is not None:
                    self.on_click(self.name)
                    return 1
                elif event.button == 3 and self.on_r_click is not None:
                    self.on_r_click(self.name)
                    return 1
        return 0

    def glow(self, on):
        if on:
            if self.hover_font_color:
                self.font_color = self.hover_font_color
        else:
            self.font_color = self.normal_font_color

    def draw(self, surface):
        if self.visible == 1:
            self.vec.x -= Camera.pos[0]
            self.vec.y -= Camera.pos[1]
            super().draw(surface)
            self.vec.x += Camera.pos[0]
            self.vec.y += Camera.pos[1]
            position = [self.vec.x + self.margin.x, self.vec.y + self.margin.y]
            for i in self.text:
                surface.blit(Global.font.render(i, 1, self.font_color), position)
                position[1] += self.text_spacing
            for i in self.children:
                i.draw(surface)

    def set_text(self, text, resize=True):
        if resize:
            self.text = Window.resize_text(text, self.size.x - (self.margin.x * 2) - 24)
        else:
            self.text = text
        self.size.y = self.text_spacing * len(self.text)
        self.vertices = Shape.make_rect(self.size.to_list())
        self.redraw()

    @staticmethod
    def resize_text(text, size):
        r = []
        for line in text:
            length = 0
            newline = ''
            words = line.split(' ')
            for word in words:
                wordlength = 0
                newword = ''
                for char in word:
                    newword += char
                    wordlength += Global.font.size(char)[0]
                if length + wordlength > size:
                    r.append(newline)
                    newline = ''
                    length = 0
                length += wordlength
                newline += newword + ' '
            r.append(newline)
        return r

    def add(self, child):
        self.children.append(child)
        child.vec.load(child.vec.x + self.margin.x + self.vec.x, child.vec.y + self.next_y)
        self.next_y += child.size.y + self.margin.y
