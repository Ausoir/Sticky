from src.entity.unit.item.Item import Item


class Focus(Item):
    def describe(self):
        spell = self.tags.get('spell').title()
        r = super().describe().replace('Durability', 'Number of casts')
        r += '\nCasts Spell: ' + spell
        from src.tools.Data import Data
        line = Data.get_line('descriptions.txt', spell)
        if line:
            r += '\n' + line[1]
        return r

    def get_value(self):
        v = self.tags.get('$')
        if v:
            return v
        else:
            r = 2
            r += int(self.tags.get('p') / 2)
            r += int(self.tags.get('power', 0) / 50)
            return max(1, r - self.tags.get('w', 1))

    def use(self):
        if self.host:
            power = self.tags.get('power', 0)
            spell = self.tags.get('spell')
            from src.entity.unit.item.Spell import Spell
            Spell.get(spell, power=power).cast(self.host)
            self.decay(1)

    def consume(self):
        self.decay(1)
