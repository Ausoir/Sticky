from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.Attribute import Attribute
from src.form.Body import Body
from src.map.Tile import Tile
from src.tools.Random import Random


class Unit(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.Actions import Actions
        self.action = Actions(self)
        self.proficiency = []
        self.next_action = 'idle'
        self.next_target = Space()
        self.direction = 1
        self.collide = Tile.COLLIDE_UNIT
        self.attributes = Attribute()
        self.pilot = None
        self.depth = 4
        self.delay = 0
        self.standables = Tile.CHECK_LANDABLE

    def __str__(self):
        att = '[' + self.attributes.__str__() + '],[' + self.action.__str__() + '],[' + ','.join(self.proficiency) + ']'
        return super().__str__() + ',' + str(self.faction) + ',' + self.pilot.__str__() + ',' + att

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
        self.proficiency = p[index]
        self.form.randomize(self.attributes.gene)
        index += 1
        return index

    def make_form(self, arg):
        self.form_name = arg
        self.form = Body(arg)

    def draw(self, surface):
        super().draw(surface)
        self.form.update()

    def turn(self):
        super().turn()
        if self.is_fall():
            ground = self.get_offset_tile(0, 1)
            landables = self.standables.copy()
            landables.remove(Tile.COLLIDE_UNIT)
            if not ground.is_land(landables):
                for thing in ground.things:
                    if isinstance(thing, Unit):
                        thing.action.set('down', auto=1)
                self.attributes.exert(1, 2)
                self.move(0, 1, flag=Tile.CHECK_FIRM)
        self.pilot.update()
        if self.delay > 0:
            self.delay -= 1
        elif self.delay == 0:
            if self.next_target.x > 0 and self.direction != 1:
                self.face(1)
            elif self.next_target.x < 0 and self.direction != -1:
                self.face(-1)
            self.action.attempt(self.next_action)
            self.next_action = 'idle'

    def input(self, action, target):
        self.next_action = action
        if target:
            self.next_target = target

    def get_target_tile(self):
        return self.location.get_tile(self.pos[0] + self.next_target)

    def get_interact_pos(self):
        return self.pos[0]

    def face(self, direction):
        self.direction = direction
        self.form.face(direction)

    def on_fall(self, distance):
        super().on_fall(distance)
        if distance > 1 and not self.get_proficiency('Constitution'):
            self.action.set('down', auto=1)
        else:
            if not self.action.auto:
                self.form.set('drop')

    def is_hit(self, chance, faction=0):
        if super().is_hit(chance, faction):
            dodge = self.get_proficiency('Dodge')
            if self.action.current_action == 'block':
                dodge += self.on_block()
            if chance - dodge >= Random.rand_int(1, 4):
                if self.states.get('Distraction'):
                    self.die()
                return 1
            else:
                self.form.randomize_once(14)

    def on_block(self):
        self.action.exert(1, 1)
        return 2

    def hit(self, damage):
        self.pilot.hit()
        self.action.set('hit', auto=1)
        return super().hit(damage)

    def die(self):
        from src.entity.Stock import Stock
        r = Stock.get('Ragdoll')
        r.relocate(self.pos[0].x, self.pos[0].y, force=1)
        r.set(self.form)
        self.remove()

    def will_hit(self, tile):
        for i in self.pos:
            if tile == i:
                return 1
        return 0

    def get_proficiency(self, school):
        return 1 if school in self.proficiency else 0
