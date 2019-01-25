from src.entity.Humanoid import Humanoid
from src.entity.Prop import Prop
from src.game.Pilot import Pilot


class Stock:
    @staticmethod
    def get(name, loc):
        if hasattr(Stock, name):
            r = getattr(Stock, name)(loc)
            r.name = name
            return r

    @staticmethod
    def player(loc):
        from src.interface.Menu import Menu
        from src.interface.Control import Control
        from src.game.Group import Group
        player = Humanoid('unit/Man', loc)
        control = Control(Menu(player), player)
        Group.interface.append(control)
        player.durability = 3
        return player

    @staticmethod
    def man(loc):
        r = Humanoid('unit/Man', loc)
        r.durability = 3
        Pilot(r)
        return r

    @staticmethod
    def error(loc):
        return Prop('Error', loc)

    @staticmethod
    def crate(loc):
        r = Prop('Data/object/Crate', loc)
        r.durability = 2
        return r
