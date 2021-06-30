import pygame
from .camera import Camera
from .toolbar import Toolbar
from .gui import GUI

WINDOWSIZE = 1500, 800

class Window:
    def __init__(self, editor):
        # init the module
        pygame.init()

        self.editor = editor

        # create the editor window
        self.window = pygame.display.set_mode(WINDOWSIZE, flags=pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption('Tile Editor')

        # scale for pixel art aesthetic
        self.scale = 2

        # initialize the toolbar, camera, and font system
        self.toolbar = Toolbar(self)
        self.camera = Camera(self)
        self.gui = GUI(self)

    def update(self):
        self.window.fill((0, 0, 0))

        self.toolbar.render()
        self.camera.render()
        self.editor.chunks.render()
        self.gui.render(self.editor.input)

        pygame.display.flip()
