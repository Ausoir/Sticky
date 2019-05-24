from src.entity.Effect import Effect
from src.entity.Stock import Stock
from src.entity.unit.ai.Faction import Faction
from src.tools.Random import Random


class Spells:
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
    def conjure(host):
        rift = host.states.get('Rift')
        if rift:
            Spells.teleport(host)
        else:
            Effect.make('barrier', host.vec)
            r = Stock.get('Portal').add()
            r.relocate(host.pos[0].x, host.pos[0].y - 1, force=1)
            host.states.add('Rift', 160, var=r.id)

    @staticmethod
    def pull(host):
        obj = Spells.check_rift(host)
        if obj:
            aoe = host.location.get_area(obj.pos[0], 8, 8)
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
            r.location.attack.register(0, r.get_offset_tile(0, -1), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(0, 1), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(1, 0), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.get_offset_tile(-1, 0), faction=Faction.PROJECTILE, callback=on_hit)
            r.location.attack.register(0, r.pos[0], faction=Faction.PROJECTILE, callback=on_hit)
            Effect.make('wind', r.pos[0].get_center(), offset=4)
        r = Stock.project('wind', host.get_offset_tile(host.direction, 0), 20)
        r.last_pos = r.pos[0]
        r.effect = effect
        return r

    @staticmethod
    def summon(host):
        obj = Spells.check_rift(host)
        if obj:
            r = Stock.get('Summon').add()
            r.relocate(obj.pos[0].x, obj.pos[0].y, force=1)
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
            Effect.make('zip', r1.vec)
            r1.move(Random.rand_int(-1, 1), Random.rand_int(-1, 0))

    @staticmethod
    def torrent(host):
        host.move(Random.rand_int(-4, 4), Random.rand_int(-4, 4))
        Spells.dispell(host)
