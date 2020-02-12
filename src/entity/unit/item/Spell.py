from src.entity.Particle import Particle
from src.entity.unit.item.Item import Item
from src.game import Global
from src.tools import Direction


class Spell(Item):
    def __init__(self):
        super().__init__()
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

    def use(self):
        if self.catalyst != 'Scroll' or Global.player.character.is_bright():
            self.host.action.set('cast')
            self.host.action.on_finish = self.cast

    def cast(self):
        Spell.perform(self.host, self.spell)
        self.decay(1)

    @staticmethod
    def perform(host, spell):
        getattr(Spell, spell.lower())(host)

    @staticmethod
    def marker(host):
        marker = Global.location.population.get_from_name(Global.location.population.other, 'Marker')
        while marker:
            marker.remove()
            marker = Global.location.population.get_from_name(Global.location.population.other, 'Marker')
        from src.entity.Stock import Stock
        Stock.make('Marker', host.pos)

    @staticmethod
    def dispel(host):
        aoe = Global.location.get_area(host.pos, 8, 8)
        for i in aoe:
            for thing in i.things:
                Particle.make('sonic', thing.vec)
                thing.hit(0)
                if not thing.states.get('Immune'):
                    from src.entity.unit.Buff import BuffTags
                    thing.states.clear(lambda x: BuffTags.magic in x.tags)
        Global.location.sound.register(host.pos, 8, file='void')
        if host == Global.player.character:
            Global.player.set_darkness()

    @staticmethod
    def gravity(host):
        def test():
            Global.location.sound.register(host.pos, 8, file='twist')
            if turnee.lifetime % 2 == 0:
                units = Global.location.population.get_all()
                for unit in units:
                    if (unit.pos - host.pos).difference() <= 12:
                        Particle.make('zwip', unit.vec)
                        unit.move_toward(unit.get_direction_toward(host.pos))
        from src.tools.Turnee import Turnee
        turnee = Turnee(test, 80)

    @staticmethod
    def glow(host):
        front = host.get_front_tile(host.direction, mag=6)
        aoe = Global.location.get_area(front, 5, 5)
        for tile in aoe:
            for thing in tile.things:
                glow = thing.states.get('Glow')
                if glow:
                    thing.states.add('Glow', -1, min(7, glow.var + 3))
                else:
                    thing.states.add('Glow', -1, 1)

    @staticmethod
    def scorch(host):
        from src.entity.Stock import Stock
        Global.location.sound.register(host.pos, 9, file='fire')
        Stock.make('Flame', host.get_front_tile(host.direction))

    @staticmethod
    def bread(host):
        from src.entity.Stock import Stock
        bread = Stock.make('Bread', host.pos)
        host.drop()
        bread.on_equip(host)

    @staticmethod
    def slime(host):
        host.states.add('Shapeshift', -1, 'Slime')

    @staticmethod
    def darkness(host):
        def casting():
            if turnee.lifetime == 0:
                Global.player.set_darkness()
                Global.map_view.on_sight_change()
            elif turnee.lifetime % 2 == 0:
                Global.overlay.weather = [50, 15, 15, 160]
                new = max(4, Global.map_view.sight_range - 1)
                if Global.map_view.sight_range != new:
                    Global.map_view.sight_range = new
                    Global.map_view.view_range = Global.map_view.sight_range + 4
                    Global.map_view.on_sight_change()
        from src.tools.Turnee import Turnee
        turnee = Turnee(casting, 60)

    @staticmethod
    def scry(host):
        def effect():
            coord = Direction.coord[host.direction]
            r.move(coord[0], coord[1], flag=[Tile.COLLIDE_MAGIC])
            if turnee.lifetime == 1:
                Global.player.set_darkness()
                Global.map_view.on_sight_change()
                host.center_camera()
                r.remove()
            Particle.make('sonic', r.pos.get_center())
        from src.map.Tile import Tile
        from src.entity.Stock import Stock
        from src.tools.Turnee import Turnee
        Global.overlay.weather = [45, 25, 75, 160]
        Global.map_view.sight_range = 13
        Global.map_view.view_range = 13
        Global.map_view.on_sight_change()
        turnee = Turnee(effect, 60)
        host.states.add('Speed', 60, var=-12)
        r = Stock.make('Force', host.pos)
        Global.location.population.remove(r)
        r.center_camera()

    @staticmethod
    def blink(host):
        def effect():
            coord = Direction.coord[host.direction]
            r.move(coord[0], coord[1], flag=[Tile.COLLIDE_MAGIC])
            if turnee.lifetime == 1:
                host.relocate(r.pos.x, r.pos.y, force=1)
                host.center_camera()
                r.remove()
        from src.map.Tile import Tile
        from src.entity.Stock import Stock
        from src.tools.Turnee import Turnee
        turnee = Turnee(effect, 16)
        host.states.add('Speed', 16, var=-12)
        r = Stock.make('Force', host.pos)
        Global.location.population.remove(r)
        r.center_camera()

    @staticmethod
    def restoration(host):
        aoe = Global.location.get_area(host.pos, 6, 6)
        for i in aoe:
            for thing in i.things:
                Particle.make('heal', thing.vec)
                i.states.add('Health', 100, 1)

    @staticmethod
    def haste(host):
        host.states.add('Speed', -2, 1)

    @staticmethod
    def invisibility(host):
        host.states.add('Invisible', -2, 2)

    @staticmethod
    def barkskin(host):
        host.states.add('Barkskin', -1)

    @staticmethod
    def dog(host):
        host.states.add('Shapeshift', -1, 'Dog')

    @staticmethod
    def charm(host):
        for i in host.get_front_tile(host.direction).things:
            if not i.tags.get('npc'):
                i.tags.set('npc', 1, add=True)

    @staticmethod
    def purge(host):
        from src.entity.unit.Unit import Unit
        for i in host.get_front_tile(host.direction).things:
            if isinstance(i, Unit):
                i.pilot = host.pilot

    @staticmethod
    def possess(host):
        from src.entity.unit.Unit import Unit
        for i in host.get_front_tile(host.direction).things:
            if isinstance(i, Unit):
                Global.player.character.tags.set('#', 'possess', add=True)
                Global.player.set_player(i)
                i.center_camera()
                break

    @staticmethod
    def ghost(host):
        host.states.add('Shapeshift', 120, 'Ghost')

    @staticmethod
    def stoneskin(host):
        host.states.add('Petrified', -1)

    @staticmethod
    def blizzard(host):
        def test():
            Global.location.sound.register(host.pos, 8, file='twist')
            if turnee.lifetime % 2 == 0:
                for i in [1, 2, 3, 4]:
                    adj = host.get_front_tile(i)
                    Particle.make('wind', adj.get_center())
                    coord = Direction.coord[i]
                    for thing in adj.things.copy():
                        thing.move(coord[0] * 4, coord[1] * 4)
                        Particle.make('mist', thing.vec)
                        thing.states.add('Speed', 80, -12)
        from src.tools.Turnee import Turnee
        turnee = Turnee(test, 80)

    @staticmethod
    def mine(host):
        from src.entity.Stock import Stock
        Global.location.sound.register(host.pos, 5, file='fire')
        Stock.make('Mine', host.get_front_tile(host.direction))

    @staticmethod
    def shockwave(host):
        from src.entity.unit.Actions import Actions
        for i in Global.location.population.get_units():
            if (i.pos - host.pos).difference() < 13:
                Particle.make('spin', i.vec)
                Actions.knockdown(i, time=48)
                i.states.add('Burn', 16)

    @staticmethod
    def wall(host):
        def effect():
            coord = Direction.coord[host.direction]
            if r.pos == r.move(coord[0], coord[1], flag=Tile.CHECK_ANY):
                host.center_camera()
                r.remove()
                return
            Stock.make('Window', r.pos)
            if turnee.lifetime == 1:
                host.center_camera()
                r.remove()
        from src.map.Tile import Tile
        from src.entity.Stock import Stock
        from src.tools.Turnee import Turnee
        turnee = Turnee(effect, 16)
        host.states.add('Speed', 16, var=-12)
        r = Stock.make('Force', host.pos)
        Global.location.population.remove(r)
        r.center_camera()

    @staticmethod
    def zombie(host):
        from src.entity.Stock import Stock
        for i in Global.location.population.other:
            if (i.pos - host.pos).difference() < 13:
                if i.name == 'Corpse':
                    Particle.make('mist', i.vec)
                    Stock.make('Zombie', i.pos)
                    i.remove()

    @staticmethod
    def weapon(host):
        from src.entity.Stock import Stock
        Global.location.sound.register(host.pos, 3, file='wield')
        weapon = Global.r.rand_list(['Stick', 'Bottle', 'Parasol', 'Club', 'Dagger', 'Hammer'])
        r = Stock.make(weapon, host.get_front_tile(host.direction))
        host.drop()
        r.on_equip(host)

    @staticmethod
    def armor(host):
        from src.entity.Stock import Stock
        Global.location.sound.register(host.pos, 3, file='wield')
        armors = ['Casual Wear', 'Green Robe', 'Teal Robe', 'Blue Robe', 'Tuxedo', 'Leather Armor', 'Jumpsuit',
                  'Hat', 'Headband', 'Bandana', 'Beanie', 'Sunglasses', 'Top Hat', 'Cap']
        armor = Global.r.rand_list(armors)
        r = Stock.make(armor, host.get_front_tile(host.direction))
        host.drop()
        r.on_equip(host)

    @staticmethod
    def phantom(host):
        tile = host.get_front_tile(host.direction)
        Particle.make('mist', tile.get_center())
        from src.entity.Stock import Stock
        phantom = Stock.make('Phantom', tile)
        for i in host.pos.things:
            if isinstance(i, Item):
                phantom.set_host(i)
                break

    @staticmethod
    def evacuate(host):
        from src.entity.Space import Space
        host.travel('home', Space())

    @staticmethod
    def banish(host):
        for i in host.get_front_tile(host.direction).things:
            i.states.add('Banish', Global.r.rand_int(30, 90))
