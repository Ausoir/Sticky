from src.entity.Effect import Effect
from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.item.Weapon import Weapon
from src.form.Body import Body
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Random import Random


class Light(Prop):
    def turn(self):
        if Random.rand_int(0, 80) == 0:
            self.remove()
        else:
            Effect.make('energy', self.get_offset_tile(Random.rand_int(-3, 3), Random.rand_int(-3, 3)).get_center())
            for x in range(-3, 4):
                for y in range(-3, 4):
                    if Random.rand_int(0, 1) == 0:
                        pos = str(self.pos[0].x + x) + ',' + str(self.pos[0].y + y)
                        self.location.draw_tiles[pos] = self.get_offset_tile(x, y)


class Travel(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.to_map = ''
        self.to_pos = Space(0, 0)

    def __str__(self):
        return super().__str__() + ',' + self.to_map + ',' + self.to_pos.__str__()

    def load(self, arg):
        index = super().load(arg)
        self.to_map = arg[index]
        index += 1
        self.to_pos.load(arg[index])
        return index + 1

    def trigger(self, host):
        from src.game.World import World
        from src.game import Global
        host.location.delay = 0
        host.location.turn()
        host.action.set('idle')
        host.form.set('interact')
        host.relocate(self.to_pos.x, self.to_pos.y, force=1)
        self.remove()
        Global.main.world.map.name = self.to_map
        Global.main.world.turn()
        Global.main.world = World()


class Portal(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.to_map = ''
        self.to_pos = Space(0, 0)

    def __str__(self):
        return super().__str__() + ',' + self.to_map + ',' + self.to_pos.__str__()

    def load(self, arg):
        index = super().load(arg)
        self.to_map = arg[index]
        index += 1
        self.to_pos.load(arg[index])
        return index + 1


class Bridge(Prop):
    def load(self, arg):
        super().load(arg)
        self.gravity = 0

    def turn(self):
        super().turn()
        support = 0
        adj = [self.get_offset_tile(-1, 0), self.get_offset_tile(1, 0)]
        for i in adj:
            if i.is_land(Tile.CHECK_FIRM):
                support += 2
            elif i.is_land(Tile.CHECK_SUPPORTED):
                support += 1
        if support < 2:
            self.die()


class Hammer(Weapon):
    def use(self):
        from src.entity.Stock import Stock
        for thing in self.pos[0].things:
            if thing.name == 'Scaffold':
                top = not thing.get_offset_tile(0, -1).is_land(Tile.CHECK_SUPPORTED)
                topleft = not thing.get_offset_tile(-1, -1).is_land(Tile.CHECK_SUPPORTED)
                topright = not thing.get_offset_tile(1, -1).is_land(Tile.CHECK_SUPPORTED)
                left = not thing.get_offset_tile(-1, 0).is_land(Tile.CHECK_SUPPORTED)
                right = not thing.get_offset_tile(1, 0).is_land(Tile.CHECK_SUPPORTED)
                down = not thing.get_offset_tile(0, 1).is_land([Tile.COLLIDE_TERRAIN])
                downleft = not thing.get_offset_tile(-1, 1).is_land(Tile.CHECK_SUPPORTED)
                downright = not thing.get_offset_tile(1, 1).is_land(Tile.CHECK_SUPPORTED)
                thing.remove()
                door = not self.pos[0].is_land([Tile.COLLIDE_DOODAD])
                if down and door and (top or left or right or topleft or topright or downleft or downright):
                    construct = 'Wall'
                else:
                    construct = 'Tile'
                    for thing2 in self.pos[0].things:
                        if thing2.name == 'Tile':
                            thing2.remove()
                            construct = 'Wall'
                            break
                Stock.make(construct, thing.pos[0])
                self.host.action.set('hit')
                self.host.form.set('interact')
                return
            if thing.name == 'Planks':
                thing.remove()
                Stock.make('Scaffold', thing.pos[0])
                self.host.action.set('hit')
                self.host.form.set('interact')
                return
        super().use()


class Bow(Weapon):
    def use(self):
        self.host.action.set('arch')
        self.hit(1)


class Ragdoll(Prop):
    template = None

    def __init__(self, loc):
        super().__init__(loc)
        self.direction = 1
        self.collide = Tile.COLLIDE_COVER
        self.depth = 3
        self.standables = Tile.CHECK_LANDABLE

    def add(self):
        Turn.add(self)
        self.relocate(self.pos[0].x, self.pos[0].y, force=1)
        return self

    def make_form(self, arg):
        self.form_name = arg
        if not Ragdoll.template:
            Ragdoll.template = Body('unit/man')
        self.form = Ragdoll.template

    def set(self, form):
        def invalid(str):
            pass
        self.add()
        self.form = form
        self.durability = 8
        dead = 'dead' + str(Random.rand_int(1, 2))
        self.form.randomize_clip(dead, 12)
        self.form.set(dead)
        self.form.set = invalid
        return self

    def draw(self, surface):
        if super().draw(surface):
            self.form.update()
            return 1
        return 0

    def is_hit(self, chance, faction=0):
        if self.hittable:
            return 1

    def hit(self, damage):
        self.form.randomize_once(18)
        return super().hit(damage)

    def die(self):
        self.remove()


class Command(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.frame = 0
        self.state = 'start'
        self.open = []
        self.closed = []
        self.construct = []
        self.units = []
        self.houses = []
        self.warehouses = []

    def __str__(self):
        r = super().__str__()
        unit = ','.join(i.id for i in self.units)
        return r + ',[' + unit + ']'

    def load(self, p):
        super().load(p)
        self.open.append(self.pos[0])

    def turn(self):
        super().turn()
        self.frame += 1
        if not self.frame % 3:
            if not self.construct:
                self.build()
            elif not self.frame % 24:
                if self.frame > 40:
                    self.frame = 0
                    if len(self.houses) >= len(self.units):
                        from src.entity.Stock import Stock
                        Effect.make('zip', self.pos[0].get_center())
                        for i in range(12 * (1 + len(self.warehouses))):
                            res = Stock.get("Planks")
                            res.pos[0] = self.pos[0]
                            res.add()
                        unit = Stock.get("Worker")
                        unit.pos[0] = self.pos[0]
                        unit.faction = self.faction
                        unit.add()
                        unit.pilot.task.command = self
                        self.units.append(unit)

    def build(self):
        if len(self.closed) < 64:
            new = []
            sites = []
            while self.open:
                pos = self.open.pop()
                if pos not in self.closed:
                    self.closed.append(pos)
                    options = self.location.get_routes(pos)
                    for option in options:
                        tile = self.location.get_tile(pos.x + option[0], pos.y + option[1])
                        if tile not in self.open:
                            new.append(tile)
                            sites.append(self.get_clearing(tile, 7))
            self.open += new
            self.construct = sites[Random.rand_int(0, len(sites) - 1)]
            for cols in self.construct:
                for rows in cols:
                    Effect.make('blood', rows.get_center())
        else:
            self.open = [self.pos[0]]
            self.closed = []

    def get_clearing(self, tile, size):
        sites = []
        site = 1
        count = 0
        radius = int(size/2)
        while site and count <= radius:
            site = self.check_clearing(tile, count)
            count += 1
            if site:
                sites += site
        return sites

    def check_clearing(self, tile, x):
        r = []
        ranges = [1] if x == 0 else [-1, 1]
        for i in ranges:
            pos_x = tile.x + (x * i)
            ground = self.location.get_tile(pos_x, tile.y + 1)
            space = self.location.get_tile(pos_x, tile.y)
            air = self.location.get_tile(pos_x, tile.y - 1)
            ceiling = self.location.get_tile(pos_x, tile.y - 2)
            if ground.is_land(Tile.CHECK_FIRM) and not space.is_land(Tile.CHECK_FIRM)\
                    and not air.is_land(Tile.CHECK_FIRM) and not ceiling.is_land(Tile.CHECK_FIRM):
                r.append([space, air, ceiling])
        return r


class Zapper(Weapon):
    def __init__(self, loc):
        super().__init__(loc)
        self.charge = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.charge)

    def load(self, arg):
        index = super().load(arg)
        self.charge = arg[index]
        return index + 1

    def attack(self, damage=0, callback=None):
        self.charge += 1
        if self.charge > 3:
            super().attack(damage + 2, callback)
            self.charge = -1

    def on_attack(self, target):
        super().on_attack(target)
        if self.charge == -1:
            target.states.add('Stun', 16)
