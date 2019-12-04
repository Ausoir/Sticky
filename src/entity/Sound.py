from src.game.Turn import Turn


class Sound:
    def __init__(self, location):
        Turn.add(self.turn)
        self.location = location
        self.registry = []

    def turn(self):
        new_reg = []
        while self.registry:
            new = self.registry.pop(0)
            if new[1] > 0:
                self.update(new)
                new_reg.append(new)
                new[1] -= 1
        self.registry = new_reg

    def register(self, pos, magnitude):
        data = [pos, magnitude]
        self.registry.append(data)

    def update(self, data):
        tiles = []
        for x in range(-data[1], data[1] + 1):
            tiles.append(data[0] + (x, -data[1]))
            tiles.append(data[0] + (x, data[1]))
        for y in range(-data[1] + 1, data[1]):
            tiles.append(data[0] + (-data[1], y))
            tiles.append(data[0] + (data[1], y))
        from src.entity.unit.Unit import Unit
        for i in tiles:
            tile = self.location.get_tile(i)
            for thing in tile.things:
                if isinstance(thing, Unit) and 'hear' in thing.tags:
                    thing.pilot.hear(data[0])
