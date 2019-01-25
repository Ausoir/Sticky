from src.entity.Prop import Prop
from src.form.Body import Body
from src.tools.Random import Random


# has Body form, is movable
class Unit(Prop):
    def __init__(self, form, loc):
        super().__init__(form, loc)
        from src.entity.action.Action import Action
        self.action = Action(self)
        self.next_action = 'idle'
        self.next_target = [0, 0]
        self.direction = 1

    def make_form(self, arg):
        self.form = Body(arg, self.seed)

    def draw(self, tile, surface, pos):
        super().draw(tile, surface, pos)
        self.form.update()

    def turn(self):
        super().turn()
        if self.delay == 0:
            self.face(1 if self.next_target[0] > self.pos.x else -1)
            continuous = self.action.perform(self.next_action)
            if not continuous:
                self.next_action = 'idle'

    def input(self, action, target):
        self.next_action = action
        self.next_target = target

    def face(self, direction):
        self.direction = direction
        self.form.face(direction)

    def on_fall(self, distance):
        damage = 1 if distance > 4 else 0
        self.hit(None, damage)

    def hit(self, hitter, damage):
        r = super().hit(hitter, damage)
        if r and self.delay != -1:
            self.action.perform('hit')
        return r

    def die(self):
        self.delay = -1
        self.form.set('dead' + str(Random.rand_int(1, 3)))
        self.form.set_height(4)
        self.collide = 0
        self.hittable = 0
        self.save = 0

    def will_hit(self, tile):
        return tile == self.pos
