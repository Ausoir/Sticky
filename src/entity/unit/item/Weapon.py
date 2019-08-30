from src.entity.unit.item.Equipment import Equipment


class Weapon(Equipment):
    def __str__(self):
        return super().__str__() + ',' + str(self.form.pivot.y) + ',[' + ','.join(str(x) for x in self.range) + '],' \
               + str(self.damage) + ',' + str(self.speed)

    def load(self, arg):
        index = super().load(arg)
        self.form.pivot.y = arg[index]
        index += 1
        self.range = arg[index]
        index += 1
        self.damage = arg[index]
        index += 1
        self.speed = arg[index]
        return index + 1

    def set_form(self, arg):
        if not self.form:
            super().set_form(arg)

    def on_unequip(self):
        self.form.rotate(0)
        super().on_unequip()

    def describe(self):
        r = super().describe()
        r += '\nRange: ' + ','.join(str(x) for x in self.range)
        r += '\nAttack: ' + str(self.damage)
        r += '\nDamage: ' + str(self.weight)
        r += '\nSpeed: ' + Weapon.describe_speed(self.speed)
        return r

    @staticmethod
    def describe_speed(speed):
        if speed < 2:
            return 'Flurry'
        elif speed == 2:
            return 'Fast'
        elif speed == 3:
            return 'Normal'
        elif speed == 4:
            return 'Slow'
        elif speed > 4:
            return 'Very Slow'

    def get_value(self):
        if self.durability == -1:
            hp = 4
        else:
            if self.max_durability >= 16:
                hp = 1
            elif self.max_durability >= 32:
                hp = 2
            elif self.max_durability >= 64:
                hp = 3
            else:
                hp = 0
        reach = len(self.range)
        other = 0
        if 'ps' in self.tags:
            other += 1
        if 'is' in self.tags:
            other += 1
        damage = int(self.damage / 2)
        score = hp + other + reach + damage - self.weight - self.speed
        return score
