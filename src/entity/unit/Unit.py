from src.entity.Prop import Prop
from src.form.Body import Body
from src.game import Global
from src.game.Camera import Camera
from src.map.Tile import Tile
from src.tools import Direction


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
        self.face(self.tags.get('dir', 4))
        self.update_skill()
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
        diff = self.pos.get_center() - self.vec
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
                        Particle.make('blood', self.vec, offset=8)
                        self.bleed_frame = hurt * hurt * 32
                    else:
                        self.bleed_frame -= 1

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
        if direction != self.direction:
            self.direction = direction
            self.form.face(direction)
            return True

    def face_toward(self, pos):
        return self.face(Direction.get_direction_toward((pos - self.pos).to_list()))

    def is_facing(self, pos):
        diff = pos - self.pos
        return diff.x <= 0 and self.direction == 1 or\
            diff.y <= 0 and self.direction == 2 or\
            diff.x >= 0 and self.direction == 3 or\
            diff.y >= 0 and self.direction == 4

    def update_skill(self):
        self.dodge = self.get_skill('dodge', stacks=True)
        self.strength = self.get_skill('strength', stacks=True)
        self.stealth = self.get_skill('stealth', stacks=True)

    def get_defense(self):
        if self.action.current_action == 'fall':
            return 0
        return self.dodge

    def get_damage(self):
        return self.strength + 1

    def roll_defense(self):
        defense = self.get_defense()
        return Global.r.rand_int(0, defense)

    def roll_damage(self):
        damage = self.get_damage()
        dex = min(self.get_skill('dexterity', stacks=True), damage)
        return Global.r.rand_int(dex, damage)

    def hit(self, damage, hitter=None):
        r = 0
        self.action.frame = 0
        backstab = False
        if isinstance(hitter, Prop):
            if self.is_facing(hitter.pos):
                if hitter.pos == self.get_front_tile(self.direction):
                    damage -= self.get_skill('block')
            else:
                backstab = True
        if not backstab:
            damage -= self.roll_defense()
        if self.get_skill('vengeance'):
            if self.states.add('Vengeance', 20).duration == 0:
                damage = 0
        self.states.trigger(['hit', damage])
        if damage > 0:
            if self.get_skill('constitution'):
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
                        hitter.decay(damage + self.get_defense())
                    return 0
            self.form.timer.set(4)
            self.form.randomize_once(4)
            r = super().hit(damage, hitter)
        return r

    def get_hitter(self):
        return self

    def on_attack(self, target):
        self.states.trigger(['attack', target])
        if isinstance(target, Unit):
            if self.get_skill('cleave'):
                left = self.get_front_tile(Direction.add(self.direction, -1))
                right = self.get_front_tile(Direction.add(self.direction, 1))
                dmg = self.roll_damage() - 1
                hitter = self.get_hitter()
                self.location.field.register(dmg, left, hitter=hitter, delay=0)
                self.location.field.register(dmg, right, hitter=hitter, delay=0)
            if self.get_skill('frenzy'):
                self.states.add('Damage', 40, 1)
            if not target.is_facing(self.pos):
                if self.get_skill('assassinate'):
                    target.tags.set('deaf', 1, add=True)
                    self.critical_attack(target)
        flurry = self.get_skill('flurry', stacks=True)
        if flurry:
            concentration = self.states.get('Concentration')
            if concentration:
                concentration.trigger(['spend'])
                concentration.var += 1
                if concentration.var <= flurry:
                    self.tags.increment('spd', -self.get_attack_speed(), add=True)
                    self.action.attack()
                    self.form.set_state('flurry')
                    self.tags.increment('spd', self.get_attack_speed(), remove=True)
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
        if self.tags.get('mat') == 'flesh':
            self.tags.remove('ai')
            from src.entity.Stock import Stock
            r = Stock.make('Corpse', pos)
            r.set(self.form)
            hp = self.tags.get('p>', 1)
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
        Particle.make('power', target.vec)
        self.location.sound.register(target.pos, 0, file='critical')

    def is_team(self, target):
        return self.tags.get('bad') == target.tags.get('bad')

    def get_attack_speed(self):
        return 0

    def get_team(self, ally=True):
        if bool(self.tags.get('bad') == 1) == ally:
            return self.location.population.bad
        else:
            return self.location.population.good

    def set_team(self, target):
        bad = target.tags.get('bad')
        if bad == 1:
            self.tags.set('bad', 1, add=True)
        elif self.tags.get('bad') == 1:
            self.tags.remove('bad')

    def describe(self):
        r = super().describe()
        from src.tools.Dialog import Dialog
        r += '\n' + Dialog.get('level') + ': ' + str(len(self.skills) + 1)
        return r
