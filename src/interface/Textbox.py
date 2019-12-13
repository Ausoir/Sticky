import pyglet
from pyglet.text import Label

from src.game import Global


class Textbox:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.display = 220
        self.color1 = (220, 220, 220)
        self.color2 = (40, 40, 40)
        self.label = Label('', x=x, y=y,
                           font_size=16, bold=True,
                           color=(127, 127, 127, 127))

    def input(self, code):
        if code in Global.player.control.keymap:
            if Global.player.control.keymap[code] == 'text':
                self.display = 100
                self.color1 = (200, 230, 200)
                self.color2 = (60, 100, 60)
                Global.main.text_mode = False
                Global.player.control.player.input('command', (0, 0))
                return
            elif Global.player.control.keymap[code] == 'quit':
                self.label.text = ''
                Global.main.text_mode = False
                return
        self.display = -1
        self.color1 = (220, 220, 220)
        self.color2 = (40, 40, 40)
        if code == pyglet.window.key.BACKSPACE:
            self.label.text = self.label.text[:-1]
        elif code == pyglet.window.key.SPACE:
            self.label.text += ' '
        else:
            self.label.text += pyglet.window.key.symbol_string(code)

    def set(self, arg, time=200):
        self.display = time
        self.label.text = arg
        self.label.x = self.x - int(self.label.content_width / 2)

    def draw(self):
        if self.display:
            self.label.draw()
            self.display -= 1
