from src.entity.Prop import Prop
from src.form.Body import Body
from src.game import Global
from src.game.Camera import Camera
from src.map.Tile import Tile


class Unit(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.Actions import Actions
        self.draw_frame = 0
        self.bleed_frame = 0
        self.action = Actions(self)
        self.proficiency = []
        self.next_action = 'idle'
        self.direction = 3
        self.collision_type = Tile.COLLIDE_UNIT
        self.pilot = None
        self.delay = 0

    def __str__(self):
        att = '[' + self.action.__str__() + '],[' + ','.join(self.proficiency) + ']'
        return super().__str__() + ',' + att

    def load(self, p):
        index = super().load(p)
        self.action.load(p[index])
        index += 1
        self.proficiency = p[index]
        self.form.randomize(self.tags.get('seed', 0))
        from src.entity.unit.ai import Pilot
        ai = self.tags.get('ai')
        if ai:
            self.pilot = Pilot.Pilot(self)
            self.pilot.load(ai)
        else:
            self.pilot = Pilot.Manual(self)
        index += 1
        return index

    def add(self):
        r = super().add()
        self.face(self.tags.get('dir', 4))
        return r

    def set_form(self, arg):
        self.form_name = arg
        from src.tools.Data import Data
        line = Data.get_line('raw/model.txt', arg)
        self.form = Body(line[1])
        self.form.set_model(line[2])

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
        mhp = self.tags.get('p>')
        if mhp:
            hp = self.tags.get('p')
            if hp:
                if self.tags.get('mat') == 'flesh':
                    hurt = hp / mhp
                    if hurt < 1 and self.bleed_frame <= 0:
                        from src.entity.Particle import Particle
                        Particle.make('blood', self.vec)
                        self.bleed_frame = hurt * hurt * 32
                    else:
                        self.bleed_frame -= 1

    def set_row(self, row):
        self.form.set_row(self.depth(row))

    def center_camera(self):
        super().center_camera()

    def input(self, action):
        self.next_action = action

    def use(self):
        self.action.attack()

    def face(self, direction):
        if direction != self.direction:
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

    def get_defense(self):
        if self.action.current_action == 'fall':
            return 0, 0
        r = self.get_proficiency('dodge')
        return 0, r

    def hit(self, damage, hitter=None):
        min_d, max_d = self.get_defense()
        max_d = max(min_d, max_d)
        damage -= Global.r.rand_int(min_d, max_d)
        if damage > 0:
            self.pilot.hit(hitter)
            if self.states.get('Distraction'):
                self.die()
                return 2
            self.form.timer.set(4)
            self.form.randomize_once(4)
            return super().hit(damage, hitter)

    def get_hitter(self):
        return self

    def die(self):
        pos = self.pos
        super().die()
        if not self.tags.get('ix'):
            from src.entity.Stock import Stock
            r = Stock.get('Corpse')
            r.tags.set('p', self.tags.get('p>'))
            r.relocate(pos.x, pos.y, force=1)
            r.set(self.form)

    def get_proficiency(self, school):
        return 1 if school.lower() in self.proficiency else 0

    def say(self, text):
        pass
