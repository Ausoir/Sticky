import random

from src.entity.Particle import Particle
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.map.Tile import Tile


class Actions:
    default = ['idle', 'left', 'right', 'up', 'down', 'fall' 'walk', 'hit', 'interact', 'use', 'attack',
               'pocket_1', 'pocket_2', 'pocket_3', 'pocket_4',
               'power_1', 'power_2', 'power_3', 'power_4', 'trinket']
    priority = ['fall', 'hit']

    def __init__(self, host):
        self.host = host
        self.current_action = 'idle'
        self.current_action_fn = self.idle
        self.on_finish = None
        self.last_action = None
        self.skills = []

    def __str__(self):
        return ','.join(self.skills)

    def load(self, arg):
        for i in arg:
            self.skills.append(i)

    def attempt(self, action, idle=True):
        if action in Actions.default or action in self.skills:
            return self.set(action)
        elif idle:
            self.set('idle')

    def set(self, action):
        if self.host.attributes.is_exhausted() and action not in Actions.priority:
            action = 'rest'
        if self.current_action != action:
            frenzy = self.host.states.get('Frenzy')
            if frenzy and action not in Actions.priority:
                action = frenzy.var
            self.current_action = action
            self.current_action_fn = getattr(self, action)
        if self.on_finish:
            if self.host.delay:
                self.on_finish = None
            else:
                fn = self.on_finish  # prevent recursion
                self.on_finish = None
                fn()
        r = self.current_action_fn()
        self.last_action = action
        return r

    def set_animation(self, arg):
        if self.host.form.state_name != arg or self.host.form.animation_ended:
            self.host.form.set_state(arg)

    def make(self, animation=None, turn=0):
        if animation:
            self.set_animation(animation)
        else:
            self.set_animation(self.current_action)
        self.host.delay = turn

    @staticmethod
    def knockdown(victim):
        if isinstance(victim, Unit):
            if victim.action.current_action != 'fall':
                victim.action.set('fall')

    def idle(self):
        if self.last_action == 'idle':
            self.make(animation='standby', turn=0)
        else:
            self.make(turn=0)

    def wait(self):
        self.host.weapon.form.rotation = 20 * self.host.direction
        self.make(animation='block', turn=2)

    def offhand(self):
        self.host.swap()
        self.make(animation='block', turn=2)

    def rest(self):
        self.host.attributes.body = 0
        if self.host.states.get('Exhaustion'):
            self.make(turn=16)
        else:
            self.make(turn=5)

    def wield(self, pocket):
        if len(self.host.armor.pockets) > pocket:
            if self.host.is_armed():
                item = None
                pos = None
                if self.host.armor.pockets[pocket] != -1:
                    pos = self.host.armor.items[self.host.armor.pockets[pocket]].pos.to_list()
                    item = self.host.armor.get_item(self.host.armor.pockets[pocket])
                    weapon = self.host.weapon
                    item.on_equip(self.host)
                else:
                    weapon = self.host.weapon
                fit = False
                rows = [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]]
                for i in rows:
                    if self.host.armor.is_vacant(weapon, i[0], i[1]):
                        fit = True
                        self.host.drop()
                        self.host.armor.pockets[pocket] = self.host.armor.add_inventory(weapon, i[0], i[1])
                        break
                if item:
                    if fit:
                        item.on_equip(self.host)
                    else:
                        self.host.armor.pockets[pocket] = self.host.armor.add_inventory(item, pos[0], pos[1])
                        weapon.on_equip(self.host)
            else:
                item = self.host.armor.get_item(self.host.armor.pockets[pocket])
                if item:
                    item.on_equip(self.host)
        self.make(animation='block', turn=2)

    def pocket_1(self):
        self.wield(0)

    def pocket_2(self):
        self.wield(1)

    def pocket_3(self):
        self.wield(2)

    def pocket_4(self):
        self.wield(3)

    def trinket(self):
        if self.host.is_headgeared():
            def fin():
                self.host.headgear.activate()
            self.on_finish = fin
            self.make(animation='cast', turn=4)

    def ability(self, arg):
        from src.entity.unit.AdvAction import AdvAction
        from src.entity.unit.Character import Character
        name = Character.get_var(self.host, arg)
        if name:
            ability = AdvAction.get(self.host, name.title())
            if ability and ability.is_valid():
                if self.host.stamina(ability.energy):
                    self.on_finish = ability.on_cast
                    ability.on_start()
                    self.make(animation=ability.animation, turn=ability.delay)

    def power_1(self):
        self.ability('power1')

    def power_2(self):
        self.ability('power2')

    def power_3(self):
        self.ability('power3')

    def power_4(self):
        self.ability('power4')

    def left(self):
        if self.host.direction != 1:
            self.host.face(1)
            self.make(turn=1, animation='idle')
        else:
            self.set('walk')

    def up(self):
        if self.host.direction != 2:
            self.host.face(2)
            self.make(turn=1, animation='idle')
        else:
            self.set('walk')

    def right(self):
        if self.host.direction != 3:
            self.host.face(3)
            self.make(turn=1, animation='idle')
        else:
            self.set('walk')

    def down(self):
        if self.host.direction != 4:
            self.host.face(4)
            self.make(turn=1, animation='idle')
        else:
            self.set('walk')

    def walk(self):
        front = self.host.get_front_tile(self.host.direction)
        if front.is_land(Tile.CHECK_FIRM):
            self.set('idle')
        else:
            for thing in front.things:
                if thing.faction == self.host.faction and isinstance(thing, Unit)\
                        and thing.action.current_action == 'idle':
                    thing.move(-self.host.direction, 0, flag=Tile.CHECK_FIRM)
                    self.host.move_toward(self.host.direction)
                    self.make(turn=max(0, 3 - self.host.attributes.speed))
                    return
            self.host.move_toward(self.host.direction)
            self.make(turn=max(0, 2 - self.host.attributes.speed))

    def hit(self):
        self.make(turn=2)

    def interact(self):
        self.make(turn=3)
        if not self.host.is_armed():
            from src.entity.unit.item.Item import Item
            for thing in reversed(self.host.get_target_tile().things):
                if isinstance(thing, Item):
                    thing.on_equip(self.host)
                    return
        else:
            self.host.drop()

    def fall(self):
        def fin():
            for thing in self.host.pos.things:
                if thing != self.host and isinstance(thing, Unit):
                    thing.move(self.host.direction, 0)
                    self.knockdown(thing)
        self.on_finish = fin
        self.make(turn=11)

    def block(self):
        self.host.weapon.form.rotation = 20 * self.host.direction
        self.make(turn=1)

    def peek(self):
        def fin():
            self.host.center_camera()
        self.on_finish = fin
        prof = self.host.get_proficiency('peek') * 7 + 1
        new_pos = self.host.location.collide_land(self.host.pos, self.host.next_target.x, self.host.next_target.y,
                                                  distance=prof, flag=Tile.CHECK_LARGE)
        from src.game.TempObject import TempObject
        viewer = TempObject(new_pos)
        from src.game.Camera import Camera
        Camera.target = viewer
        self.make(animation='idle', turn=1)

    def use(self):
        self.host.use()

    def attack(self):
        def callback(target):
            self.host.states.trigger(['attack', target])
        self.host.attributes.body += 1
        front = self.host.get_offset_tile(self.host.direction, 0)
        chance = self.host.get_proficiency('attack') + 1
        damage = self.host.get_proficiency('damage') + 1
        self.host.location.attack.register(damage, front, hitter=self.host, delay=0, chance=chance, callback=callback)
        self.make(animation='attack', turn=4)

    def swing(self):
        self.host.attributes.body += self.host.weapon.weight
        if self.host.is_armed():
            self.host.weapon.rotation = 40
        self.host.weapon.attack(self.host.get_proficiency('attack'))
        self.make(animation='slash', turn=self.host.weapon.speed)

    def leap(self):
        if not self.host.attributes.exert(1, 6):
            degree = self.host.next_target.get_atan()
            from src.tools.Math import Math
            prof = self.host.get_proficiency('leap') * 2 + 2.4
            self.host.move(round(Math.cos(degree) * prof), round(Math.sin(degree) * prof))
            self.make(animation='jump', turn=3)

    def lunge(self):
        if not self.host.attributes.exert(1, 3):
            def hit(victim):
                victim.move(self.host.direction, 0)
                self.knockdown(victim)
            self.host.attributes.body += self.host.weapon.weight + 1
            self.host.weapon.rotation = 15
            self.host.move(self.host.direction, 0)
            rand = random.randint(-12, 12)
            prof = self.host.get_proficiency('lunge') * 2
            self.host.weapon.attack(delay=2, chance=prof, callback=hit)
            self.make(turn=2 + self.host.weapon.speed - prof)

    def tackle(self):
        def hit(victim):
            if isinstance(victim, Unit):
                victim.move(self.host.direction, 0)
                self.knockdown(victim)
                victim.states.add('Cripple', 40, var=1)
        if not self.host.attributes.exert(1, 6):
            self.host.location.sound.register(self.host.pos, 5)
            self.host.move(self.host.direction, 0)
            prof = self.host.get_proficiency('tackle') + 1
            self.host.location.attack.register(0, self.host.get_offset_tile(self.host.direction, 0), delay=0,
                                               chance=prof, hitter=self.host, callback=hit)
            self.host.move(self.host.direction, 0, flag=Tile.CHECK_FIRM)
            self.make(animation='kick', turn=3)
            return True

    def slam(self):
        if not self.host.attributes.exert(1, 9):
            self.host.location.sound.register(self.host.pos, 9)
            self.host.attributes.body += self.host.weapon.weight + 2
            self.host.weapon.rotation = 10
            self.host.weapon.attack(chance=2, delay=5)
            self.host.weapon.attack(chance=2, delay=5)
            if self.host.get_proficiency('slam'):
                self.host.weapon.attack(chance=2, delay=5)
            self.make(turn=7)
            return True
        else:
            self.make(animation='rest', turn=2)

    def charge(self):
        def hit(victim):
            from src.game.Tags import Tags
            if Tags.back not in victim.tags:
                victim.move(self.host.direction * 2, 0)
            if isinstance(victim, Unit):
                self.knockdown(victim)
                victim.states.add('Cripple', 40, var=1)
        frenzy = self.host.states.get('Influence')
        if not frenzy:
            if not self.host.attributes.exert(1, 3):
                self.host.states.add('Influence', 12, var='charge')
                self.host.states.add('Effect', 12, var='spin')
            else:
                self.make(animation='rest', turn=2)
        else:
            prof = 1 - self.host.get_proficiency('charge')
            self.host.attributes.exert(1, 1 + prof)
            self.host.location.sound.register(self.host.pos, 7)
            self.host.location.attack.register(0, self.host.get_offset_tile(self.host.direction, 0), delay=0,
                                               hitter=self.host, callback=hit)
            if self.host.pos == self.host.move(self.host.direction, 0, flag=Tile.CHECK_FIRM):
                self.host.location.attack.register(1, self.host.pos, delay=0,
                                                   hitter=self.host, callback=hit)
                frenzy.end()
                self.host.action.set('fall')
            else:
                self.make(turn=0)

    def arch(self):
        def fin():
            def check_collision():
                col = r.pos.is_land(Tile.CHECK_FIRM)
                if not col:
                    for i in r.pos.things:
                        if isinstance(i, Unit) and i.faction != r.faction:
                            return True
                return col

            def collision():
                r.remove()
                r.location.attack.register(rating, r.pos, delay=0, chance=rating, hitter=self.host, faction=r.faction)
            r = Stock.make('Arrow', self.host.get_front_tile())
            r.faction = self.host.faction
            r.shoot(dest.x, dest.y)
            r.is_collide = check_collision
            r.on_collide = collision
            self.host.weapon.rotation = orig_rot
        rating = 1 + self.host.get_proficiency('bow')
        orig_rot = self.host.weapon.rotation
        self.host.weapon.rotation = 0
        self.host.attributes.exert(0, self.host.weapon.weight)
        dest = self.host.next_target
        self.on_finish = fin
        self.make(turn=9)

    def shoot(self):
        def fin():
            def check_collision():
                col = r.pos.is_land(Tile.CHECK_FIRM)
                if not col:
                    for i in r.pos.things:
                        if isinstance(i, Unit) and i.faction != r.faction:
                            return True
                return col

            def collision():
                r.remove()
                r.location.attack.register(3, r.pos, delay=0, chance=20, hitter=self.host, faction=r.faction)
                Particle.make('slash', r.vec)
            r = Stock.make('Bullet', self.host.get_front_tile())
            r.gravity = False
            r.friction = 1
            r.lifetime = 10
            r.faction = self.host.faction
            r.shoot(dest.x, dest.y)
            r.is_collide = check_collision
            r.on_collide = collision
            self.host.weapon.rotation = orig_rot
        rating = 7 - (self.host.get_proficiency('gun') * 3)
        orig_rot = self.host.weapon.rotation
        self.host.weapon.rotation = 0
        self.host.attributes.exert(0, self.host.weapon.weight)
        dest = self.host.next_target
        self.on_finish = fin
        self.make(animation='block', turn=rating)
