from src.game import Global
from src.map.Generator import Generator


class Tunneler(Generator):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.activity_threshold = int(x * y * .1)
        self.tunneler = None
        self.blocked = False
        self.turning = 10

    def initialize_tunneler(self):
        start_pos = [self.random.rand_int(1, self.get_width() - 2), self.random.rand_int(1, self.get_height() - 2)]
        return [self.random.rand_int(0, 3), start_pos]

    def build_structure(self):
        for i in range(12):
            self.tunneler = self.initialize_tunneler()
            start = self.tunneler[1]
            self.iterate()
            self.tunneler[1] = start
            self.iterate()
            self.str_map[start[1]][start[0]] = 'D'

    def iterate(self):
        for i in range(self.activity_threshold * 5):
            self.step()
            self.str_map[self.tunneler[1][1]][self.tunneler[1][0]] = 'X'
            if self.blocked:
                self.blocked = False
                break
            elif self.random.rand_int(1, self.activity_threshold) == 1:
                self.turning = self.random.rand_int(2, 8)

    def step(self):
        pos = self.get_front(self.tunneler[0])
        routes = self.get_options(self.tunneler[1][0], self.tunneler[1][1])
        routes2 = []
        for i in routes:
            if len(self.get_options(i[0], i[1])) >= 3 and not self.diagonals(i[0], i[1]):
                routes2.append(i)
        frontfront = self.get_front(self.tunneler[0], mag=2)
        if len(routes) < 3 or self.is_blocked(pos):
            self.change_direction(routes2)
        elif self.is_blocked(frontfront):
            if not self.out_of_bound(frontfront[0], frontfront[1]):
                self.str_map[pos[1]][pos[0]] = 'D'
            self.change_direction(routes2)
        elif self.random.rand_int(1, self.turning) == 1:
            self.change_direction(routes2)
        else:
            self.tunneler[1] = [pos[0], pos[1]]

    def is_blocked(self, pos):
        if self.out_of_bound(pos[0], pos[1]):
            return True
        return self.str_map[pos[1]][pos[0]] in Generator.BLOCKED

    def get_front(self, direction, mag=1):
        coord = Global.cardinal_coord[direction % 4]
        x = self.tunneler[1][0] + coord[0] * mag
        y = self.tunneler[1][1] + coord[1] * mag
        return [x, y]

    def out_of_bound(self, x, y, margin=2):
        return x < margin or x >= self.get_width() - margin or y < margin or y >= self.get_height() - margin

    def change_direction(self, routes):
        if not routes:
            self.blocked = True
            return
        route = self.random.rand_list(routes)
        if route[0] < self.tunneler[1][0]:
            self.tunneler[0] = 1
        elif route[0] > self.tunneler[1][0]:
            self.tunneler[0] = 3
        elif route[1] < self.tunneler[1][1]:
            self.tunneler[0] = 2
        elif route[1] > self.tunneler[1][1]:
            self.tunneler[0] = 0

    def get_options(self, x, y):
        ways = []
        for v in Global.cardinal_coord:
            tx = x + v[0]
            ty = y + v[1]
            if not self.out_of_bound(tx, ty) and not self.is_blocked([tx, ty]):
                ways.append([tx, ty])
        return ways

    def diagonals(self, x, y):
        diagonal = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
        for v in diagonal:
            tx = x + v[0]
            ty = y + v[1]
            if self.tunneler[1][0] != tx and self.tunneler[1][1] != ty:
                if self.is_blocked([tx, ty]):
                    return True


class GenerateMansion(Tunneler):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.theme = {'.': 'h', 'o': '.', 'X': 'B', 'D': 'Door', 'W': 'Window'}

    def process(self):
        self.build_structure()
        self.adapt_tiles()

    def adapt_tiles(self):
        for y in range(1, self.get_height() - 1):
            for x in range(1, self.get_width() - 1):
                if self.str_map[y][x] in ['X', 'D']:
                    blocked = []
                    for i in Global.cardinal_coord:
                        if self.str_map[y + i[1]][x + i[0]] in Generator.BLOCKED:
                            blocked.append(1)
                        else:
                            blocked.append(0)
                    if self.str_map[y][x] == 'X':
                        if self.random.rand_int(1, 8) == 1 and (blocked == [1, 0, 1, 0] or blocked == [0, 1, 0, 1]):
                            if self.random.rand_int(1, 4) == 1:
                                self.str_map[y][x] = 'Bead Door'
                            else:
                                self.str_map[y][x] = 'W'
                    if self.str_map[y][x] == 'D':
                        if blocked != [1, 0, 1, 0] and blocked != [0, 1, 0, 1]:
                            self.str_map[y][x] = 'X'


class GenerateCave(Tunneler):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.theme = {'.': 'R', 'o': 'R', 'X': '=', 'D': '=', 'W': 'R'}
        self.pivots = []

    def process(self):
        self.tunneler = self.initialize_tunneler()
        self.iterate()
        for x in range(self.get_width()):
            for y in range(self.start[1] - 1, self.start[1] + 2):
                self.str_map[y][x] = 'm'

    def initialize_tunneler(self):
        return [self.random.rand_int(0, 3), self.start]

    def step(self):
        pos = self.get_front(self.tunneler[0])
        if not pos or self.out_of_bound(pos[0], pos[1]):
            self.tunneler[0] = self.random.rand_int(0, 3)
        elif self.random.rand_int(1, self.turning) == 1:
            self.tunneler[0] = self.random.rand_int(0, 3)
            self.pivots.append(self.tunneler[1])
        else:
            self.tunneler[1] = [pos[0], pos[1]]
