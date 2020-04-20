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
        properties = dict(font_name='Ubuntu', font_size=16, bold=True, color=(120, 30, 30, 220))
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
        self.x = -80
        self.y = Global.CENTER[0] + 400

    def set(self, arg, time=120):
        if self.display <= 0:
            self.add_batch()
        self.display = time
        self.document.text = arg
        self.text.x = self.x - int(self.text.content_width / 2) + Global.OFFSET[0]
        self.text.y = Global.DISPLAY[1] - self.y + Global.OFFSET[1]

    def update(self):
        if self.display > 0:
            self.display -= 1
        else:
            self.remove_batch()
