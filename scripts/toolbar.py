import pygame
from .font import Font
from .sheets import Sheets

class Toolbar:
    def __init__(self, window):
        self.window = window
        self.font = Font(self.window.scale)
        self.sheets = Sheets(self)
        self.clock = self.window.editor.clock

        self.display = pygame.Surface((self.window.window.get_width() * .2, self.window.window.get_height()))
        self.width = self.display.get_width()

        self.sheetnameSurf = pygame.Surface((self.width, self.display.get_height() * .2))
        self.tilerenderSurf = pygame.Surface((self.width, self.display.get_height() * .8))

        self.divider = pygame.Rect(self.display.get_width() * .05, self.display.get_height() * .2, self.display.get_width() * .9, 2)
        padHeight = self.display.get_height() * .05
        self.dividerPad = pygame.Rect(0, self.divider.top - padHeight // 2, self.width, padHeight)

        self.COLOR = 47, 62, 70

        self.sheets.loadSheets()
        self.nameOffsets = {}
        self.nameOrigins = {}
        for sheet in self.sheets.sheets:
            self.nameOffsets[sheet] = 0
            self.nameOrigins[sheet] = self.sheets.sheets[sheet][1].y

        self.currentSheet = None
        self.sheetLock = None
        self.NAMESPEED = 10
        self.MAXNAMEOFFSET = 20
        self.lockOffset = -20
        self.currentSheetScroll = 0

    def renderSheetNames(self):
        self.sheetnameSurf.fill(self.COLOR)

        for sheetname in self.sheets.sheets:
            if sheetname == self.sheetLock:
                self.font.render(self.sheetnameSurf, sheetname, (self.sheets.sheets[sheetname][1].x + self.nameOffsets[sheetname], self.sheets.sheets[sheetname][1].y))
                self.font.render(self.sheetnameSurf, '-', (self.sheets.sheets[sheetname][1].x + self.lockOffset, self.sheets.sheets[sheetname][1].y))
            else:
                self.font.render(self.sheetnameSurf, sheetname, (self.sheets.sheets[sheetname][1].x + self.nameOffsets[sheetname], self.sheets.sheets[sheetname][1].y))


        self.display.blit(self.sheetnameSurf, (0, 0))

    def updateSheetRects(self):
        for sheetname in self.sheets.sheets:
            if sheetname == self.currentSheet:
                self.nameOffsets[sheetname] = min(self.MAXNAMEOFFSET, self.nameOffsets[sheetname] + self.NAMESPEED * self.clock.dt)
            elif sheetname != self.sheetLock:
                self.nameOffsets[sheetname] = max(0, self.nameOffsets[sheetname] - self.NAMESPEED * self.clock.dt)

            self.sheets.sheets[sheetname][1].y -= (self.sheets.sheets[sheetname][1].y - (self.nameOrigins[sheetname] - self.currentSheetScroll)) * self.clock.dt // 2

        self.lockOffset = min(self.lockOffset + self.NAMESPEED * self.clock.dt // 2, 0)

    def adjustNameScroll(self, direction):
        current = self.currentSheetScroll
        self.currentSheetScroll = max(0, self.currentSheetScroll + self.NAMESPEED * direction)
        self.currentSheetScroll = min(self.sheets.NAMESCROLLBOUND, self.currentSheetScroll)

    def selectSheet(self, cursor, lock=False):
        self.currentSheet = None
        for sheetname in self.sheets.sheets:
            if self.sheets.sheets[sheetname][1].colliderect(cursor):
                self.currentSheet = sheetname
                if lock and self.sheetLock != sheetname:
                    self.lockOffset = -20
                    self.sheetLock = self.currentSheet

    def renderTiles(self):
        self.tilerenderSurf.fill(self.COLOR)

    def render(self):
        self.display.fill(self.COLOR)

        self.updateSheetRects()
        self.renderSheetNames()

        pygame.draw.rect(self.display, self.COLOR, self.dividerPad)
        pygame.draw.rect(self.display, (202, 210, 197), self.divider)

        self.window.window.blit(self.display, (0, 0))

    def getAsset(self):
        pass

    def swapSheets(self):
        pass
