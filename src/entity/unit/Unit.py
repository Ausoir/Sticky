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
        self.bleed_frame = 0
        self.action = Actions(self)
        self.skills = []
        self.next_action = 'idle'
        self.direction = 3
        self.obstruct_type = Tile.COLLIDE_UNIT
        self.pilot = None
        from src.form.HealthBar import HealthBar
        self.healthbar = HealthBar(self.tags)
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
        self.face(self.tags.get('dir', 4))
        self.update_skill()
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
        self.healthbar.place(self.vec.x, self.vec.y)

    def turn(self):
        if self.tags.get('ai'):
            self.pilot.update()
        super().turn()
        if self.action.delay > 0:
            self.action.delay -= 1
        elif self.action.delay == 0:
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
        return self.face(self.get_direction_toward(pos))

    def is_facing(self, pos):
        diff = pos - self.pos
        return diff.x <= 0 and self.direction == 1 or\
            diff.y <= 0 and self.direction == 2 or\
            diff.x >= 0 and self.direction == 3 or\
            diff.y >= 0 and self.direction == 4

    def update_skill(self):
        self.dodge += self.get_skill('dodge', stacks=True)
        self.strength += self.get_skill('might', stacks=True)
        self.stealth += self.get_skill('stealth', stacks=True)

    def get_defense(self):
        if self.action.current_action == 'fall':
            return 0, 0
        armor = self.states.get('Armor')
        if armor:
            return 0, max(0, self.dodge + armor.var)
        return 0, self.dodge

    def get_damage(self):
        return 0, self.strength + 1

    def roll_damage(self):
        min_d, max_d = self.get_damage()
        return Global.r.rand_int(min_d, min_d + max_d)

    def hit(self, damage, hitter=None):
        r = 0
        self.action.frame = 0
        min_d, max_d = self.get_defense()
        max_d = max(min_d, max_d)
        backstab = False
        if isinstance(hitter, Prop):
            from src.tools import Direction
            if self.is_facing(hitter.pos):
                if hitter.pos == self.get_front_tile(self.direction):
                    damage -= self.get_skill('block')
                elif Global.r.rand_int(0, self.get_skill('guard')) != 0:
                    damage -= self.get_skill('guard')
            else:
                backstab = True
        if not backstab:
            damage -= Global.r.rand_int(min_d, max_d)
        if self.get_skill('vengeance'):
            self.states.add('Vengeance', 20)
        self.states.trigger(['hit', damage])
        if damage > 0:
            if self.get_skill('toughness'):
                self.states.add('Invulnerable', 40)
            if self.get_skill('fury'):
                self.states.add('Speed', 40, 1)
            self.pilot.hit(hitter)
            if self.get_skill('parry'):
                concentration = self.states.get('Concentration')
                if concentration:
                    concentration.trigger(['spend'])
                    from src.entity.Particle import Particle
                    Particle.make('barrier', self.pos.get_center())
                    if isinstance(hitter, Prop):
                        from src.entity.unit.Actions import Actions
                        Actions.knockdown(hitter)
                        hitter.decay(damage)
                    return 0
            self.form.timer.set(4)
            self.form.randomize_once(4)
            r = super().hit(damage, hitter)
        self.healthbar.show()
        return r

    def get_hitter(self):
        return self

    def on_attack(self, target):
        self.states.trigger(['attack', target])
        if isinstance(target, Unit):
            if self.get_skill('cleave'):
                from src.tools import Direction
                left = self.get_front_tile(Direction.add(self.direction, -1))
                right = self.get_front_tile(Direction.add(self.direction, 1))
                dmg = self.roll_damage() - 1
                hitter = self.get_hitter()
                self.location.field.register(dmg, left, hitter=hitter, delay=0)
                self.location.field.register(dmg, right, hitter=hitter, delay=0)
            if self.get_skill('frenzy'):
                self.states.add('Damage', 40, 1)
            if self.get_skill('sunder'):
                target.states.add('Armor', 40, -4)
            if self.get_skill('assassination') and not target.is_facing(self.pos):
                target.tags.set('deaf', 1, add=True)
                self.critical_attack(target)
            critical = self.get_skill('critical strike', stacks=True)
            if critical and Global.r.rand_int(1, 10) <= critical:
                self.critical_attack(target)
        flurry = self.get_skill('flurry', stacks=True)
        calculation = self.get_skill('calculated hit')
        if flurry or calculation:
            concentration = self.states.get('Concentration')
            if concentration:
                concentration.trigger(['spend'])
                if calculation:
                    concentration.duration = self.action.delay
                    self.critical_attack(target)
                if flurry:
                    from src.entity.unit.Actions import Actions
                    concentration.var += 1
                    if concentration.var <= flurry:
                        self.action.attack()
                        concentration.duration = self.action.delay
        if self.get_skill('execute'):
            if target.tags.get('p', 20) <= self.get_damage()[1]:
                target.die()

    def die(self):
        pos = self.pos
        super().die()
        if not self.tags.get('ix'):
            self.tags.remove('ai')
            from src.entity.Stock import Stock
            r = Stock.make('Corpse', pos)
            r.set(self.form)

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
        target.decay(7)
        from src.entity.Particle import Particle
        Particle.make('power', target.vec)
        self.location.sound.register(target.pos, 0, file='hit_impale')
        if self.get_skill('adrenaline'):
            self.states.add('Speed', 40, 2)
        if self.get_skill('trip'):
            from src.entity.unit.Actions import Actions
            Actions.knockdown(target)
            from src.tools import Direction
            target.move_toward(self.direction)

    def is_team(self, target):
        return self.tags.get('bad') == target.tags.get('bad')

    def get_attack_speed(self):
        return 0

    def get_team(self, ally=True):
        if bool(self.tags.get('bad')) == ally:
            return self.location.population.bad
        else:
            return self.location.population.good
