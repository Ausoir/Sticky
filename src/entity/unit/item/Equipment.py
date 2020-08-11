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
        self.location.sound.register(self.pos, 3, file='wear')
        self.host.tags.sync('str', self.tags.get('str'))
        self.host.tags.sync('def', self.tags.get('DEF'))
        self.host.tags.sync('sth', self.tags.get('sth'))
        self.host.tags.sync('sth', self.tags.get('sth'))
        self.host.tags.sync('spd', self.tags.get('spd'))
        self.host.tags.sync('P', self.tags.get('end'))
        self.host.tags.sync('p', self.tags.get('end'))

    def on_unwear(self):
        self.location.sound.register(self.pos, 3, file='wear')
        self.host.tags.sync('str', self.tags.get('str'), ratio=-1)
        self.host.tags.sync('def', self.tags.get('DEF'), ratio=-1)
        self.host.tags.sync('sth', self.tags.get('sth'), ratio=-1)
        self.host.tags.sync('spd', self.tags.get('spd'), ratio=-1)
        self.host.tags.sync('P', self.tags.get('end'), ratio=-1)
        self.host.tags.sync('p', self.tags.get('end'), ratio=-1)
