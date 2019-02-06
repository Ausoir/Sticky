from src.entity.Object import Object


class Travel(Object):
    def __init__(self, loc, destination):
        super().__init__('Icon_4x0', 0, loc)
        self.destination = destination

    def __str__(self):
        return super().__str__() + ',[' + str(self.destination[0]) + ',' + str(self.destination[1]) + ']'

    def load(self, p):
        index = super().load(p)
        self.destination = p[index]

    def interact(self, host):
        host.relocate(self.destination[0], self.destination[1])
