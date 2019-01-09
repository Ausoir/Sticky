from src.entity.Entity import Entity
from src.entity.Object import Object
from src.form.Body import Body


class Unit(Object):
    def __init__(self, form):
        super().__init__(form)

    def load(self, p):
        Entity.load(self, p)

    def make_form(self, p):
        return Body(texture_name=p)
