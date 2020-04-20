from src.entity.unit.item.Item import Item
from src.tools.Dialog import Dialog


class Equipment(Item):
    def describe(self):
        r = super().describe()
        spd = self.tags.get('enc', 0)
        if spd:
            r += '\n' + Dialog.get('equipment_spd', [Dialog.sign(spd)])
        space = self.tags.get('space', 0)
        if space > 0:
            r += '\n' + Dialog.get('equipment_inv', [Dialog.weight(space)])
        defense = self.tags.get('DEF', 0)
        if defense:
            r += '\n' + Dialog.get('equipment_def', [Dialog.sign(defense)])
        skill = self.tags.get('skill')
        if skill:
            r += '\n' + Dialog.get('equipment_skill', [skill.title()])
        return r

    def use(self):
        self.wear()

    def wear(self, start=False):
        self.show(False)
        if self.host.weapon == self:
            host = self.host
            self.host.drop()
            self.host = host
        if not start:
            self.host.action.act('grab', 8)
            self.on_wear()
        host = self.host
        if self.host.weapon == self:
            self.host.drop()
        self.save = False
        self.host = host
        self.host.face(self.host.direction)

    def remove(self):
        if self.host:
            self.unwear()
        super().remove()

    def unwear(self):
        self.show(True)
        self.on_unwear()
        self.on_unwield()
        return self

    def on_wear(self):
        self.host.update_skill(self.tags.get('skill'))
        self.location.sound.register(self.pos, 3, file='wear')
        self.host.tags.sync('silver', self.tags.get('silver'))
        self.host.tags.sync('DEF', self.tags.get('DEF'))
        self.host.tags.sync('spd', self.tags.get('enc'))
        self.host.tags.sync('p', self.tags.get('hp'))
        self.host.tags.sync('P', self.tags.get('hp'))

    def on_unwear(self):
        self.host.update_skill(self.tags.get('skill'), remove=True)
        self.location.sound.register(self.pos, 3, file='wear')
        self.host.tags.sync('silver', self.tags.get('silver'), ratio=-1)
        self.host.tags.sync('DEF', self.tags.get('DEF'), ratio=-1)
        self.host.tags.sync('spd', self.tags.get('enc'), ratio=-1)
        self.host.tags.sync('p', self.tags.get('hp'), ratio=-1)
        self.host.tags.sync('P', self.tags.get('hp'), ratio=-1)
