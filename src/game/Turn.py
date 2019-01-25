from src.tools.List import List


class Turn:
    queue = List()
    frame = 0

    @staticmethod
    def update():
        Turn.frame += 1
        if Turn.frame >= 10:
            Turn.frame = 0
            for i in Turn.queue:
                i.turn()
                if i.delay > 0:
                    i.delay -= 1
