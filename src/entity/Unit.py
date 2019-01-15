from src.entity.Object import Object
from src.form.Body import Body


class Unit(Object):
    def __init__(self, form):
        super().__init__(form)

    def make_form(self, p):
        self.form = Body(self.pos, texture_name=p)

    def update(self):
        self.form.update()
