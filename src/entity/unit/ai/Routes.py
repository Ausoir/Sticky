from src.map.Tile import Tile


class Immobile:
    def __init__(self, loc, ground):
        self.location = loc
        self.ground = ground
        self.wall = Tile.CHECK_FIRM

    def get(self, pos):
        return []


class Ground(Immobile):
    def get(self, pos):
        options = []
        right = self.location.get_tile(pos + (1, 0))
        upright = self.location.get_tile(pos + (1, -1))
        left = self.location.get_tile(pos + (-1, 0))
        upleft = self.location.get_tile(pos + (-1, -1))
        ground = self.location.get_tile(pos + (0, 1))
        air = self.location.get_tile(pos + (0, -1))
        if not air.is_land(self.wall) and pos.is_climbable():
            options.append((0, -1))
        if not right.is_land(self.wall):
            if self.location.get_tile(pos + (1, 1)).is_land(self.ground):
                options.append((1, 0))
            elif self.location.get_tile(pos + (1, 2)).is_land(self.ground):
                options.append((1, 1))
        if not upright.is_land(self.wall) and right.is_land(self.ground):
            options.append((1, -1))
        if not left.is_land(self.wall):
            if self.location.get_tile(pos + (-1, 1)).is_land(self.ground):
                options.append((-1, 0))
            elif self.location.get_tile(pos + (-1, 2)).is_land(self.ground):
                options.append((-1, 1))
        if not upleft.is_land(self.wall) and left.is_land(self.ground):
            options.append((-1, -1))
        if not ground.is_land(self.wall) and ground.is_climbable():
            options.append((0, 1))
        return options


class Flying(Immobile):
    def __init__(self, loc, ground):
        super().__init__(loc, ground)
        self.directions = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))

    def get(self, pos):
        options = []
        for i in self.directions:
            tile = self.location.get_tile(pos + i)
            if not tile.is_land(self.wall):
                options.append(i)
        return options
