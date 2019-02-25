from src.entity.unit.item.Item import Item
from src.game.Tags import Tags


class Weapon(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.weight = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.form.pivot.y) + ',[' + ','.join(str(x) for x in self.range) + '],'\
               + str(self.weight)

    def load(self, arg):
        index = super().load(arg)
        self.form.pivot.y = arg[index]
        index += 1
        self.range = arg[index]
        index += 1
        self.weight = arg[index]
        return index + 1

    def use(self):
        self.host.action.set('attack')

    def describe(self):
        r = super().describe()
        r += '\nWeight: ' + str(self.weight)
        r += '\nRange: ' + ','.join(str(x) for x in self.range)
        if Tags.sharp in self.tags:
            r += '\nThis weapon has a sharp edge.'
        return r

    def attack(self, delay=0, callback=None):
        def cb(target):
            self.hit(1)
            if self.states.get('fire'):
                target.states.add('burn', 4)
            if Tags.sharp in self.tags:
                target.states.add('bleed', 80)
            if callback:
                callback()
        for i in self.range:
            tile = self.host.location.collide_line(self.host.get_interact_pos(),
                                                   self.host.next_target.x, self.host.next_target.y,
                                                   distance=i, flag=[])
            self.location.attack.register(1, tile, delay, 'batter',
                                          faction=self.host.faction, callback=cb)
