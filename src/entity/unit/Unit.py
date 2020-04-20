from src.entity.Prop import Prop
from src.form.Body import Body
from src.game import Global
from src.game.Camera import Camera
from src.map.Tile import Tile


class Unit(Prop):
    def __init__(self, location):
        super().__init__(location)
        from src.entity.unit.Actions import Actions
        self.draw_frame = 0
        self.action = Actions(self)
        self.skills = []
        self.next_action = 'idle'
        self.direction = 3
        self.obstruct_type = Tile.COLLIDE_UNIT
        self.pilot = None
        from src.form.HealthBar import HealthBar
        self.healthbar = HealthBar(self.tags)
        self.sight = Tile.CHECK_SIGHT
        self.dodge = 0
        self.strength = 0
        self.stealth = 0

    def __str__(self):
        self.pilot.record()
        att = '[' + ','.join(self.skills) + ']'
        return super().__str__() + ',' + att

    def load(self, p):
        index = super().load(p)
        self.skills = p[index]
        from src.entity.unit.ai import Pilot
        ai = self.tags.get('ai')
        self.pilot = Pilot.Pilot(self)
        self.pilot.load(ai)
        index += 1
        return index

    def update_tags(self):
        super().update_tags()
        self.form.randomize(self.tags.get('seed', 0))

    def add(self):
        r = super().add()
        self.update_skill()
        self.face(self.tags.get('dir', 0))
        return r

    def set_form(self, arg):
        self.form_name = arg
        from src.tools.Data import Data
        line = Data.get_line('model.txt', arg)
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
        diff = self.destination.get_center() - self.vec
        self.vec.x += diff.x * .08
        self.vec.y += diff.y * .08
        bound_x, bound_y = Camera.get_relative_pos(self.vec.x, self.vec.y)
        self.form.place(bound_x, bound_y)
        self.healthbar.place(bound_x, Global.DISPLAY[1] - bound_y)
        return bound_x, bound_y

    def turn(self):
        self.healthbar.turn()
        if self.tags.get('ai'):
            self.pilot.update()
        super().turn()
        if self.action.delay > 0:
            self.action.delay -= 1
        elif self.action.delay == 0:
            self.action.set(self.next_action)
            self.next_action = 'idle'

    def set_row(self, row):
        self.form.set_row(row * 20 + 100)

    def show(self, visible):
        self.healthbar.show(visible)
        super().show(visible)

    def bound(self, visible):
        self.healthbar.bound(visible)
        super().bound(visible)

    def input(self, action):
        self.next_action = action

    def use(self):
        self.action.attack()

    def face(self, direction):
        direction = direction % 4
        if direction != self.direction:
            self.direction = direction
            self.form.face(direction)
            return True

    def face_toward(self, pos):
        diff = pos - self.pos
        horizontal = abs(diff.x) >= abs(diff.y)
        if horizontal:
            if diff.x < 0:
                direction = 1
            else:
                direction = 3
        else:
            if diff.y < 0:
                direction = 2
            else:
                direction = 0
        self.face(direction)

    def is_facing(self, pos):
        diff = pos - self.pos
        return diff.x <= 0 and self.direction == 1 or\
            diff.y <= 0 and self.direction == 2 or\
            diff.x >= 0 and self.direction == 3 or\
            diff.y >= 0 and self.direction == 0

    def update_skill(self, skill=None, remove=False):
        if not skill:
            self.dodge = self.get_skill('dodge', stacks=True)
            self.strength = self.get_skill('strength', stacks=True)
            self.stealth = self.get_skill('stealth', stacks=True)
        else:
            if skill == 'dodge':
                if remove:
                    self.dodge -= 1
                else:
                    self.dodge += 1
            elif skill == 'strength':
                if remove:
                    self.strength -= 1
                else:
                    self.strength += 1
            elif skill == 'stealth':
                if remove:
                    self.stealth -= 1
                else:
                    self.stealth += 1

    def get_defense(self):
        if self.action.current_action == 'fall':
            return 0
        return self.dodge + self.tags.get('DEF', 0)

    def get_damage(self):
        return self.strength + self.tags.get('dmg', 0) + 1

    def roll_defense(self):
        defense = self.get_defense()
        return Global.r.rand_int(0, defense)

    def roll_damage(self):
        damage = self.get_damage()
        dex = min(self.get_skill('dexterity', stacks=True), damage)
        return Global.r.rand_int(dex, damage)

    def hit(self, damage, hitter=None):
        r = 0
        backstab = False
        if isinstance(hitter, Prop):
            if self.is_facing(hitter.pos):
                if hitter.pos == self.pos.get_cardinal(self.direction, 1):
                    damage -= self.get_skill('block')
            else:
                backstab = True
        if not backstab:
            damage -= self.roll_defense()
        if self.get_skill('vengeance'):
            if self.states.add('Vengeance', 20).duration == 0:
                damage = 0
        self.states.trigger(['act', 'hit', damage])
        if damage > 0:
            self.action.idle_frame = 0
            if self.get_skill('constitution'):
                self.states.add('Invulnerable', 40)
            self.pilot.hit(hitter)
            if self.get_skill('parry'):
                concentration = self.states.get('Concentration')
                if concentration:
                    concentration.trigger(['spend'])
                    from src.entity.Particle import Particle
                    Particle.make('barrier', self.pos)
                    self.location.sound.register(self.pos, 0, file='critical')
                    if isinstance(hitter, Prop):
                        hitter.decay(damage + self.get_defense())
                    return 0
            self.form.randomize_once(4)
            r = super().hit(damage, hitter)
        return r

    def get_hitter(self):
        return self

    def on_attack(self, target):
        self.states.trigger(['attack', target])
        if isinstance(target, Unit):
            if self.get_skill('cleave'):
                left = self.pos.get_cardinal((self.direction - 1) % 4, 1)
                right = self.pos.get_cardinal((self.direction + 1) % 4, 1)
                dmg = self.roll_damage() - 1
                hitter = self.get_hitter()
                self.location.field.register(dmg, left, hitter=hitter, delay=0)
                self.location.field.register(dmg, right, hitter=hitter, delay=0)
            if self.get_skill('frenzy'):
                self.states.add('Damage', 40, 1)
            if not target.is_facing(self.pos):
                if self.get_skill('assassinate'):
                    target.tags.set('deaf', 1)
                    self.critical_attack(target)
        flurry = self.get_skill('flurry', stacks=True)
        if flurry:
            concentration = self.states.get('Concentration')
            if concentration:
                concentration.trigger(['spend'])
                concentration.var += 1
                if concentration.var <= flurry:
                    self.action.attack()
                    self.form.set_state('attack')
                    concentration.duration = self.action.delay
        if self.get_skill('execute'):
            if target.tags.get('p', 20) <= self.get_damage():
                target.die()

    def decay(self, damage):
        r = super().decay(damage)
        self.healthbar.appear()
        return r

    def die(self):
        pos = self.pos
        super().die()
        if self.tags.get('corpse', 1) != 0:
            self.tags.remove('ai')
            from src.entity.Stock import Stock
            r = Stock.make('Corpse', pos)
            r.set(self.form)
            hp = self.tags.get('P', 1)
            r.tags.set('p', hp)

    def remove(self):
        self.healthbar.remove()
        super().remove()

    def get_skill(self, skill, stacks=False):
        r = 0
        for i in self.skills:
            if skill == i:
                if not stacks:
                    return 1
                r += 1
        return r

    def critical_attack(self, target):
        critical = self.get_skill('assassinate', stacks=True)
        target.decay(max(7, critical * 7))
        from src.entity.Particle import Particle
        Particle.make('power', target.pos)
        self.location.sound.register(target.pos, 0, file='critical')

    def is_team(self, target):
        return self.tags.get('bad') == target.tags.get('bad')

    def get_attack_motion(self):
        return 'attack'

    def get_attack_speed(self):
        return self.tags.get('aspd', 0) + self.get_skill('agility', stacks=True)

    def get_team(self, ally=True):
        if bool(self.tags.get('bad') == 1) == ally:
            return self.location.population.bad
        else:
            return self.location.population.good

    def set_team(self, target):
        bad = target.tags.get('bad')
        if bad == 1:
            self.tags.set('bad', 1)
        elif self.tags.get('bad') == 1:
            self.tags.remove('bad')

    def describe(self):
        r = super().describe()
        from src.tools.Dialog import Dialog
        r += '\n' + Dialog.get('Level') + ': ' + str(len(self.skills))
        return r

    def get_weight(self):
        return super().get_weight() + self.tags.get('seed', 0) % 4 + 4
