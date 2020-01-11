from src.game import Global


class Attribute:
    def __init__(self):
        self.hp = 0
        self.max_hp = 0

    def __str__(self):
        att = [self.hp, self.max_hp]
        return ','.join(str(x) for x in att)

    def load(self, arg):
        self.hp = arg[0]
        self.max_hp = arg[1]
        return 2


class AdvAttribute(Attribute):
    def __init__(self):
        super().__init__()

        self.gene = 0

        self.max_hp = 0

        self.strength = 0
        self.agility = 0
        self.intelligence = 0

        self.speed = 0

    def __str__(self):
        att = [self.gene, self.strength, self.agility, self.intelligence]
        return super().__str__() + ',' + (','.join(str(x) for x in att))

    def load(self, arg):
        index = super().load(arg)
        if arg[index] != -1:
            self.gene = arg[index]
        else:
            self.gene = Global.r.rand_int(1, 9999)
        index += 1
        self.strength = arg[index]
        index += 1
        self.agility = arg[index]
        index += 1
        self.intelligence = arg[index]
        return index + 1
