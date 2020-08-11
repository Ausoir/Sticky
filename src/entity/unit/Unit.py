from src.entity.Container import Container
from src.form.Body import Body
from src.game import Global
from src.game.Camera import Camera
from src.map.Tile import Tile


class Unit(Container):
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
        skills = self.tags.remove('skills')
        if skills:
            for i in skills.split('&'):
                self.skills.append(i)
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
        diff = self.pos.get_center() - self.vec
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
        self.shadow.z = row * 20 + 100
        self.form.set_row(row * 20 + 100)

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

    def progress_level(self, exp, mode='other', var=None):
        personality = self.tags.get('class', 'classless')
        current_level = self.get_level()
        curve = int(3 / current_level)
        if exp <= 0:
            if mode == 'sabotage' and personality == 'agent' and var.name in self.tags.get('mission').split('&'):
                exp += var.tags.get('def', 0) * 2 + var.tags.get('P', 2) + var.get_value()
            else:
                return
        if mode == 'kill':
            if personality == 'psycho' and var.tags.get('team') == self.tags.get('team'):
                exp *= 3
            elif personality == 'avenger' and var.name == self.tags.get('revenge'):
                exp += var.get_level()
        elif mode == 'eat' and personality == 'gourmet' and var.name == self.tags.get('favorite'):
            exp *= 4
        elif mode == 'survive' and personality == 'survivor':
            exp *= 2
        elif mode == 'explore':
            if personality == 'explorer':
                curve = int(curve * current_level / 5) * 2
            else:
                return
        elif mode == 'observe' and personality == 'scholar':
            exp *= 4
        current_experience = self.tags.get('lvl', 100) % 100
        current_experience = min(99, exp * curve + current_experience)
        self.tags.set('lvl', current_level * 100 + current_experience)

    def hit(self, damage, hitter=None):
        r = 0
        self.action.idle_frame = 0
        backstab = False
        if hitter is not None and self.action.delay == 0:
            if self.is_facing(hitter.pos):
                if self.get_skill('block') and self.states.get('Concentration'):
                    damage -= 1
            else:
                backstab = True
        if not backstab and self.action.current_action != 'fall':
            damage -= self.tags.get('def', 0)
        if self.states.get('Barrier'):
            damage = 0
        self.states.trigger(['act', 'hit', damage])
        self.pilot.hit(hitter)
        if damage > 0:
            self.location.field.unregister(self)
            if self.get_skill('fortitude'):
                self.states.add('Invincible', 8)
            if not backstab and self.get_skill('parry'):
                concentration = self.states.get('Concentration')
                if concentration:
                    concentration.trigger(['spend'])
                    from src.entity.Particle import Particle
                    Particle.make('barrier', self.pos)
                    self.location.sound.register(self.pos, 0, file='critical')
                    return 0
            self.form.randomize_once(4)
            r = self.decay(damage)
            if r == 2:
                if hitter:
                    exp = self.get_level() - hitter.get_level() + 1
                    hitter.progress_level(exp, mode='kill', var=self)
                self.on_hit(effect='splat', sound='hit_cut')
            else:
                self.on_hit()
                if hitter and not self.removed:
                    front = self.pos.get_cardinal(hitter.pos.get_face(self.pos))
                    self.action.knockdown(self, 4, push=front)
                else:
                    self.action.knockdown(self, 4)
        else:
            self.on_hit(effect='slash', sound='hit_armor')
        return r

    def on_attack(self, target):
        self.states.trigger(['attack', target])
        if isinstance(target, Unit):
            if self.get_skill('frenzy'):
                self.states.add('Damage', 40, 1)
            if not target.is_facing(self.pos):
                if self.get_skill('assassinate'):
                    target.tags.set('deaf', 1)
                    self.critical_attack(target)
            if self.get_skill('feed'):
                for i in target.skills:
                    if i not in self.skills:
                        self.skills.remove('feed')
                        self.skills.append(i)
                        from src.entity.Particle import Particle
                        Particle.make('spin', target.pos)
                        target.skills.remove(i)
                        self.location.sound.register(target.pos, 2, file='drain', priority=2)
                        break
        flurry = self.get_skill('flurry')
        if flurry:
            valid_sides = []
            for sides in [1, -1, 2]:
                front = self.pos.get_cardinal(self.direction + sides)
                if front:
                    for i in front.things:
                        if isinstance(i, Unit) and i.tags.get('team') != self.tags.get('team'):
                            valid_sides.append(sides)
                            break
            if valid_sides:
                self.face(self.direction + valid_sides[0])
                self.action.attack()
                self.form.set_state('flurry')
                self.form.timer.set(4)

    def decay(self, damage):
        r = super().decay(damage)
        self.display_hp()
        return r

    def get_durability(self):
        hp = self.tags.get('p', 0)
        mhp = self.tags.get('P', 0)
        return 0, 0, hp, mhp

    def display_hp(self):
        hp = self.tags.get('p')
        m_hp = self.tags.get('P')
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
            return True

    def get_accessibles(self):
        r = []
        from src.entity.unit.item.Item import Item
        for thing in self.pos.things:
            if isinstance(thing, Item):
                r.append(thing)
        return r

    def get_skills(self):
        r = self.skills.copy()
        if self.tags.get('abi'):
            r.append(self.tags.get('abi'))
        return r

    def get_skill(self, skill):
        r = 0
        for i in self.skills:
            if skill == i:
                r += 1
        return r

    def critical_attack(self, target):
        target.decay(1)
        from src.entity.Particle import Particle
        Particle.make('power', target.pos, offset=16)
        self.location.sound.register(target.pos, 0, file='critical')

    def is_team(self, target):
        return self.tags.get('bad') == target.tags.get('bad')

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

    def describe(self):
        r = super().describe()
        from src.tools.Dialog import Dialog
        r += '\n' + Dialog.get('Level') + ': ' + str(self.get_level())
        spd = self.tags.get('spd')
        if spd:
            r += '\n' + Dialog.get('Speed') + ': ' + str(spd)
        if self.skills:
            r += '\n' + Dialog.get('Skills') + ': ' + ', '.join(self.skills)
        return r

    def get_level(self):
        level = self.tags.get('lvl')
        if level:
            r = int(level / 100)
        else:
            r = len(self.skills)
            r += self.tags.get('P', 10) + self.tags.get('str', 1)
            r += self.tags.get('sth', 0) + self.tags.get('int', 0) + self.tags.get('cha', 0)
            if self.tags.get('abi'):
                r += 1
            r -= 2
        return max(1, r)

    def get_weight(self):
        return super().get_weight() + self.get_seed() % 4 + 4

    def get_value(self):
        return 2
