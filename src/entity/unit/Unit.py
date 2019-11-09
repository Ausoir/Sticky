from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.Attribute import Attribute
from src.form.Body import Body
from src.game import Global
from src.game.Camera import Camera
from src.game.Tags import Tags
from src.map.Tile import Tile
from src.tools.Math import Math


class Unit(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.Actions import Actions
        self.draw_frame = 0
        self.action = Actions(self)
        self.proficiency = []
        self.next_action = 'idle'
        self.next_target = Space()
        self.direction = 1
        self.collision_type = Tile.COLLIDE_UNIT
        self.attributes = Attribute()
        self.pilot = None
        self.pilot_name = None
        self.depth = 4
        self.delay = 0
        self.standables = Tile.CHECK_LANDABLE
        self.frame = 0

    def __str__(self):
        att = '[' + self.attributes.__str__() + '],[' + self.action.__str__() + '],[' + ','.join(self.proficiency) + ']'
        return super().__str__() + ',' + str(self.faction) + ',' + self.pilot_name + ',' + att

    def load(self, p):
        index = super().load(p)
        self.faction = p[index]
        index += 1
        from src.entity.unit.ai import Pilot
        from src.tools.Data import Data
        template = Data.get_line('data/raw/behaviors.txt', p[index])
        self.pilot_name = p[index]
        self.pilot = getattr(Pilot, template[1])(self, template[2])
        index += 1
        self.attributes.load(p[index])
        index += 1
        self.action.load(p[index])
        index += 1
        self.proficiency = p[index]
        self.form.randomize(self.attributes.gene)
        index += 1
        return index

    def add(self):
        r = super().add()
        self.face(1 if self.attributes.gene % 2 == 0 else -1)
        return r

    def set_form(self, arg):
        self.form_name = arg
        self.form = Body(arg)

    def draw_synchronize(self):
        if self.draw_frame != self.location.draw_frame:
            self.update_vec()
            self.draw_frame = self.location.draw_frame
        self.draw_frame += 1

    def draw(self, surface):
        if Camera.target != self:
            self.draw_synchronize()
        diff = self.pos.get_center() - self.vec
        self.vec.x += diff.x * .07
        if 0 < diff.y and self.gravity and self.form.state_name != 'climb':
            self.vec.y += min(16, diff.y)
        else:
            self.vec.y += diff.y * .07
        self.form.draw(surface, self.vec.x, self.vec.y)
        self.form.update()

    def turn(self):
        self.pilot.update()
        super().turn()
        self.frame += 1
        if not self.frame % 8:
            self.attributes.leg = max(0, self.attributes.leg - 1)
            if self.action.current_action not in ['idle', 'walk', 'jump', 'duck']:
                self.frame = 0
            if self.frame > 160:
                self.attributes.body = 0
                self.frame = 0
        if self.delay > 0:
            self.delay -= 1
        elif self.delay == 0:
            if self.next_target.x > 0 and self.direction != 1:
                self.face(1)
            elif self.next_target.x < 0 and self.direction != -1:
                self.face(-1)
            self.action.attempt(self.next_action)
            self.next_action = 'idle'

    def center_camera(self):
        super().center_camera()

    def input(self, action, target):
        self.next_action = action
        if target:
            self.next_target = target

    def use(self):
        self.action.attack()

    def get_target_tile(self):
        return self.location.get_tile(self.pos + self.next_target)

    def get_front_tile(self):
        degree = self.next_target.get_atan()
        target = self.pos + (round(Math.cos(degree) * 1.4), round(Math.sin(degree) * 1.4))
        return self.location.get_tile(target)

    def face(self, direction):
        if not self.states.get('Influence'):
            self.direction = direction
            self.form.face(direction)

    def fell(self, distance, me=False):
        if self.get_proficiency('nimble'):
            distance = min(distance, 2)
        super().fell(distance, me)
        if not me:
            self.action.set('down')
            self.delay = 5

    def on_fall(self):
        super().on_fall()
        if self.falling > 1:
            self.attributes.exert(1, self.falling * 3)
            self.action.set('down')
            self.states.add('Cripple', self.falling * 4, var=1)
            return True
        else:
            if self.action.current_action != 'down':
                self.form.set('drop')

    def get_dodge(self):
        if self.action.current_action == 'down':
            return 0
        r = self.get_proficiency('dodge')
        if self.action.current_action == 'block':
            r += 8
        return r

    def hit(self, damage, accuracy=None, hitter=None):
        if accuracy:
            sick = self.states.get('Weak')
            if sick:
                chance = 1
            else:
                chance = accuracy / max(1, accuracy + self.get_dodge())
            self.location.attack.unregister(self.get_hitter())
            self.pilot.hit(hitter)
            if Global.r.rand_float() < chance:
                if self.states.get('Distraction'):
                    self.die()
                    return 2
                self.action.set('hit')
                return super().hit(damage, accuracy, hitter)
            else:
                self.form.set('hit')
                self.form.randomize_once(8)
        else:
            self.action.set('hit')
            return super().hit(damage, accuracy, hitter)
        return 0

    def get_hitter(self):
        return self

    def die(self):
        if Tags.insubstantial not in self.tags:
            from src.entity.Stock import Stock
            r = Stock.get('Corpse')
            r.durability = int(self.attributes.get_total() / 3)
            r.relocate(self.pos.x, self.pos.y, force=1)
            r.set(self.form)
        super().die()

    def get_proficiency(self, school):
        return 1 if school.lower() in self.proficiency else 0

    def say(self, text):
        pass
