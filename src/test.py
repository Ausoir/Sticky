from src.map.Biome import Biome

seed = 5243
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
# count = biome.get_level(14, 12)
level = 1
count = 0
while level != 0:
    count += 1
    biome = Biome(count)
    level = biome.get_level(14, 12)
print(str(count))
