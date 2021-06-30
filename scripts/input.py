import pygame
import sys

class Input:
    def __init__(self, editor):
        self.editor = editor

        self.mouseposition = 0, 0
        self.tileSize = self.editor.chunks.tileSize

        self.penPositionTypes = ['exact', 'grid']
        self.penPositionIndex = 0

        self.penToolTypes = ['draw', 'erase']
        self.penToolIndex = 0

        self.currentLayer = 0

        self.cursor = pygame.Rect(0, 0, 5, 5)

    @property
    def penPosition(self):
        mx = (self.mouseposition[0] - self.editor.window.toolbar.width) * self.editor.window.camera.ratio[0]
        my = self.mouseposition[1] * self.editor.window.camera.ratio[1]
        if self.penPositionTypes[self.penPositionIndex] == 'exact':
            return mx * self.editor.window.camera.zoom + self.editor.window.camera.scroll[0], my * self.editor.window.camera.zoom + self.editor.window.camera.scroll[1]
        elif self.penPositionTypes[self.penPositionIndex] == 'grid':
            return (mx * self.editor.window.camera.zoom + self.editor.window.camera.scroll[0]) // self.tileSize, (my * self.editor.window.camera.zoom + self.editor.window.camera.scroll[1]) // self.tileSize

    def update(self):
        # get the mouse position
        self.mouseposition = pygame.mouse.get_pos()
        self.cursor.center = self.mouseposition

        # handle inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.editor.stop()

            elif event.type == pygame.MOUSEWHEEL:
                if self.mouseposition[0] > self.editor.window.toolbar.width:
                    self.editor.window.camera.adjustZoom(-event.y)
                elif self.mouseposition[0] < self.editor.window.toolbar.width and self.mouseposition[1] < self.editor.window.toolbar.dividerPad.centery:
                    self.editor.window.toolbar.adjustNameScroll(-event.y)
                elif self.mouseposition[0] < self.editor.window.toolbar.width and self.mouseposition[1] > self.editor.window.toolbar.dividerPad.centery:
                    self.editor.window.toolbar.adjustTileScroll(-event.y)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.mouseposition[0] < self.editor.window.toolbar.width and self.mouseposition[1] < self.editor.window.toolbar.divider.centery:
                        self.editor.window.toolbar.selectSheet(self.cursor, lock=True)
                    elif self.mouseposition[0] < self.editor.window.toolbar.width and self.mouseposition[1] > self.editor.window.toolbar.divider.centery:
                        self.editor.window.toolbar.selectTile(self.mouseposition, lock=True)
                elif event.button == 2:
                    if self.mouseposition[0] > self.editor.window.toolbar.width:
                        self.editor.window.camera.setScrollBoolean(True)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    if self.mouseposition[0] > self.editor.window.toolbar.width:
                        self.editor.window.camera.setScrollBoolean(False)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.penToolIndex = 0
                elif event.key == pygame.K_2:
                    self.penToolIndex = 1
                elif event.key == pygame.K_q:
                    self.penPositionIndex += 1
                    if self.penPositionIndex >= len(self.penPositionTypes):
                        self.penPositionIndex = 0
                elif event.key == pygame.K_EQUALS:
                    self.currentLayer += 1
                elif event.key == pygame.K_MINUS:
                    self.currentLayer -= 1

        # update the selected sheet name
        self.editor.window.toolbar.selectSheet(self.cursor)

        # update the selected tile
        self.editor.window.toolbar.selectTile(self.mouseposition)

        # stop scrolling if the mouse goes into the toolbar
        if self.mouseposition[0] < self.editor.window.toolbar.width:
            self.editor.window.camera.setScrollBoolean(False)

        # update the camera scroll in here since it only updates based on inputs anyways
        self.editor.window.camera.updateScroll()
