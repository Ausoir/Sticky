from src.entity.unit.item.Equipment import Equipment


class Headgear(Equipment):
    def die(self):
        if self.host:
            self.host.unheadgear()
        super().die()

    def use(self):
        self.host.headgear = self
        host = self.host
        if self.host.weapon == self:
            self.host.drop()
        self.remove()
        host.update_durability(0)
        self.host = host
        self.host.action.set('wait')

    def activate(self):
        self.host.action.set('wait')
