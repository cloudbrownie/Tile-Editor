import pygame
from .font import Font

class GUI:
    def __init__(self, window):
        self.window = window

        self.scale = self.window.scale
        self.font = Font(self.scale)

    def render(self, input):
        # making the render text
        renderText = f'[-] or [+] Layer {input.currentLayer}\n[Q] {input.penPositionInfo}\nCurrent Tool: {input.currentToolType}\n[1] Draw\n[2] Erase'

        # render the text
        self.font.render(self.window.window, renderText, (self.window.window.get_width() * .2 + 2, 2))
