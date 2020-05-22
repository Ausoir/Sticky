from src.entity.Prop import Prop
from src.map.Tile import Tile


class Item(Prop):
    def __init__(self, location):
        super().__init__(location)
        self.obstruct_type = Tile.COLLIDE_ITEM
        self.host = None

    def remove(self):
        if self.host:
            if self.host.weapon == self:
                self.host.drop()
            elif self in self.host.inventory.items:
                self.host.inventory.items.remove(self)
        super().remove()

    def on_wield(self, host):
        self.save = False
        self.host = host
        host.weapon = self
        self.host.face(self.host.direction)

    def on_unwield(self):
        self.update_vec()
        self.save = True
        self.host = None

    def get_value(self):
        return self.tags.get('$', 1)

    def use(self):
        self.host.action.attack()

    def on_attack(self, target):
        self.states.trigger(['attack', target])

    def update(self):
        if not self.host:
            super().update()

    def set_row(self, row):
        if not self.host:
            super().set_row(row)

    def enhance(self, rng):
        if rng <= int(100 * (1 / max(1, self.tags.get('mod', 0) + 1))):
            self.tags.increment('mod', 1)
            return True
        else:
            self.die()
        return False

    def get_display_name(self):
        r = super().get_display_name()
        level = self.tags.get('mod', 0)
        if level > 0:
            return r + ' +' + str(level)
        else:
            return r

    def on_sleep(self, time):
        super().on_sleep(time)
        if not self.host:
            thief = self.location.tags.get('thief')
            if thief:
                if self.get_value() >= thief:
                    self.remove()
