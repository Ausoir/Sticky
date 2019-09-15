from src.entity.Effect import Effect
from src.entity.Object import Object
from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.item.Headgear import Headgear
from src.entity.unit.item.Item import Item
from src.entity.unit.item.Weapon import Weapon
from src.game import Global
from src.map.Tile import Tile


class Beacon(Object):
    def __init__(self, loc):
        super().__init__(loc)
        self.var = 'estate'
        self.depth = 5

    def __str__(self):
        return super().__str__() + ',' + str(self.var)

    def load(self, arg):
        index = super().load(arg)
        self.var = arg[index]
        return index + 1


class Interactive(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.depth = 3
        self.argument = ''

    def __str__(self):
        return super().__str__() + ',[' + ','.join(str(x) for x in self.argument) + ']'

    def load(self, arg):
        index = super().load(arg)
        self.argument = arg[index]
        return index + 1

    def trigger(self):
        if self.argument[0] == 'enter':
            Global.player.travel(self.argument[1], Space(int(self.argument[2]), int(self.argument[3])))
        elif self.argument[0] == 'travel':
            if Global.player.is_safe():
                Global.menu.var = self.argument[1:]
                Global.menu.state = Global.menu.menu_travel
                Global.menu.display(1)


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
            elif i.is_land([Tile.COLLIDE_DOODAD]):
                support += 1
        if support < 2:
            self.die()


class Gold(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.capacity = 16

    def __str__(self):
        return super().__str__() + ',' + str(self.capacity)

    def describe(self):
        return super().describe().replace('Durability', 'Coins')

    def load(self, arg):
        index = super().load(arg)
        self.capacity = arg[index]
        return index + 1

    def use(self):
        self.host.action.set('wait')
        self.name = 'Bag'
        self.host.modify_gold(self.durability)
        self.die()


class Sonic(Prop):
    def turn(self):
        if self.durability == 0:
            self.remove()
        else:
            self.durability -= 1
            Effect.make('sonic', self.get_offset_tile(Global.r.rand_int(-3, 3), Global.r.rand_int(-3, 3)).get_center())
            for x in range(-4, 5):
                for y in range(-4, 5):
                    if Global.r.rand_bool():
                        pos = str(self.pos.x + x) + ',' + str(self.pos.y + y)
                        self.location.draw_tiles[pos] = self.get_offset_tile(x, y)


class Block(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.standables = Tile.CHECK_FOUNDATION.copy()
        self.standables.append(Tile.COLLIDE_BACK)


class Corpse(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.direction = 1
        self.collision_type = 0
        self.depth = 3
        self.standables = Tile.CHECK_LANDABLE
        from src.tools.Data import Data
        self.form = Data.run_cache('g_9x3')
        self.is_ragdoll = False

    def invalid(self, state):
        pass

    def set_form(self, arg):
        self.form_name = arg

    def set(self, form):
        self.is_ragdoll = True
        self.add()
        self.form = form
        self.durability = 8
        dead = 'dead' + str(Global.r.rand_int(1, 2))
        self.form.randomize_clip(dead, 8)
        # noinspection PyArgumentList
        self.form.set(dead)
        self.form.set = self.invalid
        return self

    def draw(self, surface):
        super().draw(surface)
        if self.is_ragdoll:
            self.form.update()

    def is_hit(self, chance, faction=0):
        if self.hittable:
            return 1

    def hit(self, damage):
        if self.is_ragdoll:
            self.form.randomize_once(18)
        return super().hit(damage)

    def die(self):
        self.remove()


class Break(Prop):
    def die(self):
        super().die()
        if self.pos.terrain:
            self.pos.terrain = None


class Builder(Weapon):
    def use(self):
        from src.entity.Stock import Stock
        for thing in self.pos.things:
            if thing.name == 'Scaffold':
                top = not thing.get_offset_tile(0, -1).is_land(Tile.CHECK_FOUNDATION)
                top_left = not thing.get_offset_tile(-1, -1).is_land(Tile.CHECK_FOUNDATION)
                top_right = not thing.get_offset_tile(1, -1).is_land(Tile.CHECK_FOUNDATION)
                left = not thing.get_offset_tile(-1, 0).is_land(Tile.CHECK_FOUNDATION)
                right = not thing.get_offset_tile(1, 0).is_land(Tile.CHECK_FOUNDATION)
                down = not thing.get_offset_tile(0, 1).is_land([Tile.COLLIDE_TERRAIN])
                down_left = not thing.get_offset_tile(-1, 1).is_land(Tile.CHECK_FOUNDATION)
                down_right = not thing.get_offset_tile(1, 1).is_land(Tile.CHECK_FOUNDATION)
                thing.remove()
                door = not self.pos.is_land([Tile.COLLIDE_DOODAD])
                if down and door and (top or left or right or top_left or top_right or down_left or down_right):
                    construct = 'Wall'
                else:
                    construct = 'Tile'
                    for thing2 in self.pos.things:
                        if thing2.name == 'Tile':
                            thing2.remove()
                            construct = 'Wall'
                            break
                Stock.make(construct, thing.pos)
                self.host.action.set('hit')
                self.host.form.set('interact')
                return
            elif thing.name == 'Plank':
                thing.remove()
                Stock.make('Scaffold', thing.pos)
                self.host.action.set('hit')
                self.host.form.set('interact')
                self.hit(1)
                return
            elif thing.name == 'Scrap':
                thing.remove()
                Stock.make('Plating', thing.pos)
                self.host.action.set('hit')
                self.host.form.set('interact')
                self.hit(1)
                return
        super().use()


class Mushroom(Item):
    def die(self):
        if self.host:
            self.host.states.add('Sick', 40)
        else:
            for thing in self.pos.things:
                thing.states.add('Sick', 40)
        super().die()


class Explosive(Item):
    def die(self):
        if self.states.get('Burn'):
            from src.entity.Stock import Stock
            Stock.make('Flame', self.pos)
            aoe = self.location.get_area(self.pos, 1, 1)
            for tile in aoe:
                Effect.make('explode', tile.get_center(), offset=4)
                for thing in tile.things:
                    thing.states.add('Burn', 24)
                    thing.hit(1)
        super().die()


class Manual(Item):
    skills = ['Block', 'Sprint', 'Lunge', 'Leap', 'Tackle', 'Flurry']
    req = [2, 3, 4, 5, 6, 7]

    def __init__(self, loc):
        super().__init__(loc)
        self.skill = None

    def __str__(self):
        return super().__str__() + ',' + self.skill

    def load(self, arg):
        index = super().load(arg)
        self.skill = arg[index]
        if self.skill == 'Random':
            self.skill = Global.r.rand_list(Manual.skills)
        return index + 1

    def get_display_name(self):
        return 'Manual of ' + self.skill

    def describe(self):
        return super().describe() + '\nTeaches skill [' + self.skill + ']'

    def use(self):
        req = Manual.req[Manual.skills.index(self.skill)]
        if self.host.attributes.strength > req:
            skill = self.skill.lower()
            if skill not in self.host.action.skills:
                self.host.action.skills.append(skill)
                if self.host == Global.player.character:
                    Global.player.monologue.text('Learned ' + self.skill + '!')
            elif self.host == Global.player.character:
                Global.player.monologue.text('I already know ' + self.skill + '.')
        elif self.host == Global.player.character:
            Global.player.monologue.text('Need ' + str(req) + ' Strength to learn this skill!')


class MemoryAmulet(Headgear):
    def __init__(self, loc):
        super().__init__(loc)
        self.visible = 0
        self.memory_map = None
        self.memory_pos = Space()

    def __str__(self):
        return super().__str__() + ',' + self.memory_map + ',' + self.memory_pos.__str__()

    def load(self, arg):
        index = super().load(arg)
        self.memory_map = arg[index]
        index += 1
        self.memory_pos.load(arg[index])
        return index + 1

    def use(self):
        super().use()
        self.memory_map = self.host.location.name
        self.memory_pos = self.host.pos

    def activate(self):
        super().activate()
        self.hit(1)
        Global.player.travel(self.memory_map, self.memory_pos)


class RubyAmulet(Headgear):
    def __init__(self, loc):
        super().__init__(loc)
        self.visible = 0

    def die(self):
        if self.host:
            return
        super().die()

    def activate(self):
        super().activate()
        if self.durability <= 0:
            for thing in self.host.pos.things:
                if thing.name == 'Corpse':
                    self.weight = thing.durability
                    thing.die()
                    break

    def on_sleep(self, time):
        self.durability = self.weight
