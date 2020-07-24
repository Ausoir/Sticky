from src.entity.unit.item.Item import Item
from src.game import Global
from src.tools.Dialog import Dialog


class Artifact(Item):
    def use(self):
        if self.tags.require('charge', 1):
            super().use()

    def on_sleep(self, time):
        if time > 0:
            self.tags.increment('charge', time)


class Telescope(Item):
    def describe(self):
        r = super().describe()
        r += '\n' + Dialog.get('sight_range', [self.tags.get('level', 1)])
        return r

    def use(self):
        if self.host == Global.player.character:
            def done():
                self.host.center_camera()
            level = self.tags.get('level', 1)
            self.host.action.act('rest', 8)
            self.host.action.on_finish = done
            coord = Global.cardinal_coord[self.host.direction]
            target = self.host.pos + [coord[0] * level, coord[1] * level]
            from src.map.Tile import Tile
            pos = self.host.location.collide_land(self.host.pos, target, distance=level, flag=Tile.COLLIDE_OBJECT)
            from src.game.TempObject import TempObject
            viewer = TempObject(pos)
            from src.game.Camera import Camera
            Camera.target = viewer


class Porter(Item):
    def on_unwield(self):
        light = self.host.states.get('Glow')
        if light and light.duration == -1 and light.var == self.tags.get('level', 1):
            light.end()
        super().on_unwield()

    def use(self):
        if self.host == Global.player.character:
            memory = self.tags.get('memory')
            if memory:
                args = memory.split('&')
            else:
                cell_coord = Global.world.get_coordinates(self.pos.x, self.pos.y)
                memory = '&'.join([str(x) for x in [cell_coord[0], cell_coord[1], self.pos.x, self.pos.y]])
                self.tags.set('memory', memory)


class Lamp(Item):
    def describe(self):
        r = super().describe()
        r += '\n' + Dialog.get('light_range', [self.tags.get('level', 1)])
        return r

    def use(self):
        super().use()
        light = self.states.get('Glow')
        if light:
            light.end()
        else:
            self.states.add('Glow', -1, var=self.tags.get('level', 1))


class Pusher(Item):
    def on_attack(self, target):
        diff = target.pos - self.host.pos
        target.relocate(to=target.pos.get_neighbor(diff.x, diff.y))
