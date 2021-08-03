import time
import datetime

class Clock:
    def __init__(self):
        self.startTime = 0
        self.lastTime = 0
        self.dt = 0
        self.fpsPace = 60
        self.averageFrames = []

    def start(self):
        self.startTime = time.time()

    def tick(self):
        self.dt = (time.time() - self.lastTime) * 60
        self.lastTime = time.time()
        self.averageFrames.append(self.fps)
        if len(self.averageFrames) > self.fpsPace:
            self.averageFrames.pop(0)

    @property
    def avgFPS(self):
        if self.averageFrames == []:
            return 0    
        return int(sum(self.averageFrames) / len(self.averageFrames))

    @property
    def fps(self):
        if self.dt != 0:
            return int(1 / (self.dt / self.fpsPace))
        return 0

    @property
    def runTime(self):
        return max(0, time.time() - self.startTime)

    def getDate(self):
        now = datetime.datetime.now()
        return now.strftime('%m-%d-%Y %H.%M.%S')
