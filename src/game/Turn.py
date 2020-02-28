class Turn:
    queue = None
    fast_queue = None
    frame = 0
    queue_turn = 0
    rounds = 1

    @staticmethod
    def init():
        Turn.queue = [[], [], [], []]
        Turn.rounds = len(Turn.queue)
        Turn.fast_queue = []
        Turn.frame = 0
        Turn.queue_turn = 0
        from src.game import Global
        Turn.add(Global.menu.turn)
        Turn.add(Global.map_view.turn)
        Turn.add(Global.map_view.update_region)

    @staticmethod
    def update():
        for i in Turn.queue[Turn.frame]:
            i()
        for i in Turn.fast_queue:
            i()
        Turn.frame += 1
        if Turn.frame >= Turn.rounds:
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
