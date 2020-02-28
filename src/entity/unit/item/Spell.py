from src.entity.Particle import Particle
from src.entity.unit.item.Item import Item
from src.game import Global
from src.tools import Direction


class Spell:
    @staticmethod
    def perform(host, spell):
        if hasattr(Spell, spell.lower()):
            getattr(Spell, spell.lower())(host)
            return True

    @staticmethod
    def dispel(host):
        Particle.make('sonic', host.pos.get_center())
        for thing in host.pos.things:
            thing.hit(0)
            from src.entity.unit.Buff import BuffTags
            thing.states.clear(lambda x: BuffTags.magic in x.get_tags())
        host.location.sound.register(host.pos, 0, file='energy')

    @staticmethod
    def gravity(host):
        from src.entity.unit.Unit import Unit
        if isinstance(host, Unit):
            direction = host.direction
        else:
            direction = 0
        targets = host.location.population.get_close(host.pos, 13)
        for i in targets:
            if i.tags.get('fly') != 1:
                Particle.make('zip', i.vec)
                old = i.pos
                if direction == 0:
                    direction = Direction.get_direction_toward((i.pos - host.pos).to_list())
                blocked = i.move_toward(direction, distance=8)
                if old != i.pos and blocked:
                    from src.entity.unit.Actions import Actions
                    Actions.knockdown(i)
            else:
                i.tags.remove('fly')

    @staticmethod
    def glow(host):
        Particle.make('shock', host.pos.get_center())
        glow = host.states.get('Glow')
        if glow:
            host.states.add('Glow', -1, glow.var + 3)
        else:
            host.states.add('Glow', -1, 1)

    @staticmethod
    def scorch(host):
        from src.entity.Stock import Stock
        host.location.sound.register(host.pos, 9, file='fire')
        Stock.make('Flame', host.pos)

    @staticmethod
    def bread(host):
        host.location.sound.register(host.pos, 3, file='spell')
        from src.entity.Stock import Stock
        Stock.make('Bread', host.pos)

    @staticmethod
    def slime(host):
        host.states.add('Shapeshift', -1, 'Slime')

    @staticmethod
    def darkness(host):
        def casting():
            if turnee.lifetime == 0:
                Global.player.set_darkness()
            elif turnee.lifetime % 2 == 0:
                Global.map_view.overlay.weather = [50, 15, 15, 160]
                new = max(4, Global.map_view.sight_range - 1)
                if Global.map_view.sight_range != new:
                    Global.map_view.sight_range = new
                    Global.map_view.view_range = Global.map_view.sight_range + 4
                    Global.map_view.on_sight_change()
        host.location.sound.register(host.pos, 0, file='void')
        from src.tools.Turnee import Turnee
        turnee = Turnee(casting, 60)

    @staticmethod
    def scry(host):
        host.states.add('Speed', 60, var=-12)
        if host == Global.player.character:
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
            Global.map_view.overlay.weather = [45, 25, 75, 160]
            Global.map_view.sight_range = 13
            Global.map_view.view_range = 13
            Global.map_view.on_sight_change()
            turnee = Turnee(effect, 60)
            r = Stock.make('Force', host.pos)
            r.center_camera()

    @staticmethod
    def vision(host):
        host.states.add('Vision', 120)

    @staticmethod
    def passwall(host):
        from src.entity.unit.Unit import Unit
        if isinstance(host, Unit):
            from src.map.Tile import Tile
            host.move_toward(host.direction, flag=[Tile.COLLIDE_MAGIC])

    @staticmethod
    def restoration(host):
        Particle.make('heal', host.vec)
        host.states.add('Health', 160, 1)
        from src.entity.unit.Actions import Actions
        Actions.knockdown(host, 80)

    @staticmethod
    def haste(host):
        host.states.add('Speed', -2, 1)

    @staticmethod
    def levitation(host):
        host.states.add('Levitate', -1)

    @staticmethod
    def invisibility(host):
        host.states.add('Invisible', -2, 2)

    @staticmethod
    def charm(host):
        if not host.tags.remove('bad'):
            host.pilot.load('ally')

    @staticmethod
    def transience(host):
        from src.entity.Stock import Stock
        ghost = Stock.make('Ghost', host.pos)
        ghost.set_team(host)
        ghost.states.add('Banish', -1)
        if host == Global.player.character:
            host.save = True
            Global.player.set_player(ghost)
        else:
            host.tags.remove('ai')

    @staticmethod
    def stoneskin(host):
        host.states.add('Petrified', -1)

    @staticmethod
    def disintegrate(host):
        host.location.sound.register(host.pos, 18, file='critical')
        for i in host.pos.things.copy():
            Particle.make('disintegrate', i.vec)
            i.decay(40)

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
        host.location.population.remove(r)
        r.center_camera()

    @staticmethod
    def zombie(host):
        from src.entity.Stock import Stock
        from src.entity.Other import Corpse
        host.location.sound.register(host.pos, 8, file='void')
        for i in host.location.population.other:
            if (i.pos - host.pos).difference() < 10:
                if isinstance(i, Corpse) or i.name == 'Raw Meat':
                    Particle.make('zwip', i.vec)
                    Stock.make('Zombie', i.pos).set_team(host)
                    i.remove()

    @staticmethod
    def weapon(host):
        from src.entity.Stock import Stock
        host.location.sound.register(host.pos, 3, file='spell')
        weapon = Global.r.rand_list(['Stick', 'Bottle', 'Parasol', 'Club', 'Dagger', 'Hammer'])
        r = Stock.make(weapon, host.get_front_tile(host.direction))
        host.drop()
        r.on_wield(host)

    @staticmethod
    def armor(host):
        from src.entity.Stock import Stock
        host.location.sound.register(host.pos, 3, file='spell')
        armors = ['Casual Wear', 'Green Robe', 'Teal Robe', 'Blue Robe', 'Tuxedo', 'Leather Armor', 'Jumpsuit',
                  'Hat', 'Headband', 'Bandana', 'Beanie', 'Sunglasses', 'Top Hat', 'Cap']
        armor = Global.r.rand_list(armors)
        r = Stock.make(armor, host.get_front_tile(host.direction))
        host.drop()
        r.on_wield(host)

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
        phantom.set_team(host)

    @staticmethod
    def evacuate(host):
        from src.entity.Space import Space
        host.travel('home', Space())

    @staticmethod
    def banish(host):
        for i in host.pos.things:
            i.states.add('Banish', Global.r.rand_int(120, 360))

    @staticmethod
    def barkskin(host):
        host.states.add('Barkskin', -1)

    @staticmethod
    def dog(host):
        host.states.add('Shapeshift', -1, 'Dog')

    @staticmethod
    def man(host):
        host.states.add('Shapeshift', -1, 'Human')
