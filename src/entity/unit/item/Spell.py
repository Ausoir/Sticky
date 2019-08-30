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
        return index + 1

    def get_display_name(self):
        self.is_known = self.name in Global.player.knowledge
        if self.is_known:
            return self.name
        else:
            return 'Artifact'

    def describe(self):
        r = super().describe().replace('Durability', 'Number of casts')
        if self.is_known:
            r += '\nCasts Spell: ' + self.spell
        else:
            r += '\nCasts an unknown spell'
        return r

    def use(self):
        self.host.action.set('block')
        getattr(self, self.spell.lower())(self.host)
        self.hit(1)

    @staticmethod
    def echo(host):
        from src.entity.Stock import Stock
        Stock.make('Sonic', host.get_target_tile())

    @staticmethod
    def dispell(host):
        from src.entity.Prop import Prop
        aoe = host.location.get_area(host.pos, 8, 8)
        for i in aoe:
            for thing in i.things:
                Effect.make('sonic', thing.vec)
                if isinstance(thing, Prop):
                    thing.hit(0)
                    from src.entity.unit.Buff import BuffTags
                    thing.states.clear(lambda x: x.duration >= 0 and BuffTags.magic in x.tags)
        if host == Global.player.character:
            Global.player.set_darkness()

    @staticmethod
    def scorch(host):
        from src.entity.Stock import Stock
        host.location.sound.register(host.pos, 12)
        Stock.make('Flame', host.pos).move(host.next_target.x, host.next_target.y, distance=1)

    @staticmethod
    def scry(host):
        def effect():
            if host.next_target.distance() > 3:
                print(str(host.next_target))
                r.move(host.next_target.x, host.next_target.y, distance=1)
            if turnee.lifetime <= 1:
                host.center_camera()
                r.remove()
            Effect.make('sonic', r.pos.get_center())

        from src.entity.Stock import Stock
        from src.tools.Turnee import Turnee
        turnee = Turnee(effect, 40)
        r = Stock.make('Force', host.pos)
        r.gravity = False
        r.location.record.remove(r)
        host.states.add('Stun', 40)
        r.center_camera()

    @staticmethod
    def tornado(host):
        def test():
            if channel.effect(2):
                left = channel.host.get_offset_tile(-1, 0)
                right = channel.host.get_offset_tile(1, 0)
                Effect.make('wind', left.get_center())
                Effect.make('wind', right.get_center())
                for thing in left.things:
                    thing.move(-1, 0, 1)
                for thing in right.things:
                    thing.move(1, 0, 1)
        channel = host.states.add('Channel', 40)
        channel.on_update = test

    @staticmethod
    def levitate(host):
        host.states.add('Levitate', 40)

    @staticmethod
    def summon(host):
        things = []
        things += host.pos.things
        things += host.get_offset_tile(-1, 0).things
        things += host.get_offset_tile(1, 0).things
        for thing in things:
            if isinstance(thing, Item):
                from src.entity.Stock import Stock
                r = Stock.make('Summon', host.pos)
                Effect.make('zwip', r.vec)
                return

    @staticmethod
    def immolation(host):
        Effect.make('burn', host.weapon.vec, offset=0)
        host.states.add('Fire', 240)

    @staticmethod
    def crystallize(host):
        def casting():
            crystal = Stock.make('Crystal', host.pos)
            crystal.states.add('Levitate', 10)
            crystal.move(host.next_target.x, host.next_target.y)
            Effect.make('zip', crystal.vec)
        from src.entity.Stock import Stock
        channel = host.states.add('Channel', 8)
        channel.on_update = casting

    @staticmethod
    def fireball(host):
        def effect():
            aoe = r.location.get_area(r.pos, 2, 2)
            for tile in aoe:
                Effect.make('explode', tile.get_center(), offset=4)
                for thing in tile.things:
                    thing.states.add('Burn', 24)
            r.remove()
        from src.entity.Stock import Stock
        r = Stock.make('Fireball', host.get_interact_pos())
        r.set(lifetime=5, speed=12, speed_var=2)
        r.shoot(host.next_target.x, host.next_target.y)
        r.on_collide = effect

    @staticmethod
    def entomb(host):
        from src.entity.Stock import Stock
        target = host.get_target_tile()
        for i in [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, -1], [-1, 1], [1, 1]]:
            r = Stock.make('Crystal', host.location.get_tile(target + (i[0], i[1])))
            r.states.add('Levitate', 120)
            r.states.add('Banish', 100)

    @staticmethod
    def gravitas(host):
        def effect():
            aoe = r.location.get_area(r.pos, 2, 2)
            for tile in aoe:
                Effect.make('wind', tile.get_center(), offset=6)
                for thing in tile.things:
                    thing.move((thing.pos.x - r.pos.x) * 2, (thing.pos.y - r.pos.y) * 2 - 2)
            r.remove()
            channel.end()
        from src.entity.Stock import Stock
        r = Stock.make('Fireball', host.get_interact_pos())
        r.set(gravity=0, lifetime=40, speed=7, speed_var=0)
        r.on_collide = effect

        def casting():
            if channel.effect(7):
                Effect.make('spin', host.vec)
            r.shoot(host.pos.x - r.pos.x + host.next_target.x, host.pos.y - r.pos.y + host.next_target.y)
            aoe = r.location.get_area(r.pos, 2, 2)
            for tile in aoe:
                for thing in tile.things:
                    thing.move(r.pos.x - thing.pos.x, r.pos.y - thing.pos.y)
        channel = host.states.add('Channel', 40)
        channel.on_update = casting

    @staticmethod
    def darkness(host):
        def casting():
            if channel.effect(4):
                Effect.make('spin', host.vec)
                Global.main.colorize(1, [30, 0, 0, 60 + (channel.frame * 4)])
                host.location.sight_range = max(4, host.location.sight_range - 1)
                host.location.resize()
                host.location.update_fog()
            if channel.frame == 38:
                host.location.sight_range = 4
                host.location.resize()
                host.location.update_fog()
        channel = host.states.add('Channel', 40)
        channel.on_update = casting

    @staticmethod
    def haste(host):
        host.states.add('Speed', 240, var=1)

    @staticmethod
    def ensnare(host):
        aoe = host.location.get_area(host.get_target_tile(), 2, 0)
        for tile in aoe:
            Effect.make('spin', tile.get_center(), offset=6)
            for thing in tile.things:
                thing.states.add('Speed', 80, var=-9)
                thing.states.add('Cripple', 80)

    @staticmethod
    def irradiate(host):
        def effect():
            aoe = r.location.get_area(r.pos, 2, 2)
            for tile in aoe:
                Effect.make('explode', tile.get_center(), offset=4)
                for thing in tile.things:
                    thing.states.add('Burn', 24)
            r.remove()
        from src.entity.Stock import Stock
        r = Stock.make('Fireball', host.get_interact_pos())
        r.set(lifetime=5, speed=12, speed_var=2)
        r.shoot(host.next_target.x, host.next_target.y)
        r.on_collide = effect
