from src.entity.unit.item.Item import Item


class Equipment(Item):
    def use(self):
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
        self.pos.location.sound.register(self.pos, 3, file='wear')
        self.host.tags.sync('str', self.tags.get('str'))
        self.host.tags.sync('def', self.tags.get('DEF'))
        self.host.tags.sync('sth', self.tags.get('sth'))
        self.host.tags.sync('cha', self.tags.get('cha'))
        self.host.tags.sync('spd', self.tags.get('spd'))
        self.host.tags.sync('P', self.tags.get('end'))
        self.host.tags.sync('p', self.tags.get('end'))
        self.host.tags.sync('abp', self.tags.get('abp'))
        team = self.tags.get('team')
        if team:
            self.tags.set('team', self.host.tags.get('team', 0))
            self.host.tags.set('team', team)

    def on_unwear(self):
        self.pos.location.sound.register(self.pos, 3, file='wear')
        self.host.tags.sync('str', self.tags.get('str'), ratio=-1)
        self.host.tags.sync('def', self.tags.get('DEF'), ratio=-1)
        self.host.tags.sync('sth', self.tags.get('sth'), ratio=-1)
        self.host.tags.sync('cha', self.tags.get('cha'), ratio=-1)
        self.host.tags.sync('spd', self.tags.get('spd'), ratio=-1)
        self.host.tags.sync('P', self.tags.get('end'), ratio=-1)
        self.host.tags.sync('p', self.tags.get('end'), ratio=-1, remove=None)
        self.host.tags.sync('abp', self.tags.get('abp'), ratio=-1)
        team = self.tags.get('team')
        if team:
            self.tags.set('team', self.host.tags.get('team', 0))
            self.host.tags.set('team', team)
        self.host.decay(0)
