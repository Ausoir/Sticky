from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.ai.Faction import Faction
from src.map.Tile import Tile
from src.tools.Math import Math


class Projectile(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.faction = Faction.PROJECTILE
        self.collide = 0
        self.lifetime = 9
        self.gravity = 1
        self.hittable = 0
        self.durability = -1
        self.speed = 24
        self.chance = 4
        self.depth = 5
        self.fast = 1
        self.vel = Space()
        self.start = Space()

    def draw(self, surface):
        if not self.removed:
            self.vel *= .98
            if self.is_fall():
                self.vel.y += .5
            if self.pos[0].is_land(Tile.CHECK_LARGE) and self.pos[0] != self.start:
                self.location.attack.register(1, self.pos[0], delay=0, chance=self.chance,
                                              type='batter', faction=self.faction)
                self.remove()
            else:
                self.vec += self.vel
                self.form.rotate(-self.vel.get_atan())
                self.pos[0] = self.location.get_tile_from_vec(self.vec.x, self.vec.y)
            self.form.draw(surface, self.vec.x, self.vec.y)

    def turn(self):
        if self.lifetime == 0:
            self.remove()
        else:
            if self.lifetime > 0:
                self.lifetime -= 1

    def effect(self):
        pass

    def shoot(self, x, y):
        from src.tools.Random import Random
        offset = min(4, abs(int(x / 4)))
        rand = Random.rand_int(15, 25) + offset
        atan = Space(x, y - offset).get_atan()
        self.vel.load(rand * Math.cos(atan), rand * Math.sin(atan))
        self.start = self.pos[0]
