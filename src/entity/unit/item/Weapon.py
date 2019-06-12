from src.entity.unit.item.Item import Item
from src.game.Tags import Tags


class Weapon(Item):
    def __str__(self):
        return super().__str__() + ',' + str(self.form.pivot.y) + ',[' + ','.join(str(x) for x in self.range) + '],' \
               + str(self.weight) + ',' + str(self.damage) + ',' + str(self.speed)

    def load(self, arg):
        index = super().load(arg)
        self.form.pivot.y = arg[index]
        index += 1
        self.range = arg[index]
        index += 1
        self.weight = arg[index]
        index += 1
        self.damage = arg[index]
        index += 1
        self.speed = arg[index]
        return index + 1

    def use(self):
        self.host.action.set('attack')

    def describe(self):
        r = super().describe()
        r += '\nRange: ' + ','.join(str(x) for x in self.range)
        r += '\nWeight: ' + str(self.weight)
        r += '\nDamage: ' + str(self.damage)
        r += '\nSpeed: ' + Weapon.describe_speed(self.speed)
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

    def get_value(self):
        if self.durability == -1:
            hp = 3
        else:
            hp = min(2, int(self.durability / 8))
        reach = len(self.range)
        if 1 in self.range:
            reach += 1
        other = 0
        if 'ps' in self.tags:
            other += 1
        if 'is' in self.tags:
            other += 1
        weight = int((self.weight + 1) / 2)
        score = hp + other + reach + self.damage - weight
        return score

    def die(self):
        if Tags.sharp in self.tags:
            self.tags.remove(Tags.sharp)
            self.durability = 8
        else:
            super().die()
