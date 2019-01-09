from src.entity.Entity import Entity
from src.form.Sprite import Sprite


class Object(Entity):
    def __init__(self, form):  # same characteristics across all objects
        Entity.__init__(self)
        self.form = self.make_form(form)
        self.seed = -1

    def load(self, p):  # instance specific characteristics
        super().load(p)
        self.form.resize(self.size)

    def make_form(self, p):
        return Sprite(texture_name=p)

    def draw(self, surface):
        self.form.draw(surface, self.pos)
