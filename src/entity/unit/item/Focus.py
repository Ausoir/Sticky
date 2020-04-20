from src.entity.unit.item.Item import Item


class Focus(Item):
    def __init__(self, location):
        super().__init__(location)
        self.catalyst = None
        self.spell = None

    def __str__(self):
        r = super().__str__()
        r += ',' + self.catalyst + ',' + self.spell
        return r

    def load(self, p):
        index = super().load(p)
        self.catalyst = p[index]
        index += 1
        self.spell = p[index]
        return index + 1

    def get_description(self):
        from src.tools.Data import Data
        return Data.get_line('descriptions.txt', self.spell)

    def describe(self):
        r = super().describe().replace('Durability', 'Number of casts')
        r += '\nCasts Spell: ' + self.spell
        return r

    def get_value(self):
        price = super().get_value()
        from src.tools.Data import Data
        ingreds = Data.get_line('recipes.txt', self.name)
        if ingreds:
            for i in ingreds[1]:
                from src.entity.Stock import Stock
                item = Stock.get(self.location, i)
                price += item.get_value()
        return super().get_value() + ingreds + 1

    def hit(self, damage, hitter=None):
        if damage > 0 and self.catalyst == 'Potion':
            from src.entity.Stock import Stock
            r = Stock.make('Mine', self.pos)
            r.spell = self.spell
        return super().hit(damage, hitter)

    def use(self):
        if self.host:
            from src.entity.unit.item.Spell import Spell
            Spell.cast(self.host, self.catalyst, self.spell, callback=self.consume)

    def consume(self):
        self.decay(1)
