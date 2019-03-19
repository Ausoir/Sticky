from src.entity.Effect import Effect
from src.game.Turn import Turn


class Field:
    def __init__(self):
        Turn.add(self)
        self.registry = []
        self.delay = 0

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

    def register(self, damage, pos, delay=1, type=0, faction=0, chance=6, callback=None):
        self.registry.append([delay, pos, damage, type, faction, chance, callback])

    @staticmethod
    def hit(data):
        for thing in data[1].things:
            if thing.is_hit(data[5], faction=data[4]):
                if data[3]:
                    Effect.make(data[3], data[1].get_center())
                if not thing.hit(data[2]):
                    if data[6]:
                        data[6](thing)
