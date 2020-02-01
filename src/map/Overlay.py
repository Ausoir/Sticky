from src.form.Shape import Shape
from src.game import Global
from src.game.Turn import Turn


class Overlay:
    def __init__(self):
        self.fade = Shape(0, 0, 700, Global.draw_group.group_overlay,
                          width=Global.DISPLAY[0], height=Global.DISPLAY[1])
        self.weather = [0, 0, 0, 0]
        Turn.add(self.turn)

    def colorize(self, color):
        if not color:
            self.weather = [0, 0, 0, 0]
        else:
            self.weather = color

    def blackout(self):
        self.fade.set_solid_color([0, 0, 0, 255])
        self.fade.add_batch()

    def on_resize(self):
        self.fade.width = Global.DISPLAY[0]
        self.fade.height = Global.DISPLAY[1]
        self.fade.update()

    def turn(self):
        if not self.fade.removed:
            if self.fade.color[3] <= 10:
                self.fade.remove_batch()
            else:
                self.fade.set_solid_color([self.fade.color[0], self.fade.color[1],
                                           self.fade.color[2], self.fade.color[3] - 8])
                self.fade.update()
