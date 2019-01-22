from src.map.Tile import Tile


class Action:
    def __init__(self, host):
        self.host = host

    def perform(self, action):
        if hasattr(self, action):
            turn, continuous, animation = getattr(self, action)()
            self.host.delay = turn
            if animation:
                self.host.form.set(animation)
            else:
                self.host.form.set(action)
            self.host.form.set_speed(turn)
            return continuous
        return 0

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
        return 1, 0, None

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
        return 4, 0, None

    def kick(self):
        return 6, 0, None

    def jump(self):
        self.host.move(self.host.direction, -3)
        return 3, 0, None
