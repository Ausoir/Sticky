from src.entity.Effect import Effect
from src.entity.Stock import Stock
from src.entity.unit.ai.Faction import Faction
from src.tools.Random import Random


class Spells:
    @staticmethod
    def spellcast(host, cast):
        incantation = ''
        if host.states.get('Air') or host.states.get('Levitate'):
            incantation += 'a'
        if host.states.get('Fire') or host.states.get('Burn'):
            incantation += 'f'
        if host.states.get('Rift'):
            incantation += 'r'
        if cast:
            incantation += 't'
        else:
            incantation += 'c'
        if incantation not in spellbook:
            Effect.make('fail', host.pos[0].get_center())
        else:
            spellbook[incantation](host)

    @staticmethod
    def charm(host):
        Spells.spellcast(host, False)

    @staticmethod
    def cast(host):
        Spells.spellcast(host, True)

    @staticmethod
    def check_rift(host):
        rift = host.states.get('Rift')
        if rift:
            obj = host.location.get_object(rift.var)
            if obj:
                obj.remove()
                rift.end()
                return obj
        return None

    @staticmethod
    def sonic(host):
        Effect.make('energy', host.get_target_tile().get_center())
        aoe = host.location.get_area(host.get_target_tile(), 4)
        for i in aoe:
            for thing in i.things:
                thing.hit(0)

    @staticmethod
    def ignite(host):
        if host.states.get('Fire'):
            Spells.combust(host)
        else:
            host.states.add('Fire', 120)

    @staticmethod
    def combust(host):
        fire = host.states.get('Fire')
        if fire:
            fire.end()
        aoe = host.location.get_area(host.pos[0], 3)
        for i in aoe:
            for thing in i.things:
                thing.states.add('Burn', 8)

    @staticmethod
    def whirlwind(host):
        if host.states.get('Air') or host.states.get('Levitate'):
            Spells.dispell(host)
        else:
            host.states.add('Air', 10)

    @staticmethod
    def dispell(host):
        from src.entity.Prop import Prop
        aoe = host.location.get_area(host.pos[0], 8)
        for i in aoe:
            for thing in i.things:
                Effect.make('energy', thing.vec)
                if isinstance(thing, Prop):
                    thing.hit(0)
                    thing.clean_buffs()

    @staticmethod
    def conjure(host):
        Effect.make('barrier', host.vec)
        r = Stock.get('Portal').add()
        r.relocate(host.pos[0].x, host.pos[0].y - 1, force=1)
        host.states.add('Rift', 160, var=r.id)

    @staticmethod
    def pull(host):
        obj = Spells.check_rift(host)
        if obj:
            aoe = host.location.get_area(obj.pos[0], 8)
            for i in aoe:
                x = 0
                y = 0
                if obj.pos[0].x > i.x:
                    x = 4
                elif obj.pos[0].x < i.x:
                    x = -4
                if obj.pos[0].y > i.y:
                    y = 4
                elif obj.pos[0].y < i.y:
                    y = -4
                for thing in i.things:
                    Effect.make('wind', thing.vec)
                    thing.move(x, y)

    @staticmethod
    def scry(host):
        def effect():
            if host.next_target.distance() > 4:
                r.move(host.next_target.x, host.next_target.y, 2, flag=[])
            if r.lifetime <= 1:
                host.center_camera()

        r = Stock.project('g_0x0', host.pos[0], 40)
        r.fast = 0
        host.states.add('Stun', 40)
        r.lifetime = 40
        r.center_camera()
        r.effect = effect

    @staticmethod
    def scorch(host):
        def effect():
            if not r.lifetime % 2:
                Effect.make('scorch', r.pos[0].get_center(), offset=6)
            for thing in r.pos[0].things:
                if thing != r:
                    thing.states.add('Burn', 8)
        r = Stock.project('g_0x0', host.get_offset_tile(host.direction, 0), 80)
        r.fast = 0
        r.effect = effect

    @staticmethod
    def fireblast(host):
        def effect():
            def on_hit(target):
                aoe = r.location.get_area(target.pos[0], 1)
                for i in aoe:
                    Effect.make('burn', i.get_center(), offset=4, lifetime=40)
                    for thing in i.things:
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
                r.location.attack.register(0, r.pos[0], faction=Faction.PROJECTILE, callback=on_hit)
                Effect.make('explode', r.pos[0].get_center(), offset=4).form.face(final_dir)
        r = Stock.project('g_0x0', host.get_offset_tile(host.direction, 0), 6)
        final_dir = host.direction
        r.effect = effect

    @staticmethod
    def tornado(host):
        def effect():
            def on_hit(target):
                if r.last_pos.x - r.pos[0].x > 0:
                    target.move(-4, -4)
                else:
                    target.move(4, -4)
            tgt = host.get_target_tile() - r.pos[0]
            r.last_pos = r.pos[0] + 0
            r.move(tgt.x, tgt.y, 1)
            r.location.attack.register(0, r.get_offset_tile(0, -1), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(0, 1), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(1, 0), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(-1, 0), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.pos[0], faction=Faction.PROJECTILE, callback=on_hit)
            Effect.make('wind', r.pos[0].get_center(), offset=4)
        r = Stock.project('wind', host.get_offset_tile(host.direction, 0), 16)
        r.last_pos = r.pos[0]
        r.effect = effect
        return r

    @staticmethod
    def summon(host):
        obj = Spells.check_rift(host)
        if obj:
            r = Stock.get('Summon').add()
            r.relocate(obj.pos[0].x, obj.pos[0].y, force=1)
            r.states.add('Banish', 100)
            Effect.make('zip', r.vec)

    @staticmethod
    def fargate(host):
        def effect():
            flight = placer.pos[0] != placer.move(host.next_target.x, host.next_target.y, 2)
            if not flight or placer.lifetime == 1:
                Effect.make('barrier', placer.vec)
                r = Stock.get('Portal').add()
                r.relocate(placer.pos[0].x, placer.pos[0].y, force=1)
                host.states.add('Rift', 80, var=r.id)
                host.center_camera()
                placer.remove()
        obj = Spells.check_rift(host)
        placer = Stock.project('portal', obj.pos[0], 30)
        placer.fast = 0
        host.states.add('Stun', 20)
        placer.effect = effect
        placer.center_camera()

    @staticmethod
    def shock(host):
        host.weapon.states.add('Shock', 80)

    @staticmethod
    def levitate(host):
        if host.states.get('Levitate'):
            Spells.dispell(host)
        else:
            host.states.add('Levitate', 60)

    @staticmethod
    def brand(host):
        Effect.make('burn', host.weapon.vec, offset=0)
        host.states.add('Fire', 400)
        host.weapon.states.add('Fire', 400)

    @staticmethod
    def teleport(host):
        obj = Spells.check_rift(host)
        host.relocate(obj.pos[0].x, obj.pos[0].y, force=1)
        host.center_camera()

    @staticmethod
    def crystallize(host):
        obj = Spells.check_rift(host)
        for i in range(5):
            r1 = Stock.get('Crystal').add()
            r1.relocate(obj.pos[0].x, obj.pos[0].y, force=1)
            r1.states.add('Levitate', 1)
            r1.states.add('Banish', 80)
            Effect.make('zip', r1.vec)
            r1.move(Random.rand_int(-1, 1), Random.rand_int(-1, 0))

    @staticmethod
    def torrent(host):
        host.move(Random.rand_int(-4, 4), Random.rand_int(-4, 4))
        Spells.dispell(host)


spellbook = {'arc': Spells.teleport,
             'art': Spells.fargate,
             'afc': Spells.shock,
             'aft': Spells.fireblast,
             'fc': Spells.brand,
             'ft': Spells.scorch,
             'ac': Spells.levitate,
             'at': Spells.tornado,
             'rc': Spells.crystallize,
             'rt': Spells.summon,
             'ff': Spells.combust,
             'aa': Spells.dispell,
             'rr': Spells.pull,
             'c': Spells.scry,
             't': Spells.sonic}
