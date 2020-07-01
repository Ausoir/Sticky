import time
import timeit

from src.map.Biome import Biome

seed = 77644
biome = Biome(seed)


def draw():
    base = []
    for i in range(64):
        row = []
        for j in range(128):
            val = biome.get_level(abs(j), abs(i))
            if val == 3:
                row.append('0')
            elif val == 2:
                row.append('o')
            elif val == 1:
                row.append('-')
            else:
                row.append('.')
        base.append(row)

    for i in base:
        row = ''
        for j in i:
            row += j
        print(row)


# draw()
print(time.perf_counter())
for i in range(100):
    biome.get_level(i, i)
print(time.perf_counter())
