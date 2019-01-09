class Entity:
    def __init__(self):
        self.id = -1
        self.pos = [0, 0]
        self.size = [0, 0]
        self.vel = [0, 0]

    def load(self, p):
        self.id = p[0]
        self.pos = p[1]
        self.size = p[2]
        return 3

    def __str__(self):
        return [self.id, self.pos, self.size].__str__()

