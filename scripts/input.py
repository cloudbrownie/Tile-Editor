import pygame
import sys

class Input:
    def __init__(self, editor):
        self.editor = editor

        self.mouseposition = 0, 0
        self.tileSize = self.editor.chunks.tileSize

    @property
    def penPosition(self):
        mx = (self.mouseposition[0] - self.editor.window.toolbar.width) * self.editor.window.camera.ratio[0]
        my = self.mouseposition[1] * self.editor.window.camera.ratio[1]
        return (mx * self.editor.window.camera.zoom + self.editor.window.camera.scroll[0]) // self.tileSize, (my * self.editor.window.camera.zoom + self.editor.window.camera.scroll[1]) // self.tileSize

    def update(self):
        # get the mouse position
        self.mouseposition = pygame.mouse.get_pos()

        # handle inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEWHEEL:
                self.editor.window.camera.adjustZoom(-event.y)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    self.editor.window.camera.setScrollBoolean(True)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    self.editor.window.camera.setScrollBoolean(False)


        # update the camera scroll in here since it only updates based on inputs anyways
        self.editor.window.camera.updateScroll()
