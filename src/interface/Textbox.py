from pyglet.text import Label

from src.game import Global


class Textbox:
    def __init__(self):
        self.display = 0
        self.text = Label(batch=Global.draw_group.batch, font_name='Ubuntu', font_size=16, bold=True,
                          color=(150, 0, 0, 240), width=800, height=240,
                          group=Global.draw_group.group_gui, multiline=True)
        self.on_resize()

    def on_resize(self):
        self.text.x = Global.OFFSET[0] - Global.CENTER[0] + 120
        self.text.y = Global.OFFSET[1] - 200

    def set(self, line, time=120):
        self.text.batch = Global.draw_group.batch
        self.display = time
        line = [line[i:i + 100] for i in range(0, len(line), 100)]
        self.text.text = '\n'.join(line)

    def update(self):
        if self.display > 0:
            self.display -= 1
        else:
            self.text.batch = None
