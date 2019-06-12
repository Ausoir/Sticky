from src.entity.Effect import Effect
from src.game.Turn import Turn


class Field:
    def __init__(self):
        Turn.add(self)
        self.registry = []

    def turn(self):
        new_reg = []
        while self.registry:
            new = self.registry.pop(0)
            if new[0] == 0:
                self.hit(new)
            else:
                new[0] -= 1
                new_reg.append(new)
        self.registry = new_reg

    def register(self, damage, pos, chance=4, delay=1, type=0, faction=0, callback=None):
        self.registry.append([delay, pos, damage, chance, type, faction, callback])

    @staticmethod
    def hit(data):
        for thing in data[1].things:
            if thing.is_hit(data[3], faction=data[5]):
                if data[4]:
                    Effect.make(data[4], data[1].get_center())
                if not thing.hit(data[2]):
                    if data[6]:
                        data[6](thing)
