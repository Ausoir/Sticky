from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.Attribute import Attribute
from src.form.Body import Body
from src.game.Global import DEPTH_UNIT
from src.map.Tile import Tile
from src.tools.Random import Random


class Unit(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.action.Actions import Actions
        self.action = Actions(self)
        self.proficiency = []
        self.next_action = 'idle'
        self.next_target = Space()
        self.direction = 1
        self.collide = Tile.COLLIDE_UNIT
        self.attributes = Attribute()
        self.pilot = None
        self.depth = DEPTH_UNIT
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

    def face(self, direction):
        self.direction = direction
        self.form.face(direction)

    def on_fall(self, distance):
        if distance > 1 + self.get_proficiency('fall'):
            self.action.set('down', auto=1)
        else:
            if not self.action.auto:
                self.form.set('drop')

    def is_hit(self, chance, faction=0):
        if super().is_hit(chance, faction):
            if self.action.current_action == 'down':
                return 1
            elif max(0, chance - self.get_dodge()) + 1 >= Random.rand_int(1, 6):
                return 1
            else:
                self.form.set('interact')

    def get_dodge(self):
        return self.get_proficiency('dodge')

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

    @staticmethod
    def describe_proficiency(prof):
        if prof == 0:
            return 'Untrained'
        if prof == 1:
            return 'Familiar'
        if prof == 2:
            return 'Trained'
        if prof == 3:
            return 'Skilled'
        if prof == 4:
            return 'Expert'
        if prof >= 5:
            return 'Mastered'
