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
# noinspection PyUnresolvedReferences
from src.entity.unit.Humanoid import Humanoid
# noinspection PyUnresolvedReferences
from src.entity.Other import *
from src.tools.Data import Data


class Stock:
    registry = {}

    @staticmethod
    def init():
        for i in Data.registry_list:
            registry_items = Data.process_raw(Data.read('raw/' + i + '.txt'))
            for item in registry_items:
                Stock.registry[item[0]] = item
        for model in Data.get_line('raw/raw.txt', 'face')[1]:
            face = []
            for image in model:
                face.append(Data.get_cache(image))
            Humanoid.faces.append(face)

    @staticmethod
    def get(name, data=None):
        if not data:
            if name in Stock.registry:
                record = Stock.registry[name]
                object_id = Global.location.get_id()
                pos = [0, 0]
                data = [object_id, pos] + record
                r = globals()[record[1]]()
            else:
                name = name or 'UNDEFINED'
                print("Cannot load Stock Object " + name)
                return None
        else:
            r = globals()[data[3]]()
        r.load(data)
        return r

    @staticmethod
    def make(name, pos):
        r = Stock.get(name)
        r.pos = pos
        r.add()
        return r
