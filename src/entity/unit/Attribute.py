from src.tools.Random import Random


class Attribute:
    def __init__(self):
        self.gene = 0

        self.strength = 1
        self.agility = 1
        self.intelligence = 1

        self.leg = 0
        self.biceps = 0
        self.triceps = 0

    def __str__(self):
        return str(self.gene) + ',' + str(self.strength) + ',' + str(self.agility) + ',' + str(self.intelligence)\
               + ',' + str(self.leg) + ',' + str(self.biceps) + ',' + str(self.triceps)

    def load(self, arg):
        if arg[0]:
            self.gene = arg[0]
        else:
            self.gene = Random.rand_int(1, 9999)
        self.strength = arg[1]
        self.agility = arg[2]
        self.intelligence = arg[3]
        if len(arg) > 4:
            self.leg = arg[4]
            self.biceps = arg[5]
            self.triceps = arg[6]

    def exert(self, muscle, mag):
        stamina = self.strength * 4
        if muscle == 0:
            self.leg += mag
            if self.leg > stamina:
                return 1
        elif muscle == 1:
            self.biceps += mag
            if self.biceps > stamina:
                return 1
        elif muscle == 2:
            self.triceps += mag
            if self.triceps > stamina:
                return 1
        return 0

    def is_rested(self):
        return self.leg == 0 and self.biceps == 0 and self.triceps == 0

    def rest(self, mag=1):
        if self.leg > 0:
            self.leg -= mag
        if self.biceps > 0:
            self.biceps -= mag
        if self.triceps > 0:
            self.triceps -= mag
