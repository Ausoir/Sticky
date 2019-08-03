from src.entity.Effect import Effect
from src.entity.Object import Object
from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.NPC import NPC
from src.entity.unit.item.Item import Item
from src.entity.unit.item.Weapon import Weapon
from src.game import Global
from src.map.Tile import Tile


class Light(Prop):
    def turn(self):
        if Global.r.rand_int(0, 80) == 0:
            self.remove()
        else:
            Effect.make('energy', self.get_offset_tile(Global.r.rand_int(-3, 3), Global.r.rand_int(-3, 3)).get_center())
            for x in range(-3, 4):
                for y in range(-3, 4):
                    if Global.r.rand_int(0, 1) == 0:
                        pos = str(self.pos[0].x + x) + ',' + str(self.pos[0].y + y)
                        self.location.draw_tiles[pos] = self.get_offset_tile(x, y)


class Beacon(Object):
    def __init__(self, loc):
        super().__init__(loc)
        self.var = 'estate'

    def __str__(self):
        return super().__str__() + ',' + self.var

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
            Global.main.fade = 255
            Global.main.player.travel(self.argument[1], Space(int(self.argument[2]), int(self.argument[3])))
        elif self.argument[0] == 'travel':
            Global.menu.var = self.argument[1:]
            Global.menu.state = Global.menu.menu_travel
            Global.menu.display(1)


class Gold(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.capacity = 5

    def __str__(self):
        return super().__str__() + ',' + str(self.capacity)

    def describe(self):
        return super().describe().replace('Durability', 'Coins')

    def load(self, arg):
        index = super().load(arg)
        self.capacity = arg[index]
        return index + 1

    def use(self):
        self.host.action.set('block')
        self.name = 'Bag'
        self.host.modify_gold(self.durability)
        self.die()


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


class Corpse(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.direction = 1
        self.collide = 0
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
        self.form.randomize_clip(dead, 12)
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
                top = not thing.get_offset_tile(0, -1).is_land(Tile.CHECK_FOUNDATION)
                top_left = not thing.get_offset_tile(-1, -1).is_land(Tile.CHECK_FOUNDATION)
                top_right = not thing.get_offset_tile(1, -1).is_land(Tile.CHECK_FOUNDATION)
                left = not thing.get_offset_tile(-1, 0).is_land(Tile.CHECK_FOUNDATION)
                right = not thing.get_offset_tile(1, 0).is_land(Tile.CHECK_FOUNDATION)
                down = not thing.get_offset_tile(0, 1).is_land([Tile.COLLIDE_TERRAIN])
                down_left = not thing.get_offset_tile(-1, 1).is_land(Tile.CHECK_FOUNDATION)
                down_right = not thing.get_offset_tile(1, 1).is_land(Tile.CHECK_FOUNDATION)
                thing.remove()
                door = not self.pos[0].is_land([Tile.COLLIDE_DOODAD])
                if down and door and (top or left or right or top_left or top_right or down_left or down_right):
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
            elif thing.name == 'Plank':
                thing.remove()
                Stock.make('Scaffold', thing.pos[0])
                self.host.action.set('hit')
                self.host.form.set('interact')
                self.hit(1)
                return
            elif thing.name == 'Scrap':
                thing.remove()
                Stock.make('Plating', thing.pos[0])
                self.host.action.set('hit')
                self.host.form.set('interact')
                self.hit(1)
                return
        super().use()


class Talker(NPC):
    def talk(self):
        self.face(1 if Global.main.player.character.pos[0].x > self.pos[0].x else -1)
        from src.tools.Data import Data
        conversation = Data.get_line('data/raw/conversation.txt', self.var[0])[1:]
        output = []
        for sentence in conversation:
            new = ','.join(sentence)
            output.append(new)
        Global.menu.show_dialog([output[self.attributes.gene % len(output)]])


class Merchant(NPC):
    def talk(self):
        self.face(1 if Global.main.player.character.pos[0].x > self.pos[0].x else -1)
        if self.var[0] == 'shop':
            from src.entity.Stock import Stock
            Global.menu.var = [Stock.get(i) for i in self.var[1:]]
            Global.menu.state = Global.menu.menu_shop
            Global.menu.display(1)
        elif self.var[0] == 'trainer':
            Global.menu.state = Global.menu.menu_trainer
            Global.menu.display(1)
        elif self.var[0] == 'host':
            if Global.main.player.days > self.var[1]:
                from src.tools.Data import Data
                from src.tools.Random import Random
                from src.entity.Stock import Stock
                data = Data.get_line('data/raw/trade.txt', 'host')
                rng = Random(self.attributes.gene + Global.main.player.days)
                due_date = Global.main.player.days + rng.rand_int(1, 3)
                value = Stock.get(rng.rand_list(data[1])).get_value()
                self.var = ['host', due_date, rng.rand_list(data[1]), 1, value + 1]
            Global.menu.var = self.var
            Global.menu.state = Global.menu.menu_guild
            Global.menu.display(1)
        elif self.var[0] == 'guild':
            if Global.main.player.days > self.var[1]:
                from src.tools.Data import Data
                from src.tools.Random import Random
                from src.entity.Stock import Stock
                data = Data.get_line('data/raw/trade.txt', 'guild')
                rng = Random(self.attributes.gene + Global.main.player.days)
                due_date = Global.main.player.days + rng.rand_int(2, 5)
                value = Stock.get(rng.rand_list(data[1])).get_value()
                self.var = ['guild', due_date, rng.rand_list(data[1]), rng.rand_int(1, 7), rng.rand_int(1, 3) * value]
            Global.menu.var = self.var
            Global.menu.state = Global.menu.menu_guild
            Global.menu.display(1)
