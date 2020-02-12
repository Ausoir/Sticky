class Timer:
    def __init__(self, p, repeat=0):
        self.time = 0
        self.max = 0
        self.repeat = repeat
        self.set(p)

    def set(self, p):
        self.time = p
        self.max = p

    def update(self, p=1):
        if self.time > 0:
            self.time = max(0, self.time - p)
        if self.time == 0:
            if self.repeat:
                self.time = self.max
            return True
