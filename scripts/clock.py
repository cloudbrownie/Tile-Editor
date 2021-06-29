import time


class Clock:
    def __init__(self):
        self.startTime = 0
        self.lastTime = 0
        self.dt = 0
        self.fpsPace = 60

    def start(self):
        self.startTime = time.time()

    def tick(self):
        self.dt = (time.time() - self.lastTime) * 60
        self.lastTime = time.time()

    @property
    def runTime(self):
        return max(0, time.time() - self.startTime)
