class Overlay:
    def __init__(self):
        self.weather = [0, 0, 0, 0]
        self.fade = [0, 0, 0, 0]
        self.fading = False
        self.minimum = [0, 0, 0, 0]

    def colorize(self, color):
        if not color:
            self.weather = [0, 0, 0, 0]
        else:
            self.weather = color

    def blackout(self):
        self.fade = [0, 0, 0, 255]
        self.fading = True

    def clear(self):
        self.fade[3] = 0
        self.turn()

    def turn(self):
        if self.fading:
            if self.fade[3] <= 10:
                self.fading = False
                self.fade[3] = 0
            else:
                self.fade = [self.fade[0], self.fade[1], self.fade[2], self.fade[3] - 8]
            for i in range(4):
                self.minimum[i] = max(self.weather[i], self.fade[i])
