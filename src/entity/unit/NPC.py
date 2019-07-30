from src.entity.unit.Humanoid import Humanoid


class NPC(Humanoid):
    def __init__(self, loc):
        super().__init__(loc)
        self.var = []

    def __str__(self):
        return super().__str__() + ',[' + ','.join(str(x) for x in self.var) + ']'

    def load(self, p):
        index = super().load(p)
        self.var = p[index]
        return index + 1
