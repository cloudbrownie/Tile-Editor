import pygame


class Camera:
    def __init__(self, window, scale):
        self.window = window
        self.scale = scale
        self.color = 53, 79, 82

        self.originCross = 16 * self.scale

        self.display = pygame.Surface((self.window.window.get_width() * .8, self.window.window.get_height()))

        self.originalSize = self.display.get_width() // 2, self.display.get_height() // 2
        self.camera = pygame.Surface(self.originalSize)
        self.ratio = self.originalSize[0] / self.display.get_width(), self.originalSize[1] / self.display.get_height()

        self.cameraRect = pygame.Rect((0, 0), self.originalSize)

        self.scroll = [-self.camera.get_width() // 2, -self.camera.get_height() // 2]
        self.scrolling = False
        self.zoomValues = [.25, .5, 1, 2, 4]
        self.zIndex = 1

    @property
    def zoom(self):
        return self.zoomValues[self.zIndex]

    def moveScroll(self, values):
        pass

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
        self.camera.fill(self.color)

        pygame.draw.line(self.camera, (202, 210, 197), (0 - self.scroll[0], self.originCross // 2 - self.scroll[1]), (0 - self.scroll[0], -self.originCross // 2 - self.scroll[1]), self.scale)
        pygame.draw.line(self.camera, (202, 210, 197), (self.originCross // 2 - self.scroll[0], 0 - self.scroll[1]), (-self.originCross // 2 - self.scroll[0], 0 - self.scroll[1]), self.scale)

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
