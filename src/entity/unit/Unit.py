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
        self.obstruct_type = Tile.COLLIDE_UNIT
        self.pilot = None
        from src.form.HealthBar import HealthBar
        self.healthbar = HealthBar()
        self.sight = Tile.CHECK_SIGHT
        from src.tools.Data import Data
        self.shadow = Data.get_form('g_7x0')

    def __str__(self):
        self.tags.set('dir', self.direction)
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
        self.form.randomize(self.get_seed())
        rare = self.tags.get('rare', 0)
        if rare > 0:
            from src.tools.Data import Data
            line = Data.get_line('model.txt', self.form_name)
            self.form.set_model(line[3])

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
        self.vec += diff * .1
        bound_x, bound_y = Camera.get_relative_pos(self.vec.x, self.vec.y)
        self.form.place(bound_x, bound_y)
        self.healthbar.place(bound_x, Global.DISPLAY[1] - bound_y)
        self.shadow.place(bound_x, bound_y)
        return bound_x, bound_y

    def turn(self):
        self.healthbar.turn()
        if self.tags.get('ai'):
            self.pilot.update()
        if self.action.delay > 0:
            self.action.delay -= 1
        elif self.action.delay == 0:
            self.action.set(self.next_action)
            self.next_action = 'idle'

    def on_natural_spawn(self):
        self.face(Global.r.rand_int(0, 3))

    def set_row(self, row):
        diff = self.destination.y - self.pos.y
        if diff > 0:
            self.form.set_row((row + diff) * 20 + 100)
            self.shadow.z = (row + diff) * 20 + 101
        else:
            self.form.set_row(row * 20 + 100)
            self.shadow.z = row * 20 + 101

    def show(self, visible):
        self.healthbar.show(visible)
        super().show(visible)
        self.shadow.show(visible)

    def bound(self, visible):
        self.healthbar.bound(visible)
        super().bound(visible)
        self.shadow.bound(visible)

    def input(self, action):
        self.next_action = action

    def use(self):
        self.action.attack()

    def face_toward(self, pos):
        self.face(self.pos.get_face(pos))

    def is_facing(self, pos):
        diff = pos - self.pos
        return diff.x <= 0 and self.direction == 1 or\
            diff.y <= 0 and self.direction == 2 or\
            diff.x >= 0 and self.direction == 3 or\
            diff.y >= 0 and self.direction == 0

    def get_defense(self):
        if self.action.current_action == 'fall':
            return 0
        return max(0, self.tags.get('DEF', 0))

    def get_damage(self):
        return max(0, self.tags.get('DMG', 0) + 1)

    def roll_defense(self):
        defense = self.get_defense()
        return Global.r.rand_int(0, defense)

    def roll_damage(self):
        damage = self.get_damage()
        dex = min(self.tags.get('dmg', 0), damage)
        return Global.r.rand_int(dex, damage)

    def calculate_hit(self, damage, hitter=None):
        self.action.idle_frame = 0
        backstab = False
        if isinstance(hitter, Prop):
            if self.is_facing(hitter.pos):
                block = self.get_skill('block')
                if block and hitter.pos == self.pos.get_cardinal(self.direction, 1):
                    if self.states.get('Concentration'):
                        damage -= block
            else:
                backstab = True
        if not backstab and self.action.current_action != 'fall':
            damage -= self.roll_defense()
        if self.get_skill('vengeance'):
            if self.states.add('Vengeance', 20).duration == 0:
                damage = 0
        self.states.trigger(['act', 'hit', damage])
        if damage > 0:
            if self.get_skill('constitution'):
                self.states.add('Invulnerability', 40)
            self.pilot.hit(hitter)
            if self.get_skill('parry') and Global.r.rand_int(0, 4) == 0:
                from src.entity.Particle import Particle
                Particle.make('barrier', self.pos)
                self.location.sound.register(self.pos, 0, file='critical')
                if isinstance(hitter, Prop):
                    hitter.decay(damage + self.get_defense())
                return False
            self.form.randomize_once(4)
            return True

    def hit(self, damage, hitter=None):
        r = 0
        if self.calculate_hit(damage, hitter):
            r = super().hit(damage, hitter)
        return r

    def on_hit(self, hitter=None):
        from src.entity.Particle import Particle
        if hitter.tags.get('sharp'):
            self.location.sound.register(self.pos, 7, file='hit_cut')
            Particle.make('splat', self.pos)
        else:
            self.location.sound.register(self.pos, 7, file='hit_bash')
            Particle.make('batter', self.pos)

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
                self.location.field.register(dmg, left, hitter=hitter)
                self.location.field.register(dmg, right, hitter=hitter)
            if self.get_skill('frenzy'):
                self.states.add('Damage', 40, 1)
            if not target.is_facing(self.pos):
                if self.get_skill('assassination'):
                    target.tags.set('deaf', 1)
                    self.critical_attack(target)
            if self.get_skill('knockout') and Global.r.rand_int(0, 4) == 0:
                target.states.add('Knockout', 20)
            if self.get_skill('feed'):
                for i in target.skills:
                    if i not in self.skills:
                        self.skills.remove('feed')
                        self.skills.append(i)
                        from src.entity.Particle import Particle
                        Particle.make('spin', target.pos)
                        self.location.sound.register(target.pos, 2, file='drain', priority=2)
                        break
        flurry = self.get_skill('flurry', stacks=True)
        if flurry:
            concentration = self.states.get('Concentration')
            if concentration:
                concentration.trigger(['spend'])
                concentration.var += 1
                if concentration.var <= flurry:
                    self.action.attack()
                    concentration.duration = self.action.delay
                self.form.set_state('flurry')
                self.form.timer.set(4)
        if self.get_skill('execute'):
            if target.tags.get('p', 20) <= self.get_damage():
                target.die()

    def decay(self, damage):
        r = super().decay(damage)
        self.display_hp()
        return r

    def get_durability(self):
        hp = self.tags.get('p')
        mhp = self.tags.get('P')
        return 0, 0, hp, mhp

    def display_hp(self):
        hp = self.tags.get('p')
        if hp is not None:
            m_hp = self.tags.get('P', -1)
            if m_hp > 0:
                self.healthbar.appear(hp, m_hp)

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

    def add(self):
        r = super().add()
        if r:
            from src.game.Turn import Turn
            Turn.add(self.turn)
            self.states.on_load()
            return r

    def remove(self):
        if super().remove():
            from src.game.Turn import Turn
            Turn.remove(self.turn)
            self.healthbar.remove()

    def get_accessibles(self):
        r = []
        from src.entity.unit.item.Item import Item
        for thing in self.pos.things:
            if isinstance(thing, Item):
                r.append(thing)
        return r

    def get_skill(self, skill, stacks=False):
        r = 0
        for i in self.skills:
            if skill == i:
                if not stacks:
                    return 1
                r += 1
        return r

    def critical_attack(self, target):
        critical = self.get_skill('assassination', stacks=True)
        target.decay(max(7, critical * 7))
        from src.entity.Particle import Particle
        Particle.make('power', target.pos)
        self.location.sound.register(target.pos, 0, file='critical')

    def is_team(self, target):
        return self.tags.get('bad') == target.tags.get('bad')

    def get_attack_motion(self):
        return 'attack'

    def get_attack_speed(self):
        return self.tags.get('aspd', 0)

    def get_team(self, ally=True):
        if ally:
            teams = self.location.population.get_team(self.tags.get('team', 0))
            r = []
            for i in teams:
                if i != self:
                    r.append(i)
            return teams
        else:
            return self.location.population.get_foe(self.tags.get('team', 0))

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
        return super().get_weight() + self.get_seed() % 4 + 4

    def get_value(self):
        return 2

    def progress_level(self, exp):
        multiplier = 10000 - self.tags.get('hunger', 0)
        self.tags.increment('level', int(exp * multiplier))
