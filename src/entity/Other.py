from src.entity.Effect import Effect
from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.item.Item import Item
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
        self.depth = 3
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

    def draw(self, surface):
        super().draw(surface)

    def trigger(self, host):
        from src.game.Player import Player
        from src.game import Global
        host.location.delay = 0
        host.location.turn()
        host.action.set('idle')
        host.form.set('interact')
        host.relocate(self.to_pos.x, self.to_pos.y, force=1)
        self.remove()
        Global.main.player.map.name = self.to_map
        Global.main.player.turn()
        Global.main.player = Player()


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


class Ragdoll(Prop):
    template = None

    def __init__(self, loc):
        super().__init__(loc)
        self.direction = 1
        self.collide = 0
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
        super().draw(surface)
        self.form.update()

    def is_hit(self, chance, faction=0):
        if self.hittable:
            return 1

    def hit(self, damage):
        self.form.randomize_once(18)
        return super().hit(damage)

    def die(self):
        self.remove()


class Estate(Prop):
    def build(self, theme):
        from src.tools.Data import Data
        if self.durability == 2:
            size = 'L'
        else:
            size = 'S'
        maps = Data.get_files('data/map/' + theme, lambda x: x.startswith(size) and x.endswith('.map'))
        chosen = maps[Random.rand_int(0, len(maps) - 1)]
        building = Data.process_raw(Data.read('data/map/' + theme + '/' + chosen))
        return self.location.load_map(building, new=True, offset=(self.pos[0].x, self.pos[0].y))


class Goldbag(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.gold = 0
        self.jewel = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.gold) + ',' + str(self.jewel)

    def load(self, arg):
        index = super().load(arg)
        self.gold = arg[index]
        index += 1
        self.jewel = arg[index]
        return index + 1

    def describe(self):
        return super().describe() + '\nGold: ' + str(self.gold) + '\nJewels: ' + str(self.jewel)


class Backpack(Item):
    def describe(self):
        if self.host.is_armored() and self.host.armor.inventory[1][1] == 1:
            return super().describe() + '\nBackpack cannot be attached to your current armor.'
        return super().describe()

    def use(self):
        if self.host.is_armored():
            if self.host.armor.inventory[1][1] == 1:
                self.host.armor.inventory[1][1] = 2
                self.host.action.set('block')
                self.die()


class Food(Item):
    def describe(self):
        if not self.host.states.get('Hunger'):
            return super().describe() + '\nItem cannot be used because you are not hungry.'
        return super().describe()

    def use(self):
        hunger = self.host.states.get('Hunger')
        if hunger:
            hunger.end()
            self.host.action.set('block')
            self.hit(1)
        else:
            super().use()


class Break(Prop):
    def die(self):
        super().die()
        if self.pos[0].terrain:
            self.pos[0].terrain = None


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
            if thing.name == 'Plank':
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

    def attack(self, chance=0, callback=None):
        self.charge += 1
        if self.charge > 3:
            super().attack(chance + 2, callback)
            self.charge = -1

    def on_attack(self, target):
        super().on_attack(target)
        if self.charge == -1:
            target.states.add('Stun', 16)
