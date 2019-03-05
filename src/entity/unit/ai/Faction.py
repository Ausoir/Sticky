class Faction:
    FFA = 0
    PLAYER = 1
    A = 2
    B = 3
    PROJECTILE = 4
    ROGUE = 5

    @staticmethod
    def is_against(faction1, faction2):
        return not faction1 or not faction2 or faction1 != faction2
