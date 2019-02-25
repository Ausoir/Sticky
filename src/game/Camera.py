from src.game import Global


class Camera:
    pos = [0, 0]
    target = None

    @staticmethod
    def update():
        Camera.pos = [-Camera.target.x + Global.CENTER[0],
                      -Camera.target.y + Global.CENTER[1]]

    @staticmethod
    def get_relative_tile_pos(x, y, rel_x=Global.CENTER[0], rel_y=Global.CENTER[1]):
        return [round((x - rel_x) / Global.BLOCK), round((y - rel_y) / Global.BLOCK)]
