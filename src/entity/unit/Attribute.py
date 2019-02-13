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
        if len(arg) > 3:
            self.leg = arg[3]
            self.biceps = arg[4]
            self.triceps = arg[5]

    def exert(self, muscle, mag):
        stamina = self.strength * 5
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

    def rest(self, mag=1):
        if self.leg > 0:
            self.leg -= mag
        if self.biceps > 0:
            self.biceps -= mag
        if self.triceps > 0:
            self.triceps -= mag
