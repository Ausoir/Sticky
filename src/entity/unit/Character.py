from src.entity.unit.Humanoid import Humanoid
from src.player.Inventory import Inventory


class Character(Humanoid):
    def __init__(self, loc):
        super().__init__(loc)
        self.inventory = Inventory(self)

    def __str__(self):
        return super().__str__() + ',' + self.inventory.__str__()

    def load(self, p):
        index = super().load(p)
        self.inventory.load(p[index])
        return index + 1

    def load_attributes(self, arg):
        from src.entity.unit.Attribute import AdvAttribute
        self.attributes = AdvAttribute()
        self.attributes.load(arg)

    def fell(self, distance, me=False):
        if self.get_tag('talent') != 'Assassin' or not me:
            if distance > 1:
                self.tags['sign'] = 'Accident'
            super().fell(distance, me)

    def hit(self, damage, accuracy=None, hitter=None):
        r = super().hit(damage, accuracy, hitter)
        if r == 2:
            from src.entity.unit.Unit import Unit
            from src.entity.unit.Buff import Buff
            from src.entity.unit.item.Item import Item
            if hitter == self.weapon:
                self.tags['sign'] = 'Suicide'
            elif isinstance(hitter, Humanoid) or (isinstance(hitter, Item) and hitter.host):
                self.tags['sign'] = 'Homicide'
            elif isinstance(hitter, Unit):
                self.tags['sign'] = 'Wildlife'
            elif isinstance(hitter, Buff):
                self.tags['sign'] = 'Illness'
        return r

    def out_of_bounds(self):
        self.tags['sign'] = 'Accident'
        super().out_of_bounds()

    def is_bright(self):
        from src.game import Global
        if Global.player.is_daytime() or self.pos.light > 0:
            return True
        self.say('Too dark!')

    def require_var(self, var, mag, cost=True):
        if var in self.tags:
            if self.tags[var] >= mag:
                if cost:
                    self.tags[var] -= mag
                return True
            else:
                self.say('Not enough ' + var + '!')
                return False

    def get_possessions(self):
        r = [self.weapon]
        r += self.inventory.items
        r.append(self.armor)
        if self.headgear:
            r.append(self.headgear)
        return r

    def get_accessibles(self):
        r = []
        from src.entity.unit.item.Item import Item
        for thing in self.pos.things:
            if isinstance(thing, Item):
                r.append(thing)
        r += self.get_possessions()
        return r
