from src.entity.Stock import Stock, Global
from src.entity.unit.Unit import Unit
from src.map.Tile import Tile


class Actions:
    basic = ['idle', 'left', 'right', 'up', 'down', 'fall', 'walk', 'use', 'attack', 'click']
    priority = ['fall']

    def __init__(self, host):
        self.host = host
        from src.entity.unit.Humanoid import Humanoid
        self.humanoid = isinstance(self.host, Humanoid)
        self.current_action = 'idle'
        self.current_action_fn = self.idle
        self.on_finish = None
        self.last_action = None
        self.delay = 0
        self.frame = 0

    def attempt(self, action):
        if self.humanoid or action in Actions.basic:
            return self.set(action)
        else:
            self.set('idle')

    def set(self, action):
        if self.current_action != action:
            if self.delay > 0:
                self.host.location.field.unregister(self.host.get_hitter())
            self.current_action = action
            self.current_action_fn = getattr(self, action)
            self.frame = 0
        else:
            self.frame += 1
        if self.on_finish:
            if self.delay:
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

    def make(self, animation, turn=0):
        self.set_animation(animation)
        self.delay = turn

    @staticmethod
    def knockdown(victim, time=None):
        if isinstance(victim, Unit):
            if not victim.get_skill('toughness'):
                victim.action.set('fall')
                if time:
                    victim.action.delay = time

    def idle(self):
        if self.last_action == 'idle':
            if self.frame == 18:
                self.make('standby', turn=0)
                self.host.states.add('Concentration', -1)
        else:
            self.make('idle', turn=0)

    def nothing(self):
        pass

    def act(self, action, time):
        self.set('nothing')  # calls the set function
        self.make(action, turn=time)

    def trinket(self):
        if self.host.headgear:
            def fin():
                self.host.headgear.activate()
            self.make('cast', turn=4)
            self.on_finish = fin

    def power_1(self):
        pass
        # self.ability('power1')

    def left(self):
        if self.host.direction != 1:
            self.make('idle', turn=1)
            self.host.face(1)
        else:
            self.set('walk')

    def up(self):
        if self.host.direction != 2:
            self.make('idle', turn=1)
            self.host.face(2)
        else:
            self.set('walk')

    def right(self):
        if self.host.direction != 3:
            self.make('idle', turn=1)
            self.host.face(3)
        else:
            self.set('walk')

    def down(self):
        if self.host.direction != 4:
            self.make('idle', turn=1)
            self.host.face(4)
        else:
            self.set('walk')

    def walk(self):
        front = self.host.get_front_tile(self.host.direction)
        if not front:
            self.idle()
        elif front.is_land(self.host.collision_type):
            from src.game.Script import Script
            if self.host == Global.player.character:
                for thing in front.things:
                    code = thing.tags.get('#')
                    if code:
                        self.make('interact', turn=3)
                        Script.execute_code(code, host=thing)
                        return
            self.idle()
        else:
            speed = self.host.tags.get('spd', 0)
            speed += front.type
            if speed > -10:
                if self.host.move_toward(self.host.direction):
                    self.make('walk', turn=max(0, 2 - speed))
                    self.host.location.sound.register(self.host.pos, 0, file='step')
                    invis = self.host.states.get('Invisible')
                    if invis:
                        invis.trigger(['move'])

    def fall(self):
        def rise():
            self.host.obstruct_type = t
        t = self.host.obstruct_type
        self.host.obstruct_type = 4
        self.on_finish = rise
        self.make('fall', turn=18)

    def peek(self):
        def fin():
            self.host.center_camera()
        self.make('idle', turn=1)
        self.on_finish = fin
        new_pos = self.host.location.collide_land(self.host.pos, self.host.next_target.x, self.host.next_target.y,
                                                  distance=1, flag=Tile.CHECK_FIRM)
        from src.game.TempObject import TempObject
        viewer = TempObject(new_pos)
        from src.game.Camera import Camera
        Camera.target = viewer

    def click(self):
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
        self.host.states.trigger(['act', 'use'])
        self.host.use()

    def grab(self):
        self.host.states.trigger(['act', 'grab'])
        from src.entity.unit.item.Item import Item
        target = None
        for thing in reversed(self.host.pos.things):
            if isinstance(thing, Item):
                if thing not in [self.host.weapon, self.host.headgear, self.host.armor]:
                    target = thing
                    break
        if target:
            self.make('grab', turn=3)
            if self.host.weapon:
                self.host.inventory.attempt_add(target)
            else:
                if self.host.inventory.is_vacant(target.weight):
                    target.on_wield(self.host)
                else:
                    from src.tools.Dialog import Dialog
                    Global.main.monologue.set(Dialog.get('!heavy'))
        else:
            self.make('grab', turn=1)
            self.host.drop()

    def attack(self):
        speed = self.host.tags.get('spd', 0) + self.host.get_attack_speed()
        self.make('attack', turn=max(6, 10 - speed))
        slow = max(0, 1 - speed)
        dmg = self.host.roll_damage()
        front = self.host.get_front_tile(self.host.direction)
        hitter = self.host.get_hitter()
        self.host.location.field.register(dmg, front, hitter=hitter, delay=slow,
                                   sound=['swing', 0], callback=self.host.on_attack)
        self.host.form.timer.set(slow * 4 + 4)

    def arch(self):
        def fin():
            def check_collision():
                ob = r.pos.is_land(Tile.CHECK_FIRM)
                if not ob:
                    for i in r.pos.things:
                        if isinstance(i, Unit):
                            return True
                return ob

            def collision():
                r.remove()
                r.location.field.register(rating, r.pos, delay=0, hitter=self.host, faction=r.faction)
            r = Stock.make('Arrow', self.host.get_front_tile())
            r.faction = self.host.faction
            r.shoot(dest.x, dest.y)
            r.is_collide = check_collision
            r.on_collide = collision
            self.host.weapon.rotation = orig_rot
        self.make('arch', turn=9)
        rating = 1 + self.host.get_skill('bow')
        orig_rot = self.host.weapon.rotation
        self.host.weapon.rotation = 0
        self.host.attributes.exert(0, self.host.weapon.weight)
        dest = self.host.next_target
        self.on_finish = fin

    def cast(self):
        self.make('cast', turn=12)
