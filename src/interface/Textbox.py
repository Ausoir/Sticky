import pyglet
from pyglet.text.document import FormattedDocument
from pyglet.text.layout import TextLayout

from src.game import Global


class Textbox:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.display = 0
        self.document = FormattedDocument(' ')
        properties = dict(font_name='Default Font', font_size=16, bold=True, color=(70, 70, 70, 240))
        self.document.set_style(0, 1, properties)
        self.text = TextLayout(self.document, 120, 120, multiline=True, wrap_lines=True, group=Global.draw_group.group_gui)

    def add_batch(self):
        self.text.batch = Global.draw_group.batch

    def remove_batch(self):
        self.display = 0
        self.text.batch = None
        self.text.group = None

    def on_resize(self):
        self.text.width = Global.DISPLAY[0]
        self.x = Global.CENTER[0]

    def input(self, code):
        if code in Global.player.control.keymap:
            if Global.player.control.keymap[code] == 'text':
                self.display = 100
                self.document.set_style(0, 1, {'color': (200, 230, 200)})
                Global.main.text_mode = False
                Global.player.control.player.input('command', (0, 0))
                return
            elif Global.player.control.keymap[code] == 'quit':
                self.document.text = ''
                Global.main.text_mode = False
                return
        self.display = -1
        self.document.set_style(0, 1, {'color': (220, 220, 220)})
        if code == pyglet.window.key.BACKSPACE:
            self.document.text = self.document.text[:-1]
        elif code == pyglet.window.key.SPACE:
            self.document.text += ' '
        else:
            self.document.text += pyglet.window.key.symbol_string(code)

    def set(self, arg, time=200):
        if self.display <= 0:
            self.add_batch()
        self.display = time
        self.document.text = arg
        self.text.x = self.x - int(self.text.content_width / 2)
        self.text.y = self.y

    def update(self):
        if self.display > 0:
            self.display -= 1
        else:
            self.remove_batch()
