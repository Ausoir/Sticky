from pyglet.text.document import FormattedDocument
from pyglet.text.layout import TextLayout

from src.entity.Space import Space
from src.form.Shape import Shape
from src.game import Global


class Window(Shape):
    fore_color_transparent = (0, 0, 0, 0)
    fore_color1 = (68, 102, 120, 160)
    fore_color2 = (95, 112, 120, 220)
    fore_color3 = (120, 130, 150, 250)
    fore_color_disabled = (210, 140, 140, 80)
    font_color1 = (205, 209, 227, 255)
    font_color2 = (120, 180, 140, 200)
    font_color3 = (60, 80, 80, 220)

    def __init__(self, x, y, width, height, name=0, color=fore_color1, multi_line=False):
        super().__init__(x, y, 900, group=Global.draw_group.group_gui, width=width, height=height, color=color)
        self.name = name
        self.children = []
        self.visible = -1
        self.on_click = None
        self.on_r_click = None
        self.margin = Space(8, 8)
        self.normal_color = self.color
        self.hover_color = Window.fore_color3
        self.next_y = self.y + self.margin.y
        self.document = FormattedDocument(' ')
        self.document.set_style(0, 1, dict(font_name='Default Font', font_size=16, color=Window.font_color1))
        self.text = TextLayout(self.document, width, height, multiline=multi_line, group=Global.draw_group.group_gui)

    def display(self, visible):
        if self.visible != visible:
            if visible == 1:
                self.add_batch()
                self.text.batch = Global.draw_group.batch
                self.update_text()
            elif visible == -1:
                self.remove_batch()
                self.text.batch = None
                self.update_text()
        self.visible = visible
        for i in self.children:
            i.display(visible)

    def flush(self):
        self.next_y = self.y + self.margin.y
        for i in self.children:
            i.flush()
        self.children = []

    def input(self, event):
        if self.visible != 1:
            return 0
        for i in self.children:
            if i.input(event):
                return 1
        if event == 0:
            mouse = Global.player.control.cursor
            if self.hover_color:
                self.glow(self.collide(mouse[0], mouse[1]))
        if event in [1, 4]:
            mouse = Global.player.control.cursor
            if self.collide(mouse[0], mouse[1]):
                if event == 1 and self.on_click is not None:
                    self.on_click(self.name)
                    return 1
                elif event == 4 and self.on_r_click is not None:
                    self.on_r_click(self.name)
                    return 1
        return 0

    def glow(self, on):
        if on:
            self.color = self.hover_color
        else:
            self.color = self.normal_color

    def update_text(self):
        self.text.width = self.width
        self.text.height = self.height
        position = [self.x + self.margin.x, self.y]
        self.text.x = position[0]
        font = self.document.get_font(0)
        self.text.y = Global.DISPLAY[1] - position[1] - self.document.get_style('font_size')
        self.text.y += (font.ascent - font.descent) - self.height
        if self.text.multiline:
            self.text.y += -font.ascent
        else:
            self.text.y += int((-font.descent - self.height)/2)
        self.text.z = self.z + 1

    def set_text(self, text):
        self.document.text = text

    def add(self, child, index=-1, reverse=False):
        if reverse:
            self.next_y -= child.height + self.margin.y
        if index == -1:
            self.children.append(child)
        else:
            self.children.insert(index, child)
        child.x += self.margin.x + self.x
        child.y += self.next_y
        if not reverse:
            self.next_y += child.height + self.margin.y
