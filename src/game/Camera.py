import math

from src.game import Global


class Camera:
    pos = [0, 0]
    sight = [math.ceil(Global.DISPLAY[0] / Global.BLOCK / 2) + 1, math.ceil(Global.DISPLAY[1] / Global.BLOCK / 2) + 1]
    target = None

    @staticmethod
    def update():
        Camera.pos = [-Camera.target.x + Global.CENTER[0],
                      -Camera.target.y + Global.CENTER[1]]

    @staticmethod
    def get_relative_tile_pos(x, y, rel_x=Global.CENTER[0], rel_y=Global.CENTER[1]):
        return [round((x - rel_x) / Global.BLOCK), round((y - rel_y) / Global.BLOCK)]

    @staticmethod
    def get_relative_pos(x, y, rel_x=Global.CENTER[0], rel_y=Global.CENTER[1]):
        return [round(x - rel_x), round(y - rel_y)]

    @staticmethod
    def tile_in_camera(x, y):
        rel = Camera.get_relative_tile_pos(Camera.pos[0], Camera.pos[1])
        in_x = -rel[0] - Camera.sight[0] < x < -rel[0] + Camera.sight[0]
        in_y = -rel[1] - Camera.sight[1] < y < -rel[1] + Camera.sight[1]
        return in_x and in_y

    @staticmethod
    def in_camera(x, y):
        rel = Camera.get_relative_pos(Camera.pos[0], Camera.pos[1])
        sight = [Camera.sight[0] * Global.BLOCK, Camera.sight[1] * Global.BLOCK]
        in_x = -rel[0] - sight[0] < x < -rel[0] + sight[0]
        in_y = -rel[1] - sight[1] < y < -rel[1] + sight[1]
        return in_x and in_y
