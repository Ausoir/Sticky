import random

from src.entity.Effect import Effect
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.game import Global
from src.map.Tile import Tile


class Actions:
    default = ['idle', 'left', 'right', 'walk', 'hit', 'down', 'interact', 'use', 'jump', 'duck', 'peek', 'power',
               'run_left', 'run_right', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6', 'attack']
    priority = ['down', 'hit']

    def __init__(self, host):
        self.host = host
        self.current_action = 'idle'
        self.on_finish = None
        self.last_action = None
        self.skills = []
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

    def set(self, action):
        self.host.location.attack.unregister(self.host)
        if self.exhausted and action not in Actions.priority:
            action = 'rest'
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

    def make(self, animation=None, turn=0):
        if animation:
            self.set_animation(animation)
        else:
            self.set_animation(self.current_action)
        self.host.delay = turn

    def exert(self, organ, mag):
        self.exhausted = self.exhausted or self.host.attributes.exert(organ, mag)
        return self.exhausted

    @staticmethod
    def knockdown(victim):
        if isinstance(victim, Unit):
            victim.action.set('down')

    def idle(self):
        if self.last_action == 'idle':
            self.make(animation='standby', turn=0)
        else:
            self.make(turn=0)

    def rest(self):
        self.exhausted = False
        self.host.attributes.body = 0
        self.host.attributes.leg = 0
        if self.host.states.get('Exhaustion'):
            self.make(turn=16)
        else:
            self.make(turn=4)

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
        far = self.host.get_offset_tile(self.host.direction * 2, 0)
        if far.is_land([Tile.COLLIDE_UNIT]) or front.is_land([Tile.COLLIDE_UNIT]):
            if self.attempt('tackle', idle=False):
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
            if front.is_land(Tile.CHECK_FIRM):
                if not self.host.get_offset_tile(self.host.direction, -1).is_land(Tile.CHECK_FIRM):
                    self.set('jump')
                else:
                    self.set('idle')
            else:
                self.host.move(self.host.direction, 0)
                self.make(turn=1 - self.host.attributes.speed + slow)
        else:
            self.host.move(self.host.direction, 0)
            self.make(animation='swim', turn=4 - self.host.attributes.speed)

    def hit(self):
        self.make(turn=2)

    def interact(self):
        self.make(turn=3)
        if not self.host.is_armed():
            from src.entity.unit.item.Item import Item
            for thing in reversed(self.host.pos.things):
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

    def duck(self):
        ground = self.host.get_offset_tile(0, 1)
        if ground.is_climbable():
            self.host.move(0, 1, flag=Tile.CHECK_BREAKABLE)
            self.make('climb', turn=2)
        else:
            if self.host.gravity:
                from src.game.Interaction import Interaction
                if Interaction.trigger(self.host.pos):
                    self.make(animation='interact', turn=4)
                else:
                    self.attempt('block')
            else:
                self.host.move(0, 1)
                self.make(animation='swim', turn=4)

    def jump(self):
        if self.host.gravity:
            cripple = self.host.states.get('Cripple')
            if not cripple:
                if self.host.pos.is_climbable():
                    if self.host.pos != self.host.move(0, -1):
                        self.make('climb', turn=2)
                else:
                    from src.entity.unit.Character import Character
                    if not Character.check_var(self.host, 'passive', 'Monk'):
                        self.exert(1, 3)
                    destination = self.host.get_offset_tile(self.host.direction, -1)
                    if destination.is_land(Tile.CHECK_FIRM):
                        self.host.move(0, -1)
                    else:
                        self.host.move(self.host.direction * 1, -1)
                    self.make(turn=2)
        else:
            self.host.move(0, -1)
            self.make(animation='swim', turn=6)

    def down(self):
        def fin():
            for thing in self.host.pos.things:
                if thing != self.host and isinstance(thing, Unit):
                    thing.move(self.host.direction, 0)
                    self.knockdown(thing)
        self.on_finish = fin
        self.make(turn=10)

    def block(self):
        self.host.weapon.form.rotate(20 * self.host.direction)
        self.make(turn=1)

    def peek(self):
        def fin():
            self.host.center_camera()
        self.on_finish = fin
        new_pos = self.host.location.collide_land(self.host.pos, self.host.next_target.x, self.host.next_target.y,
                                                  distance=1, flag=Tile.CHECK_LARGE)
        from src.game.TempObject import TempObject
        viewer = TempObject(new_pos)
        from src.game.Camera import Camera
        Camera.target = viewer
        self.make(animation='idle', turn=1)

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
            from src.entity.unit.Character import Character
            if not Character.check_var(self.host, 'passive', 'Monk'):
                self.exert(1, 1)
            self.host.move(self.host.direction, 0)
            self.make(turn=slow)

    def tackle(self):
        self.exert(1, 18)
        self.host.move(self.host.direction, 0)
        self.host.location.attack.register(0, self.host.get_offset_tile(self.host.direction, 0), delay=0,
                                           faction=self.host.faction, type='batter', callback=self.knockdown)
        self.host.move(self.host.direction, 0, flag=Tile.CHECK_FIRM)
        self.make(animation='kick', turn=3)

    def use(self):
        self.host.use()

    def attack(self):
        def callback(target):
            self.host.states.trigger(['attack', target])
        self.exert(0, 1)
        front = self.host.get_offset_tile(self.host.direction, 0)
        self.host.location.attack.register(1, front, type='batter', delay=0, chance=1, callback=callback)
        self.make(animation='attack', turn=4)

    def swing(self):
        self.host.weapon.rotation = 60
        self.exert(0, self.host.weapon.weight)
        self.host.form.rotate_appendage(19, 0, self.host.next_target, offset=50)
        self.host.weapon.attack()
        if self.host.weapon.speed < 4:
            self.make(animation='slash', turn=self.host.weapon.speed)
        else:
            self.make(animation='attack', turn=self.host.weapon.speed)

    def leap(self):
        self.exert(1, 12)
        degree = self.host.next_target.get_atan()
        from src.tools.Math import Math
        self.host.move(round(Math.cos(degree) * 2.4), round(Math.sin(degree) * 2.4))
        self.make(animation='jump', turn=3)

    def lunge(self):
        def hit(victim):
            victim.move(self.host.direction, 0)
            self.knockdown(victim)
            victim.hit(1)
            victim.states.add('Cripple', 40)
        self.exert(0, self.host.weapon.weight + 1)
        self.host.weapon.rotation = 15
        self.host.move(self.host.direction, 0)
        rand = random.randint(-15, 15)
        self.host.form.rotate_appendage(40, 0, self.host.next_target, offset=rand)
        prof = self.host.get_proficiency('lunge')
        self.host.weapon.attack(delay=2, chance=prof, callback=hit)
        self.make(turn=max(1, self.host.weapon.speed - prof))

    def flurry(self):
        if Global.player.stamina(1):
            self.host.weapon.rotation = 10
            self.exert(1, 1)
            self.host.weapon.attack(chance=self.host.get_proficiency('flurry'))
            rand = random.randint(-15, 15)
            self.host.form.rotate_appendage(38, 0, self.host.next_target, offset=rand)
            self.host.form.rotate_appendage(38, 5, self.host.next_target, offset=rand)
            self.make(animation='flurry', turn=1)
        else:
            self.make(animation='idle', turn=1)

    def arch(self):
        def fin():
            def collision():
                r.remove()
                r.location.attack.register(1, r.pos, delay=0, chance=r.chance, type='batter', faction=r.faction)
            r = Stock.make('Arrow', self.host.get_interact_pos())
            r.faction = self.host.faction
            r.shoot(dest.x, dest.y)
            r.on_collide = collision
            self.host.weapon.rotation = orig_rot
        orig_rot = self.host.weapon.rotation
        self.host.weapon.rotation = 0
        self.exert(2, self.host.weapon.weight)
        dest = self.host.next_target
        self.host.form.rotate_appendage(33, 0, self.host.next_target)
        self.host.form.rotate_appendage(34, 0, self.host.next_target)
        self.on_finish = fin
        self.make(turn=7)

    def power(self):
        if self.host.var['power'] == 'Thief' and Global.player.stamina(3):
            def fin():
                from src.entity.unit.Humanoid import Humanoid
                for thing in self.host.get_interact_pos().things:
                    if isinstance(thing, Humanoid):
                        item = thing.armor.get_item(0)
                        if item:
                            item.on_equip(self.host)
            self.on_finish = fin
            self.make(animation='cast', turn=4)
        elif self.host.var['power'] == 'Summoner' and self.host.is_armed() and Global.player.stamina(1):
            def fin():
                phantom = Stock.make('Phantom', self.host.get_interact_pos())
                phantom.form.organs[0].set(self.host.weapon.form)
                phantom.durability = self.host.weapon.durability
                phantom.attributes.strength = self.host.weapon.durability
                phantom.loot = self.host.weapon.loot
                phantom.faction = self.host.faction
                self.host.weapon.loot = []
                phantom.states.add('Sick', 80)
                self.host.weapon.die()
            self.on_finish = fin
            self.make(animation='cast', turn=4)
        elif self.host.var['power'] == 'Necromancer' and Global.player.stamina(1):
            def fin():
                def casting():
                    if channel.effect(5):
                        Effect.make('portal', target.get_center(), offset=0)
                    total = 0
                    if channel.frame == 38:
                        for thing in target.things:
                            if thing.name == 'Corpse':
                                total += thing.durability
                    if total > 1:
                        r = Stock.make('Undead', target)
                        r.faction = self.host.faction
                        r.durability = total * 2
                        r.attributes.strength = total
                    else:
                        Effect.make('zwip', target.get_center(), offset=0)
                channel = self.host.states.add('Channel', 40)
                channel.on_update = casting
                target = self.host.get_target_tile()
                aoe = self.host.location.get_area(target, 2, 2)
                for tile in aoe:
                    corpses = []
                    for thing in tile.things:
                        if thing.name == 'Corpse':
                            corpses.append(thing)
                            thing.gravity = 0
                            thing.states.add('Banish', 40)
                            thing.move(target.x - thing.pos.x, target.y - thing.pos.y)
            self.on_finish = fin
            self.make(animation='cast', turn=4)
        elif self.host.var['power'] == 'Druid':
            def fin():
                from src.entity.unit.Humanoid import Humanoid
                for thing in self.host.get_interact_pos().things:
                    if isinstance(thing, Humanoid):
                        item = thing.armor.get_item(0)
                        if item:
                            item.on_equip(self.host)
            self.on_finish = fin
            self.make(animation='cast', turn=4)
