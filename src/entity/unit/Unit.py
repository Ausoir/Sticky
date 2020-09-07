from src.entity.Container import Container
from src.form.Body import Body
from src.game import Global
from src.game.Camera import Camera
from src.map.Tile import Tile


class Unit(Container):
    SHADOW = None

    def __init__(self):
        super().__init__()
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
        self.shadow = Data.get_form('_g_7_0')

    def __str__(self):
        att = '[' + ','.join(self.skills) + ']'
        return super().__str__() + ',' + att

    def save(self):
        if self.action.delay:
            if self.action.current_action:
                self.tags.set('action', self.action.current_action)
            self.tags.set('delay', self.action.delay)
        self.pilot.record()
        return super().save()

    def load(self, p):
        index = super().load(p)
        self.skills = p[index].copy()
        from src.entity.unit.ai import Pilot
        ai = self.tags.get('ai')
        self.pilot = Pilot.Pilot(self)
        self.pilot.load(ai)
        skills = self.tags.remove('skills')
        if skills:
            for i in skills.split('&'):
                self.skills.append(i)
        action = self.tags.remove('action')
        delay = self.tags.remove('delay')
        if action:
            self.action.set(action)
        if delay:
            self.action.delay = delay
        index += 1
        return index

    def update_tags(self):
        super().update_tags()
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
        self.form.randomize(self.get_seed())
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
        if self.pos.get_icon() == '~':
            self.drown()

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
        if exp <= 0:
            if mode == 'sabotage' and personality == 'agent' and var.name in self.tags.get('classg').split('&'):
                exp += var.tags.get('def', 0) * 2 + var.tags.get('P', 0) + var.get_value() + current_level
            else:
                return
        if mode == 'kill':
            if personality == 'psycho' and var.tags.get('team') == self.tags.get('team'):
                exp *= 3
            elif personality == 'avenger':
                if var.name == self.tags.get('classg'):
                    exp *= 2
                exp += 1
        elif mode == 'eat':
            if personality == 'gourmet':
                exp *= 2
                if var.name == self.tags.get('classg'):
                    exp *= 2
        elif mode == 'survive' and personality != 'survivor':
            return
        elif mode == 'explore' and personality != 'survivor':
            return
        elif mode == 'observe' and personality == 'scholar':
            exp *= 2
        current_experience = self.tags.get('lvl', 100) % 100
        exp += exp * self.get_skill('clairvoyance')
        new_experience = min(99, int(exp * 5 / current_level) + current_experience)
        if current_experience < 99 and new_experience == 99:
            from src.entity.Particle import Particle
            Particle.make('barrier3', self.pos)
            Global.world.location.sound.register(self.pos, 0, file='level', priority=1)
        self.tags.set('lvl', current_level * 100 + new_experience)

    def hit(self, damage, hitter=None):
        r = 0
        self.action.idle_frame = 0
        has_hitter = hitter is not None
        if has_hitter and not self.is_facing(hitter.pos):
            backstab = True
        else:
            backstab = False
        if self.states.get('Barrier'):
            damage = 0
        if not backstab and self.action.current_action != 'fall':
            damage -= self.tags.get('def', 0)
        self.states.trigger(['act', 'hit', damage])
        self.pilot.hit(hitter)
        if damage > 0 and not backstab and self.get_skill('block'):
            concentration = self.states.get('Concentration')
            if concentration:
                concentration.trigger(['spend'])
                from src.entity.Particle import Particle
                Particle.make('barrier', self.pos)
                damage -= 1
        if damage > 0:
            self.pos.location.field.unregister(self)
            if self.get_skill('fortitude'):
                self.states.add('Invincible', 8)
            hitter_direction = self.pos.get_face(hitter.pos)
            if has_hitter:
                if self.direction == hitter_direction and self.get_skill('parry'):
                    concentration = self.states.get('Concentration')
                    if concentration:
                        concentration.trigger(['spend'])
                        from src.entity.Particle import Particle
                        Particle.make('barrier', self.pos)
                        self.pos.location.sound.register(self.pos, 0, file='critical')
                        self.action.hit()
                        return 0
            self.form.randomize_once(4)
            r = self.decay(damage)
            if r == 2:
                if has_hitter:
                    hitter.progress_level(self.get_level(), mode='kill', var=self)
                self.on_hit(effect='splat', sound='hit_cut')
            else:
                self.on_hit()
                if has_hitter and not self.removed:
                    front = self.pos.get_cardinal(hitter_direction + 2)
                    self.action.knockdown(self, 4, push=front)
                else:
                    self.action.knockdown(self, 4)
        else:
            self.on_hit(effect='slash', sound='hit_armor')
        return r

    def on_attack(self, result, target):
        self.states.trigger(['attack', target])
        if isinstance(target, Unit):
            if self.get_skill('disorient'):
                target.face(Global.r.rand_int(0, 3))
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
                        self.pos.location.sound.register(target.pos, 2, file='drain', priority=2)
                        break
            if result > 0:
                if self.get_skill('frenzy'):
                    self.states.add('Damage', 40, 1)
            elif result == 0 and self.get_skill('crush'):
                concentration = self.states.get('Concentration')
                if concentration:
                    concentration.trigger(['spend'])
                    target.states.add('Armoring', 40, -1)
                    target.hit(self.get_damage(), hitter=self)
        if result > 0:
            flurry = self.get_skill('flurry')
            if flurry:
                valid_sides = []
                for sides in [0, 1, -1, 2]:
                    attack_range = 1 + self.get_skill('reach') + self.get_skill('lunge')
                    front = self.pos.get_cardinal(self.direction + sides, distance=attack_range)
                    if front:
                        for i in front.things:
                            if isinstance(i, Unit) and i.tags.get('team') != self.tags.get('team'):
                                valid_sides.append(sides)
                                break
                if valid_sides:
                    concentration = self.states.get('Concentration')
                    if concentration:
                        concentration.trigger(['spend'])
                        concentration.var += 1
                        if concentration.var <= flurry:
                            self.face(self.direction + valid_sides[0])
                            self.action.attack()
                            self.form.set_state('flurry')
                            self.form.timer.set(4)
                            concentration.duration = self.action.delay

    def decay(self, damage):
        r = super().decay(damage)
        self.form.colorize([255, 0, 0])
        self.display_hp()
        return r

    def display_hp(self):
        hp = self.tags.get('p')
        m_hp = self.tags.get('P')
        self.healthbar.appear(hp, m_hp)

    def die(self):
        self.action.die()

    def death(self):
        pos = self.pos
        super().die()
        if self.tags.get('corpse', 1) != 0:
            self.tags.remove('ai')
            from src.entity.Stock import Stock
            r = Stock.make('Corpse', pos)
            hp = self.tags.get('P', 1)
            r.tags.set('p', hp)
        return True

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
        r += self.inventory.get_all_items()
        return r

    def get_skills(self):
        r = self.skills.copy()
        for i in ['ab1', 'ab2', 'ab3']:
            ability = self.tags.get(i)
            if ability:
                r.append(ability)
        return r

    def get_skill(self, skill):
        r = 0
        for i in self.skills:
            if skill == i:
                r += 1
        return r

    def critical_attack(self, target):
        target.decay(7)
        from src.entity.Particle import Particle
        Particle.make('power', target.pos, offset=16)
        self.pos.location.sound.register(target.pos, 0, file='critical')

    def is_team(self, target):
        return self.tags.get('bad') == target.tags.get('bad')

    def get_team(self, ally=True):
        if ally:
            teams = self.pos.location.population.get_team(self.tags.get('team', 0))
            r = []
            for i in teams:
                if i != self:
                    r.append(i)
            return teams
        else:
            return self.pos.location.population.get_foe(self.tags.get('team', 0))

    def describe(self):
        r = super().describe()
        from src.tools.Dialog import Dialog
        if self.tags.get('team', 1) <= 1:
            r += '\n' + Dialog.get(':neutral')
        r += '\n' + Dialog.get('Level') + ': ' + str(self.get_level())
        spd = self.tags.get('spd')
        if spd:
            r += '\n' + Dialog.get('Speed') + ': ' + str(spd)
        skills = self.get_skills()
        if skills:
            r += '\n' + Dialog.get('Skills') + ': ' + ', '.join(skills)
        return r

    def get_level(self):
        level = self.tags.get('lvl')
        if level:
            r = int(level / 100)
        else:
            r = self.tags.get_level() + self.tags.get('P', 2) - 1
            r += self.tags.get('def', 0) + self.tags.get('dmg', 0)
            if self.tags.get('spd', 0) > 0:
                r += 1
        return max(1, r)

    def get_weight(self):
        return super().get_weight() + int(self.form.get_height(self.get_seed()) * 7)

    def get_damage(self):
        return self.tags.get('dmg', 0) + 1

    def adjust_pos(self, x, y):
        old = self.pos
        super().adjust_pos(x, y)
        self.pilot.adjust_pos(self.pos - old)

    def on_sleep(self, time):
        super().on_sleep(time)
        if not self.is_hungry():
            if time >= 4:
                mhp = self.tags.get('P')
                if mhp:
                    self.tags.set('p', mhp)
            elif time > 0 and self.get_skill('perseverance'):
                self.decay(-time)
        hunger = self.tags.get('hunger')
        if hunger:
            new = min(100000, hunger + (500 * abs(time)))
            self.tags.set('hunger', new)
            if new >= 100000:
                self.decay(time)

    def is_hungry(self):
        hunger = self.tags.get('hunger')
        return hunger and hunger >= 10000
