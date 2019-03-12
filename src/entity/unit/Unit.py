from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.Attribute import Attribute
from src.form.Body import Body
from src.game.Global import DEPTH_UNIT
# has Body form, is movable
from src.map.Tile import Tile


class Unit(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.action.Actions import Actions
        self.action = Actions(self)
        self.next_action = 'idle'
        self.next_target = Space()
        self.direction = 1
        self.collide = Tile.COLLIDE_UNIT
        self.attributes = Attribute()
        self.pilot = None
        self.depth = DEPTH_UNIT

    def __str__(self):
        return super().__str__() + ',' + str(self.faction) + ',' + self.pilot.__str__() +\
               ',[' + self.attributes.__str__() + '],[' + self.action.__str__() + ']'

    def load(self, p):
        from src.entity.unit.ai.Pilot import Pilot
        index = super().load(p)
        self.faction = p[index]
        index += 1
        self.pilot = Pilot(self, p[index])
        index += 1
        self.attributes.load(p[index])
        index += 1
        self.action.load(p[index])
        index += 1
        self.form.randomize(self.attributes.gene)
        return index

    def make_form(self, arg):
        self.form_name = arg
        self.form = Body(arg)

    def draw(self, surface):
        if super().draw(surface):
            self.form.update()
            return 1
        return 0

    def turn(self):
        super().turn()
        self.pilot.update()
        if self.delay == 0:
            self.attributes.rest()
            if self.next_target.x > 0 and self.direction != 1:
                self.face(1)
            elif self.next_target.x < 0 and self.direction != -1:
                self.face(-1)
            self.action.attempt(self.next_action)
            self.next_action = 'idle'

    def input(self, action, target):
        self.next_action = action
        self.next_target = target

    def get_target_tile(self):
        return self.location.get_tile(self.pos[0].x + self.next_target.x, self.pos[0].y + self.next_target.y)

    def get_interact_pos(self):
        return self.pos[0]

    def get_offset_tile(self, x, y):
        return self.location.get_tile(self.pos[0] + (x, y))

    def face(self, direction):
        self.direction = direction
        self.form.face(direction)

    def on_fall(self, distance):
        if not self.is_dead():
            if distance > 1:
                self.action.set('down', auto=1)
            else:
                if not self.action.auto:
                    self.form.set('drop')

    def hit(self, damage):
        r = super().hit(damage)
        if r and not self.is_dead():
            self.pilot.hit()
            self.action.set('hit', auto=1)
        return r

    def die(self):
        self.pilot.on_dead()
        self.action.set('dead', auto=1)

    def will_hit(self, tile):
        for i in self.pos:
            if tile == i:
                return 1
        return 0

    def is_dead(self):
        return self.action.current_action == 'dead'
