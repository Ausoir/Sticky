from src.game import Global


class Attribute:
    def __init__(self):
        self.gene = 0

        self.max_hp = 1

        self.strength = 0
        self.agility = 0
        self.intelligence = 0

        self.speed = 0

    def __str__(self):
        att = [self.gene, self.max_hp, self.strength, self.agility, self.intelligence]
        return ','.join(str(x) for x in att)

    def load(self, arg):
        if arg[0] != -1:
            self.gene = arg[0]
        else:
            self.gene = Global.r.rand_int(1, 9999)
        self.max_hp = arg[1]
        self.strength = arg[2]
        self.agility = arg[3]
        self.intelligence = arg[4]
        return 5


class AdvAttribute(Attribute):
    def __init__(self):
        super().__init__()
        self.exhaustion = 0
        self.qi = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.exhaustion) + ',' + str(self.qi)

    def load(self, arg):
        index = super().load(arg)
        self.exhaustion = arg[index]
        self.qi = arg[index + 1]
        return index + 2
