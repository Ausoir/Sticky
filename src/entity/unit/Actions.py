from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.map.Tile import Tile
from src.tools.Random import Random


class Actions:
    default = ['idle', 'left', 'right', 'walk', 'hit', 'down', 'interact', 'use', 'jump', 'duck',
               'run_left', 'run_right', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']

    def __init__(self, host):
        self.host = host
        self.current_action = 'idle'
        self.on_finish = None
        self.last_action = None
        self.skills = []
        self.auto = 0
        self.exhausted = 0

    def __str__(self):
        return ','.join(self.skills)

    def load(self, arg):
        for i in arg:
            self.skills.append(i)

    def attempt(self, action, idle=True):
        if action in Actions.default or action in self.skills:
            self.set(action)
            return True
        elif idle:
            self.set('idle')

    def set(self, action, auto=0):
        if self.exhausted and not auto:
            action = 'idle'
        self.host.weapon.rotation = 60
        self.auto = auto
        self.current_action = action
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
        self.exhausted = not self.host.attributes.is_rested()
        if self.exhausted:
            self.host.attributes.rest()
            self.make(animation='rest', interrupt=0)
        else:
            if self.last_action == 'idle':
                self.make(animation='standby', turn=0)
            else:
                self.make(turn=0)

    def wield(self, pocket):
        if len(self.host.armor.pockets) > pocket:
            item = self.host.armor.get_item(self.host.armor.pockets[pocket])
            armed = self.host.is_armed()
            if item and not armed:
                item.on_equip(self.host)
            elif not item and armed:
                rows = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2], [3, 0], [3, 1], [3, 2]]
                for i in rows:
                    weapon = self.host.weapon
                    if self.host.armor.is_vacant(weapon, i[0], i[1]):
                        self.host.drop()
                        self.host.armor.pockets[pocket] = self.host.armor.add_inventory(weapon, i[0], i[1])
                        break
        self.make(animation='block', turn=2)

    def item1(self):
        self.wield(0)

    def item2(self):
        self.wield(1)

    def item3(self):
        self.wield(2)

    def item4(self):
        self.wield(3)

    def item5(self):
        self.wield(4)

    def item6(self):
        self.wield(5)

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
            self.attempt('kick')
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
        if self.host.gravity:
            front = self.host.get_offset_tile(self.host.direction, 0)
            if front.is_land([Tile.COLLIDE_UNIT]):
                self.set('attack')
            elif front.is_land(Tile.CHECK_FIRM):
                self.set('jump')
            else:
                self.host.move(self.host.direction, 0)
                self.make(turn=1 - self.host.attributes.speed + slow)
        else:
            self.host.move(self.host.direction, 0)
            self.make(animation='swim', turn=4 - self.host.attributes.speed)

    def hit(self):
        self.host.attributes.rest(5)
        self.make(turn=4, interrupt=0)

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
                            y -= 1
                            end = False
                            break
                self.make(animation='interact', turn=2)
                weapon = self.host.weapon
                self.host.drop()
                weapon.move(0, y)
            else:
                self.host.drop()

    def offhand(self):
        self.host.swap()
        self.make(animation='block', turn=2)

    def duck(self):
        ground = self.host.get_offset_tile(0, 1)
        if ground.is_climbable():
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
            stand = self.host.get_offset_tile(0, -1).is_climbable() or self.host.pos[0].is_land([Tile.COLLIDE_DOODAD])
            if stand and self.host.pos[0].is_climbable():
                self.exert(1, 1)
                if self.host.pos[0] != self.host.move(0, -1):
                    self.make('climb', turn=2)
            else:
                self.exert(1, 3)
                self.host.move(self.host.direction*1, -1)
                self.make(turn=2)
        else:
            self.host.move(0, -1)
            self.make(animation='swim', turn=6)

    def down(self):
        def fin():
            for thing in self.host.pos[0].things:
                if thing != self.host and isinstance(thing, Unit):
                    thing.move(self.host.direction, 0)
                    self.knockdown(thing)
        self.on_finish = fin
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
            self.exert(0, 1)
            self.exert(1, self.host.attributes.leg + 1)
            self.host.location.attack.register(0, self.host.get_offset_tile(self.host.direction, 0),
                                               faction=self.host.faction, type='batter', callback=self.knockdown)
            self.host.move(self.host.direction, 0, flag=Tile.CHECK_FIRM)
            self.make(turn=4)

    def use(self):
        self.host.weapon.use()

    def attack(self):
        self.host.weapon.rotation = 60
        self.exert(0, self.host.weapon.weight)
        self.host.form.rotate_appendage(30, 0, self.host.next_target, offset=50)
        self.host.weapon.attack()
        if self.host.weapon.speed < 5:
            self.make(animation='slash', turn=self.host.weapon.speed)
        else:
            self.make(turn=self.host.weapon.speed)

    def kick(self):
        self.exert(1, 3)
        front = self.host.get_offset_tile(self.host.direction, 0)
        self.host.location.attack.register(1, front, type='batter', chance=1 + self.host.get_proficiency('Fist'))
        self.make(turn=4)

    def leap(self):
        self.exert(1, 12)
        self.host.move(self.host.direction * 2, -2)
        self.make(animation='jump', turn=3)

    def lunge(self):
        def hit(victim):
            victim.move(self.host.direction, 0)
            self.knockdown(victim)
            victim.hit(1)
            victim.states.add('Cripple', 40)
        self.exert(0, self.host.weapon.weight)
        self.host.weapon.rotation = 20
        self.host.move(self.host.direction, 0)
        rand = Random.rand_int(-10, 10)
        self.host.form.rotate_appendage(40, 0, self.host.next_target, offset=rand)
        self.host.weapon.attack(chance=self.host.get_proficiency('Lunge') - 1, callback=hit)
        self.make(turn=self.host.weapon.speed)

    def flurry(self):
        self.host.weapon.rotation = 20
        self.exert(0, 1)
        self.host.weapon.attack(chance=1 - self.host.weapon.damage + self.host.get_proficiency('Flurry'))
        rand = Random.rand_int(-15, 15)
        self.host.form.rotate_appendage(38, 0, self.host.next_target, offset=rand)
        self.host.form.rotate_appendage(38, 5, self.host.next_target, offset=rand)
        self.make(animation='flurry', turn=2)

    def arch(self):
        def fin():
            r = Stock.project('g_0x7', self.host.get_interact_pos())
            r.faction = self.host.faction
            r.shoot(dest.x, dest.y)
            self.host.weapon.rotation = orig_rot
        orig_rot = self.host.weapon.rotation
        self.host.weapon.rotation = 0
        self.exert(2, self.host.weapon.weight)
        dest = self.host.next_target
        self.host.form.rotate_appendage(33, 0, self.host.next_target)
        self.host.form.rotate_appendage(34, 0, self.host.next_target)
        self.on_finish = fin
        self.make(turn=7)
