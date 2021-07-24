import time
import datetime

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
    def fps(self):
        try:
            return int(1 / (self.dt / self.fpsPace))
        except:
            return 0

    @property
    def runTime(self):
        return max(0, time.time() - self.startTime)

    def getDate(self):
        now = datetime.datetime.now()
        return now.strftime('%m-%d-%Y %H.%M.%S')
