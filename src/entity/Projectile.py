from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.ai.Faction import Faction
from src.game.Camera import Camera
from src.game.Global import DEPTH_EFFECT
from src.map.Tile import Tile
from src.tools.Math import Math


class Projectile(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.faction = Faction.PROJECTILE
        self.lifetime = 2
        self.gravity = 0
        self.hittable = 0
        self.durability = 999
        self.speed = 24
        self.depth = DEPTH_EFFECT
        self.fast = 1
        self.chance = 9

    def __str__(self):
        return super().__str__() + ',' + str(self.lifetime)

    def load(self, arg):
        index = super().load(arg)
        self.lifetime = arg[index]
        return index + 1

    def draw(self, surface):
        if self.fast:
            if Camera.tile_in_camera(self.pos[0].x, self.pos[0].y) or \
                    Camera.in_camera(self.motion_pos.x, self.motion_pos.y):
                diff = self.pos[0].get_center() - self.motion_pos
                da = (self.pos[0].get_center() - self.motion_pos).get_atan()
                self.motion_pos += (Math.cos(da)*self.speed, Math.sin(da)*self.speed)
                ndiff = self.pos[0].get_center() - self.motion_pos
                if (diff.x > 0) == (ndiff.x > 0) and (diff.y > 0) == (ndiff.y > 0):
                    self.form.draw(surface, self.motion_pos.x, self.motion_pos.y)
                else:
                    self.form.size.x = 0
                return 1
        else:
            super().draw(surface)

    def turn(self):
        if self.lifetime == 0:
            self.remove()
        else:
            self.effect()
        self.lifetime -= 1

    def effect(self):
        pass

    def crash(self, damage=1, delay=1, callback=None):
        self.location.attack.register(damage, self.pos[0], delay=delay, faction=self.faction,
                                      chance=self.chance, callback=callback)

    def move(self, x, y, distance=8, flag=Tile.CHECK_LARGE):
        def fn(prev, tile):
            for thing in tile.things:
                if thing.is_hit(self.chance, self.faction):
                    return tile
        new_pos = self.location.collide_line(self.pos[0], x, y, fn, distance=distance)
        self.relocate(new_pos.x, new_pos.y)
        return new_pos

    def fly(self, tx, ty, distance, flag=Tile.CHECK_TERRAIN):
        self.form.rotate(Space(tx, -ty).get_atan())
        return self.move(tx, ty, distance=distance, flag=flag)
