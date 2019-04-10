from src.entity.Effect import Effect
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.entity.unit.action.Spells import Spells, miscast
from src.map.Tile import Tile
from src.tools.Random import Random


class Actions:
    default = ['idle', 'left', 'right', 'walk', 'hit', 'down', 'interact', 'use', 'jump', 'sprint', 'duck',
               'act1', 'act2', 'act3', 'act4', 'act5', 'act6']
    spell_list = ['fireblast', 'levitate', 'brand', 'scorch', 'tornado', 'crystallize', 'grapple', 'summon', 'fargate',
                  'teleport', 'shock']

    def __init__(self, host):
        self.host = host
        self.current_action = 'idle'
        self.on_finish = None
        self.last_action = None
        self.spells = []
        self.skills = []
        self.auto = 0
        self.exhausted = 0

    def __str__(self):
        return ','.join(self.skills + self.spells)

    def load(self, arg):
        for i in arg:
            if i in self.spell_list:
                self.spells.append(i)
            else:
                self.skills.append(i)
        self.spells = Actions.spell_list

    def attempt(self, action):
        if action in self.skills or action in Actions.default:
            self.set(action)

    def set(self, action, auto=0):
        if self.exhausted and not auto:
            action = 'idle'
        self.auto = auto
        self.current_action = action
        self.host.hang = 0
        if self.on_finish:
            if self.host.delay:
                self.on_finish = None
            else:
                fn = self.on_finish  # prevent recursion
                self.on_finish = None
                fn()
        getattr(self, action)()
        self.last_action = action
        return 1

    def set_animation(self, arg):
        if self.host.form.state_name != arg or self.host.form.animation_ended:
            self.host.form.set(arg)

    def make(self, animation=None, turn=0, interrupt=1):
        if interrupt:
            self.host.attributes.rest_time = 0
        if animation:
            self.set_animation(animation)
        else:
            self.set_animation(self.current_action)
        self.host.delay = turn

    def exert(self, organ, mag):
        self.exhausted = self.host.attributes.exert(organ, mag)
        return self.exhausted

    @staticmethod
    def knockdown(victim):
        if isinstance(victim, Unit):
            victim.action.set('down', auto=1)

    def idle(self):
        if not self.host.get_offset_tile(0, 1).is_land(Tile.CHECK_LANDABLE) and self.host.pos[0].is_climbable():
            self.host.hang = 1
            self.make(animation='hang', turn=0)
        else:
            if self.host.attributes.is_rested():
                if self.last_action == 'idle':
                    self.make(animation='standby', turn=0)
                else:
                    self.make(turn=0)
            else:
                self.host.attributes.rest()
                self.exhausted = self.exert(0, 0) or self.exert(1, 0) or self.exert(2, 0)
                self.make(animation='rest', interrupt=0)

    def act1(self):
        self.set(self.skills[0])

    def act2(self):
        self.set(self.skills[1])

    def act3(self):
        self.set(self.skills[2])

    def act4(self):
        self.set(self.skills[3])

    def act5(self):
        self.set(self.skills[4])

    def act6(self):
        self.set(self.skills[5])

    def left(self):
        self.host.face(-1)
        self.set('walk')

    def right(self):
        self.host.face(1)
        self.set('walk')

    def walk(self):
        if not self.host.attributes.is_rested():
            self.exert(0, 2)
        if self.host.pos[0].is_climbable() and\
                not self.host.get_offset_tile(self.host.direction, 1).is_land(Tile.CHECK_LANDABLE):
            self.host.move(self.host.direction, 0)
            if self.host.pos[0].is_climbable():
                self.host.hang = 1
                self.make(animation='hike', turn=6 - self.host.attributes.speed)
            else:
                self.make(turn=2 - self.host.attributes.speed)
        else:
            self.host.move(self.host.direction, 0)
            if self.host.gravity:
                self.make(turn=2 - self.host.attributes.speed)
            else:
                self.make(animation='swim', turn=4 - self.host.attributes.speed)

    def hit(self):
        self.host.attributes.rest()
        self.make(turn=5, interrupt=0)

    def interact(self):
        self.make(turn=3)
        if not self.host.is_armed():
            from src.entity.unit.item.Item import Item
            for thing in reversed(self.host.pos[0].things):
                if thing != self.host.weapon and isinstance(thing, Item):
                    thing.on_equip(self.host)
                    return
                elif isinstance(thing, Unit) and 'grapple' in self.spells and thing.action.current_action == 'down':
                    # thing.on_equip(self.host) // Pick up and make throwable
                    return
        else:
            self.host.drop()

    def duck(self):
        def finish():
            self.host.gravity = 1
        ground = self.host.get_offset_tile(0, 1)
        climbable = ground.is_climbable()
        if climbable:
            if self.host.gravity or self.host.form.state_name == 'climb':
                self.host.gravity = 0
                self.host.move(0, 1, flag=Tile.CHECK_BREAKABLE)
                self.on_finish = finish
                self.make('climb', turn=2)
            elif not self.host.gravity:
                self.host.move(0, 1)
                self.make(animation='swim', turn=4)
        else:
            self.make(animation='interact', turn=2)
            for thing in self.host.pos[0].things:
                if thing.name == 'Travel':
                    thing.trigger(self.host)
                    return

    def jump(self):
        if self.host.pos[0].is_climbable() and \
                (self.host.get_offset_tile(0, -1).is_climbable() or self.host.pos[0].is_land([Tile.COLLIDE_DOODAD])):
            self.host.hang = 1
            if self.host.pos[0] != self.host.move(0, -1):
                self.make('climb', turn=2)
        else:
            if self.host.gravity:
                self.exert(0, 2)
                self.host.hang = 0
                self.host.move(self.host.direction*1, -1)
                self.make(turn=2)
            else:
                self.host.move(0, -1)
                self.make(animation='swim', turn=4)

    def down(self):
        self.host.attributes.rest()
        self.make(turn=7, interrupt=0)

    def dodge(self):
        self.host.attributes.rest()
        self.host.weapon.form.rotate(20 * self.host.direction)
        self.make(animation='dodge', turn=1, interrupt=0)

    def sprint(self):
        self.exert(0, 1)
        self.host.move(self.host.direction, 0)
        self.make(turn=0)

    def use(self):
        self.host.weapon.use()

    def attack(self):
        self.exert(1, self.host.weapon.weight)
        self.host.aim()
        self.host.form.rotate_appendage(30, 0, self.host.next_target)
        self.host.weapon.attack(1 + self.host.get_proficiency(self.current_action))
        self.make(turn=4)

    def dash(self):
        self.exert(2, 2 + self.host.weapon.weight)
        self.exert(0, 6)
        self.host.aim()
        prof = self.host.get_proficiency(self.current_action) - 1
        orig_x = self.host.pos[0].x
        destination = self.host.move(self.host.direction*3, 0, flag=[Tile.COLLIDE_TERRAIN])
        for i in range(abs(destination.x - orig_x)):
            aoe = self.host.get_offset_tile(-self.host.direction*i, 0)
            self.host.location.attack.register(1, aoe, type='batter',
                                               faction=self.host.faction, chance=prof, callback=self.knockdown)
        self.host.weapon.attack(1 + prof, callback=self.knockdown)
        self.make(turn=6)

    def kick(self):
        def on_hit(victim):
            victim.move(direction, 0)
            self.knockdown(victim)
        self.exert(0, 8)
        direction = self.host.direction
        chance = 4 + self.host.get_proficiency(self.current_action)
        self.host.location.attack.register(0, self.host.get_offset_tile(self.host.direction, 0),
                                           chance=chance, type='batter', callback=on_hit)
        self.make(turn=4)

    def leap(self):
        def fall():
            self.host.gravity = 1
        self.exert(0, 3)
        self.host.move(self.host.direction * 2, -2)
        if self.host.gravity:
            self.host.gravity = 0
            self.on_finish = fall
        self.make(animation='jump', turn=1)

    def lunge(self):
        self.exert(2, 2 + self.host.weapon.weight)
        if self.host.pos[0] != self.host.move(self.host.direction, 0):
            self.host.weapon.attack(self.host.get_proficiency(self.current_action), callback=self.knockdown)
            self.make(turn=4)
        else:
            self.make(animation='drop', turn=4)

    def underhand(self):
        self.exert(2, self.host.weapon.weight)
        self.host.form.rotate_appendage(41, 0, self.host.next_target)
        self.host.aim()
        self.host.weapon.attack(self.host.get_proficiency(self.current_action))
        self.host.move(-self.host.direction, 0)
        self.host.weapon.attack(self.host.get_proficiency(self.current_action))
        self.make(turn=2)

    def stab(self):
        self.exert(1, 1 + self.host.weapon.weight)
        self.exert(2, 1 + self.host.weapon.weight)
        self.host.form.rotate_appendage(41, 0, self.host.next_target)
        self.host.aim()
        self.host.weapon.attack(2 + self.host.get_proficiency(self.current_action))
        self.make(turn=2 + self.host.weapon.speed)

    def flurry(self):
        self.exert(1, self.host.weapon.weight)
        self.host.weapon.attack(self.host.get_proficiency(self.current_action) - 1)
        angle = self.host.next_target.get_atan() + (Random.rand_int(-15, 15))
        self.host.weapon.form.rotate(-angle + 90)
        self.host.form.rotate_appendage(55, 0, self.host.next_target)
        self.host.form.rotate_appendage(55, 5, self.host.next_target)
        self.make(animation='flurry', turn=1)

    def arch(self):
        def fin():
            def effect(target):
                if target:
                    Effect.make('batter', r.pos[0].get_center())
            r = Stock.project('g_0x2', self.host.get_interact_pos(), 2)
            r.faction = self.host.faction
            r.chance = self.host.get_proficiency(self.current_action)
            r.shoot(dest.x, dest.y, 9)
            r.location.attack.register(1, r.pos[0], delay=0, faction=r.faction, chance=6, callback=effect)
        self.exert(2, self.host.weapon.weight)
        dest = self.host.next_target * 10
        self.host.form.rotate_appendage(31, 0, self.host.next_target)
        self.host.form.rotate_appendage(32, 0, self.host.next_target)
        self.on_finish = fin
        self.host.aim()
        self.make(turn=7)

    def on_cast(self, spell):
        def cast():
            return spell(self.host)
        self.on_finish = cast

    def ignite(self):
        self.exert(1, 3)
        self.exert(2, 3)
        if self.host.is_casted('pyromancy'):
            self.on_cast(Spells.ignite)
            self.make(animation='charm', turn=8)
        else:
            Effect.make('fail', self.host.pos[0].get_center(), lifetime=16)
            self.host.action.set('hit', auto=4)
            miscast['f'](self.host)

    def whirlwind(self):
        self.exert(1, 3)
        self.exert(2, 3)
        if self.host.is_casted('aeromancy'):
            self.on_cast(Spells.whirlwind)
            self.make(animation='charm', turn=2)
        else:
            Effect.make('fail', self.host.pos[0].get_center(), lifetime=16)
            self.host.action.set('hit', auto=4)
            miscast['a'](self.host)

    def conjure(self):
        self.exert(1, 3)
        self.exert(2, 3)
        if self.host.is_casted('conjuration'):
            self.on_cast(Spells.conjure)
            self.make(animation='charm', turn=12)
        else:
            Effect.make('fail', self.host.pos[0].get_center(), lifetime=16)
            self.host.action.set('hit', auto=4)
            miscast['r'](self.host)

    def charm(self):
        self.exert(0, 3)
        if self.host.is_casted('charm'):
            self.on_cast(Spells.charm)
            self.make(turn=8)
        else:
            Effect.make('fail', self.host.pos[0].get_center(), lifetime=16)
            self.host.action.set('hit', auto=4)

    def cast(self):
        self.exert(0, 3)
        if self.host.is_casted('cast'):
            self.on_cast(Spells.cast)
            self.host.form.rotate_appendage(28, 0, self.host.next_target)
            self.host.form.rotate_appendage(28, 5, self.host.next_target)
            self.make(turn=6)
        else:
            Effect.make('fail', self.host.pos[0].get_center(), lifetime=16)
            self.host.action.set('hit', auto=4)
