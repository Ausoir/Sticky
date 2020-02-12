from src.form.Shape import Shape
from src.game import Global
from src.game.Camera import Camera
from src.tools.Timer import Timer


class HealthBar:
    color_back = (0, 0, 0, 200)
    color_front = (0, 250, 0, 200)

    def __init__(self, target):
        self.background = Shape(0, 0, 600, Global.draw_group.group_gui,
                                width=Global.BLOCK, height=8, color=HealthBar.color_back)
        self.foreground = Shape(0, 0, 600, Global.draw_group.group_gui,
                                width=Global.BLOCK - 2, height=6, color=HealthBar.color_front)
        self.timer = Timer(0)
        self.attribute = target
        self.visible = False

    def show(self):
        hp = self.attribute.get('p')
        mhp = self.attribute.get('p>')
        if hp and mhp:
            width = int(Global.BLOCK * (hp / mhp)) - 2
            self.foreground.width = width
            if not self.visible:
                self.visible = True
                self.background.add_batch()
                self.foreground.add_batch()
                self.timer.set(80)

    def place(self, x, y):
        if self.visible:
            bound_x, bound_y = Camera.get_relative_pos(x, y)
            bound_x = int(bound_x)
            bound_y = int(bound_y)
            self.background.update(bound_x - Global.HALF_BLOCK, Global.DISPLAY[1] - bound_y)
            self.foreground.update(bound_x + 1 - Global.HALF_BLOCK, Global.DISPLAY[1] - bound_y + 1)
            if self.timer.update():
                self.remove()

    def remove(self):
        if self.visible:
            self.visible = False
            self.background.remove_batch()
            self.foreground.remove_batch()
