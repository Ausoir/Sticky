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
        if damage > 0 and self.tags.get('catalyst') == 'Potion' and self.pos.get_yield() > -9:
            from src.entity.Stock import Stock
            r = Stock.make('Mine', self.pos)
            r.spell = self.tags.get('spell')
        return super().hit(damage, hitter)

    def use(self):
        if self.host:
            catalyst = self.tags.get('catalyst')
            power = self.tags.get('power', 0)
            spell = self.tags.get('spell')
            from src.entity.unit.item.Spell import Spell
            if catalyst == 'potion':
                Spell.get(spell, power=power, on_self=True).cast(self.host, motion='eat')
            else:
                Spell.get(spell, power=power).cast(self.host, delay=12)
            self.decay(1)

    def consume(self):
        self.decay(1)
