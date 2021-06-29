import pygame
import json
import os
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
        self.input.update()
        self.chunks.update()
        self.window.update()
        self.clock.tick()

    def run(self):
        self.clock.start()
        while True:
            self.update()

Editor().run()
