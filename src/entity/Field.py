from src.game.Turn import Turn


class Field:
    def __init__(self):
        Turn.add(self.turn)
        self.registry = []

    def turn(self):
        count = len(self.registry)
        while count > 0:
            count -= 1
            if self.registry[count][1] == 0:
                self.perform(self.registry[count])
                self.registry.pop(count)
                count -= 1
            elif self.registry[count][1] > 0:
                self.registry[count][1] -= 1
            else:
                self.registry.pop(count)
                count -= 1

    def register(self, damage, pos, chance=4, delay=1, faction=0, hitter=None, callback=None):
        data = [hitter, delay, pos, damage, chance, faction, callback]
        if delay == 0:
            Field.perform(data)
        else:
            self.registry.append(data)

    def unregister(self, victim):
        for i in self.registry:
            if i[0] == victim:
                i[1] = -1

    @staticmethod
    def perform(data):
        for thing in data[2].things.copy():
            if thing.is_hit(data[4], faction=data[5]):
                if thing.hit(data[3], accuracy=data[4], hitter=data[0]) == 1:
                    if data[6]:
                        data[6](thing)
