from src.game import Global


class Camera:
    pos = [0, 0]
    target = [0, 0]

    @staticmethod
    def update():
        Camera.pos = [-Camera.target[0] + Global.CENTER[0],
                      -Camera.target[1] + Global.CENTER[1] + Global.BLOCK]
