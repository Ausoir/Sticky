from src.entity.unit.item.Item import Item


class Focus(Item):
    def get_description(self):
        from src.tools.Data import Data
        return Data.get_line('descriptions.txt', self.tags.get('spell'))

    def describe(self):
        r = super().describe().replace('Durability', 'Number of casts')
        r += '\nCasts Spell: ' + self.tags.get('spell')
        return r

    def get_value(self):
        return int(self.tags.get('power', 0) / 33) + self.tags.get('p') + super().get_value()

    def use(self):
        if self.host:
            power = self.tags.get('power', 0)
            spell = self.tags.get('spell')
            from src.entity.unit.item.Spell import Spell
            Spell.get(spell, power=power).cast(self.host, delay=12)
            self.decay(1)

    def consume(self):
        self.decay(1)
