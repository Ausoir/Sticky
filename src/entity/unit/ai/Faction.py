class Faction:
    FFA = 0
    PLAYER = 1
    A = 2
    B = 3
    PROJECTILE = 4

    @staticmethod
    def is_against(faction1, faction2):
        return faction1 == Faction.FFA or faction2 == Faction.FFA or faction1 != faction2
