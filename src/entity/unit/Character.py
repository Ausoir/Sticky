from src.entity.unit.Humanoid import Humanoid


class Character(Humanoid):
    def __init__(self, location):
        super().__init__(location)
        from src.tools.Data import Data
        self.shadow = Data.get_form('g_7x0')
        self.shadow.bound(True)

    def add(self):
        r = super().add()
        self.shadow.show(True)
        return r

    def remove(self):
        super().remove()
        self.shadow.show(False)

    def show(self, visible):
        super().show(visible)
        self.shadow.show(visible)

    def set_row(self, row):
        super().set_row(row)
        self.shadow.z = row * 20 + 100

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
            if isinstance(hitter, Humanoid) or (isinstance(hitter, Item) and hitter.host):
                self.tags.set('sign', 'Homicide')
            elif isinstance(hitter, Unit):
                self.tags.set('sign', 'Wildlife')
            elif isinstance(hitter, Buff):
                self.tags.set('sign', 'Illness')
        return r

    def out_of_bounds(self):
        self.tags.set('sign', 'Accident')
        super().out_of_bounds()
