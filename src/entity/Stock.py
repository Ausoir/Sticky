from src.entity.Projectile import Projectile
from src.entity.Prop import Prop
from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Headgear import Headgear
from src.entity.unit.item.Item import Item
from src.entity.unit.item.Weapon import Weapon
from src.tools.Data import Data


class Stock:
    registry = {}

    @staticmethod
    def init():
        for i in Data.registry_list:
            registry_items = Data.process_raw(Data.get_cache_file('data/raw/' + i + '.txt'))
            for item in registry_items:
                Stock.registry[item[0]] = [getattr(Stock, i), item]

    @staticmethod
    def get(name, loc, data=None):
        if name in Stock.registry.keys():
            record = Stock.registry[name]
            if not data:
                object_id = loc.get_id()
                pos = [[0, 0]]
                data = [object_id, pos] + record[1]
            r = record[0](loc, data)
            return r

    @staticmethod
    def props(loc, arg):
        r = Prop(loc)
        r.load(arg)
        return r

    @staticmethod
    def units(loc, arg):
        from src.entity.unit.Humanoid import Humanoid
        r = Humanoid(loc)
        r.load(arg)
        return r

    @staticmethod
    def items(loc, arg):
        r = Item(loc)
        r.load(arg)
        return r

    @staticmethod
    def armors(loc, arg):
        r = Armor(loc)
        r.load(arg)
        return r

    @staticmethod
    def headgears(loc, arg):
        r = Headgear(loc)
        r.load(arg)
        return r

    @staticmethod
    def weapons(loc, arg):
        r = Weapon(loc)
        r.load(arg)
        return r

    @staticmethod
    def projectiles(loc, arg):
        r = Projectile(loc)
        r.load(arg)
        return r
