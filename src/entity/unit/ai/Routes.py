from src.map.Tile import Tile


class Immobile:
    def __init__(self, loc):
        self.location = loc
        self.wall = Tile.CHECK_LARGE

    def get(self, pos):
        return []


class Ground(Immobile):
    def get(self, pos):
        options = []
        left = self.location.get_tile(pos + (-1, 0))
        right = self.location.get_tile(pos + (1, 0))
        down = self.location.get_tile(pos + (0, 1))
        up = self.location.get_tile(pos + (0, -1))
        if not up.is_land(self.wall):
            options.append((0, -1))
        if not right.is_land(self.wall):
            options.append((1, 0))
        if not left.is_land(self.wall):
            options.append((-1, 0))
        if not down.is_land(self.wall):
            options.append((0, 1))
        return options
