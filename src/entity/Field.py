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
            if new[1] == 0:
                self.hit(new)
            else:
                new[1] -= 1
                new_reg.append(new)
        self.registry = new_reg

    def register(self, damage, pos, chance=4, delay=1, type=0, faction=0, hitter=None, callback=None):
        data = [hitter, delay, pos, damage, chance, type, faction, callback]
        if delay == 0:
            Field.hit(data)
        else:
            self.registry.append(data)

    def unregister(self, hitter):
        for i in self.registry:
            if i[0] == hitter:
                self.registry.remove(i)

    @staticmethod
    def hit(data):
        for thing in data[2].things.copy():
            if thing.is_hit(data[4], faction=data[6]):
                if data[5]:
                    Effect.make(data[5], data[2].get_center())
                if not thing.hit(data[3]):
                    if data[7]:
                        data[7](thing)
