from src.entity.unit.item.Item import Item
from src.tools.Dialog import Dialog


class Equipment(Item):
    def describe(self):
        r = super().describe()
        stat = self.tags.get('sth')
        if stat:
            r += '\n' + Dialog.get(':equipment_sth', [Dialog.sign(stat)])
        space = self.tags.get('str', 0)
        if space > 0:
            r += '\n' + Dialog.get(':equipment_inv', [Dialog.sign(space)])
        end = self.tags.get('end', 0)
        if end > 0:
            r += '\n' + Dialog.get(':equipment_end', [Dialog.sign(end)])
        cha = self.tags.get('cha', 0)
        if cha > 0:
            r += '\n' + Dialog.get(':equipment_cha', [Dialog.sign(cha)])
        defense = self.tags.get('DEF', 0)
        if defense > 0:
            r += '\n' + Dialog.get(':equipment_def', [Dialog.sign(defense)])
        spd = self.tags.get('spd')
        if spd:
            r += '\n' + Dialog.get(':equipment_spd', [Dialog.sign(spd)])
        cdr = self.tags.get('cdr')
        if cdr:
            r += '\n' + Dialog.get(':equipment_cdr', [Dialog.sign(cdr)])
        fuel = self.tags.get('fuel')
        if fuel and fuel < 0:
            r += '\n' + Dialog.get(':equipment_fire')
        return r

    def use(self):
        self.pos.location.sound.register(self.pos, 0, file='wear')
        self.wear()

    def wear(self, start=False):
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

    def unwear(self):
        self.show(True)
        self.on_unwear()
        self.on_unwield()
        return self

    def on_wear(self):
        self.host.tags.sync('str', self.tags.get('str'))
        self.host.tags.sync('def', self.tags.get('DEF'))
        self.host.tags.sync('sth', self.tags.get('sth'))
        self.host.tags.sync('cha', self.tags.get('cha'))
        self.host.tags.sync('spd', self.tags.get('spd'))
        self.host.tags.sync('P', self.tags.get('end'))
        self.host.tags.sync('abp', self.tags.get('abp'))
        self.host.tags.sync('cdr', self.tags.get('cdr'))
        self.host.tags.sync('fuel', self.tags.get('fuel'))

    def on_unwear(self):
        self.host.tags.sync('str', self.tags.get('str'), ratio=-1)
        self.host.tags.sync('def', self.tags.get('DEF'), ratio=-1)
        self.host.tags.sync('sth', self.tags.get('sth'), ratio=-1)
        self.host.tags.sync('cha', self.tags.get('cha'), ratio=-1)
        self.host.tags.sync('spd', self.tags.get('spd'), ratio=-1)
        self.host.tags.sync('P', self.tags.get('end'), ratio=-1)
        self.host.tags.sync('abp', self.tags.get('abp'), ratio=-1)
        self.host.tags.sync('cdr', self.tags.get('cdr'), ratio=-1)
        self.host.tags.sync('fuel', self.tags.get('fuel'), ratio=-1)

    def on_hit(self, effect=None, sound=None):
        if self.host:
            pass
        else:
            super().on_hit(effect=effect, sound=sound)
