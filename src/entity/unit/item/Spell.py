from src.entity.Particle import Particle
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.entity.unit.item.Item import Item
from src.game import Global


class Spell:
    @staticmethod
    def cast(host, catalyst, spell, callback=None):
        def on_cast():
            if catalyst == 'Potion':
                Spell.perform(host.pos, spell)
            elif catalyst in 'Wand':
                if host == Global.player.character:
                    tile = Global.player.control.get_mark()
                    if tile:
                        host.face_toward(tile)
                        Spell.perform(tile, spell)
            elif catalyst == 'Scroll':
                targets = host.location.get_area(host.pos, 6, 4)
                for i in targets:
                    Spell.perform(i, spell)
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
    def perform(tile, spell):
        if hasattr(Spell, spell.lower()):
            getattr(Spell, spell.lower())(tile)
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
    def dispel(pos):
        pos.location.sound.register(pos, 0, file='energy')
        Particle.make('sonic', pos)
        for thing in pos.things.copy():
            thing.hit(0)
            thing.states.clear(lambda x: 'magic' in x.get_tags())

    @staticmethod
    def gravity(pos):
        Particle.make('zwip', pos)
        for i in Spell.get_subjects(pos):
            i.move_line(i.pos.get_cardinal(4, 8))
            diff = abs(i.pos.y - pos.y)
            weight = i.tags.get('w', 1)
            if diff != 8:
                Particle.make('batter', i.pos)
                i.decay(weight)
            from src.entity.unit.Actions import Actions
            Actions.knockdown(i)
            levitate = i.states.get('Levitation')
            if levitate:
                levitate.end()
            else:
                if isinstance(i, Item):
                    if i.enhance(Global.r.rand_int(1, 100)):
                        i.tags.set('w', weight + 1)
            return

    @staticmethod
    def glow(pos):
        Particle.make('shock', pos)
        for i in Spell.get_subjects(pos):
            glow = i.states.get('Glow')
            if glow:
                i.states.add('Glow', -1, glow.var + 3)
            else:
                i.states.add('Glow', -1, 1)
            return

    @staticmethod
    def scorch(pos):
        pos.location.sound.register(pos, 9, file='fire')
        Stock.make('Flame', pos)

    @staticmethod
    def bread(pos):
        pos.location.sound.register(pos, 3, file='spell')
        Stock.make('Bread', pos)

    @staticmethod
    def scry(pos):
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
    def vision(pos):
        for i in pos.things:
            if isinstance(i, Unit):
                i.states.add('Vision', -1)

    @staticmethod
    def passwall(pos):
        for i in pos.things:
            if isinstance(i, Unit):
                from src.map.Tile import Tile
                front = i.pos.get_cardinal(i.direction)
                if front.speed == -10:
                    i.move_line(front, flag=[Tile.COLLIDE_MAGIC])
                    return

    @staticmethod
    def gateway(pos):
        for i in pos.things:
            if i.name == 'Door':
                pos.location.sound.register(pos, 9, file='void')
                Particle.make('portal', pos)
                return

    @staticmethod
    def restoration(pos):
        Particle.make('heal', pos)
        for i in Spell.get_subjects(pos):
            i.states.add('Health', 70, 1)
            if isinstance(i, Unit):
                if i.pilot.priority > 1:
                    from src.entity.unit.Actions import Actions
                    Actions.knockdown(i, 80)
            return

    @staticmethod
    def haste(pos):
        for i in Spell.get_subjects(pos):
            if isinstance(i, Item) and i.tags.get('enc', 0) < 0 and i.enhance(Global.r.rand_int(1, 100)):
                i.tags.increment('enc', 1)
            else:
                i.states.add('Speed', -2, 1)
            return

    @staticmethod
    def levitation(pos):
        for i in Spell.get_subjects(pos):
            i.states.add('Levitation', -1)
            if isinstance(i, Item):
                w = i.tags.get('w')
                if w > 1:
                    if i.enhance(Global.r.rand_int(1, 100)):
                        i.tags.increment('w', -1)
            return

    @staticmethod
    def invisibility(pos):
        for i in Spell.get_subjects(pos):
            i.states.add('Invisible', -2, 2)
            return

    @staticmethod
    def charm(pos):
        for i in pos.things:
            if not i.tags.remove('bad'):
                i.pilot.load('ally')

    @staticmethod
    def transience(pos):
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
    def lignify(pos):
        for i in Spell.get_subjects(pos):
            if isinstance(i, Item):
                from src.entity.unit.item.Focus import Focus
                if isinstance(i, Focus):
                    i.catalyst = 'Wand'
                    i.set_form('g_20x4')
                    i.show(True)
                elif i.enhance(Global.r.rand_int(1, 100)):
                    i.tags.increment('DEF', 1)
                else:
                    Stock.make('Plank', pos)
                    i.remove()
            else:
                i.states.add('Lignification', -1)
            return

    @staticmethod
    def petrify(pos):
        for i in Spell.get_subjects(pos):
            if isinstance(i, Item):
                if i.enhance(Global.r.rand_int(1, 100)):
                    i.tags.increment('def', 1)
                else:
                    Stock.make('Rock', pos)
                    i.remove()
            else:
                i.states.add('Petrification', -1)
            return

    @staticmethod
    def disintegrate(pos):
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
    def wall(pos):
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x != 0 or y != 0:
                    tile = pos.get_neighbor(x, y)
                    if tile and not tile.things:
                        Stock.make('Spell Wall', pos)

    @staticmethod
    def zombie(pos):
        from src.entity.Other import Corpse
        pos.location.sound.register(pos, 8, file='void')
        Particle.make('zwip', pos)
        for i in pos.things.copy():
            if isinstance(i, Corpse) or i.name == 'Raw Meat':
                Stock.make('Zombie', i.pos)
                i.remove()
                return

    @staticmethod
    def fog(pos):
        pos.location.sound.register(pos, 3, file='spell')
        for x in range(-1, 2):
            for y in range(-1, 2):
                tile = pos.get_neighbor(x, y)
                if tile and not tile.things:
                    Stock.make('Fog', tile)

    @staticmethod
    def equipment(pos):
        pos.location.sound.register(pos, 3, file='spell')
        armors = ['Casual Wear', 'Teal Robe', 'Tuxedo', 'Leather Armor', 'Jumpsuit', 'Chainmail',
                  'Hat', 'Bandana', 'Beanie', 'Sunglasses', 'Glasses', 'Straw Hat', 'Lace Helm',
                  'Parasol', 'Shortsword', 'Mace', 'Torch', 'Shortsword', 'Katana', 'Rapier', 'Scythe']
        armor = Global.r.rand_list(armors)
        Stock.make(armor, pos)

    @staticmethod
    def phantom(pos):
        pos.location.sound.register(pos, 8, file='void')
        Particle.make('mist', pos)
        for i in pos.things.copy():
            if isinstance(i, Item):
                phantom = Stock.make('Phantom', pos)
                phantom.set_host(i)
                return

    @staticmethod
    def evacuate(pos):
        if Global.player.character.pos == pos:
            Global.player.travel('worldmap')
        else:
            for i in Spell.get_subjects(pos):
                x = Global.r.rand_int(0, i.location.get_width())
                y = Global.r.rand_int(0, i.location.get_height())
                i.relocate(x=x, y=y, force=True)
                return

    @staticmethod
    def slime(pos):
        from src.entity.unit.item.Focus import Focus
        for i in Spell.get_subjects(pos):
            if isinstance(i, Focus):
                i.catalyst = 'Potion'
                i.set_form('g_10x4')
                i.show(True)
            else:
                Spell.shapeshift(i, 'Slime')
            return

    @staticmethod
    def dog(pos):
        for i in Spell.get_subjects(pos):
            Spell.shapeshift(i, 'Dog')
            return

    @staticmethod
    def man(pos):
        for i in Spell.get_subjects(pos):
            Spell.shapeshift(i, 'Human')
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
