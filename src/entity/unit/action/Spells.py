from src.entity.Effect import Effect
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.entity.unit.ai.Faction import Faction
from src.tools.Random import Random


class Spells:
    @staticmethod
    def check_rift(host):
        rift = host.states.get('rift')
        if rift:
            obj = host.location.get_object(host.states.var(rift))
            if obj:
                host.states.end(rift)
                return obj
        return None

    @staticmethod
    def burn(target):
        target.states.add('burn', 8)

    @staticmethod
    def charm(host):
        obj = Spells.check_rift(host)
        if 'teleport' in host.action.spells and obj and host.states.get('air'):
            host.relocate(obj.pos[0].x, obj.pos[0].y)
            host.center_camera()
        elif 'levitate' in host.action.spells and host.states.get('air'):
            host.states.add('levitate', 60)
        elif 'brand' in host.action.spells and host.states.get('fire'):
            Effect.make('burn', host.motion_pos)
            host.states.add('fire', 120)
            host.weapon.states.add('fire', 120)
        elif 'crystallize' in host.action.spells and obj:
            for i in range(5):
                r1 = Stock.get('Crystal').add()
                r1.relocate(obj.pos[0].x, obj.pos[0].y, force=1)
                r1.states.add('levitate', 1)
                Effect.make('zip', r1.motion_pos)
                r1.move(Random.rand_int(-1, 1), Random.rand_int(-1, 0))
        else:
            Spells.scry(host)

    @staticmethod
    def cast(host):
        obj = Spells.check_rift(host)
        if 'fargate' in host.action.spells and obj and host.states.get('air'):
            Spells.fargate(host, obj)
        elif 'fireblast' in host.action.spells and host.states.get('fire'):
            Spells.fireblast(host)
        elif 'tornado' in host.action.spells and host.states.get('air'):
            Spells.tornado(host)
        elif 'summon' in host.action.spells and obj:
            r = Stock.get('Summon').add()
            r.relocate(obj.pos[0].x, obj.pos[0].y, force=1)
            Effect.make('zip', r.motion_pos)
        else:
            def effect(target):
                if target and isinstance(target, Unit):
                    target.states.add('stun', 40)

            r = Stock.project('energy', host.get_interact_pos(), 40)
            r.fly(host.next_target.x, host.next_target.y, 8)
            r.crash(damage=0, callback=effect)

    @staticmethod
    def ignite(host):
        if host.states.get('fire'):
            aoe = host.location.get_area(host.pos[0], 5)
            for i in aoe:
                for thing in i.things:
                    Spells.burn(thing)
        else:
            host.states.add('fire', 20)
            host.weapon.states.add('fire', 20)

    @staticmethod
    def whirlwind(host):
        if host.states.get('air') or host.states.get('levitate'):
            from src.entity.Prop import Prop
            aoe = host.location.get_area(host.pos[0], 8)
            for i in aoe:
                for thing in i.things:
                    Effect.make('energy', thing.motion_pos)
                    if isinstance(thing, Prop):
                        thing.hit(0)
                        thing.clean_buffs()
        else:
            host.states.add('air', 10)

    @staticmethod
    def conjure(host):
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
        else:
            Effect.make('barrier', host.motion_pos)
            r = Stock.get('Portal').add()
            r.relocate(host.pos[0].x, host.pos[0].y - 1, force=1)
            host.states.add('rift', 60, var=r.id)

    @staticmethod
    def scry(host):
        def effect():
            if host.next_target.distance() > 4:
                r.fly(host.next_target.x, host.next_target.y, 2, flag=[])
            if r.lifetime <= 1:
                host.center_camera()

        r = Stock.project('none', host.pos[0], 40)
        host.states.add('stun', 40)
        r.lifetime = 40
        r.center_camera()
        r.effect = effect

    @staticmethod
    def fireblast(host):
        def effect():
            def on_hit(target):
                Spells.burn(target)
                r.remove()

            r.fly(final_dir, round(Random.gauss(0, 1)), 1)
            r.location.attack.register(1, r.pos[0], faction=Faction.PROJECTILE, callback=on_hit)
            Effect.make('explode', r.pos[0].get_center(), offset=4).form.face(final_dir)

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
            r.location.attack.register(0, r.pos[0], faction=Faction.PROJECTILE, callback=on_hit)
            Effect.make('wind', r.pos[0].get_center(), offset=4)
        r = Stock.project('wind', host.get_offset_tile(host.direction, 0), 16)
        r.durability = 8
        r.last_pos = r.pos[0]
        r.effect = effect
        return r

    @staticmethod
    def fargate(host, obj):
        def effect():
            flight = placer.fly(host.next_target.x, host.next_target.y, 2)
            if not flight or placer.lifetime == 1:
                Effect.make('barrier', placer.motion_pos)
                r = Stock.get('Portal').add()
                r.relocate(placer.pos[0].x, placer.pos[0].y, force=1)
                host.states.add('rift', 80, var=r.id)
                host.center_camera()
                placer.remove()

        placer = Stock.project('portal', obj.pos[0], 30)
        host.states.add('stun', 30)
        placer.effect = effect
        placer.center_camera()
