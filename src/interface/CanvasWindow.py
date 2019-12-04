from src.entity.Space import Space
from src.game import Global


class CanvasWindow:
    def __init__(self, x, y, texture):
        self.x = x
        self.y = y
        self.image = texture
        self.children = []
        self.visible = -1
        self.text = []
        self.on_click = None
        self.on_r_click = None
        self.margin = Space(8, 8)
        self.width = self.image.width
        self.height = self.image.height

    def display(self, visible):
        self.visible = visible
        for i in self.children:
            i.display(visible)

    def flush(self):
        for i in self.children:
            i.flush()
        self.children = []

    def collide(self, pos):
        if self.x <= pos[0] <= self.x + self.width:
            if self.y <= pos[1] <= self.y + self.height:
                return 1
        return 0

    def input(self, event):
        if self.visible != 1:
            return 0
        for i in self.children:
            if i.input(event):
                return 1
        if event == 1:
            mouse = Global.player.control.cursor
            if self.collide(mouse):
                if event.button == 1 and self.on_click is not None:
                    self.on_click()
                    return 1
                elif event.button == 3 and self.on_r_click is not None:
                    self.on_r_click()
                    return 1

    def draw(self):
        self.image.blit(self.x, Global.DISPLAY[1] - self.y)

    def add_child(self, child):
        self.children.append(child)
        child.x += self.margin.x + self.x
        child.y += self.margin.y + self.y
