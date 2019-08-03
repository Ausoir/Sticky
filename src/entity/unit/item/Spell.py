from src.entity.Effect import Effect
from src.entity.unit.item.Item import Item
from src.game import Global


class Spell(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.spell = None
        self.is_known = True

    def __str__(self):
        r = super().__str__()
        r += ',' + self.spell
        return r

    def load(self, p):
        index = super().load(p)
        self.spell = p[index]
        self.is_known = not self.name.startswith('Unknown')
        if self.spell[0] == '?':
            from src.tools.Data import Data
            spells = Data.process_raw(Data.read('data/raw/spells.txt'))
            possible_spells = []
            for spell in spells:
                if spell[0].startswith('Scroll'):
                    possible_spells.append(spell[7])
            self.spell = Global.r.rand_list(possible_spells)
        return index + 1

    def describe(self):
        r = super().describe()
        if not self.is_known:
            if 'Scroll of ' + self.spell in Global.main.player.knowledge:
                self.is_known = True
                self.name = 'Scroll of ' + self.spell
        else:
            r += '\nCasts Spell: ' + self.spell
        return r

    def use(self):
        self.host.action.set('block')
        getattr(self, self.spell.lower())(self.host)
        self.hit(1)

    @staticmethod
    def unknown(host):
        pass

    @staticmethod
    def sonic(host):
        from src.entity.Stock import Stock
        Stock.make('Light', host.get_target_tile())

    @staticmethod
    def dispell(host):
        from src.entity.Prop import Prop
        aoe = host.location.get_area(host.pos[0], 8, 8)
        for i in aoe:
            for thing in i.things:
                Effect.make('energy', thing.vec)
                if isinstance(thing, Prop):
                    thing.hit(0)
                    from src.entity.unit.Buff import BuffTags
                    thing.states.clear(lambda x: x.duration >= 0 and BuffTags.magic in x.tags)

    @staticmethod
    def scorch(host):
        from src.entity.Stock import Stock
        Stock.make('Flame', host.get_offset_tile(host.direction, 0))

    @staticmethod
    def conjure(host):
        rift = host.states.get('Rift')
        if rift:
            Spell.teleport(host)
        else:
            from src.entity.Stock import Stock
            Effect.make('barrier', host.vec)
            r = Stock.get('Portal').add()
            r.relocate(host.pos[0].x, host.pos[0].y - 1, force=1)
            host.states.add('Rift', 160, var=r.id)

    @staticmethod
    def scry(host):
        def effect():
            if host.next_target.distance() > 4:
                r.move(host.next_target.x, host.next_target.y, distance=2)
            if turnee.lifetime <= 1:
                host.center_camera()
                r.remove()
            Effect.make('energy', r.pos[0].get_center())

        from src.entity.Stock import Stock
        from src.tools.Turnee import Turnee
        turnee = Turnee(effect, 40)
        r = Stock.make('Force', host.pos[0])
        r.location.record.remove(r)
        host.states.add('Stun', 40)
        r.center_camera()

    @staticmethod
    def fireblast(host):
        def effect():
            def on_hit(target):
                Effect.make('burn', target.pos[0].get_center(), offset=4, lifetime=40)
                for thing in target.pos[0].things:
                    thing.states.add('Burn', 16)
                r.remove()

            if host.next_target.y > 0:
                y = 1
            elif host.next_target.y < 0:
                y = -1
            else:
                y = 0
            if r.pos[0] == r.move(final_dir, y):
                on_hit(r)
            else:
                r.location.attack.register(0, r.pos[0], faction=0, callback=on_hit)
                Effect.make('explode', r.pos[0].get_center(), offset=4).form.face(final_dir)

        from src.entity.Stock import Stock
        r = Stock.project('g_0x0', host.get_offset_tile(host.direction, 0), 6)
        final_dir = host.direction
        r.effect = effect

    @staticmethod
    def haste(host):
        host.states.add('Haste', 50)

    @staticmethod
    def tornado(host):
        def effect():
            def on_hit(target):
                if r.last_pos.x - r.pos[0].x > 0:
                    target.move(-4, -4)
                else:
                    target.move(4, -4)

            r.last_pos = r.pos[0] + 0
            r.move(host.direction, 0, 1)
            r.location.attack.register(0, r.get_offset_tile(0, -1), faction=0, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(0, 1), faction=0, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(1, 0), faction=0, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(-1, 0), faction=0, callback=on_hit)
            r.location.attack.register(0, r.pos[0], faction=0, callback=on_hit)
            Effect.make('wind', r.pos[0].get_center(), offset=4)

        from src.entity.Stock import Stock
        r = Stock.project('wind', host.get_offset_tile(host.direction, 0), 20)
        r.last_pos = r.pos[0]
        r.effect = effect
        return r

    @staticmethod
    def summon(host):
        rift = host.states.get('Rift')
        if rift:
            from src.entity.Stock import Stock
            r = Stock.get('Summon').add()
            r.relocate(rift.pos[0].x, rift.pos[0].y, force=1)
            Effect.make('zip', r.vec)

    @staticmethod
    def fargate(host):
        from src.entity.Stock import Stock

        def effect():
            flight = placer.pos[0] != placer.move(host.next_target.x, host.next_target.y, 2)
            if not flight or placer.lifetime == 1:
                Effect.make('barrier', placer.vec)
                r = Stock.get('Portal').add()
                r.relocate(placer.pos[0].x, placer.pos[0].y, force=1)
                host.states.add('Rift', 80, var=r.id)
                host.center_camera()
                placer.remove()

        obj = host.states.get('Rift')
        placer = Stock.project('portal', obj.pos[0], 30)
        placer.fast = 0
        host.states.add('Stun', 20)
        placer.effect = effect
        placer.center_camera()

    @staticmethod
    def levitate(host):
        host.states.add('Levitate', 40)

    @staticmethod
    def brand(host):
        Effect.make('burn', host.weapon.vec, offset=0)
        host.weapon.states.add('Fire', 400)

    @staticmethod
    def teleport(host):
        rift = host.states.get('Rift')
        if rift:
            Spell.teleport(host)
        else:
            Effect.make('barrier', host.vec)
            from src.entity.Stock import Stock
            r = Stock.get('Portal').add()
            r.relocate(host.pos[0].x, host.pos[0].y - 1, force=1)
            host.states.add('Rift', 160, var=r.id)

    @staticmethod
    def crystallize(host):
        rift = host.states.get('Rift')
        from src.entity.Stock import Stock
        for i in range(5):
            r1 = Stock.get('Crystal').add()
            r1.relocate(rift.pos[0].x, rift.pos[0].y, force=1)
            r1.states.add('Levitate', 1)
            Effect.make('zip', r1.vec)
            r1.move(Global.r.rand_int(-1, 1), Global.r.rand_int(-1, 0))

    @staticmethod
    def torrent(host):
        host.move(Global.r.rand_int(-4, 4), Global.r.rand_int(-4, 4))
        Spell.dispell(host)
