from src.entity.Stock import Global
from src.entity.unit.Unit import Unit
from src.game.Script import Script


class Actions:
    def __init__(self, host):
        self.host = host
        self.humanoid = False
        self.current_action = None
        self.current_action_fn = self.idle
        self.on_finish = None
        self.last_action = None
        self.delay = 0
        self.idle_frame = 0

    def set(self, action):
        if self.current_action != action:
            self.idle_frame = 0
            if self.delay > 0:
                self.host.location.field.unregister(self.host.get_hitter())
            self.current_action = action
            self.current_action_fn = getattr(self, action)
        if self.on_finish:
            if self.delay:
                self.on_finish = None
            else:
                fn = self.on_finish  # prevent recursion
                self.on_finish = None
                if fn():
                    return True
        self.current_action_fn()
        self.last_action = action

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
                victim.action.fall()
                if time:
                    victim.action.delay = time

    def idle(self):
        if self.idle_frame >= 12:
            self.idle_frame = 0
            self.host.states.add('Concentration', -1)
        else:
            self.idle_frame += 1
        self.make('idle', turn=0)

    def nothing(self):
        pass

    def act(self, action, time):
        self.set('nothing')  # calls the set function
        self.make(action, turn=time)

    def turn_direction(self, direction):
        speed = min(1, max(0, 3 - self.host.tags.get('spd', 0)))
        self.make('default', turn=speed)
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
        if self.host.direction != 0:
            self.turn_direction(0)
        else:
            self.set('walk')

    def walk(self):
        front = self.host.pos.get_cardinal(self.host.direction, 1)
        if not front:
            on_edge = self.host.location.tags.get('edge')
            if on_edge:
                Script.var['host'] = self.host
                Script.execute_code(on_edge)
            else:
                self.idle()
        else:
            solid = front.get_solidity()
            if solid >= self.host.collision_type:
                if self.interact_on(front):
                    return
                team = self.host.get_team()
                for thing in front.things:
                    if thing in team:
                        Script.var['host'] = thing
                        Script.var['1'] = self.host
                        Script.execute_code('#push')
                        return
                if self.host.get_skill('side step'):
                    if self.side_step(front):
                        return
                if self.host.tags.get('fly', 0) == 0:
                    self.idle()
                else:
                    self.move(front)
            else:
                self.move(front)

    def move(self, front):
        speed = self.host.tags.get('spd', 0)
        fly = self.host.tags.get('fly', 0)
        if front.get_yield() > -10 and fly == 0:
            speed += front.get_move_speed()
        if speed > -10:
            if fly:
                self.make('fly', turn=max(0, 2 - speed))
            else:
                self.make('walk', turn=max(0, 1 - speed))
                sound = max(0, -self.host.tags.get('sth', 0))
                self.host.location.sound.register(self.host.pos, sound, file='step', priority=4)
            self.host.destination = self.host.pos.get_cardinal(self.host.direction, 1)
            self.on_finish = self.finish_moving
            self.host.states.trigger(['act', 'move'])
            return True
        else:
            self.idle()

    def finish_moving(self):
        self.host.relocate(to=self.host.destination)
        return False

    def interact_on(self, tile):
        if self.host == Global.player.character:
            self.host.location.sound.register(self.host.pos, 1)
            for thing in tile.things:
                if thing != self.host.weapon and self.interact(thing):
                    return True

    def interact(self, target):
        def fn():
            Script.var['host'] = self.host
            Script.var['1'] = target
            Script.execute_code(code)
        code = target.tags.get('#')
        if code:
            self.make('interact', turn=3)
            self.on_finish = fn
            return True

    def side_step(self, tile):
        for thing in tile.things:
            if isinstance(thing, Unit) and thing.action.delay == 0:
                concentration = self.host.states.get('Concentration')
                if concentration:
                    concentration.trigger(['spend'])
                    old = thing.pos
                    thing.relocate(to=self.host.pos)
                    thing.states.add('Knockout', 20)
                    self.move(old)
                    return True

    def fall(self):
        self.make('fall', turn=18)

    def click(self):
        x_diff = Global.player.control.cursor_tile[0] - self.host.pos.x
        y_diff = Global.player.control.cursor_tile[1] - self.host.pos.y
        front = self.host.pos.get_cardinal(self.host.direction, 1)
        if x_diff == y_diff == 0:
            Script.execute_code('menu')
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
        self.host.use()

    def grab(self):
        if self.humanoid:
            self.host.states.trigger(['act', 'grab'])
            from src.entity.unit.item.Item import Item
            targets = []
            for thing in self.host.pos.things:
                if isinstance(thing, Item):
                    if thing not in [self.host.weapon, self.host.headgear, self.host.armor]:
                        targets.append(thing)
            if targets:
                self.make('grab', turn=3)
                if len(targets) > 1 and self.host == Global.player.character:
                    Global.menu.var = targets
                    Global.menu.direct(Global.menu.menu_pickup)
                else:
                    self.host.pick_up(targets[0])
            elif not self.interact_on(self.host.pos):
                self.make('grab', turn=1)
                self.host.drop()

    def sheathe(self):
        if self.host.weapon:
            def change():
                self.host.inventory.attempt_add(self.host.weapon, insert=True)
            self.make('grab', turn=4)
            self.on_finish = change
        else:
            self.host.unsheathe(0)

    def crush(self):
        front = self.host.pos.get_cardinal(self.host.direction, 1)
        if front.get_yield() == -10:
            self.host.location.sound.register(self.host.pos, 16, file='critical')
            front.set_terrain('.')
            front.connect_connect()
            front.update_update_shader()

    def attack(self):
        self.host.states.trigger(['act', 'attack'])
        self.make(self.host.get_attack_motion(), turn=5 + max(0, 2 + self.host.get_attack_speed()))
        dmg = self.host.roll_damage()
        front = self.host.pos.get_cardinal(self.host.direction, 1)
        hitter = self.host.get_hitter()
        if self.host.tags.get('spd', 0) > 0:
            delay = 0
        else:
            delay = 1
        self.host.location.field.register(dmg, front, delay=delay, hitter=hitter,
                                          sound=['swing', 0], callback=self.host.on_attack)
        if self.host.get_skill('crush') and dmg >= front.get_hardness():
            self.on_finish = self.crush

    def ability(self):
        ability = self.host.tags.get('abi')
        if ability:
            from src.entity.unit.item.Spell import Spell
            Spell.get(ability, power=self.host.tags.get('abp', 0)).cast(self.host)
            self.make('cast', turn=12)

    def ability2(self):
        ability = self.host.tags.get('abi2')
        if ability:
            from src.entity.unit.item.Spell import Spell
            Spell.get(ability, power=self.host.tags.get('abp2', 0)).cast(self.host)
            self.make('cast', turn=12)
