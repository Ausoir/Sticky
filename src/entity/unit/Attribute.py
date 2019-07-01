from src.tools.Random import Random


class Attribute:
    def __init__(self):
        self.gene = 0

        self.strength = 1
        self.agility = 1
        self.intelligence = 1

        self.speed = 0

        self.breath = 0
        self.body = 0
        self.leg = 0

    def __str__(self):
        return str(self.gene) + ',' + str(self.strength) + ',' + str(self.agility) + ',' + str(self.intelligence)\
               + ',' + str(self.breath) + ',' + str(self.body) + ',' + str(self.leg)

    def load(self, arg):
        if arg[0]:
            self.gene = arg[0]
        else:
            self.gene = Random.rand_int(1, 9999)
        self.strength = arg[1]
        self.agility = arg[2]
        self.intelligence = arg[3]
        if len(arg) > 4:
            self.breath = arg[4]
            self.body = arg[5]
            self.leg = arg[6]

    def exert(self, muscle, mag):
        if muscle == 0:
            self.body += mag
            if self.body >= self.strength:
                return 1
        elif muscle == 1:
            self.leg += mag
            if self.leg >= self.strength * 3:
                return 1
        return 0

    def is_rested(self):
        return self.leg == 0 and self.body == 0

    def rest(self, mag=1):
        self.breath += mag
        if self.breath >= 8:
            self.breath = 0
            self.body = 0
            self.leg = 0
