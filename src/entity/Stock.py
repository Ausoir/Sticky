from src.entity.Container import Container
from src.entity.unit.Humanoid import Humanoid
from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Focus import Focus
from src.entity.unit.item.Headgear import *
from src.entity.unit.item.Trinket import *
from src.entity.Other import *
from src.tools.Data import Data


class Stock:
    registry = None

    @staticmethod
    def init():
        Stock.registry = {}
        for i in Data.registry_list:
            registry_items = Data.process_raw(Data.read('data/raw/' + i + '.txt'))
            for item in registry_items:
                if item:
                    Stock.registry[item[0]] = item
        for model in Data.get_line('raw.txt', 'face')[1]:
            face = []
            for image in model:
                face.append(Data.get_graphics(image))
            Humanoid.faces.append(face)

    @staticmethod
    def get_class_by_name(name):
        if name == 'Prop':
            return Prop
        elif name == 'Container':
            return Container
        elif name == 'Item':
            return Item
        elif name == 'Armor':
            return Armor
        elif name == 'Headgear':
            return Headgear
        elif name == 'Talisman':
            return Talisman
        elif name == 'Focus':
            return Focus
        elif name == 'Unit':
            return Unit
        elif name == 'Humanoid':
            return Humanoid
        elif name == 'Telescope':
            return Telescope
        elif name == 'Porter':
            return Porter
        elif name == 'Lamp':
            return Lamp
        elif name == 'Scripter':
            return Scripter
        elif name == 'Force':
            return Force
        elif name == 'Door':
            return Door
        elif name == 'Specie':
            return Specie
        elif name == 'Marker':
            return Marker
        elif name == 'Food':
            return Food
        elif name == 'Corpse':
            return Corpse
        elif name == 'Manual':
            return Manual
        elif name == 'Potion':
            return Potion
        elif name == 'Mine':
            return Mine
        elif name == 'Phantom':
            return Phantom
        elif name == 'Ghost':
            return Ghost
        elif name == 'Ceiling':
            return Ceiling

    @staticmethod
    def check(name):
        if name in Stock.registry:
            return True

    @staticmethod
    def get(name, data=None):
        if not data:
            if name in Stock.registry:
                record = Stock.registry[name]
                data = [[0, 0]] + record
                r = Stock.get_class_by_name(record[1])()
            else:
                name = name or 'UNDEFINED'
                print("Cannot load Stock Object " + name)
                return Stock.get_class_by_name('Humanoid')
        else:
            r = Stock.get_class_by_name(data[2])()
        r.load(data)
        return r

    @staticmethod
    def make(name, pos):
        r = Stock.get(name)
        r.pos = pos
        r.add()
        return r
