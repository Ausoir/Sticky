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
    def knockdown(victim, time, push=None):
        from src.entity.unit.item.Item import Item
        if isinstance(victim, Item):
            if victim.host:
                victim = victim.host
        if isinstance(victim, Unit):
            if victim.get_skill('constitution'):
                victim.action.hit()
            else:
                if push:
                    victim.action.move(push, check=victim.collision_type + 2)
                if victim.action.current_action != 'fall':
                    victim.action.fall()
                victim.action.delay = max(victim.action.delay, time)
            return True

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
        if self.host.tags.get('spd', 0) > 0:
            speed = 0
        else:
            speed = 1
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
        if front:
            solid = front.get_solidity()
            if solid >= self.host.collision_type:
                if self.host.get_skill('parkour') and self.parkour(front):
                    return
                elif self.interact_on(front, self.host.collision_type):
                    return
                elif self.host.get_skill('side step') and self.side_step(front):
                    return
            else:
                self.move(front)

    def move(self, front, check=10):
        solidity = front.get_solidity()
        if solidity < check:
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
                    self.host.pos.location.sound.register(self.host.pos, sound, file='step', priority=4)
                self.host.relocate(to=front)
                self.host.states.trigger(['act', 'move'])
                from src.map.Tile import Tile
                if solidity == Tile.COLLIDE_UNIT:
                    for i in self.host.pos.things:
                        if i != self.host and self.host.obstruct_type >= Tile.COLLIDE_UNIT and isinstance(i, Unit):
                            i.action.knockdown(i, 4)
                return True
            else:
                self.idle()

    def interact_on(self, tile, col=0):
        if self.host == Global.player.character and self.humanoid:
            self.host.pos.location.sound.register(self.host.pos, 1)
            for thing in tile.things:
                if thing != self.host.weapon and thing.obstruct_type >= col and self.interact(thing):
                    return True

    def interact(self, target):
        def fn():
            Script.var['host'] = self.host
            Script.var['menu'] = target
            Script.var['1'] = target
            Script.execute_code(code)
        code = target.tags.get('#')
        if code:
            self.make('interact', turn=1)
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

    def parkour(self, tile):
        if tile.get_yield() > -8:
            for thing in tile.things:
                if not isinstance(thing, Unit) and thing.obstruct_type <= 4:
                    if self.host.states.get('Concentration'):
                        old = thing.pos
                        self.move(old)
                        self.make('fly', turn=self.delay + 2)
                        return True

    def fall(self):
        self.make('fall', turn=0)
        self.on_finish = self.stand

    def hit(self):
        self.make('idle', turn=4)
        self.host.form.randomize_once(4)

    def stand(self):
        for i in self.host.pos.things:
            if i != self.host and isinstance(i, Unit):
                self.knockdown(i, 2, push=i.pos.get_cardinal(i.direction))

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
                    if not thing.host:
                        targets.append(thing)
            if targets:
                self.make('grab', turn=2)
                if len(targets) > 1 and self.host == Global.player.character:
                    Global.menu.var = targets
                    Global.menu.direct(Global.menu.menu_pickup)
                    Global.player.control.clear_press()
                else:
                    self.host.pick_up(targets[0])
            elif not self.interact_on(self.host.pos):
                self.make('grab', turn=1)
                self.host.drop()

    def sheathe(self):
        if self.humanoid:
            if self.host.weapon:
                def change():
                    weapon = self.host.weapon
                    self.host.unsheathe(0)
                    if weapon:
                        self.host.inventory.add_item(weapon, insert=True)
                self.make('grab', turn=2)
                self.on_finish = change
            else:
                self.host.unsheathe(0)

    def attack(self):
        self.host.states.trigger(['act', 'attack'])
        for i in range(self.host.get_skill('lunge')):
            front = self.host.pos.get_cardinal(self.host.direction, 1)
            self.move(front, self.host.collision_type)
        atk_spd = self.host.get_skill('deft')
        self.host.form.animation_ended = 1
        reach = self.host.get_skill('reach')
        if reach > 0:
            front = self.host.pos.get_cardinal(self.host.direction, 1 + reach)
            land = self.host.pos.location.collide_land(self.host.pos, front, flag=self.host.collision_type + 2,
                                                       return_prev=False)
            if front != land:
                front = self.host.pos.get_cardinal(self.host.direction, 1)
        else:
            front = self.host.pos.get_cardinal(self.host.direction, 1)
        dmg = self.host.get_damage()
        if self.humanoid and not self.host.weapon:
            motion = 'kick'
        else:
            motion = 'attack'
        self.make(motion, turn=6 - atk_spd)
        self.host.pos.location.field.register(dmg, front, delay=1 - self.host.get_skill('instinct'), hitter=self.host,
                                              sound=['swing', 0], callback=self.host.on_attack)
        if self.host.get_skill('crush') and dmg > front.get_hardness():
            self.on_finish = self.crush

    def crush(self):
        front = self.host.pos.get_cardinal(self.host.direction, 1)
        if front.get_yield() == -10:
            if self.host == Global.player.character:
                self.host.tags.increment('hunger', 1000)
            self.host.pos.location.sound.register(self.host.pos, 16, file='critical')
            front.set_terrain('.')
            front.connect_connect()
            front.update_update_shader()

    def ability(self, ability):
        if ability:
            exhaustion = self.host.states.get('Exhaustion')
            if not exhaustion:
                from src.entity.unit.item.Spell import Spell
                spell = Spell.get(ability)
                cooldown = spell.get_cooldown()
                cdr = self.host.tags.get('cdr', 0) + 1
                if cdr > 1:
                    cooldown = int(cooldown / cdr)
                elif cdr <= 0:
                    cooldown = cooldown * (-cdr + 2)
                if cooldown > 0:
                    self.host.states.add('Exhaustion', cooldown)
                spell.cast(self.host)
            elif self.host == Global.player.character:
                from src.tools.Dialog import Dialog
                Global.main.monologue.set(Dialog.get(':wait', [exhaustion.duration]), time=20)

    def ability1(self):
        self.ability(self.host.tags.get('ab1'))

    def ability2(self):
        self.ability(self.host.tags.get('ab2'))

    def ability3(self):
        self.ability(self.host.tags.get('ab3'))
