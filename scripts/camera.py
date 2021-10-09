import pygame
import math

def absround(val):
    if val > 0:
        return math.ceil(val)
    return math.floor(val)

class Camera:
    def __init__(self, window):
        self.window = window
        self.clock = self.window.editor.clock
        self.scale = self.window.scale
        self.COLOR = 53, 79, 82

        self.originCross = 16 * self.scale

        self.display = pygame.Surface((self.window.window.get_width() * .8, self.window.window.get_height()))

        self.originalSize = self.display.get_width() // 2, self.display.get_height() // 2
        self.camera = pygame.Surface(self.originalSize)
        self.ratio = self.originalSize[0] / self.display.get_width(), self.originalSize[1] / self.display.get_height()

        self.scroll = [-self.camera.get_width() // 2, -self.camera.get_height() // 2]
        self.scrollTarget = [self.scroll[0], self.scroll[1]]
        self.scrollSpeed = 5
        self.targetSpeed = 3
        self.cameraRect = pygame.Rect(self.scroll, self.originalSize)
        self.scrolling = False
        self.zoomValues = [.25, .5, 1, 2, 4, 8]
        self.zIndex = 2
        self.zoom = self.zoomValues[self.zIndex]
        self.zoomTarget = self.zoomValues[self.zIndex]
        self.zoomSpeed = 5
        self.ASSETHOVERALPHA = 120

    def render(self):
        self.camera.fill(self.COLOR)

        # render the visual effects
        effectData = self.window.vfx.effectData
        for data in effectData:
            surface, blitLocation = data
            self.camera.blit(surface, (blitLocation[0] - self.scroll[0], blitLocation[1] - self.scroll[1]), special_flags=pygame.BLEND_RGBA_ADD)

        # render the chunks
        chunkInfo = self.window.editor.chunks.getRenderList(self.cameraRect)
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
        pygame.draw.line(self.camera, (202, 210, 197), (0 - self.scroll[0] - self.scale / 2, self.originCross // 2 - self.scroll[1]), (0 - self.scroll[0] - self.scale / 2, -self.originCross // 2 - self.scroll[1] - self.scale / 2), self.scale) # bottom to top
        pygame.draw.line(self.camera, (202, 210, 197), (self.originCross // 2 - self.scroll[0], 0 - self.scroll[1] - self.scale / 2), (-self.originCross // 2 - self.scroll[0] - self.scale / 2, 0 - self.scroll[1] - self.scale / 2), self.scale) # right to left

        # draw the input class's selection box
        if self.window.editor.input.validSBox:
            color = self.window.editor.input.sboxColor
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
            color = self.window.editor.input.sBoxRed
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

    def arrowScroll(self, x, y):
        self.scrollTarget[0] += x * self.scrollSpeed * self.zoom
        self.scrollTarget[1] += y * self.scrollSpeed * self.zoom

    def applyScroll(self, values):
        return [(value[0] - self.scroll[0], value[1] - self.scroll[1]) for value in values]

    def updateScroll(self):
        if self.scrolling:
            dx, dy = pygame.mouse.get_rel()
            dx *= self.ratio[0]
            dy *= self.ratio[1]
            self.scrollTarget[0] -= dx * self.zoom
            self.scrollTarget[1] -= dy * self.zoom
            self.cameraRect.topleft = self.scroll
        if self.scroll != self.scrollTarget:
            dx = ((self.scrollTarget[0] - self.scroll[0]) / self.targetSpeed) * self.clock.dt
            dy = ((self.scrollTarget[1] - self.scroll[1]) / self.targetSpeed) * self.clock.dt
            self.scroll[0] += absround(dx)
            self.scroll[1] += absround(dy)
            self.cameraRect.topleft = self.scroll
            if abs(self.scroll[0] - self.scrollTarget[0]) <= .5:
                self.scroll[0] = self.scrollTarget[0]
            if abs(self.scroll[1] - self.scrollTarget[1]) <= .5:
                self.scroll[1] = self.scrollTarget[1]

    def updateZoom(self):
        if self.zoom != self.zoomTarget:
            dz = ((self.zoomTarget - self.zoom) / self.zoomSpeed) * self.clock.dt
            self.zoom += dz
            self.adjustCamera()
            if abs(self.zoom - self.zoomTarget) <= .01:
                self.zoom = self.zoomTarget

    def adjustZoom(self, value):
        self.zIndex += value
        self.zIndex = max(0, self.zIndex)
        self.zIndex = min(self.zIndex, len(self.zoomValues) - 1)
        self.zoomTarget = self.zoomValues[self.zIndex]

    def adjustCamera(self):
        center = self.cameraRect.center
        self.cameraRect.width = self.originalSize[0] * self.zoom
        self.cameraRect.height = self.originalSize[1] * self.zoom
        self.camera = pygame.Surface(self.cameraRect.size)
        self.cameraRect.center = center
        self.scroll = list(self.cameraRect.topleft)
        self.scrollTarget = list(self.cameraRect.topleft)
        pygame.mouse.get_rel()

    def grid(self):
        '''
        '''