class Turn:
    HOUR_FRAME = 800
    queue = None
    fast_queue = None
    hour_change = None
    frame = 0
    queue_turn = 0
    rounds = 1

    @staticmethod
    def init():
        Turn.hour_change = []
        Turn.queue = [[], [], [], []]
        Turn.rounds = len(Turn.queue)
        Turn.fast_queue = []
        Turn.frame = 0
        Turn.queue_turn = 0

    @staticmethod
    def update():
        for i in Turn.queue[Turn.frame % Turn.rounds]:
            i()
        for i in Turn.fast_queue:
            i()
        Turn.frame += 1
        if Turn.frame >= Turn.HOUR_FRAME:
            for i in Turn.hour_change:
                i()
            Turn.frame = 0

    @staticmethod
    def add(arg):
        Turn.queue[Turn.queue_turn].append(arg)
        Turn.queue_turn += 1
        if Turn.queue_turn >= Turn.rounds:
            Turn.queue_turn = 0

    @staticmethod
    def remove(arg):
        for i in Turn.queue:
            if arg in i:
                i.remove(arg)
