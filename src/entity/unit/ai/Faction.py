class Faction:
    FFA = 0
    PLAYER = 1
    A = 2
    B = 3

    def __init__(self, arg):
        self.team = None
        self.load(arg)

    def __str__(self):
        return str(self.team)

    def load(self, arg):
        self.team = arg

    def is_against(self, faction):
        if isinstance(faction, Faction):
            team = faction.team
        else:
            team = faction
        return self.team == Faction.FFA or self.team != team
