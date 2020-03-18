from src.entity.Stock import Stock, Global
from src.entity.unit.Unit import Unit
from src.map.Tile import Tile


class Actions:
    basic = ['idle', 'left', 'right', 'up', 'down', 'fall', 'walk', 'use', 'attack', 'click']
    priority = ['fall']

    def __init__(self, host):
        self.host = host
        self.humanoid = False
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
                if fn():
                    return True
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
            if victim.action.current_action != 'fall' and not victim.get_skill('toughness'):
                victim.action.set('fall')
                if time:
                    victim.action.delay = time

    def idle(self):
        if self.last_action == 'idle':
            if self.frame % 18 == 17:
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
            self.make('eat', turn=4)
            self.on_finish = fin

    def turn_direction(self, direction):
        speed = min(1, max(0, 3 - self.host.tags.get('spd', 0)))
        self.make('idle', turn=speed)
        self.host.face(direction)

    def left(self):
        if self.host.direction != 1:
            self.turn_direction(1)
        else:
            self.set('walk')

    def up(self):
        if self.host.direction != 2:
            self.turn_direction(2)
        else:
            self.set('walk')

    def right(self):
        if self.host.direction != 3:
            self.turn_direction(3)
        else:
            self.set('walk')

    def down(self):
        if self.host.direction != 4:
            self.turn_direction(4)
        else:
            self.set('walk')

    def walk(self):
        front = self.host.get_front_tile(self.host.direction)
        if not front:
            on_edge = self.host.location.tags.get('edge')
            if on_edge:
                from src.game.Script import Script
                Script.execute_code(on_edge, host=self.host)
            else:
                self.idle()
        elif front.is_land(self.host.collision_type):
            from src.game.Script import Script
            if self.host == Global.player.character:
                for thing in front.things:
                    code = thing.tags.get('#')
                    if code:
                        self.make('interact', turn=3)
                        Script.execute_code(code, host=thing, var=self.host)
                        return
            if self.host.get_skill('side step'):
                if front.is_land([Tile.COLLIDE_UNIT]):
                    for thing in front.things:
                        if isinstance(thing, Unit) and thing.action.delay == 0:
                            concentration = self.host.states.get('Concentration')
                            if concentration:
                                concentration.trigger(['spend'])
                                old = thing.pos
                                thing.relocate(self.host.pos.x, self.host.pos.y)
                                Actions.knockdown(thing, 12)
                                from src.tools import Direction
                                toward = Direction.get_direction_toward((old - self.host.pos).to_list())
                                self.host.move_toward(toward)
                                speed = self.host.tags.get('spd', 0)
                                if front.speed > -10 and not self.host.tags.get('fly'):
                                    speed += front.speed
                                self.make('walk', turn=max(0, 4 - speed))
                                return
            self.idle()
        else:
            speed = self.host.tags.get('spd', 0)
            fly = self.host.tags.get('fly')
            if front.speed > -10 and not fly:
                speed += front.get_speed()
            if speed > -10:
                if self.host.move_toward(self.host.direction):
                    self.make('walk', turn=max(0, 2 - speed))
                    if not fly:
                        self.host.location.sound.register(self.host.pos, 0, file='step')
                self.host.states.trigger(['act', 'move'])

    def fall(self):
        def rise():
            self.host.obstruct_type = t
            self.host.collision_type = t2
            for i in self.host.pos.things:
                if i != self.host and i.obstruct_type in self.host.collision_type:
                    i.move_toward(self.host.direction)
                    Actions.knockdown(i, 8)
        t = self.host.obstruct_type
        t2 = self.host.collision_type
        self.host.obstruct_type = 4
        self.host.collision_type = Tile.CHECK_FIRM
        self.on_finish = rise
        self.make('fall', turn=18)

    def click(self):
        x_diff = Global.player.control.cursor_tile[0] - self.host.pos.x
        y_diff = Global.player.control.cursor_tile[1] - self.host.pos.y
        front = self.host.get_front_tile(self.host.direction)
        if x_diff == y_diff == 0:
            Global.menu.toggle()
        elif front and front.to_list() == Global.player.control.cursor_tile:
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
        for thing in self.host.pos.things:
            if isinstance(thing, Item):
                if thing not in [self.host.weapon, self.host.headgear, self.host.armor]:
                    target = thing
                    break
        if target:
            self.make('grab', turn=3)
            if self.host.weapon:
                self.host.inventory.attempt_add(target)
            else:
                if self.host.inventory.is_vacant(target.get_weight()):
                    target.on_wield(self.host)
                else:
                    from src.tools.Dialog import Dialog
                    params = [self.host.inventory.get_weight(), self.host.inventory.get_capacity(), target.get_weight()]
                    Global.main.monologue.set(Dialog.get('!heavy', params))
        else:
            self.make('grab', turn=1)
            self.host.drop()

    def crush(self):
        front = self.host.get_front_tile(self.host.direction)
        if front.speed == -10:
            self.host.location.sound.register(self.host.pos, 16, file='critical')
            front.set_terrain('.')
            front.update_update_shader()

    def attack(self):
        speed = self.host.tags.get('spd', 0) + self.host.get_attack_speed()
        self.make('attack', turn=max(6, 10 - speed))
        slow = max(0, 1 - speed)
        dmg = self.host.roll_damage()
        front = self.host.get_front_tile(self.host.direction)
        hitter = self.host.get_hitter()
        self.host.location.field.register(dmg, front, hitter=hitter, delay=slow, sound=['swing', 0],
                                          callback=self.host.on_attack)
        self.host.form.timer.set(slow * 4 + 4)
        if self.host.get_skill('crush') and dmg > 6:
            self.on_finish = self.crush

    def kick(self):
        self.attack()
        time = self.host.form.timer.time
        self.host.form.set_state('kick')
        self.host.form.timer.set(time)

    def arch(self):
        def fin():
            def check_collision():
                ob = r.pos.is_land(Tile.CHECK_SOLID)
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
        self.host.attributes.exert(0, self.host.weapon.get_weight())
        dest = self.host.next_target
        self.on_finish = fin
