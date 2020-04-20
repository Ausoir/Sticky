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
        self.inbound = False
        self.display = False
        self.visible = False
        self.displaying_health = False

    def show(self, visible):
        self.display = visible
        self.visible = self.inbound and self.display

    def bound(self, visible):
        self.inbound = visible
        self.visible = self.inbound and self.display

    def appear(self):
        hp = self.attribute.get('p')
        mhp = self.attribute.get('P')
        if hp and mhp:
            width = int(Global.BLOCK * min(1, hp / mhp)) - 2
            self.foreground.width = width
            if not self.displaying_health:
                self.displaying_health = True
                self.background.add_batch()
                self.foreground.add_batch()
                self.timer.set(80)

    def turn(self):
        if self.displaying_health:
            self.foreground.show(self.visible)
            self.background.show(self.visible)
            self.foreground.update()
            self.background.update()

    def place(self, x, y):
        if self.displaying_health and self.visible:
            bound_x = int(x)
            bound_y = int(y)
            self.background.update(bound_x - Global.HALF_BLOCK, bound_y)
            self.foreground.update(bound_x + 1 - Global.HALF_BLOCK, bound_y + 1)
            if self.timer.update():
                self.remove()

    def remove(self):
        if self.displaying_health:
            self.displaying_health = False
            self.background.remove_batch()
            self.foreground.remove_batch()
            return True
