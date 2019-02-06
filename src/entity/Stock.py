from src.entity.Prop import Prop
from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Item import Item
from src.entity.unit.item.Weapon import Weapon
from src.tools.Data import Data
from src.tools.Random import Random


class Stock:
    registry = {}

    @staticmethod
    def init():
        Stock.register('props', Stock.prop)
        Stock.register('units', Stock.man)
        Stock.register('armors', Stock.armor)
        Stock.register('weapons', Stock.weapon)
        Stock.registry['Travel'] = [Stock.travel, [None]]

    @staticmethod
    def register(arg, fn):
        registry_list = Data.process_raw(Data.get_cache_file('raw/'+arg+'.txt'))
        for i in registry_list:
            Stock.registry[i[0]] = [fn, i]

    @staticmethod
    def get(name, loc, data=None):
        if name in Stock.registry.keys():
            record = Stock.registry[name]
            if not data:
                id = 0
                seed = Random.rand_seed()
                pos = [[0, 0]]
                data = [id, seed, pos] + record[1]
            r = record[0](loc, data)
            return r

    @staticmethod
    def travel(loc, arg):
        from src.entity.Travel import Travel
        return Travel(loc, [0, 0])

    @staticmethod
    def man(loc, arg):
        from src.entity.unit.Humanoid import Humanoid
        r = Humanoid('unit/Man', arg[1], loc)
        r.load(arg)
        return r

    @staticmethod
    def armor(loc, arg):
        name = arg[3]
        fdir = 'data/item/armor/' + name
        Data.initialize_image(name, fdir, (16, 48))
        r = Armor(name, arg[1], loc, arg[4], arg[5])
        r.load(arg)
        return r

    @staticmethod
    def weapon(loc, arg):
        name = arg[3]
        r = Weapon('data/item/weapon/' + name, arg[1], loc)
        r.load(arg)
        return r

    @staticmethod
    def prop(loc, arg):
        name = arg[3]
        r = Prop('data/object/' + name, arg[1], loc)
        r.form.offset[1] = -r.form.size.y / 2
        r.load(arg)
        return r

    @staticmethod
    def arrow(loc):
        def turn():
            r.count -= 1
            if r.count == 0:
                r.remove()
        r = Item('data/item/weapon/Arrow', 0, loc)
        r.count = 2
        loc.record.remove(r)
        r.turn = turn
        r.gravity = 0
        return r
