# noinspection PyUnresolvedReferences
from src.entity.unit.item.Armor import Armor
# noinspection PyUnresolvedReferences
from src.entity.unit.item.Headgear import Headgear
# noinspection PyUnresolvedReferences
from src.entity.unit.item.Spell import Spell
# noinspection PyUnresolvedReferences
from src.entity.unit.item.Weapon import Weapon
# noinspection PyUnresolvedReferences
from src.entity.unit.Unit import Unit
# noinspection PyUnresolvedReferences
from src.entity.unit.Character import Character
# noinspection PyUnresolvedReferences
from src.entity.Projectile import Projectile
from src.entity.unit.Humanoid import Humanoid
from src.entity.Other import *
from src.tools.Data import Data


class Stock:
    registry = {}
    location = None

    @staticmethod
    def init():
        for i in Data.registry_list:
            registry_items = Data.process_raw(Data.get_cache_file('data/raw/' + i + '.txt'))
            for item in registry_items:
                Stock.registry[item[0]] = item
        item_desc = Data.process_raw(Data.get_cache_file('data/raw/descriptions.txt'))
        for i in item_desc:
            Item.description[i[0]] = i[1]
        Humanoid.faces = Data.get_line('data/raw/raw.txt', 'face')[1]

    @staticmethod
    def get(name, data=None):
        if name in Stock.registry.keys():
            record = Stock.registry[name]
            if not data:
                object_id = Stock.location.get_id()
                pos = [0, 0]
                data = [object_id, pos] + record
            r = globals()[record[1]](Stock.location)
            r.load(data)
            return r

    @staticmethod
    def make(name, pos):
        r = Stock.get(name)
        r.pos = pos
        r.add()
        return r
