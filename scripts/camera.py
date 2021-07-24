import pygame


class Camera:
    def __init__(self, window):
        self.window = window
        self.scale = self.window.scale
        self.COLOR = 53, 79, 82

        self.originCross = 16 * self.scale

        self.display = pygame.Surface((self.window.window.get_width() * .8, self.window.window.get_height()))

        self.originalSize = self.display.get_width() // 2, self.display.get_height() // 2
        self.camera = pygame.Surface(self.originalSize)
        self.ratio = self.originalSize[0] / self.display.get_width(), self.originalSize[1] / self.display.get_height()

        self.cameraRect = pygame.Rect((0, 0), self.originalSize)

        self.scroll = [-self.camera.get_width() // 2, -self.camera.get_height() // 2]
        self.scrolling = False
        self.zoomValues = [.25, .5, 1, 2, 4]
        self.zIndex = 2
        self.ASSETHOVERALPHA = 120

    @property
    def zoom(self):
        return self.zoomValues[self.zIndex]

    def moveScroll(self, values):
        pass

    def applyScroll(self, values):
        return [(value[0] - self.scroll[0], value[1] - self.scroll[1]) for value in values]

    def adjustZoom(self, value):
        currentIndex = self.zIndex
        self.zIndex += value
        self.zIndex = max(0, self.zIndex)
        self.zIndex = min(self.zIndex, len(self.zoomValues) - 1)
        if currentIndex != self.zIndex:
            self.adjustCamera(value)

    def adjustCamera(self, value):
        center = self.cameraRect.center
        self.cameraRect.width = self.originalSize[0] * self.zoom
        self.cameraRect.height = self.originalSize[1] * self.zoom
        self.cameraRect.center = center
        if value > 0:
            self.scroll = [self.scroll[0] * 2, self.scroll[1] * 2]
        elif value < 0:
            self.scroll = [self.scroll[0] * .5, self.scroll[1] * .5]
        self.camera = pygame.Surface(self.cameraRect.size)

    def render(self):
        self.camera.fill(self.COLOR)

        # render the chunks
        chunkInfo = self.window.editor.chunks.getRenderList(self.cameraRect, self.scroll)
        for chunk in chunkInfo:
            chunkx, chunky = chunk['chunkpos']
            for sub in chunk['bg subs']:
                self.camera.blit(chunk['bg img'], (chunkx + sub.x - self.scroll[0], chunky + sub.y - self.scroll[1]), sub)
            for sub in chunk['fg subs']:
                self.camera.blit(chunk['fg img'], (chunkx + sub.x - self.scroll[0], chunky + sub.y - self.scroll[1]), sub)

        # render the current tile
        if self.window.toolbar.tileLock and self.window.editor.input.currentToolType == 'draw' and self.window.editor.input.currentAssetType == 'tiles':
            tile = self.window.toolbar.tileLock.copy()
            tile.set_alpha(self.ASSETHOVERALPHA)
            x, y = self.window.editor.input.penPosition
            x *= self.window.editor.chunks.TILESIZE
            y *= self.window.editor.chunks.TILESIZE
            self.camera.blit(tile, (x - self.scroll[0], y - self.scroll[1]))

        # render differently if decor
        elif self.window.toolbar.tileLock and self.window.editor.input.currentToolType == 'draw' and self.window.editor.input.currentAssetType == 'decorations':
            decor = self.window.toolbar.tileLock.copy()
            decor.set_alpha(self.ASSETHOVERALPHA)
            x, y = self.window.editor.input.penPosition
            size = decor.get_size()
            self.camera.blit(decor, (x - self.scroll[0] - size[0] // 2, y - self.scroll[1] - size[1] // 2))


        # lines to indicate the origin
        pygame.draw.line(self.camera, (202, 210, 197), (0 - self.scroll[0], self.originCross // 2 - self.scroll[1]), (0 - self.scroll[0], -self.originCross // 2 - self.scroll[1]), self.scale)
        pygame.draw.line(self.camera, (202, 210, 197), (self.originCross // 2 - self.scroll[0], 0 - self.scroll[1]), (-self.originCross // 2 - self.scroll[0], 0 - self.scroll[1]), self.scale)

        # draw the input class's selection box
        if self.window.editor.input.validSBox:
            color = self.window.editor.input.SELECTIONBOXCOLOR
            topleft = list(self.window.editor.input.selectionBox['1'])
            bottomright = list(self.window.editor.input.selectionBox['2'])
            topright = [bottomright[0], topleft[1]]
            bottomleft = [topleft[0], bottomright[1]]
            tl, br, tr, bl = self.applyScroll((topleft, bottomright, topright, bottomleft))
            # just draw lines instead of drawing a rect with a linewidth
            pygame.draw.line(self.camera, color, tl, tr, self.scale)
            pygame.draw.line(self.camera, color, tr, br, self.scale)
            pygame.draw.line(self.camera, color, br, bl, self.scale)
            pygame.draw.line(self.camera, color, bl, tl, self.scale)
        elif self.window.editor.input.selectionBox['1'] and not self.window.editor.input.selectionBox['2']:
            color = self.window.editor.input.SELECTIONBOXCOLOR
            topleft = list(self.window.editor.input.selectionBox['1'])
            bottomright = self.window.editor.input.exactPosition
            topright = [bottomright[0], topleft[1]]
            bottomleft = [topleft[0], bottomright[1]]
            tl, br, tr, bl = self.applyScroll((topleft, bottomright, topright, bottomleft))
            # just draw lines instead of drawing a rect with a linewidth
            pygame.draw.line(self.camera, color, tl, tr, self.scale)
            pygame.draw.line(self.camera, color, tr, br, self.scale)
            pygame.draw.line(self.camera, color, br, bl, self.scale)
            pygame.draw.line(self.camera, color, bl, tl, self.scale)

        # update the camera
        self.display.blit(pygame.transform.scale(self.camera, self.display.get_size()), (0, 0))
        self.window.window.blit(self.display, (self.window.window.get_width() * .2, 0))

    def setScrollBoolean(self, boolean):
        self.scrolling = boolean
        pygame.mouse.get_rel()

    def updateScroll(self):
        if self.scrolling:
            dx, dy = pygame.mouse.get_rel()
            dx *= self.ratio[0]
            dy *= self.ratio[1]
            self.scroll[0] -= dx * self.zoom
            self.scroll[1] -= dy * self.zoom
            self.cameraRect.topleft = self.scroll
