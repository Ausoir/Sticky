from src.entity.Effect import Effect
from src.entity.Stock import Stock
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
        elif 'levitate' in host.action.spells and host.states.get('air'):
            host.states.add('levitate', 60)
        elif 'brand' in host.action.spells and host.states.get('fire'):
            Effect.make('burn', host.motion_pos)
            host.states.add('fire', 120)
            host.weapon.states.add('fire', 120)
        elif 'barrier' in host.action.spells and Spells.check_rift(host):
            host.states.add('barrier', 120)
        else:
            Spells.scry(host)

    @staticmethod
    def cast(host):
        obj = Spells.check_rift(host)
        if 'fargate' in host.action.spells and obj and host.states.get('air'):
            Spells.fargate(host)
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
                if target:
                    Effect.make('energy', r.motion_pos)

            r = Stock.project('energy', host.get_interact_pos(), 2)
            r.fly(host.next_target.x, host.next_target.y, 8)
            r.crash(callback=effect)

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
                target.move(final_dir * 4, -4)

            r.fly(host.next_target.x, host.next_target.y, 2)
            r.location.attack.register(1, r.pos[0], faction=Faction.PROJECTILE, callback=on_hit)
            Effect.make('wind', r.pos[0].get_center(), offset=4)
            if not r.lifetime % 3:
                Spells.tornado(host).lifetime = max(0, r.lifetime - 1)

        r = Stock.project('wind', host.get_offset_tile(host.direction, 0), 6)
        r.durability = 8
        r.lifetime = 8
        final_dir = host.direction
        r.effect = effect
        return r

    @staticmethod
    def fargate(host):
        def effect():
            flight = placer.fly(host.next_target.x, host.next_target.y, 2)
            if not flight or placer.lifetime == 1:
                Effect.make('barrier', placer.motion_pos)
                r = Stock.get('Portal').add()
                r.relocate(placer.pos[0].x, placer.pos[0].y, force=1)
                host.states.add('rift', 80, var=r.id)
                host.center_camera()
                placer.remove()

        placer = Stock.project('portal', host.pos[0], 30)
        host.states.add('stun', 30)
        placer.effect = effect
        placer.center_camera()
