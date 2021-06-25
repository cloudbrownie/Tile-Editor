import pygame
import json
import os
from scripts.chunks import Chonky
from scripts.sheets import Sheets
from scripts.window import Window
from scripts.input import Input

class Editor:
    def __init__(self):
        self.window = Window(self)
        self.chunks = Chonky(self)
        self.input = Input(self)
        self.sheets = Sheets(self)

    def update(self):
        self.input.update()
        self.chunks.update()
        self.window.update()

    def run(self):
        while True:
            self.update()

Editor().run()
