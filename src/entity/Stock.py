from src.entity.Projectile import Projectile
from src.entity.Prop import Prop
from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Headgear import Headgear
from src.entity.unit.item.Item import Item
from src.entity.unit.item.Weapon import Weapon
from src.tools.Data import Data


class Stock:
    registry = {}
    location = None

    @staticmethod
    def init():
        for i in Data.registry_list:
            registry_items = Data.process_raw(Data.get_cache_file('data/raw/' + i + '.txt'))
            if i == 'others':
                for item in registry_items:
                    Stock.registry[item[0]] = [getattr(Stock, item[0]), item]
            else:
                for item in registry_items:
                    Stock.registry[item[0]] = [getattr(Stock, i), item]
        Stock.registry['Projectile'] = [Stock.projectiles, None]

    @staticmethod
    def get(name, data=None):
        if name in Stock.registry.keys():
            record = Stock.registry[name]
            if not data:
                object_id = Stock.location.get_id()
                pos = [[0, 0]]
                data = [object_id, pos] + record[1]
            r = record[0](data)
            return r

    @staticmethod
    def props(arg):
        r = Prop(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def units(arg):
        from src.entity.unit.Humanoid import Humanoid
        r = Humanoid(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def items(arg):
        r = Item(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def armors(arg):
        r = Armor(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def headgears(arg):
        r = Headgear(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def weapons(arg):
        r = Weapon(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def Ladder(arg):
        r = Item(Stock.location)
        r.load(arg)
        r.collide = 32
        return r

    @staticmethod
    def Thing(arg):
        r = Item(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def projectiles(arg):
        arg[2] = 'Projectile'
        r = Projectile(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def project(form, pos, lifetime):
        r = Stock.projectiles([0, [pos]] + Stock.registry['Force'][1] + [lifetime])
        r.make_form(form)
        return r.add()
