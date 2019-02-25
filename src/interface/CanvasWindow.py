import pygame

from src.entity.Space import Space
from src.game.Camera import Camera


class CanvasWindow:
    def __init__(self, texture, vec=(0, 0)):
        self.vec = Space(vec)
        self.sprite = texture
        self.size = self.sprite.size
        self.children = []
        self.visible = -1
        self.text = []
        self.on_click = None
        self.on_r_click = None
        self.margin = Space(8, 8)

    def display(self, visible):
        self.visible = visible
        for i in self.children:
            i.display(visible)

    def flush(self):
        for i in self.children:
            i.flush()
        self.children = []

    def collide(self, pos):
        if self.vec.x <= pos[0] <= self.vec.x + self.sprite.size.x:
            if self.vec.y <= pos[1] <= self.vec.y + self.sprite.size.y:
                return 1
        return 0

    def input(self, event):
        if self.visible != 1:
            return 0
        for i in self.children:
            if i.input(event):
                return 1
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            if self.collide(mouse):
                if event.button == 1 and self.on_click is not None:
                    self.on_click()
                    return 1
                elif event.button == 3 and self.on_r_click is not None:
                    self.on_r_click()
                    return 1

    def draw(self, surface):
        self.vec.x -= Camera.pos[0]
        self.vec.y -= Camera.pos[1]
        self.sprite.draw(surface, self.vec.x, self.vec.y)
        self.vec.x += Camera.pos[0]
        self.vec.y += Camera.pos[1]

    def add_child(self, child):
        self.children.append(child)
        child.vec.load(child.vec.x + self.margin.x + self.vec.x, child.vec.y + self.margin.y + self.vec.y)
