from src.entity.Container import Container
from src.entity.Projectile import Projectile
from src.entity.Prop import Prop
from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Headgear import Headgear
from src.entity.unit.item.Item import Item
from src.entity.unit.item.Spell import Spell
from src.entity.unit.item.Weapon import Weapon
from src.tools.Data import Data


class Stock:
    registry = {}
    location = None

    @staticmethod
    def init():
        for i in Data.registry_list:
            registry_items = Data.process_raw(Data.get_cache_file('data/raw/' + i + '.txt'))
            for item in registry_items:
                Stock.registry[item[0]] = [getattr(Stock, i), item]
        Stock.registry['Projectile'] = [Stock.projectile, 'Projectile,g_0x0,[],-1,[],10']
        item_desc = Data.process_raw(Data.get_cache_file('data/raw/descriptions.txt'))
        for i in item_desc:
            Item.description[i[0]] = i[1]

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
    def make(name, pos):
        r = Stock.get(name)
        r.pos[0] = pos
        r.add()
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
    def containers(arg):
        r = Container(Stock.location)
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
    def projectile(arg):
        r = Projectile(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def spells(arg):
        r = Spell(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def others(arg):
        from src.entity import Other
        unique = getattr(Other, arg[2])
        if unique:
            r = unique(Stock.location)
        else:
            r = Prop(Stock.location)
        r.load(arg)
        return r

    @staticmethod
    def project(form, pos):
        data = [0, [pos], 'Projectile'] + Stock.registry['Force'][1][1:]
        r = Stock.projectile(data)
        r.make_form(form)
        return r.add()
