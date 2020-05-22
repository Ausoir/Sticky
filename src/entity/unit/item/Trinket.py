from src.entity.unit.item.Headgear import Headgear
from src.game import Global
from src.tools.Dialog import Dialog


class Glasses(Headgear):
    def describe(self):
        r = super().describe()
        r += '\n' + Dialog.get('sight_range', [self.tags.get('level', 1)])
        sight_type = []
        from src.map.Tile import Tile
        for i in self.collision_type:
            sight_type.append(Tile.get_collision_by_name(i))
        r += '\n' + Dialog.get('sight_type', [', '.join(sight_type)])
        return r

    def activate(self):
        super().activate()
        if self.host == Global.player.character:
            def done():
                self.host.center_camera()
            level = self.tags.get('level', 1)
            self.host.action.act('rest', 16)
            self.host.action.on_finish = done
            coord = Global.cardinal_coord[self.host.direction]
            target = self.host.pos + [coord[0] * level, coord[1] * level]
            pos = self.host.location.collide_land(self.host.pos, target, distance=level, flag=self.collision_type)
            from src.game.TempObject import TempObject
            viewer = TempObject(pos)
            from src.game.Camera import Camera
            Camera.target = viewer


class SafetyHat(Headgear):
    def describe(self):
        r = super().describe()
        r += '\n' + Dialog.get('light_range', [self.tags.get('level', 1)])
        return r

    def on_unwield(self):
        light = self.host.states.get('Glow')
        if light and light.duration == -1 and light.var == self.tags.get('level', 1):
            light.end()
        super().on_unwield()

    def activate(self):
        super().activate()
        light = self.states.get('Glow')
        if light:
            light.end()
        else:
            self.states.add('Glow', -1, var=self.tags.get('level', 1))


class Talisman(Headgear):
    def die(self):
        if self.host:
            spell = self.tags.get('spell')
            if spell:
                from src.entity.unit.item.Alchemy import Alchemy
                Alchemy.perform(self.host, spell)
        super().die()
