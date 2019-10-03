from src.entity.unit.item.Equipment import Equipment


class Weapon(Equipment):
    def __str__(self):
        return super().__str__() + ',' + str(self.form.pivot.y) + ',' + str(self.reach) + ',' \
               + str(self.accuracy) + ',' + str(self.speed)

    def load(self, arg):
        index = super().load(arg)
        self.form.pivot.y = arg[index]
        index += 1
        self.reach = arg[index]
        index += 1
        self.accuracy = arg[index]
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
        r += '\nRange: ' + str(self.reach)
        r += '\nAttack: ' + str(self.accuracy)
        r += '\nDamage: ' + str(self.damage)
        r += '\nSpeed: ' + Weapon.describe_speed(self.speed)
        return r

    @staticmethod
    def describe_speed(speed):
        if speed < 2:
            return 'Flurry'
        elif speed == 2:
            return 'Very Fast'
        elif speed == 3:
            return 'Fast'
        elif speed == 4:
            return 'Normal'
        elif speed == 5:
            return 'Slow'
        elif speed > 5:
            return 'Very Slow'

    def get_value(self):
        if self.max_durability == -1:
            hp = 2
        elif self.max_durability >= 24:
            hp = 1
        else:
            hp = int((24 - self.max_durability) / 8)
        if self.accuracy <= 1:
            damage = 0
        elif self.accuracy <= 3:
            damage = 1
        else:
            damage = 2
        other = 0
        if 'ps' in self.tags:
            other += 1
        if 'is' in self.tags:
            other += 1
        from src.entity.unit.item.Item import Item
        score = Item.get_value(self) + hp + other + self.reach + damage - self.speed - self.weight + 5
        return max(1, score)
