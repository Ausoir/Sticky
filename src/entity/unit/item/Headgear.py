from src.entity.unit.item.Equipment import Equipment


class Headgear(Equipment):
    def die(self):
        if self.host:
            self.host.unheadgear()
        super().die()

    def use(self):
        self.host.action.set('wait')
        if self.host.attributes.agility >= self.weight + self.host.armor.weight:
            self.host.headgear = self
            host = self.host
            if self.host.weapon == self:
                self.host.drop()
            self.remove()
            host.update_durability(0)
            self.host = host
        else:
            self.host.say('Total encumbrance exceeds Agility!')

    def set_form(self, arg):
        from src.tools.Data import Data
        from src.game import Global
        self.form_name = arg
        self.form = Data.get_form(arg, group=Global.draw_group.units)

    def activate(self):
        self.host.action.set('wait')
