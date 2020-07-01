import math

from src.tools.Random import Random


class Biome:
    def __init__(self, seed):
        self.seed = seed
        rand = Random(seed).random
        self.size, self.freq, self.octave = 128, 1 / 8.0, 3
        self.size2 = self.size * 2
        self.noise = rand.sample(range(self.size2), self.size2) * 2
        self.vector = [(math.cos(a * 2.0 * math.pi / self.size2),
                        math.sin(a * 2.0 * math.pi / self.size2)) for a in range(self.size2)]

    def get_noise(self, px, py):
        def get_tile(start_x, start_y, off_x, off_y):
            diff_x, diff_y = start_x - off_x, start_y - off_y
            hashed = self.noise[self.noise[int(off_x) % self.size2] + int(off_y) % self.size2]
            abs_x, abs_y = abs(diff_x), abs(diff_y)
            smooth = diff_x * self.vector[hashed][0] + diff_y * self.vector[hashed][1]
            smooth *= 1 - 6 * abs_x ** 5 + 15 * abs_x ** 4 - 10 * abs_x ** 3
            smooth *= 1 - 6 * abs_y ** 5 + 15 * abs_y ** 4 - 10 * abs_y ** 3
            return smooth
        val = 0
        px, py = abs(px), abs(py)  # mirrors on sign change
        for o in range(self.octave):
            freq_i = 1 << o
            x, y = px * self.freq * freq_i, py * self.freq * freq_i
            int_x, int_y = int(x), int(y)
            tile_values = get_tile(x, y, int_x + 0, int_y + 0) + get_tile(x, y, int_x + 1, int_y + 0)
            tile_values += get_tile(x, y, int_x + 0, int_y + 1) + get_tile(x, y, int_x + 1, int_y + 1)
            val += (1 / freq_i) * tile_values
        return max(-1, min(1, val))

    def get_level(self, px, py):
        noise = self.get_noise(px, py)
        if noise > .3:
            return 3
        elif noise > 0:
            return 2
        elif noise > -.3:
            return 1
        else:
            return 0
