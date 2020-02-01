from src.entity.Particle import Particle
from src.entity.unit.item.Item import Item
from src.game import Global
from src.tools import Direction


class Spell(Item):
    def __init__(self, loc):
        super().__init__(loc)
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
        if self.spell in Item.description:
            r += '\n' + Item.description[self.spell]
        return r

    def use(self):
        if self.catalyst != 'Scroll' or Global.player.character.is_bright():
            self.host.action.set('wait')
            self.host.action.on_finish = self.cast

    def cast(self):
        Spell.perform(self.host, self.spell)
        self.decay(1)

    @staticmethod
    def perform(host, spell):
        getattr(Spell, spell.lower())(host)

    @staticmethod
    def dispell(host):
        aoe = host.location.get_area(host.pos, 8, 8)
        for i in aoe:
            for thing in i.things:
                Particle.make('sonic', thing.vec)
                thing.hit(0)
                if not thing.states.get('Immune'):
                    from src.entity.unit.Buff import BuffTags
                    thing.states.clear(lambda x: BuffTags.magic in x.tags)
        host.location.sound.register(host.pos, 8, file='void')
        if host == Global.player.character:
            Global.player.set_darkness()

    @staticmethod
    def scry(host):
        def effect():
            coord = Direction.coord[host.direction]
            r.move(coord[0], coord[1], flag=[Tile.COLLIDE_MAGIC])
            if turnee.lifetime == 1:
                host.center_camera()
                r.remove()
            Particle.make('sonic', r.pos.get_center())
        from src.map.Tile import Tile
        from src.entity.Stock import Stock
        from src.tools.Turnee import Turnee
        turnee = Turnee(effect, 60)
        host.states.add('Speed', 60, var=0)
        r = Stock.make('Force', host.pos)
        r.location.record.remove(r)
        r.center_camera()

    @staticmethod
    def scorch(host):
        from src.entity.Stock import Stock
        host.location.sound.register(host.pos, 5, file='fire')
        Stock.make('Flame', host.get_front_tile(host.direction))

    @staticmethod
    def tornado(host):
        def test():
            host.location.sound.register(host.pos, 8, file='twist')
            if turnee.lifetime % 2 == 0:
                for i in [1, 2, 3, 4]:
                    adj = host.get_front_tile(i)
                    Particle.make('wind', adj.get_center())
                    coord = Direction.coord[i]
                    for thing in adj.things:
                        thing.move(coord[0], coord[1])
        from src.tools.Turnee import Turnee
        turnee = Turnee(test, 60)

    @staticmethod
    def summon(host):
        things = []
        things += host.pos.things
        things += host.get_offset_tile(-1, 0).things
        things += host.get_offset_tile(1, 0).things
        for thing in things:
            if isinstance(thing, Item):
                from src.entity.Stock import Stock
                r = Stock.make('Summon', host.pos)
                Particle.make('zwip', r.vec)
                return

    @staticmethod
    def crystallize(host):
        def casting():
            crystal = Stock.make('Crystal', host.pos)
            crystal.move(host.next_target.x, host.next_target.y)
            Particle.make('zip', crystal.vec)
        from src.entity.Stock import Stock
        channel = host.states.add('Channel', 8)
        channel.on_update = casting

    @staticmethod
    def darkness(host):
        def casting():
            if turnee.lifetime % 4 == 0:
                Particle.make('spin', host.vec, glow=-1)
                Global.draw_group.colorize(1, [30, 0, 0, 60 + (turnee.lifetime * 4)])
                host.location.sight_range = max(4, host.location.sight_range - 1)
                host.location.view_range = host.location.sight_range
                Global.map_view.on_sight_change()
            if turnee.lifetime == 1:
                Global.player.set_darkness()
                Global.map_view.on_sight_change()
        from src.tools.Turnee import Turnee
        turnee = Turnee(casting, 60)

    @staticmethod
    def haste(host):
        host.states.add('Speed', 240, var=1)

    @staticmethod
    def evacuate(host):
        if host == Global.player.character:
            from src.entity.Space import Space
            Global.player.travel('home', Space())

    @staticmethod
    def charm(host):
        tile = host.get_front_tile(host.direction)
        Particle.make('heal', tile.get_center())
        for i in tile.things:
            i.tags.set('team', host.faction)
