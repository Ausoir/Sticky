class Turn:
    queue = None
    frame = 0
    queue_turn = 0

    @staticmethod
    def init():
        Turn.queue = [[], [], [], [], [], [], [], [], [], []]
        Turn.frame = 0
        Turn.queue_turn = 0

    @staticmethod
    def update():
        for i in Turn.queue[Turn.frame]:
            i.turn()
        Turn.frame += 1
        if Turn.frame >= 10:
            Turn.frame = 0

    @staticmethod
    def add(arg):
        Turn.queue[Turn.queue_turn].append(arg)
        Turn.queue_turn += 1
        if Turn.queue_turn >= 10:
            Turn.queue_turn = 0

    @staticmethod
    def remove(arg):
        for i in Turn.queue:
            if arg in i:
                i.remove(arg)
