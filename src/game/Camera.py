from src.game import Global


class Camera:
    pos = None
    target = None

    @staticmethod
    def update():
        """"  Every image gets exact same camera vector every update loop """
        Camera.pos = (Camera.target.vec.x, Camera.target.vec.y)

    @staticmethod
    def get_relative_pos(x, y):
        bound_x = round(x - Camera.pos[0])
        bound_y = round(-y + Camera.pos[1])
        return bound_x, bound_y

    @staticmethod
    def get_relative_tile_pos(x, y):
        return [round((x - Global.CENTER[0]) / Global.BLOCK), round((y - Global.CENTER[1]) / Global.BLOCK)]
