from src.entity.Object import Object


class Prop(Object):
    def __init__(self, form, loc):
        super().__init__(form, loc)
        self.durability = 1
        self.hittable = 1

    def die(self):
        self.remove()

    def hit(self, hitter, damage):
        if self.hittable:
            self.durability -= damage
            if self.durability <= 0:
                self.die()
            return 1
        return 0
