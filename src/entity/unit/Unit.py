from src.entity.Prop import Prop
from src.entity.unit.Attribute import Attribute
from src.form.Body import Body
from src.game import Global
from src.game.Camera import Camera
from src.game.Tags import Tags
from src.map.Tile import Tile


class Unit(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.Actions import Actions
        self.draw_frame = 0
        self.action = Actions(self)
        self.proficiency = []
        self.next_action = 'idle'
        self.direction = 3
        self.collision_type = Tile.COLLIDE_UNIT
        self.pilot = None
        self.pilot_name = None
        self.delay = 0

    def __str__(self):
        att = '[' + self.action.__str__() + '],[' + ','.join(self.proficiency) + ']'
        return super().__str__() + ',' + str(self.faction) + ',' + self.pilot_name + ',' + att

    def load(self, p):
        index = super().load(p)
        self.faction = p[index]
        index += 1
        from src.entity.unit.ai import Pilot
        from src.tools.Data import Data
        template = Data.get_line('raw/behaviors.txt', p[index])
        self.pilot_name = p[index]
        self.pilot = getattr(Pilot, template[1])(self, template[2])
        index += 1
        self.action.load(p[index])
        index += 1
        self.proficiency = p[index]
        self.form.randomize(self.attributes.gene)
        index += 1
        return index

    def add(self):
        r = super().add()
        self.face(self.attributes.gene % 4 + 1)
        return r

    def set_form(self, arg):
        self.form_name = arg
        from src.tools.Data import Data
        line = Data.get_line('raw/model.txt', arg)
        self.form = Body(line[1])
        self.form.set_model(line[2])

    def load_attributes(self, arg):
        from src.entity.unit.Attribute import AdvAttribute
        self.attributes = AdvAttribute()
        self.attributes.load(arg)

    def draw_synchronize(self):
        if self.draw_frame != Global.map_view.draw_frame:
            self.update_vec()
            self.draw_frame = Global.map_view.draw_frame
        self.draw_frame += 1

    def update(self):
        if Camera.target != self:
            self.draw_synchronize()
        diff = self.pos.get_center() - self.vec
        self.vec.x += diff.x * .08
        self.vec.y += diff.y * .08
        self.form.place(self.vec.x, self.vec.y)

    def turn(self):
        self.pilot.update()
        super().turn()
        if self.delay > 0:
            self.delay -= 1
        elif self.delay == 0:
            self.action.attempt(self.next_action)
            self.next_action = 'idle'

    def set_row(self, row):
        self.form.set_row(row)

    def center_camera(self):
        super().center_camera()

    def input(self, action):
        self.next_action = action

    def use(self):
        self.action.attack()

    def face(self, direction):
        if direction != self.direction:
            if not self.states.get('Influence'):
                self.direction = direction
                self.form.face(direction)
            return True

    def face_toward(self, pos):
        diff = pos - self.pos
        if diff.x < 0:
            return self.face(1)
        elif diff.x > 0:
            return self.face(3)
        if diff.y < 0:
            return self.face(2)
        elif diff.y > 0:
            return self.face(4)

    def get_dodge(self):
        if self.action.current_action == 'fall':
            return 0
        r = self.get_proficiency('dodge')
        if self.action.current_action == 'block':
            r += 8
        return r

    def hit(self, damage, accuracy=None, hitter=None):
        chance = not accuracy or self.states.get('Weak') or \
                 Global.r.rand_float() < accuracy / max(1, accuracy + self.get_dodge())
        if chance:
            self.location.attack.unregister(self.get_hitter())
            self.pilot.hit(hitter)
            if self.states.get('Distraction'):
                self.die()
                return 2
            self.form.timer.set(4)
            self.form.randomize_once(4)
            return super().hit(damage, accuracy, hitter)

    def get_hitter(self):
        return self

    def die(self):
        pos = self.pos
        super().die()
        if Tags.insubstantial not in self.tags:
            from src.entity.Stock import Stock
            r = Stock.get('Corpse')
            r.attributes.hp = self.attributes.max_hp
            r.relocate(pos.x, pos.y, force=1)
            r.set(self.form)

    def get_proficiency(self, school):
        return 1 if school.lower() in self.proficiency else 0

    def say(self, text):
        pass
