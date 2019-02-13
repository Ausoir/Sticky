from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.entity.unit.action.Spells import Spells
from src.form.Effect import Effect
from src.map.Tile import Tile
from src.tools.Random import Random


class ActionSet:
    default = ['idle', 'left', 'right', 'walk', 'hit', 'down', 'dead', 'interact', 'use', 'jump', 'sprint',
               'act1', 'act2', 'act3', 'act4', 'act5', 'act6']
    spell_list = ['fireblast', 'levitate', 'brand']

    def __init__(self, host):
        self.host = host
        self.current_action = 'idle'
        self.on_finish = None
        self.last_action = None
        self.time = 0
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

    def attempt(self, action):
        if action in self.skills or action in ActionSet.default:
            self.set(action)

    def set(self, action, auto=0):
        if not self.host.is_dead():
            if self.exhausted and not auto:
                action = 'rest'
            self.auto = auto
            self.current_action = action
            if action != self.last_action:
                self.time = 0
                if self.on_finish:
                    fn = self.on_finish  # prevent recursion
                    self.on_finish = None
                    fn()
            else:
                self.time += 1
            getattr(self, action)()
            self.last_action = action

    def set_animation(self, arg):
        if self.host.form.state_name != arg or self.host.form.animation_ended:
            self.host.form.set(arg)

    def make(self, animation=None, turn=0):
        if animation:
            self.set_animation(animation)
        else:
            self.set_animation(self.current_action)
        self.host.delay += turn

    def exert(self, organ, mag):
        self.exhausted = self.host.attributes.exert(organ, mag)
        return self.exhausted

    def recover(self):
        self.host.form.set_height()

    @staticmethod
    def knockdown(victim):
        if isinstance(victim, Unit):
            victim.action.set('down')

    def idle(self):
        if self.time > 3:
            self.make(animation='standby', turn=0)
        else:
            self.make(turn=0)

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
        self.host.move(self.host.direction, 0)
        if self.host.gravity:
            self.make(turn=2)
        else:
            self.make(animation='swim', turn=4)

    def hit(self):
        self.make(turn=2)

    def climb(self):
        self.make(turn=0)

    def interact(self):
        def finish():
            self.host.gravity = 1
        if self.host.get_offset_tile(0, 1).is_land([Tile.COLLIDE_LANDABLE]):
            if self.host.gravity or self.host.form.state_name == 'climb':
                self.host.gravity = 0
                self.host.move(0, 1)
                self.on_finish = finish
                self.make('climb', turn=2)
        else:
            self.make(turn=3)
            for thing in reversed(self.host.pos[0].things):
                if thing.interact(self.host):
                    return

    def dead(self):
        self.host.form.set_height(1)
        self.host.collide = 0
        self.host.location.record.remove(self.host)
        self.on_finish = self.recover
        self.make(animation='dead' + str(Random.rand_int(1, 3)))
        self.host.delay = -1

    def down(self):
        self.host.form.set_height(1)
        self.on_finish = self.recover
        self.make(turn=7)

    def rest(self):
        self.exhausted = self.exert(0, 0) or self.exert(1, 0) or self.exert(2, 0)
        self.make(turn=3)

    def sprint(self):
        self.exert(0, 2)
        self.host.move(self.host.direction, 0)
        self.make(turn=0)

    def use(self):
        self.host.weapon.use()

    def attack(self):
        self.exert(1, 5)
        self.host.aim()
        self.host.form.rotate_appendage(30, 0, self.host.next_target)
        self.host.weapon.attack(delay=1)
        self.make(turn=4)

    def dash(self):
        self.exert(0, 10)
        self.host.aim()
        self.host.location.attack.register(1, self.host.get_offset_tile(self.host.direction, 0),
                                           delay=1, type=self.host.weapon.hit_type, callback=self.knockdown)
        self.host.location.attack.register(1, self.host.get_offset_tile(self.host.direction*2, 0),
                                           delay=1, type=self.host.weapon.hit_type, callback=self.knockdown)
        self.host.move(self.host.direction*3, 0, flag=Tile.CHECK_TERRAIN)
        self.host.weapon.attack(delay=1, callback=self.knockdown)
        self.make(turn=6)

    def kick(self):
        def on_hit(victim):
            victim.move(direction, 0)
            if isinstance(victim, Unit):
                victim.action.set('down')
        self.exert(0, 10)
        direction = self.host.direction
        self.host.location.attack.register(0, self.host.get_offset_tile(self.host.direction, 0),
                                           delay=1, type='batter', callback=on_hit)
        self.make(turn=4)

    def jump(self):
        if self.host.pos[0].is_land([Tile.COLLIDE_LANDABLE]):
            self.host.move(0, -1)
            self.make('climb', turn=2)
        else:
            self.exert(0, 5)
            self.host.move(self.host.direction*1, -1)
            self.make(turn=2)

    def leap(self):
        def fall():
            self.host.gravity = 1
        self.exert(0, 10)
        self.host.location.attack.register(1, self.host.get_offset_tile(self.host.direction*2, 0),
                                           delay=1, type='batter', callback=self.knockdown)
        self.host.move(self.host.direction * 6, -6)
        if self.host.gravity:
            self.host.gravity = 0
            self.on_finish = fall
        self.make(animation='jump', turn=1)

    def lunge(self):
        self.exert(2, 5)
        if self.host.pos[0] != self.host.move(self.host.direction, 0):
            self.host.weapon.attack(delay=2, callback=self.knockdown)
            self.make(turn=4)
        else:
            self.make(animation='drop', turn=4)

    def underhand(self):
        def fin():
            self.host.hittable = 1
        self.exert(2, 5)
        if self.host.pos[0] != self.host.move(-self.host.direction, 0):
            self.host.form.rotate_appendage(41, 0, self.host.next_target)
            self.host.weapon.attack(delay=1)
            self.host.hittable = 0
            self.on_finish = fin
            self.make(turn=5)
        else:
            self.make(animation='drop', turn=4)

    def arch(self):
        def fin():
            def effect(target):
                if target:
                    Effect.blood(r.motion_pos)
            r = Stock.get('Arrow', self.host.location).add_to(self.host.faction, self.host.get_interact_pos())
            r.fly(dest.x, dest.y-1, 8)
            r.crash(callback=effect)
        dest = self.host.next_target * 10
        self.host.form.rotate_appendage(31, 0, self.host.next_target)
        self.host.form.rotate_appendage(32, 0, self.host.next_target)
        self.on_finish = fin
        self.make(turn=7)

    def ignite(self):
        def on_cast():
            Spells.ignite(self.host)
        self.on_finish = on_cast
        self.exert(0, 5)
        self.exert(1, 5)
        self.exert(2, 5)
        self.make(animation='conjure', turn=8)

    def whirlwind(self):
        def on_cast():
            Spells.whirlwind(self.host)
        self.on_finish = on_cast
        self.exert(0, 5)
        self.exert(1, 5)
        self.exert(2, 5)
        self.make(animation='charm', turn=3)

    def conjure(self):
        def on_cast():
            Spells.conjure(self.host)
        self.on_finish = on_cast
        self.exert(0, 5)
        self.exert(1, 5)
        self.exert(2, 5)
        self.make(animation='charm', turn=12)

    def charm(self):
        def on_cast():
            Spells.charm(self.host)
        self.on_finish = on_cast
        self.exert(0, 5)
        self.exert(1, 5)
        self.exert(2, 5)
        self.make(turn=5)

    def cast(self):
        def on_cast():
            Spells.cast(self.host)
        self.on_finish = on_cast
        self.exert(0, 5)
        self.exert(1, 5)
        self.exert(2, 5)
        self.make(turn=8)
