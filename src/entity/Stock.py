from src.entity.Prop import Prop
from src.entity.unit.ai.Pilot import Pilot
from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Item import Item
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

    @staticmethod
    def register(arg, fn):
        list = Data.process_raw(Data.get_cache_file('raw/'+arg+'.txt'))
        for i in list:
            Stock.registry[i[0]] = [fn, i]

    @staticmethod
    def load(arg, loc):
        r = Stock.get(arg[1], loc)
        r.load(arg)
        return r

    @staticmethod
    def get(name, loc, seed=None):
        if name in Stock.registry.keys():
            if not seed:
                seed = Random.rand_seed()
            record = Stock.registry[name]
            r = record[0](loc, seed, record[1])
            r.name = name
            return r

    @staticmethod
    def man(loc, seed, arg):
        from src.entity.unit.Humanoid import Humanoid
        r = Humanoid('unit/Man', seed, loc)
        # r.stats = arg[1]
        r.durability = 5
        r.action.abilities = arg[2]
        Pilot(r, arg[3])
        if arg[4]:
            r.armor = Stock.get(arg[4], loc)
        if arg[5]:
            r.weapon = Stock.get(arg[5], loc)
        return r

    @staticmethod
    def armor(loc, seed, arg):
        name = arg[0]
        fdir = 'data/item/armor/' + name
        Data.initialize_image(name, fdir, (16, 48))
        return Armor(name, seed, loc, arg[1], arg[2])

    @staticmethod
    def weapon(loc, seed, arg):
        name = arg[0]
        r = Item('data/item/weapon/' + name, seed, loc)
        if arg[1]:
            r.form.pivot.x = arg[1]
        r.range = arg[2]
        return r

    @staticmethod
    def prop(loc, seed, arg):
        name = arg[0]
        r = Prop('data/object/' + name, seed, loc)
        if arg[1]:
            r.form.offset[1] = arg[1]
        else:
            r.form.offset[1] = -r.form.size.y / 2
        r.durability = arg[2]
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
