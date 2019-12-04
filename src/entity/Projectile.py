from src.entity.Prop import Prop
from src.entity.Space import Space
from src.game import Global
from src.map.Tile import Tile
from src.tools.Math import Math


class Projectile(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.faction = 0
        self.collision_type = 0
        self.lifetime = 100
        self.gravity = 1
        self.hittable = 0
        self.durability = -1
        self.speed = 24
        self.speed_var = 4
        self.chance = 6
        self.friction = .96
        self.vel = Space()
        self.start = Space()
        self.standables.append(Tile.COLLIDE_UNIT)

    def add(self):
        self.removed = 0
        self.relocate(self.pos.x, self.pos.y, force=1)
        from src.game.Turn import Turn
        Turn.fast_queue.append(self.turn)

    def remove(self):
        self.removed = 1
        self.pos.things.remove(self)
        from src.game.Turn import Turn
        if self.turn in Turn.fast_queue:
            Turn.fast_queue.remove(self.turn)

    def set(self, gravity=1, lifetime=100, speed=24, speed_var=4, durability=-1):
        self.gravity = gravity
        self.lifetime = lifetime
        self.speed = speed
        self.speed_var = speed_var
        self.durability = durability

    def draw(self, surface):
        if not self.removed:
            self.vel *= self.friction
            if self.is_fall():
                self.vel.y += .5
            self.form.draw(surface, self.vec.x, self.vec.y)

    def turn(self):
        if self.lifetime == 0:
            self.remove()
        else:
            if self.lifetime > 0:
                self.lifetime -= 1
                if self.is_collide() and self.pos != self.start:
                    self.on_collide()
                else:
                    self.vec += self.vel
                    self.form.rotate(-self.vel.get_atan())
                    self.pos = self.location.get_tile_from_vec(self.vec.x, self.vec.y)

    def is_collide(self):
        return self.pos.is_land(self.standables)

    def on_collide(self):
        self.remove()

    def shoot(self, x, y):
        if self.gravity:
            offset = min(4, abs(int(x / 4)))
        else:
            offset = 0
        rand = Global.r.rand_int(self.speed - self.speed_var, self.speed + self.speed_var) + offset
        atan = Space(x, y - offset).get_atan()
        self.vel.load(rand * Math.cos(atan), rand * Math.sin(atan))
        self.start = self.pos
