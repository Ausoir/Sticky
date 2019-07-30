class Faction:
    @staticmethod
    def is_against(faction1, faction2):
        return not faction1 or not faction2 or faction1 != faction2
