import pygame


class Camera:
    def __init__(self, window, ):
        self.window = window
        self.color = 53, 79, 82

        self.scroll = [0, 0]
        self.zoom = 1

        self.display = pygame.Surface((self.window.window.get_width() * .8, self.window.window.get_height()))

    def render(self):
        self.display.fill(self.color)

        self.window.window.blit(self.display, (self.window.window.get_width() * .2, 0))
