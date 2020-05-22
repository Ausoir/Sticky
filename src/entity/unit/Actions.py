from src.entity.Stock import Stock, Global
from src.entity.unit.Unit import Unit
from src.game.Script import Script
from src.map.Tile import Tile


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
        if self.idle_frame >= 20:
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

    def trinket(self):
        if self.humanoid and self.host.headgear:
            def fin():
                self.host.headgear.activate()
            self.make('eat', turn=6)
            self.on_finish = fin

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
        elif front.is_land(self.host.collision_type):
            if self.interact_on(front):
                return
            if front.is_land([Tile.COLLIDE_UNIT]):
                if self.host.get_skill('side step'):
                    self.side_step(front)
                    return
                else:
                    for thing in front.things:
                        if thing in self.host.get_team():
                            Script.var['host'] = thing
                            Script.var['1'] = self.host
                            Script.execute_code('#push')
                            return
            self.idle()
        else:
            self.move(front)

    def move(self, front):
        speed = self.host.tags.get('spd', 0)
        fly = self.host.tags.get('fly')
        if front.speed > -10 and not fly:
            speed += front.get_speed()
        if speed > -10:
            if fly:
                self.make('fly', turn=max(0, 2 - speed))
            else:
                self.make('walk', turn=max(0, 1 - speed))
                sound = max(0, -self.host.tags.get('sth', 0))
                self.host.location.sound.register(self.host.pos, sound, file='step', priority=4)
            self.host.destination = self.host.pos.get_cardinal(self.host.direction, 1)
            self.on_finish = lambda: self.host.move_line(self.host.pos.get_cardinal(self.host.direction))
            self.host.states.trigger(['act', 'move'])
        else:
            self.idle()

    def interact_on(self, tile):
        if tile.terrain == '~':
            Script.var['host'] = self.host
            Script.var['1'] = None
            Script.execute_code('#water')
        elif self.host == Global.player.character:
            for thing in tile.things:
                if self.interact(thing):
                    return True

    def interact(self, target):
        code = target.tags.get('#')
        if code:
            self.make('interact', turn=3)
            Script.var['host'] = self.host
            Script.var['1'] = target
            self.on_finish = lambda: Script.execute_code(code)
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
                    return

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
                        params = [self.host.get_equipment_weight(), self.host.get_capacity(), target.get_weight()]
                        Global.main.monologue.set(Dialog.get('!heavy', params))
            elif not self.host.tags.get('fly') or not self.interact_on(self.host.pos):
                self.make('grab', turn=1)
                self.host.drop()

    def sheathe(self):
        if self.host.weapon:
            def change():
                dropped = self.host.drop()
                self.host.inventory.attempt_add(dropped)
                Global.temp['sheathe'] = dropped.name
            self.make('grab', turn=4)
            self.on_finish = change
        else:
            sheathe = Global.temp.get('sheathe')
            if sheathe:
                index = self.host.inventory.get_item_index(sheathe)
                self.host.unsheathe(index)

    def crush(self):
        front = self.host.pos.get_cardinal(self.host.direction, 1)
        if front.speed == -10:
            self.host.location.sound.register(self.host.pos, 16, file='critical')
            front.set_terrain('.')
            front.update_update_shader()

    def attack(self):
        self.host.states.trigger(['act', 'attack'])
        speed = min(5, self.host.get_attack_speed())
        self.make(self.host.get_attack_motion(), turn=10 - speed)
        slow = max(0, 2 - speed)
        dmg = self.host.roll_damage()
        front = self.host.pos.get_cardinal(self.host.direction, 1)
        hitter = self.host.get_hitter()
        self.host.location.field.register(dmg, front, hitter=hitter, delay=slow, sound=['swing', 0],
                                          callback=self.host.on_attack)
        self.host.form.timer.set(slow * 4 + 4)
        if self.host.get_skill('crush') and dmg > 6:
            self.on_finish = self.crush

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
