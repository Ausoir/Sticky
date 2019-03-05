from src.entity.Prop import Prop
from src.game.Global import DEPTH_ITEM
from src.map.Tile import Tile


class Item(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.collide = Tile.COLLIDE_ITEM
        self.host = None
        self.range = [1]
        self.volume = [1, 1]
        self.depth = DEPTH_ITEM

    def __str__(self):
        return super().__str__() + ',[' + str(self.volume[0]) + ',' + str(self.volume[1]) + ']'

    def load(self, arg):
        index = super().load(arg)
        self.volume = arg[index]
        return index + 1

    def die(self):
        if self.host and self.host.weapon == self:
            self.host.drop()
        super().die()

    def on_equip(self, host):
        self.host = host
        host.weapon = self
        self.motion_pos = host.motion_pos
        self.host.face(self.host.direction)
        self.remove()

    def on_unequip(self):
        self.motion_pos = self.motion_pos + 0
        self.relocate(self.host.pos[0].x, self.host.pos[0].y, force=1)
        self.host = None
        self.form.rotation = 0
        self.add()

    def describe(self):
        r = self.name
        if self.durability == -1:
            dur = 'Unbreakable'
        else:
            dur = str(self.durability)
        r += '\nDurability: ' + dur
        r += '\nVolume: ' + str(self.volume[0]) + 'x' + str(self.volume[1])
        return r

    def use(self):
        host = self.host
        self.host.drop()
        host.armor.add_item(self)
        host.action.set('rest')
