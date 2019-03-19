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
        spell = spellbook[incantation]
        if Random.roll(host.get_proficiency(spell.__name__) + 4):
            spell(host)
        else:
            Effect.make('fail', host.pos[0].get_center())
            miscast[incantation](host)

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
            host.states.add('Fire', 8)
            host.weapon.states.add('Fire', 8)

    @staticmethod
    def combust(host):
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
                Effect.make('energy', thing.motion_pos)
                if isinstance(thing, Prop):
                    thing.hit(0)
                    thing.clean_buffs()

    @staticmethod
    def conjure(host):
        Effect.make('barrier', host.motion_pos)
        r = Stock.get('Portal').add()
        r.relocate(host.pos[0].x, host.pos[0].y - 1, force=1)
        r.states.add('Banish', 60)
        host.states.add('Rift', 60, var=r.id)

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
                    Effect.make('wind', thing.motion_pos)
                    thing.move(x, y)

    @staticmethod
    def scry(host):
        def effect():
            if host.next_target.distance() > 4:
                r.fly(host.next_target.x, host.next_target.y, 2, flag=[])
            if r.lifetime <= 1:
                host.center_camera()

        r = Stock.project('g_0x0', host.pos[0], 40)
        r.fast = 0
        host.states.add('Stun', 40)
        r.lifetime = 40
        r.center_camera()
        r.effect = effect

    @staticmethod
    def fireblast(host):
        def effect():
            def on_hit(target):
                target.states.add('Burn', 8)
                r.remove()
            r.fly(final_dir, round(Random.gauss(0, 1)), 1)
            r.location.attack.register(1, r.pos[0], faction=Faction.PROJECTILE, callback=on_hit)
            Effect.make('explode', r.pos[0].get_center(), offset=4, lifetime=40)
        r = Stock.project('explode', host.get_offset_tile(host.direction, 0), 2)
        r.durability = 10
        r.lifetime = 10
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
            r.fly(tgt.x, tgt.y, 1)
            r.location.attack.register(0, r.get_offset_tile(0, -1), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(0, 1), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(1, 0), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(-1, 0), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.pos[0], faction=Faction.PROJECTILE, callback=on_hit)
            Effect.make('wind', r.pos[0].get_center(), offset=4)
        r = Stock.project('wind', host.get_offset_tile(host.direction, 0), 16)
        r.durability = 8
        r.last_pos = r.pos[0]
        r.effect = effect
        return r

    @staticmethod
    def summon(obj):
        r = Stock.get('Summon').add()
        r.relocate(obj.pos[0].x, obj.pos[0].y, force=1)
        r.states.add('Banish', 100)
        Effect.make('zip', r.motion_pos)

    @staticmethod
    def fargate(host):
        def effect():
            flight = placer.pos[0] != placer.fly(host.next_target.x, host.next_target.y, 2)
            if not flight or placer.lifetime == 1:
                Effect.make('barrier', placer.motion_pos)
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
        Effect.make('burn', host.motion_pos)
        host.states.add('Fire', 100)
        host.weapon.states.add('Fire', 100)

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
            Effect.make('zip', r1.motion_pos)
            r1.move(Random.rand_int(-1, 1), Random.rand_int(-1, 0))

    @staticmethod
    def torrent(host):
        host.move(Random.rand_int(-4, 4), Random.rand_int(-4, 4))
        Spells.dispell(host)


spellbook = {'arc': Spells.teleport,
             'afc': Spells.shock,
             'art': Spells.fargate,
             'fc': Spells.brand,
             'ft': Spells.fireblast,
             'ac': Spells.levitate,
             'at': Spells.tornado,
             'rc': Spells.crystallize,
             'rt': Spells.summon,
             'ff': Spells.combust,
             'aa': Spells.dispell,
             'rr': Spells.pull,
             'c': Spells.scry,
             't': Spells.sonic}

miscast = {'arc': Spells.pull,
           'afc': Spells.combust,
           'art': Spells.summon,
           'fc': Spells.combust,
           'ft': Spells.combust,
           'ac': Spells.torrent,
           'at': Spells.torrent,
           'rc': Spells.pull,
           'rt': Spells.pull,
           'ff': Spells.combust,
           'aa': Spells.dispell,
           'rr': Spells.pull,
           'c': Spells.sonic,
           't': Spells.sonic}
