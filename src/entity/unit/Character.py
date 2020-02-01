from src.entity.unit.Humanoid import Humanoid
from src.player.Inventory import Inventory


class Character(Humanoid):
    def __init__(self, loc):
        super().__init__(loc)
        self.inventory = Inventory(self)
        from src.tools.Data import Data
        self.shadow = Data.get_form('g_7x0')
        self.shadow.bound(True)

    def __str__(self):
        return super().__str__() + ',' + self.inventory.__str__()

    def load(self, p):
        index = super().load(p)
        self.inventory.load(p[index])
        return index + 1

    def add(self):
        super().add()
        self.shadow.show(True)

    def remove(self):
        super().remove()
        self.shadow.show(False)

    def set_row(self, row):
        super().set_row(row)
        self.shadow.z = self.depth(row)

    def bound(self, visible):
        super().bound(visible)
        self.shadow.bound(visible)

    def update(self):
        super().update()
        self.shadow.place(self.vec.x, self.vec.y)

    def hit(self, damage, hitter=None):
        r = super().hit(damage, hitter)
        if r == 2:
            from src.entity.unit.Unit import Unit
            from src.entity.unit.Buff import Buff
            from src.entity.unit.item.Item import Item
            if hitter == self.weapon:
                self.tags.set('sign', 'Suicide')
            elif isinstance(hitter, Humanoid) or (isinstance(hitter, Item) and hitter.host):
                self.tags.set('sign', 'Homicide')
            elif isinstance(hitter, Unit):
                self.tags.set('sign', 'Wildlife')
            elif isinstance(hitter, Buff):
                self.tags.set('sign', 'Illness')
        return r

    def out_of_bounds(self):
        self.tags.set('sign', 'Accident')
        super().out_of_bounds()

    def is_bright(self):
        from src.game import Global
        if Global.player.is_daytime() or self.pos.light > 1:
            return True
        self.say('Too dark!')

    def require_var(self, param, mag, cost=True):
        if not self.tags.require(param, mag, cost):
            self.say('Not enough ' + param + '!')

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
