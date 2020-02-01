import math

from src.game import Global


class Camera:
    pos = [0, 0]
    sight = [math.ceil(Global.DISPLAY[0] / Global.BLOCK / 2) + 1, math.ceil(Global.DISPLAY[1] / Global.BLOCK / 2) + 1]
    target = None

    @staticmethod
    def update():
        Camera.pos = [round(Global.CENTER[0] - Camera.target.vec.x),
                      round(Global.CENTER[1] - Camera.target.vec.y)]

    @staticmethod
    def get_relative_pos(x, y):
        bound_x = x + Camera.pos[0]
        bound_y = Global.DISPLAY[1] - (y + Camera.pos[1])
        return bound_x, bound_y

    @staticmethod
    def get_relative_tile_pos(x, y):
        return [round((x - Global.CENTER[0]) / Global.BLOCK), round((y - Global.CENTER[1]) / Global.BLOCK)]

    @staticmethod
    def in_camera(x, y):
        rel = [round(Camera.pos[0] - Global.CENTER[0]), round(Camera.pos[1] - Global.CENTER[1])]
        sight = [Camera.sight[0] * Global.BLOCK, Camera.sight[1] * Global.BLOCK]
        in_x = -rel[0] - sight[0] < x < -rel[0] + sight[0]

        in_y = -rel[1] - sight[1] < y < -rel[1] + sight[1]
        return in_x and in_y
