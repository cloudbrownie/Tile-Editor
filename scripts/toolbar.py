import pygame


class Toolbar:
    def __init__(self, window):
        self.window = window

        self.display = pygame.Surface((self.window.window.get_width() * .2, self.window.window.get_height()))
        self.width = self.display.get_width()

        self.divider = pygame.Rect(self.display.get_width() * .05, self.display.get_height() * .2, self.display.get_width() * .9, 2)

        self.color = 47, 62, 70

        self.sheets = {}

        self.tiles = {}

    def render(self):
        self.display.fill(self.color)

        pygame.draw.rect(self.display, (202, 210, 197), self.divider)

        self.window.window.blit(self.display, (0, 0))

    def getAsset(self):
        pass

    def swapSheets(self):
        pass
