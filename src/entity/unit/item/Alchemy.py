from src.entity.Particle import Particle
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.entity.unit.item.Item import Item
from src.game import Global


class Alchemy:
    @staticmethod
    def cast(host, catalyst, spell, power, callback=None):
        def on_cast():
            if catalyst == 'Potion':
                Alchemy.perform(host.pos, spell, power)
            elif catalyst in 'Wand':
                if host == Global.player.character:
                    tile = Global.player.control.get_mark()
                    if tile:
                        host.face_toward(tile)
                        Alchemy.perform(tile, spell, power)
            elif catalyst == 'Scroll':
                targets = host.pos.get_area(6, 4)
                for i in targets:
                    Alchemy.perform(i, spell, power)
            if callback:
                callback()
            return True
        if catalyst == 'Potion':
            host.action.act('eat', time=4)
            host.action.on_finish = on_cast
        elif catalyst == 'Wand':
            host.action.act('cast', time=12)
            host.action.on_finish = on_cast
        elif catalyst == 'Scroll' and Global.player.is_bright():
            host.action.act('cast', time=12)
            host.action.on_finish = on_cast

    @staticmethod
    def perform(tile, spell, power):
        if hasattr(Alchemy, spell.lower()):
            getattr(Alchemy, spell.lower())(tile, max(0, min(100, power)))
            return True

    @staticmethod
    def get_subjects(pos):
        units = []
        props = []
        from src.entity.unit.Unit import Unit
        for i in pos.things:
            if isinstance(i, Unit):
                units.append(i)
            else:
                props.append(i)
        return units + props

    @staticmethod
    def dispel(pos, power):
        pos.location.sound.register(pos, 0, file='energy')
        magnitude = int(power / 10)
        targets = pos.get_area(magnitude, magnitude)
        for i in targets:
            Particle.make('sonic', i)
            for thing in i.things.copy():
                thing.hit(0)
                thing.states.clear(lambda x: 'magic' in x.get_tags())

    @staticmethod
    def glow(pos, power):
        Particle.make('shock', pos)
        for i in Alchemy.get_subjects(pos):
            glow = i.states.get('Glow')
            if glow:
                i.states.add('Glow', -1, glow.var + 3)
            else:
                i.states.add('Glow', -1, 1)
            return

    @staticmethod
    def scorch(pos, power):
        pos.location.sound.register(pos, 9, file='fire')
        Stock.make('Flame', pos)

    @staticmethod
    def scry(pos, power):
        if pos == Global.player.character.pos:
            def effect():
                to = r.pos.get_cardinal(Global.player.character.direction)
                r.move_line(to, flag=[Tile.COLLIDE_MAGIC])
                if turnee.lifetime == 0:
                    Global.map_view.overlay.weather = orig[0]
                    Global.map_view.set_sight_range(orig[1])
                    Global.map_view.set_view_range(orig[2])
                    Global.map_view.on_sight_change()
                    Global.player.character.center_camera()
                    r.remove()
                Particle.make('sonic', r.pos)
            Global.player.character.states.add('Speed', 60, var=-12)
            from src.map.Tile import Tile
            from src.tools.Turnee import Turnee
            orig = [Global.map_view.overlay.weather, Global.map_view.sight_range, Global.map_view.view_range]
            Global.map_view.overlay.weather = [45, 25, 75, 160]
            Global.map_view.set_sight_range(13)
            Global.map_view.set_view_range(13)
            Global.map_view.on_sight_change()
            turnee = Turnee(effect, 60)
            r = Stock.make('Force', pos)
            r.center_camera()

    @staticmethod
    def vision(pos, power):
        for i in pos.things:
            if isinstance(i, Unit):
                i.states.add('Vision', -1)

    @staticmethod
    def passwall(pos, power):
        for i in pos.things:
            if isinstance(i, Unit):
                from src.map.Tile import Tile
                front = i.pos.get_cardinal(i.direction)
                if front.speed == -10:
                    i.move_line(front, flag=[Tile.COLLIDE_MAGIC])
                    return

    @staticmethod
    def restoration(pos, power):
        Particle.make('heal', pos)
        for i in Alchemy.get_subjects(pos):
            i.states.add('Health', 70, 1)
            if isinstance(i, Unit):
                if i.pilot.priority > 1:
                    from src.entity.unit.Actions import Actions
                    Actions.knockdown(i, 80)
            return

    @staticmethod
    def haste(pos, power):
        for i in Alchemy.get_subjects(pos):
            if isinstance(i, Item) and i.tags.get('enc', 0) < 0 and i.enhance(Global.r.rand_int(1, 100)):
                i.tags.increment('enc', 1)
            else:
                i.states.add('Speed', -2, 1)
            return

    @staticmethod
    def levitation(pos, power):
        for i in Alchemy.get_subjects(pos):
            i.states.add('Levitation', -1)
            if isinstance(i, Item):
                w = i.tags.get('w')
                if w > 1:
                    if i.enhance(Global.r.rand_int(1, 100)):
                        i.tags.increment('w', -1)
            return

    @staticmethod
    def invisibility(pos, power):
        for i in Alchemy.get_subjects(pos):
            i.states.add('Invisible', -2, 2)
            return

    @staticmethod
    def charm(pos, power):
        for i in pos.things:
            if i.tags.get('team', -1) != -1:
                i.tags.set('team', 0)
                i.pilot.load('ally')

    @staticmethod
    def transience(pos, power):
        from src.entity.unit.Unit import Unit
        for i in pos.things:
            if isinstance(i, Unit):
                ghost = Stock.make('Ghost', pos)
                ghost.set_team(i)
                if i == Global.player.character:
                    i.save = True
                    Global.player.set_player(ghost)
                else:
                    i.tags.remove('ai')
                return

    @staticmethod
    def lignify(pos, power):
        for i in Alchemy.get_subjects(pos):
            if isinstance(i, Item):
                from src.entity.unit.item.Focus import Focus
                if isinstance(i, Focus):
                    i.catalyst = 'Wand'
                    i.set_form('g_20x4')
                    i.show(True)
                elif i.enhance(Global.r.rand_int(1, 100)):
                    i.tags.increment('DEF', 1)
                else:
                    Stock.make('Stick', pos)
                    i.remove()
            else:
                i.states.add('Lignification', -1)
            return

    @staticmethod
    def petrify(pos, power):
        for i in Alchemy.get_subjects(pos):
            if isinstance(i, Item):
                if i.enhance(Global.r.rand_int(1, 100)):
                    i.tags.increment('def', 1)
                else:
                    Stock.make('Chalk', pos)
                    i.remove()
            else:
                i.states.add('Petrification', -1)
            return

    @staticmethod
    def disintegration(pos, power):
        pos.location.sound.register(pos, 18, file='critical')
        Particle.make('disintegrate', pos)
        if pos.speed == -10:
            pos.set_terrain('.')
        else:
            for i in pos.things.copy():
                i.decay(40)
                if i.name == 'Corpse':
                    Stock.make('Raw Meat', i.pos)

    @staticmethod
    def wall(pos, power):
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x != 0 or y != 0:
                    tile = pos.get_neighbor(x, y)
                    if tile and not tile.things:
                        Stock.make('Spell Wall', pos)

    @staticmethod
    def zombie(pos, power):
        from src.entity.Other import Corpse
        pos.location.sound.register(pos, 8, file='void')
        Particle.make('zwip', pos)
        for i in pos.things.copy():
            if isinstance(i, Corpse) or i.name == 'Raw Meat':
                Stock.make('Zombie', i.pos)
                i.remove()
                return

    @staticmethod
    def fog(pos, power):
        pos.location.sound.register(pos, 3, file='spell')
        for x in range(-1, 2):
            for y in range(-1, 2):
                tile = pos.get_neighbor(x, y)
                if tile and not tile.things:
                    Stock.make('Fog', tile)

    @staticmethod
    def find(pos, power):
        pos.location.sound.register(pos, 3, file='spell')
        from src.tools.Data import Data
        armor = Global.r.rand_list(Data.get_line('raw.txt', 'find')[1])
        Stock.make(armor, pos)

    @staticmethod
    def phantom(pos, power):
        pos.location.sound.register(pos, 8, file='void')
        Particle.make('mist', pos)
        for i in pos.things.copy():
            if isinstance(i, Item):
                phantom = Stock.make('Phantom', pos)
                phantom.set_host(i)
                return

    @staticmethod
    def locate(pos, power):
        summon = Stock.make('Mark', pos)
        summon.tags.set('data', pos)

    @staticmethod
    def gateway(pos, power):
        summon = Stock.make('Gateway', pos)
        summon.tags.set('power', power)

    @staticmethod
    def slime(pos, power):
        from src.entity.unit.item.Focus import Focus
        for i in Alchemy.get_subjects(pos):
            if isinstance(i, Focus):
                i.catalyst = 'Potion'
                i.set_form('g_10x4')
                i.show(True)
            else:
                Alchemy.shapeshift(i, 'Slime')
            return

    @staticmethod
    def dog(pos, power):
        for i in Alchemy.get_subjects(pos):
            Alchemy.shapeshift(i, 'Dog')
            return

    @staticmethod
    def man(pos, power):
        for i in Alchemy.get_subjects(pos):
            Alchemy.shapeshift(i, 'Human')
            return

    @staticmethod
    def shapeshift(host, shape):
        if not host.tags.get('silver'):
            from src.entity.unit.Humanoid import Humanoid
            if isinstance(host, Humanoid):
                host.drop()
                host.unarmor()
                host.unheadgear()
                host.inventory.drop_all()
            from src.entity.Stock import Stock
            unit = Stock.make(shape, host.pos)
            unit.tags.remove('ai')
            if isinstance(host, Unit):
                old_host = host
                for i in host.states.buffs:
                    i.host = unit
                unit.states = old_host.states
                unit.skills = old_host.skills
                unit.face(old_host.direction)
                from src.entity.unit.Buffs import Buffs
                old_host.states = Buffs(old_host)
                old_host.remove()
                if old_host == Global.player.character:
                    Global.player.set_player(unit)
                host.location.sound.register(host.pos, 8, file='void')
            else:
                host.remove()
        else:
            host.decay(1)
            Particle.make('sonic', host.pos)
