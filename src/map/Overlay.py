class Overlay:
    DIM_LIGHT = [40, 40, 40, 90]
    WEATHER = [[0, 0, 0, 180], [10, 0, 30, 180], [10, 0, 30, 180], [10, 0, 30, 180], [30, 0, 10, 160],  # 12 ~ 4
               [40, 0, 20, 140], [40, 0, 0, 140], [60, 0, 0, 120], DIM_LIGHT, DIM_LIGHT,  # 5 ~ 9
               DIM_LIGHT, DIM_LIGHT, DIM_LIGHT, DIM_LIGHT, DIM_LIGHT,  # 10 ~ 14
               DIM_LIGHT, DIM_LIGHT, DIM_LIGHT, [0, 0, 60, 120], [20, 0, 80, 120],  # 15 ~ 19]
               [0, 0, 60, 140], [0, 0, 40, 160], [0, 0, 30, 180], [0, 0, 30, 180]]  # 20 ~ 23
    LIGHT = [0, 0, 0, 0, 0, 0, 1, 3, 6, 9, 9, 9, 9, 9, 9, 9, 9, 9, 5, 2, 0, 0, 0, 0]

    def __init__(self):
        self.weather = [0, 0, 0, 0]
        self.weather_target = [0, 0, 0, 0]
        self.fade = [0, 0, 0, 0]
        self.fading = False
        self.blending = 0
        self.minimum = [0, 0, 0, 0]

    def set_time(self, time):
        self.colorize(Overlay.WEATHER[time])

    def colorize(self, color):
        if not color:
            self.weather = [0, 0, 0, 0]
        else:
            self.weather_target = color
            self.blending = 20

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
            self.on_sight_change()
        if self.blending > 0:
            for i in range(4):
                self.weather[i] += int((self.weather_target[i] - self.weather[i]) / self.blending)
            self.blending -= 1

    def on_sight_change(self):
        for i in range(4):
            self.minimum[i] = max(self.weather[i], self.fade[i])
