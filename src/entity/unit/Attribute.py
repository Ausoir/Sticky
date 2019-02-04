class Attribute:
    def __init__(self):
        self.strength = 1
        self.agility = 1
        self.intelligence = 1

        self.leg = 0
        self.biceps = 0
        self.triceps = 0

    def __str__(self):
        return str(self.strength) + ',' + str(self.agility) + ',' + str(self.intelligence)\
               + ',' + str(self.leg) + ',' + str(self.biceps) + ',' + str(self.triceps)

    def load(self, arg):
        self.strength = arg[0]
        self.agility = arg[1]
        self.intelligence = arg[2]
        self.leg = arg[3]
        self.biceps = arg[4]
        self.triceps = arg[5]

    def exert(self, muscle, mag):
        stamina = self.strength * 3
        if muscle == 0:
            if self.leg > stamina:
                return 1
            self.leg += mag
        elif muscle == 1:
            if self.biceps > stamina:
                return 1
            self.biceps += mag
        elif muscle == 2:
            if self.triceps > stamina:
                return 1
            self.triceps += mag
        return 0

    def rest(self):
        if self.leg > 0:
            self.leg -= 1
        if self.biceps > 0:
            self.biceps -= 1
        if self.triceps > 0:
            self.triceps -= 1
