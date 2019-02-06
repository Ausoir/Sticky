from src.entity.Prop import Prop
from src.entity.unit.Attribute import Attribute
from src.form.Body import Body


# has Body form, is movable
from src.map.Tile import Tile


class Unit(Prop):
    def __init__(self, form, seed, loc):
        super().__init__(form, seed, loc)
        from src.entity.unit.action.ActionSet import ActionSet
        self.action = ActionSet(self)
        self.next_action = 'idle'
        self.next_target = [0, 0]
        self.direction = 1
        self.collide = Tile.CHECK_UNIT
        self.attributes = Attribute()
        self.pilot = None

    def __str__(self):
        return super().__str__() + ',' + self.faction.__str__() + ',' + self.pilot.__str__() +\
               ',[' + self.attributes.__str__() + '],[' + self.action.__str__() + ']'

    def load(self, p):
        from src.entity.unit.ai.Pilot import Pilot
        index = super().load(p)
        self.faction.load(p[index])
        self.pilot = Pilot(self, p[index + 1])
        self.attributes.load(p[index + 2])
        self.action.abilities = p[index + 3]
        return index + 4

    def make_form(self, arg):
        self.form = Body(arg, self.seed)

    def draw(self, surface, pos):
        super().draw(surface, pos)
        self.form.update()

    def turn(self):
        super().turn()
        if self.delay == 0:
            self.attributes.rest()
            if self.next_target[0] > 0 and self.direction != 1:
                self.face(1)
            elif self.next_target[0] < 0 and self.direction != -1:
                self.face(-1)
            self.action.attempt(self.next_action)
            self.next_action = 'idle'

    def input(self, action, target):
        self.next_action = action
        self.next_target = target

    def get_interact_pos(self):
        return self.pos[0]

    def get_offset_tile(self, x, y):
        return self.location.get_tile(self.pos[0] + (x, y))

    def face(self, direction):
        self.direction = direction
        self.form.face(direction)

    def on_fall(self, distance):
        damage = 0
        if distance > 4:
            damage = 1
        if distance > 1:
            self.hit(None, damage)
        else:
            self.form.set('drop')

    def hit(self, hitter, damage):
        r = super().hit(hitter, damage)
        if r:
            self.action.set('hit')
        return r

    def die(self):
        self.action.set('dead')

    def will_hit(self, tile):
        for i in self.pos:
            if tile == i:
                return 1
        return 0

    def is_dead(self):
        return self.action.current_action == 'dead'
