from src.entity.Particle import Particle
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.map.Tile import Tile


class Actions:
    default = ['idle', 'left', 'right', 'up', 'down', 'fall', 'walk', 'grab', 'use', 'attack',
               'click', 'power_1', 'power_2', 'power_3', 'power_4', 'trinket']
    priority = ['fall']

    def __init__(self, host):
        self.host = host
        self.current_action = 'idle'
        self.current_action_fn = self.idle
        self.on_finish = None
        self.last_action = None
        self.skills = []
        self.frame = 0

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
        if self.current_action != action:
            if self.host.delay > 0:
                self.host.location.attack.unregister(self.host.get_hitter())
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
            self.frame = 0
        else:
            self.frame += 1
        r = self.current_action_fn()
        self.last_action = action
        return r

    def set_animation(self, arg):
        if self.host.form.state_name != arg or self.host.form.animation_ended:
            self.host.form.set_state(arg)

    def make(self, animation, turn=0):
        self.set_animation(animation)
        self.host.delay = turn

    @staticmethod
    def knockdown(victim):
        if isinstance(victim, Unit):
            if victim.action.current_action != 'fall':
                victim.action.set('fall')

    def idle(self):
        if self.last_action == 'idle':
            self.make('standby', turn=0)
        else:
            self.make('idle', turn=0)

    def wait(self):
        self.make('idle', turn=2)

    def trinket(self):
        if self.host.headgear:
            def fin():
                self.host.headgear.activate()
            self.on_finish = fin
            self.make('cast', turn=4)

    def ability(self, arg):
        from src.entity.unit.AdvAction import AdvAction
        name = self.host.get_tag(self.host, arg)
        if name:
            ability = AdvAction.get(self.host, name.title())
            if ability and ability.is_valid():
                if self.host.stamina(ability.energy):
                    self.on_finish = ability.on_cast
                    ability.on_start()
                    self.make(ability.animation, turn=ability.delay)

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
            self.make('idle', turn=1)
        else:
            self.set('walk')

    def up(self):
        if self.host.direction != 2:
            self.host.face(2)
            self.make('idle', turn=1)
        else:
            self.set('walk')

    def right(self):
        if self.host.direction != 3:
            self.host.face(3)
            self.make('idle', turn=1)
        else:
            self.set('walk')

    def down(self):
        if self.host.direction != 4:
            self.host.face(4)
            self.make('idle', turn=1)
        else:
            self.set('walk')

    def walk(self):
        front = self.host.get_front_tile(self.host.direction)
        if front.is_land(Tile.CHECK_FIRM):
            from src.game.Script import Script
            from src.game import Global
            if self.host == Global.player.character:
                for thing in front.things:
                    code = thing.tags.get('#')
                    if code:
                        Script.execute_code(code, host=thing)
                        self.make('interact', turn=3)
                        return
            self.set('idle')
        else:
            speed = self.host.states.get('Speed')
            if not speed or speed.var != 0:
                if self.host.move_toward(self.host.direction):
                    self.host.location.sound.register(self.host.pos, 2, file='step')
                    if speed:
                        self.make('walk', turn=max(0, 2 - speed.var))
                    else:
                        self.make('walk', turn=max(0, 2))

    def fall(self):
        self.make('fall', turn=11)

    def block(self):
        self.host.weapon.form.rotation = 20 * self.host.direction
        self.make('block', turn=1)

    def peek(self):
        def fin():
            self.host.center_camera()
        self.on_finish = fin
        prof = self.host.get_proficiency('peek') * 7 + 1
        new_pos = self.host.location.collide_land(self.host.pos, self.host.next_target.x, self.host.next_target.y,
                                                  distance=prof, flag=Tile.CHECK_FIRM)
        from src.game.TempObject import TempObject
        viewer = TempObject(new_pos)
        from src.game.Camera import Camera
        Camera.target = viewer
        self.make('idle', turn=1)

    def click(self):
        from src.game import Global
        x_diff = Global.player.control.cursor_tile[0] - self.host.pos.x
        y_diff = Global.player.control.cursor_tile[1] - self.host.pos.y
        if x_diff == y_diff == 0:
            Global.menu.toggle()
        elif self.host.get_front_tile(self.host.direction).to_list() == Global.player.control.cursor_tile:
            self.host.use()
        elif abs(x_diff) > abs(y_diff):
            if x_diff < 0:
                self.set('left')
            else:
                self.set('right')
        else:
            if y_diff < 0:
                self.set('up')
            else:
                self.set('down')

    def use(self):
        self.host.use()

    def grab(self):
        from src.entity.unit.item.Item import Item
        target = None
        for thing in reversed(self.host.pos.things):
            if isinstance(thing, Item):
                target = thing
                break
        if target:
            self.make('grab', turn=3)
            if self.host.is_armed():
                self.host.inventory.attempt_add(target)
            else:
                target.on_equip(self.host)
        else:
            self.host.drop()
            self.make('grab', turn=1)

    def attack(self):
        def callback(target):
            self.host.states.trigger(['attack', target])
        front = self.host.get_front_tile(self.host.direction)
        damage = self.host.get_proficiency('damage') + 1
        self.host.location.attack.register(damage, front, hitter=self.host, delay=0, callback=callback)
        self.make('attack', turn=4)

    def swing(self):
        speed = self.host.states.get('Speed')
        if speed:
            slow = max(0, 2 - speed.var)
        else:
            slow = 2
        self.make('swing', turn=8 + slow)
        self.host.form.timer.set(slow * 4 + 4)
        self.host.weapon.attack(damage=self.host.tags.get('strength', 0), delay=slow)

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
                r.location.attack.register(rating, r.pos, delay=0, hitter=self.host, faction=r.faction)
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
        self.make('arch', turn=9)

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
                r.location.attack.register(3, r.pos, delay=0, hitter=self.host, faction=r.faction)
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
        self.make('block', turn=rating)
