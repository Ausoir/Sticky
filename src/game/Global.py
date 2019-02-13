main = None
DISPLAY = (1200, 600)
BLOCK = 40
HALF_BLOCK = int(BLOCK / 2)
CENTER = (DISPLAY[0] / 2, DISPLAY[1] / 2)


def get_relative_tile_pos(x, y, rel_x=CENTER[0], rel_y=CENTER[1]):
    return [round((x - rel_x) / BLOCK), round((y - rel_y) / BLOCK) - 1]
