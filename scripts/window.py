import pygame
from .camera import Camera
from .toolbar import Toolbar
from .font import Font

WINDOWSIZE = 1200, 800

class Window:
    def __init__(self, editor):
        # init the module
        pygame.init()

        # create the editor window
        self.window = pygame.display.set_mode(WINDOWSIZE, flags=pygame.SCALED | pygame.RESIZABLE)

        # initialize the toolbar, camera, and font system
        self.toolbar = Toolbar(self)
        self.camera = Camera(self)
        self.font = Font()


    def update(self):
        self.window.fill((0, 0, 0))


        pygame.display.flip()
