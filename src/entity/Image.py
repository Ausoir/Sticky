from src.game.Camera import Camera
from src.tools.Space import Space


class Image:
    def __init__(self, vec=None):
        self.name = None
        self.form = None
        self.form_name = None
        self.vec = vec or Space()

    def set_form(self, arg):
        from src.tools.Data import Data
        self.form_name = arg
        self.form = Data.get_form(arg)

    def update(self):
        bound_x, bound_y = Camera.get_relative_pos(self.vec.x, self.vec.y)
        self.form.place(bound_x, bound_y)

    def center_camera(self):
        Camera.target = self
