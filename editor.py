import pygame
import json
import os
import cProfile
import pstats
from scripts.chunks import Chonky
from scripts.clock import Clock
from scripts.sheets import Sheets
from scripts.window import Window
from scripts.input import Input

class Editor:
    def __init__(self):
        self.clock = Clock()
        self.window = Window(self)
        self.chunks = Chonky(self)
        self.input = Input(self)

    def update(self):
        self.chunks.update()
        self.window.update()
        self.input.update()
        self.clock.tick()

    def run(self):
        self.running = True

        self.clock.start()
        while self.running:
            self.update()

    def stop(self):
        self.running = False

def main():
    Editor().run()

main()

# profiling
#with cProfile.Profile() as pr:
#    main()

#stats = pstats.Stats(pr)
#stats.sort_stats(pstats.SortKey.TIME)
#stats.print_stats()
