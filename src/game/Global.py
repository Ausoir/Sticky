import math

DISPLAY = (1200, 600)
BLOCK = 40
HALF_BLOCK = BLOCK / 2
CENTER = (DISPLAY[0] / 2, DISPLAY[1] / 2)


def get_absolute_tile_pos(x, y):
    return [round((x - CENTER[0]) / BLOCK), math.floor((y - CENTER[1]) / BLOCK)]


def get_relative_tile_pos(x, y, camera_x, camera_y):
    return [round((x - camera_x) / BLOCK), math.floor((y - camera_y) / BLOCK)]
