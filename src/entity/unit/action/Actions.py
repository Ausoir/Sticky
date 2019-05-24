from src.entity.Effect import Effect
from src.entity.Stock import Stock
from src.entity.unit.Buff import BuffTags
from src.entity.unit.Unit import Unit
from src.entity.unit.action.Spells import Spells
from src.map.Tile import Tile
from src.tools.Random import Random


class Actions:
    martial = ['sprint', 'block', 'lunge', 'flurry', 'leap', 'tackle']
    default = ['idle', 'left', 'right', 'walk', 'hit', 'down', 'interact', 'use', 'jump', 'duck', 'offhand',
               'run_left', 'run_right', 'act1', 'act2', 'act3', 'act4', 'act5', 'act6']

    def __init__(self, host):
        self.host = host
        self.current_action = 'idle'
        self.on_finish = None
        self.last_action = None
        self.skills = []
        self.techniques = []
        self.auto = 0
        self.exhausted = 0

    def __str__(self):
        return ','.join(self.skills + self.techniques)

    def load(self, arg):
        for i in arg:
            if i in self.martial:
                self.techniques.append(i)
            else:
                self.skills.append(i)

    def attempt(self, action, idle=True):
        if action in Actions.default or action in self.skills or action in self.techniques:
            self.set(action)
            return True
        elif idle:
            self.set('idle')

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
            if not victim.get_proficiency('Constitution'):
                victim.action.set('down', auto=1)
            else:
                victim.form.set('drop')

    def idle(self):
        if not self.host.get_offset_tile(0, 1).is_land(Tile.CHECK_LANDABLE) and self.host.pos[0].is_climbable():
            self.host.hang = 1
            self.make(animation='hang', turn=0)
        else:
            self.exhausted = not self.host.attributes.is_rested()
            if self.exhausted:
                self.host.attributes.rest()
                self.make(animation='rest', interrupt=0)
            else:
                if self.last_action == 'idle':
                    self.make(animation='standby', turn=0)
                else:
                    self.make(turn=0)

    def act1(self):
        if len(self.skills) > 0:
            self.set(self.skills[0])

    def act2(self):
        if len(self.skills) > 1:
            self.set(self.skills[1])

    def act3(self):
        if len(self.skills) > 2:
            self.set(self.skills[2])

    def act4(self):
        if len(self.skills) > 3:
            self.set(self.skills[3])

    def act5(self):
        if len(self.skills) > 4:
            self.set(self.skills[4])

    def act6(self):
        if len(self.skills) > 5:
            self.set(self.skills[5])

    def left(self):
        self.host.face(-1)
        self.set('walk')

    def right(self):
        self.host.face(1)
        self.set('walk')

    def run_left(self):
        self.host.face(-1)
        self.set('run_attempt')

    def run_right(self):
        self.host.face(1)
        self.set('run_attempt')

    def run_attempt(self):
        front = self.host.get_offset_tile(self.host.direction, 0)
        if front.is_land(Tile.CHECK_BREAKABLE):
            self.attempt('lunge')
            return
        else:
            far = self.host.get_offset_tile(self.host.direction * 2, 0)
            if far.is_land([Tile.COLLIDE_UNIT]) and self.attempt('tackle', idle=False):
                return
        self.attempt('sprint')

    def walk(self):
        cripple = self.host.states.get('Cripple')
        if cripple:
            slow = 1
        else:
            slow = 0
        if self.host.pos[0].is_climbable() and\
                not self.host.get_offset_tile(self.host.direction, 1).is_land(Tile.CHECK_LANDABLE):
            self.host.move(self.host.direction, 0)
            if self.host.pos[0].is_climbable():
                self.host.hang = 1
                self.make(animation='hike', turn=6 - self.host.attributes.speed)
            else:
                self.make(turn=2 - self.host.attributes.speed + slow)
        else:
            if self.host.gravity:
                front = self.host.get_offset_tile(self.host.direction, 0)
                if front.is_land([Tile.COLLIDE_UNIT]):
                    self.set('attack')
                elif front.is_land(Tile.CHECK_FIRM):
                    self.set('jump')
                else:
                    self.host.move(self.host.direction, 0)
                    self.make(turn=2 - self.host.attributes.speed + slow)
            else:
                self.host.move(self.host.direction, 0)
                self.make(animation='swim', turn=4 - self.host.attributes.speed)

    def hit(self):
        self.host.attributes.rest(5)
        self.make(turn=6, interrupt=0)

    def interact(self):
        self.make(turn=3)
        if not self.host.is_armed():
            from src.entity.unit.item.Item import Item
            for thing in reversed(self.host.pos[0].things):
                if thing != self.host.weapon and isinstance(thing, Item):
                    thing.on_equip(self.host)
                    return
        else:
            if self.host.weapon.name == 'Ladder':
                y = 0
                end = False
                while not end:
                    end = True
                    for thing in self.host.get_offset_tile(0, y).things:
                        if thing.name == 'Ladder':
                            end = False
                    y -= 1
                self.make(animation='interact', turn=2)
                weapon = self.host.weapon
                self.host.drop()
                weapon.move(0, y)
            else:
                self.host.drop()

    def offhand(self):
        weapon = self.host.offhand
        self.host.offhand = self.host.weapon
        self.host.weapon = weapon
        self.make(animation='block', turn=2)

    def duck(self):
        ground = self.host.get_offset_tile(0, 1)
        climbable = ground.is_climbable()
        if climbable:
            if self.host.gravity or self.host.form.state_name == 'climb':

                def finish():
                    self.host.gravity = 1
                self.on_finish = finish
                self.host.gravity = 0
                self.host.move(0, 1, flag=Tile.CHECK_BREAKABLE)
                self.make('climb', turn=2)
        else:
            if self.host.gravity:
                for thing in self.host.pos[0].things:
                    if thing.name == 'Travel':
                        self.make(animation='interact', turn=2)
                        thing.trigger(self.host)
                        return
                self.attempt('block')
            else:
                self.host.move(0, 1)
                self.make(animation='swim', turn=4)

    def jump(self):
        if self.host.gravity:
            if self.host.pos[0].is_climbable() and \
                    (self.host.get_offset_tile(0, -1).is_climbable() or self.host.pos[0].is_land(
                        [Tile.COLLIDE_DOODAD])):
                self.host.hang = 1
                if self.host.pos[0] != self.host.move(0, -1):
                    self.make('climb', turn=2)
            else:
                self.exert(1, 1)
                self.host.hang = 0
                self.host.move(self.host.direction*1, -1)
                self.make(turn=2)
        else:
            self.host.move(0, -1)
            self.make(animation='swim', turn=6)

    def down(self):
        self.host.attributes.rest()
        self.make(turn=10, interrupt=0)

    def block(self):
        self.host.weapon.form.rotate(20 * self.host.direction)
        self.make(turn=2)

    def sprint(self):
        front = self.host.get_offset_tile(self.host.direction, 0)
        if front.is_land(Tile.CHECK_FIRM):
            self.attempt('jump')
        else:
            cripple = self.host.states.get('Cripple')
            if cripple:
                slow = 1
            else:
                slow = 0
            self.exert(1, 1)
            self.host.move(self.host.direction, 0)
            self.make(turn=slow)

    def tackle(self):
        if self.host.pos[0] != self.host.move(self.host.direction, 0):
            self.exert(0, 5)
            self.exert(1, 18)
            self.host.location.attack.register(0, self.host.get_offset_tile(self.host.direction, 0),
                                               faction=self.host.faction, type='batter', callback=self.knockdown)
            self.host.move(self.host.direction, 0, flag=Tile.CHECK_FIRM)
            self.make(turn=4)

    def use(self):
        self.host.weapon.use()

    def attack(self):
        self.exert(0, self.host.weapon.weight)
        self.host.form.rotate_appendage(30, 0, self.host.next_target, offset=50)
        self.host.weapon.attack()
        if not self.host.is_armed():
            self.make(animation='kick', turn=self.host.weapon.speed)
        elif self.host.weapon.speed < 5:
            self.make(animation='slash', turn=self.host.weapon.speed)
        else:
            self.make(turn=self.host.weapon.speed)

    def leap(self):
        self.exert(1, 12)
        self.host.move(self.host.direction * 2, -2)
        self.make(animation='jump', turn=3)

    def lunge(self):
        def fin():
            self.host.weapon.rotation = orig

        def hit(victim):
            victim.move(self.host.direction, 0)
            self.knockdown(victim)
            victim.hit(1)
            victim.states.add('Cripple', 40)
        orig = self.host.weapon.rotation
        self.host.weapon.rotation = 0
        self.on_finish = fin
        self.exert(0, self.host.weapon.weight)
        self.host.move(self.host.direction, 0)
        rand = Random.rand_int(-10, 10)
        self.host.form.rotate_appendage(40, 0, self.host.next_target, offset=rand)
        self.host.weapon.attack(damage=self.host.get_proficiency('Lunge')-1, callback=hit)
        self.make(turn=self.host.weapon.speed)

    def flurry(self):
        def fin():
            self.host.weapon.rotation = orig
        orig = self.host.weapon.rotation
        self.host.weapon.rotation = 0
        self.on_finish = fin
        self.exert(0, 1)
        self.host.weapon.attack(damage=1 - self.host.weapon.damage + self.host.get_proficiency('Flurry'))
        rand = Random.rand_int(-15, 15)
        self.host.form.rotate_appendage(38, 0, self.host.next_target, offset=rand)
        self.host.form.rotate_appendage(38, 5, self.host.next_target, offset=rand)
        self.make(animation='flurry', turn=2)

    def arch(self):
        def fin():
            def effect(target):
                if target:
                    Effect.make('batter', r.pos[0].get_center())
            r = Stock.project('g_0x3', self.host.get_interact_pos(), 2)
            r.faction = self.host.faction
            r.shoot(dest.x, dest.y, 9)
            r.location.attack.register(1, r.pos[0], delay=0, faction=r.faction, callback=effect)
            self.host.weapon.rotation = orig_rot
        orig_rot = self.host.weapon.rotation
        self.host.weapon.rotation = 0
        self.exert(2, self.host.weapon.weight)
        dest = self.host.next_target * 10
        self.host.form.rotate_appendage(33, 0, self.host.next_target)
        self.host.form.rotate_appendage(34, 0, self.host.next_target)
        self.on_finish = fin
        self.make(turn=7)

    def dispell(self):
        self.exert(1, 1)
        from src.entity.Prop import Prop
        aoe = self.host.location.get_area(self.host.pos[0], 8, 8)
        for i in aoe:
            for thing in i.things:
                Effect.make('energy', thing.vec)
                if isinstance(thing, Prop):
                    thing.hit(0)
                    thing.states.clear(lambda x: x.duration >= 0 and BuffTags.magic in x.tags)
        self.make(animation='charm', turn=8)

    def scorch(self):
        def effect():
            if not r.lifetime % 2:
                Effect.make('scorch', r.pos[0].get_center(), offset=6)
            for thing in r.pos[0].things:
                if thing != r:
                    thing.states.add('Burn', 8)
        self.exert(0, 1)
        r = Stock.project('g_0x0', self.host.get_offset_tile(self.host.direction, 0), 80)
        r.fast = 0
        r.effect = effect
        self.make(animation='cast', turn=4)

    def fireblast(self):
        def on_cast():
            def effect():
                def hit(target):
                    Effect.make('burn', target.pos[0].get_center(), offset=4, lifetime=40)
                    for thing in target.pos[0].things:
                        thing.states.add('Burn', 16)
                    r.remove()
                if self.host.next_target.y > 0:
                    y = 1
                elif self.host.next_target.y < 0:
                    y = -1
                else:
                    y = 0
                if r.pos[0] == r.move(final_dir, y):
                    hit(r)
                else:
                    r.location.attack.register(0, r.pos[0], faction=0, callback=hit)
                    Effect.make('explode', r.pos[0].get_center(), offset=4).form.face(final_dir)
            r = Stock.project('g_0x0', self.host.get_offset_tile(self.host.direction, 0), 6)
            final_dir = self.host.direction
            r.effect = effect
        self.on_finish = on_cast
        self.exert(0, 3)
        self.make(animation='cast', turn=8)

    def sonic(self):
        Stock.make('Light', self.host.get_target_tile())
        self.make(animation='cast', turn=6)

    def gateway(self):
        rift = self.host.states.get('Rift')
        if rift:
            Spells.teleport(self.host)
        else:
            Effect.make('barrier', self.host.vec)
            r = Stock.get('Portal').add()
            r.relocate(self.host.pos[0].x, self.host.pos[0].y - 1, force=1)
            self.host.states.add('Rift', 160, var=r.id)
        self.make(animation='charm', turn=8)
