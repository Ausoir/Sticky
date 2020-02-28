from src.entity.unit.item.Item import Item
from src.game import Global


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

    def describe(self):
        r = super().describe().replace('Durability', 'Number of casts')
        r += '\nCasts Spell: ' + self.spell
        return r

    def get_display_name(self):
        return self.name + ' ' + self.catalyst

    def hit(self, damage, hitter=None):
        if damage > 0 and self.catalyst == 'Potion':
            from src.entity.Stock import Stock
            r = Stock.make('Mine', self.pos)
            r.spell = self.spell
        return super().hit(damage, hitter)

    def use(self):
        if self.catalyst == 'Potion':
            self.host.action.act('eat', time=4)
            self.host.action.on_finish = self.use_potion
        elif self.catalyst == 'Wand':
            self.host.action.act('cast', time=12)
            self.host.action.on_finish = self.use_wand
        elif self.catalyst == 'Scroll' and Global.player.is_bright():
            self.host.action.act('cast', time=12)
            self.host.action.on_finish = self.use_scroll

    def use_scroll(self):
        if self.host:
            targets = self.host.location.population.get_close(self.host.pos, 13)
            for i in targets:
                from src.entity.unit.item.Spell import Spell
                Spell.perform(i, self.spell)
            self.decay(1)
        return True

    def use_wand(self):
        if self.host:
            if self.host == Global.player.character:
                tile = Global.player.control.get_mark()
                if tile:
                    for i in tile.things:
                        from src.entity.unit.item.Spell import Spell
                        Spell.perform(i, self.spell)
                        self.decay(1)
                        return
        return True

    def use_potion(self):
        if self.host:
            from src.entity.unit.item.Spell import Spell
            Spell.perform(self.host, self.spell)
            self.decay(1)
        return True
