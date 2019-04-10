from src.entity.unit.item.Item import Item
from src.game.Tags import Tags


class Weapon(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.accuracy = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.form.pivot.y) + ',[' + ','.join(str(x) for x in self.range) + '],'\
               + str(self.weight) + ',' + str(self.accuracy)

    def load(self, arg):
        index = super().load(arg)
        self.form.pivot.y = arg[index]
        index += 1
        self.range = arg[index]
        index += 1
        self.weight = arg[index]
        index += 1
        self.accuracy = arg[index]
        return index + 1

    def use(self):
        self.host.action.set('attack')

    def describe(self):
        r = super().describe()
        r += '\nRange: ' + ','.join(str(x) for x in self.range)
        r += '\nStamina Use: ' + str(self.weight)
        r += '\nAccuracy: ' + Weapon.describe_accuracy(self.accuracy)
        if Tags.sharp in self.tags:
            r += '\nThis weapon has a sharp edge.'
        return r

    @staticmethod
    def describe_speed(speed):
        if speed < 3:
            return 'Flurry'
        elif speed == 3:
            return 'Fast'
        elif speed == 4:
            return 'Normal'
        elif speed == 5:
            return 'Slow'
        else:
            return 'Burdening'

    @staticmethod
    def describe_accuracy(acc):
        if acc == 1:
            return 'Normal'
        elif acc == 2:
            return 'Accurate'
        elif acc >= 3:
            return 'Precise'
        else:
            return 'Inaccurate'

    def get_value(self):
        if self.durability == -1:
            hp = 3
        elif self.durability > 32:
            hp = 2
        elif self.durability > 16:
            hp = 1
        else:
            hp = 0
        range = len(self.range)
        if 1 in self.range:
            range += 1
        other = 0
        if 'shp' in self.tags:
                other += 1
        if 'is' in self.tags:
                other += 1
        weight = int((self.weight + 1) / 2)
        score = hp + other + range + self.accuracy - weight
        return score

    def die(self):
        if Tags.sharp in self.tags:
            self.tags.remove(Tags.sharp)
            self.durability = 8
        else:
            super().die()

    def attack(self, chance, callback=None):
        def cb(target):
            self.hit(1)
            if self.states.get('Fire'):
                target.states.add('Burn', 8)
            if self.states.get('Shock'):
                target.states.add('Stun', 40)
                self.states.get('Shock').end()
            if Tags.sharp in self.tags:
                target.states.add('Bleed', 60)
            if callback:
                callback(target)
        accuracy = chance + self.host.get_proficiency(self.name.lower()) + self.accuracy
        for i in self.range:
            tile = self.host.location.collide_land(self.host.get_interact_pos(),
                                                   self.host.next_target.x, self.host.next_target.y,
                                                   distance=i, flag=[])
            self.location.attack.register(1, tile, type='batter', faction=self.host.faction,
                                          chance=accuracy, callback=cb)
