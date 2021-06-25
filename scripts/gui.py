import pygame
from .font import Font

class GUI:
    def __init__(self, window, scale):
        self.window = window

        self.scale = scale
        self.font = Font(self.scale)

    def render(self, input):
        # pen position
        self.font.render(self.window.window, str(input.penPosition), (self.window.window.get_width() * .2 + 2, 2))