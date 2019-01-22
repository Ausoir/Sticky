class Turn:
    queue = []
    frame = 0

    @staticmethod
    def update():
        Turn.frame += 1
        if Turn.frame >= 8:
            Turn.frame = 0
            for i in Turn.queue:
                i.turn()
                if i.delay > 0:
                    i.delay -= 1
