from src.entity.Attack import Attack
from src.map.Tile import Tile


class Action:
    def __init__(self, host):
        self.host = host

    def perform(self, action):
        if hasattr(self, action):
            turn, continuous, animation = getattr(self, action)()
            self.host.delay = turn
            if animation:
                self.set_animation(animation, continuous)
            else:
                self.set_animation(action, continuous)
            self.host.form.set_speed(turn)
            return continuous
        return 0

    def set_animation(self, arg, continuous):
        if not continuous or self.host.form.state_name != arg:
            self.host.form.set(arg)

    def make(self, animation, turn, speed):
        self.host.form.set(animation)
        self.host.delay = turn
        self.host.form.set_speed(speed)

    def idle(self):
        return 0, 0, None

    def left(self):
        self.host.move(-1, 0)
        self.host.face(-1)
        self.host.delay = 1
        return 2, 1, None

    def right(self):
        self.host.move(1, 0)
        self.host.face(1)
        self.host.delay = 1
        return 2, 1, None

    def hit(self):
        return 3, 0, None

    def attack(self):
        r1, r2, r3 = self.punch()
        return r1, r2, 'punch'

    def interact(self):
        return 0, 0, 'idle'

    def down(self):
        self.host.move(self.host.direction*-6, -6)
        return 7, 0, None

    def sprint(self):
        self.host.move(self.host.direction * 4, 0, Tile.CHECK_TERRAIN)
        return 4, 0, None

    def punch(self):
        self.host.location.attack.register(self.host, 1, [self.host.direction, -1], 0, Attack.BATTER)
        return 4, 0, None

    def kick(self):
        direction = self.host.direction

        def on_hit(victim):
            victim.move(direction, 0)
        self.host.location.attack.register(self.host, 1, [direction, 0], 1, Attack.BLOODY, on_hit)
        return 4, 0, None

    def jump(self):
        self.host.move(self.host.direction*2, -3)
        return 2, 0, None

    def summon(self):
        from src.entity.Stock import Stock
        r = Stock.get('man', self.host.location)
        r.relocate(self.host.pos.x + self.host.direction, self.host.pos.y - 3)
        return 6, 0, 'conjure'
