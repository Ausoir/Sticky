from src.game import Global


class Camera:
    pos = [0, 0]
    target = None

    @staticmethod
    def update():
        Camera.pos = [-Camera.target.x + Global.CENTER[0],
                      -Camera.target.y + Global.CENTER[1] + Global.BLOCK]
