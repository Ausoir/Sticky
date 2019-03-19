from src.entity.Prop import Prop
from src.form.Body import Body
from src.game.Global import DEPTH_UNIT
from src.game.Group import Group
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Random import Random


class Ragdoll(Prop):
    template = None

    def __init__(self, loc):
        super().__init__(loc)
        self.direction = 1
        self.collide = Tile.COLLIDE_COVER
        self.depth = DEPTH_UNIT
        self.standables = Tile.CHECK_LANDABLE

    def add(self):
        Group.objects.add(self)
        Turn.add(self)
        self.relocate(self.pos[0].x, self.pos[0].y, force=1)
        return self

    def make_form(self, arg):
        self.form_name = arg
        if not Ragdoll.template:
            Ragdoll.template = Body('unit/man')
        self.form = Ragdoll.template

    def set(self, form):
        def invalid(str):
            pass
        self.add()
        self.form = form
        self.durability = 8
        dead = 'dead' + str(Random.rand_int(1, 3))
        self.form.randomize_clip(dead, 12)
        self.form.set(dead)
        self.form.set = invalid
        return self

    def draw(self, surface):
        if super().draw(surface):
            self.form.update()
            return 1
        return 0

    def is_hit(self, chance, faction=0):
        if self.hittable:
            return 1

    def hit(self, damage):
        self.form.randomize_once(18)
        return super().hit(damage)

    def die(self):
        self.remove()
