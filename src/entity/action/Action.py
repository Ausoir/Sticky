class Action:
    def __init__(self, host):
        self.host = host

    def perform(self, action):
        if hasattr(self, action):
            continuous, animation = getattr(self, action)()
            if animation:
                self.host.form.set(animation)
            else:
                self.host.form.set(action)
            return continuous
        return 0

    def idle(self):
        return 0, None

    def left(self):
        self.host.move(-1, 0)
        self.host.face(-1)
        self.host.turn = 2
        return 1, None

    def right(self):
        self.host.move(1, 0)
        self.host.face(1)
        self.host.turn = 2
        return 1, None

    def use(self):
        return 0, 'idle'

    def interact(self):
        return 0, 'idle'

    def hit(self):
        return 0, None

    def punch(self):
        self.host.turn = 4
        return 0, None

    def jump(self):
        self.host.turn = 1
        self.host.move(self.host.direction, -3)
        return 0, None
