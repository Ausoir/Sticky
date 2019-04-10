from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.item.Weapon import Weapon
from src.form.Body import Body
from src.game.Global import DEPTH_UNIT
from src.game.Group import Group
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Random import Random


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
        for thing in self.pos[0].things:
            if thing.name == 'Scaffold':
                from src.entity.Stock import Stock
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
                building = Stock.get(construct)
                building.pos[0] = thing.pos[0]
                building.add()
                self.host.form.set('interact')
                self.hit(1)
                return


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
        self.depth = DEPTH_UNIT
        self.standables = Tile.CHECK_LANDABLE

    def add(self):
        Group.objects.add(self)
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
        dead = 'dead' + str(Random.rand_int(1, 3))
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
