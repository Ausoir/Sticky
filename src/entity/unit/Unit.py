from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.Attribute import Attribute
from src.form.Body import Body
from src.game import Global
from src.game.Tags import Tags
from src.map.Tile import Tile


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
        index = super().load(p)
        self.faction = p[index]
        index += 1
        if p[index] == 'AdvPilot':
            from src.entity.unit.ai.AdvPilot import AdvPilot
            self.pilot = AdvPilot(self)
        elif p[index] == 'Pilot':
            from src.entity.unit.ai.Pilot import Pilot
            self.pilot = Pilot(self)
        else:
            from src.entity.unit.ai.Pilot import Manual
            self.pilot = Manual(self)
        index += 1
        self.attributes.load(p[index])
        index += 1
        self.action.load(p[index])
        index += 1
        self.proficiency = p[index]
        self.form.randomize(self.attributes.gene)
        index += 1
        return index

    def set_form(self, arg):
        self.form_name = arg
        self.form = Body(arg)

    def draw(self, surface):
        diff = self.pos[0].get_vec() + (Global.HALF_BLOCK, Global.BLOCK) - self.vec
        self.vec.x += diff.x * .07
        if 0 < diff.y and self.gravity:
            self.vec.y += min(16, diff.y)
        else:
            self.vec.y += diff.y * .07
        self.form.draw(surface, self.vec.x, self.vec.y)
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
                        thing.delay = 4
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

    def use(self):
        self.action.attack()

    def get_target_tile(self):
        return self.location.get_tile(self.pos[0] + self.next_target)

    def get_interact_pos(self):
        return self.pos[0]

    def face(self, direction):
        self.direction = direction
        self.form.face(direction)

    def on_fall(self, distance):
        super().on_fall(distance)
        if distance > 1 and not self.get_proficiency('constitution'):
            self.action.set('down', auto=1)
        else:
            if not self.action.auto:
                self.form.set('drop')

    def is_hit(self, accuracy, faction=0):
        if super().is_hit(accuracy, faction):
            sick = self.states.get('Sick')
            if sick:
                chance = 1
            else:
                chance = accuracy / max(1, accuracy + self.get_dodge())
            if Global.r.rand_float() < chance:
                if self.states.get('Distraction'):
                    self.die()
                return 1
            else:
                self.form.randomize_once(14)

    def get_dodge(self):
        if self.action.current_action == 'down':
            return 0
        r = self.get_proficiency('dodge')
        if self.action.current_action == 'block':
            self.action.exert(1, 1)
            r += 4
        return r

    def hit(self, damage):
        self.pilot.hit()
        self.action.set('hit', auto=1)
        return super().hit(damage)

    def die(self):
        if Tags.insubstantial in self.tags:
            from src.entity.Effect import Effect
            Effect.make('disintegrate', self.pos[0].get_center(), offset=0)
        else:
            from src.entity.Stock import Stock
            r = Stock.get('Corpse')
            r.relocate(self.pos[0].x, self.pos[0].y, force=1)
            r.set(self.form)
        super().die()

    def will_hit(self, tile):
        for i in self.pos:
            if tile == i:
                return 1
        return 0

    def get_proficiency(self, school):
        return 1 if school.lower() in self.proficiency else 0
