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
        if damage > 0 and self.tags.get('catalyst') == 'Potion' and self.pos.speed > -9:
            from src.entity.Stock import Stock
            r = Stock.make('Mine', self.pos)
            r.spell = self.tags.get('spell')
        return super().hit(damage, hitter)

    def use(self):
        if self.host:
            power = self.tags.get('power', 50)
            spell = self.tags.get('spell')
            catalyst = self.tags.get('catalyst')
            from src.entity.unit.item.Alchemy import Alchemy
            Alchemy.cast(self.host, catalyst, spell, power, callback=self.consume)

    def consume(self):
        self.decay(1)
