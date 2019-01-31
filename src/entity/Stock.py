from src.entity.Prop import Prop
from src.entity.unit.ai.Pilot import Pilot
from src.entity.unit.item.Item import Item
from src.tools.Random import Random


class Stock:
    @staticmethod
    def get(name, loc, seed=None):
        if hasattr(Stock, name):
            if not seed:
                seed = Random.rand_seed()
            r = getattr(Stock, name)(loc, seed)
            r.name = name
            return r

    @staticmethod
    def man(loc, seed=0):
        from src.entity.unit.Humanoid import Humanoid
        r = Humanoid('unit/Man', seed, loc)
        r.durability = 5
        r.action.abilities += ['lunge', 'dash']
        Pilot(r, 'Melee')
        return r

    @staticmethod
    def fist(loc, seed=0):
        return Item('Data/item/weapon/Fist', seed, loc)

    @staticmethod
    def error(loc, seed=0):
        return Prop('Error', seed, loc)

    @staticmethod
    def crate(loc, seed=0):
        r = Prop('Data/object/Crate', seed, loc)
        r.durability = 2
        return r

    @staticmethod
    def sword(loc, seed=0):
        r = Item('Data/item/weapon/Shortsword', seed, loc)
        r.form.pivot.x = 8
        return r

    @staticmethod
    def spear(loc, seed=0):
        r = Item('Data/item/weapon/Spear', seed, loc)
        r.range = [2]
        return r

    @staticmethod
    def bokken(loc, seed=0):
        r = Item('Data/item/weapon/Bokken', seed, loc)
        r.form.pivot.x = 8
        r.range = [1, 2]
        return r
