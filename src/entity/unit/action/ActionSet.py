from src.entity.Space import Space
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.entity.unit.action.Attack import Attack
from src.entity.unit.item.Item import Item
from src.map.Tile import Tile


class ActionSet:
    default = ['idle', 'left', 'right', 'walk', 'hit', 'down', 'dead', 'interact', 'use', 'jump']

    def __init__(self, host):
        self.host = host
        self.current_action = 'idle'
        self.on_finish = None
        self.last_action = None
        self.time = 0
        self.abilities = []

    def __str__(self):
        return ','.join(self.abilities)

    def attempt(self, action):
        if action in self.abilities or action in ActionSet.default:
            self.set(action)

    def set(self, action):
        if not self.host.is_dead():
            self.current_action = action
            if action != self.last_action:
                self.time = 0
                if self.on_finish:
                    self.on_finish()
                    self.on_finish = None
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

    def recover(self):
        self.host.form.set_height()

    def idle(self):
        if self.time > 3:
            self.make(animation='standby', turn=0)
        else:
            self.make(turn=0)

    def left(self):
        self.host.face(-1)
        self.set('walk')

    def right(self):
        self.host.face(1)
        self.set('walk')

    def walk(self):
        self.host.move(self.host.direction, 0)
        self.make(turn=2)

    def hit(self):
        self.make(turn=2)

    def interact(self):
        if self.host.is_armed():
            self.make(animation='throw', turn=2)
            weapon = self.host.weapon
            self.host.drop()
            to = self.host.get_interact_pos()
            weapon.relocate(to.x, to.y)
            weapon.animation_move_from = weapon.pos[0].get_vec()
            weapon.move(self.host.next_target[0], self.host.next_target[1], distance=9, flag=Tile.CHECK_ANY)
        else:
            self.make(turn=3)
            self.host.form.rotate_appendage(7, 0, self.host.next_target)
            target = self.host.location.collide_line(self.host.get_interact_pos(),
                                                     self.host.next_target[0], self.host.next_target[1],
                                                     distance=1, flag=Tile.CHECK_NONE)
            for thing in target.things:
                if isinstance(thing, Item):
                    self.host.pickup(thing)

    def dead(self):
        self.host.form.set_height(4)
        self.host.collide = 0
        self.host.location.record.remove(self.host)
        self.on_finish = self.recover
        self.make(animation='dead' + str(self.host.seed % 3 + 1))
        self.host.delay = -1

    def down(self):
        self.host.form.set_height(4)
        self.on_finish = self.recover
        self.make(turn=7)

    def rest(self):
        self.host.attributes.rest()
        self.make(turn=3)

    def sprint(self):
        if self.host.attributes.exert(0, 2):
            self.set('rest')
        else:
            self.host.move(self.host.direction, 0)
            self.make(turn=0)

    def use(self):
        self.host.weapon.use()

    def attack(self):
        if self.host.attributes.exert(1, 4):
            self.set('rest')
        else:
            self.host.aim()
            self.host.form.rotate_appendage(30, 0, self.host.next_target)
            self.host.weapon.attack(delay=1)
            self.make(turn=4)

    def dash(self):
        if self.host.attributes.exert(0, 4):
            self.set('rest')
        else:
            if self.host.weapon:
                self.host.aim()
            self.host.move(self.host.direction*2, 0, flag=Tile.CHECK_TERRAIN)
            self.host.weapon.attack(delay=1)
            self.host.move(self.host.direction, 0, flag=Tile.CHECK_TERRAIN)
            self.host.weapon.attack(delay=1)
            self.make(turn=6)

    def kick(self):
        if self.host.attributes.exert(0, 8):
            self.set('rest')
        else:
            def on_hit(victim):
                victim.move(direction, 0)
                if isinstance(victim, Unit):
                    victim.action.set('down')
            direction = self.host.direction
            self.host.location.attack.register(self.host, 0, self.host.get_offset_tile(self.host.direction, 0),
                                               delay=1, type=Attack.BATTER, callback=on_hit)
            self.make(turn=4)

    def jump(self):
        if self.host.attributes.exert(0, 4):
            self.set('rest')
        else:
            self.host.move(self.host.direction*1, -1)
            self.make(turn=2)

    def lunge(self):
        if self.host.attributes.exert(2, 6):
            self.set('rest')
        else:
            def on_hit(victim):
                victim.action.set('down')
            if self.host.pos[0] != self.host.move(self.host.direction, 0):
                self.host.weapon.attack(delay=2, on_hit=on_hit)
                self.make(turn=4)
            else:
                self.make(animation='drop', turn=4)

    def switch(self):
        from src.game import Global
        Global.main.world.switch()

    def underhand(self):
        def fin():
            self.host.hittable = 1
        self.host.form.rotate_appendage(41, 0, self.host.next_target)
        self.host.weapon.attack(delay=1)
        self.host.hittable = 0
        self.on_finish = fin
        self.make(turn=7)

    def arch(self):
        def fin():
            r = Stock.arrow(self.host.location).add()
            r.relocate(self.host.get_interact_pos().x, self.host.get_interact_pos().y, force=1)
            prev = r.move(x, y, flag=Tile.CHECK_LARGE)
            self.host.location.attack.register(self.host, 1, prev, 1)
            r.form.rotation = Space(x, y).get_atan() + 180
        x = self.host.next_target[0] * 10
        y = self.host.next_target[1] * 10
        self.host.form.rotate_appendage(31, 0, self.host.next_target)
        self.host.form.rotate_appendage(31, 5, self.host.next_target)
        self.on_finish = fin
        self.make(turn=7)
