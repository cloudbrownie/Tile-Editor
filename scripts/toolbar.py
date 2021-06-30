import pygame
from .font import Font
from .sheets import Sheets

class Toolbar:
    def __init__(self, window):
        self.window = window
        self.inactiveFont = Font(self.window.scale)
        self.inactiveFont.recolor((202, 210, 197))
        self.activeFont = Font(self.window.scale)
        self.sheets = Sheets(self)
        self.clock = self.window.editor.clock

        self.display = pygame.Surface((self.window.window.get_width() * .2, self.window.window.get_height()))
        self.width = self.display.get_width()

        self.divider = pygame.Rect(self.display.get_width() * .05, self.display.get_height() * .2, self.display.get_width() * .9, 2)
        padHeight = self.display.get_height() * .05
        self.dividerPad = pygame.Rect(0, self.divider.top - padHeight // 2, self.width, padHeight)

        self.sheetnameSurf = pygame.Surface((self.width, self.display.get_height() * .2))
        self.tilerenderSurf = pygame.Surface((self.width // 2, self.display.get_height() * .8 // 2))
        self.tileSurfRatio = self.tilerenderSurf.get_width() / self.display.get_width(), self.tilerenderSurf.get_height() / (self.display.get_height() * .8)

        self.COLOR = 47, 62, 70

        self.sheets.loadSheets()
        self.nameOffsets = {}
        self.nameOrigins = {}
        self.tileOrigins = {}
        for sheet in self.sheets.sheets:
            self.nameOffsets[sheet] = 0
            self.nameOrigins[sheet] = self.sheets.sheets[sheet][1].y
            self.tileOrigins[sheet] = [[]]
            for i, row in enumerate(self.sheets.sheets[sheet][2]):
                self.tileOrigins[sheet].append([])
                for j, tile in enumerate(row):
                    self.tileOrigins[sheet][i].append(self.sheets.sheets[sheet][2][i][j].y)

        self.currentSheet = None
        self.sheetLock = None
        self.currentTile = None
        self.tileLock = None
        self.NAMESPEED = 10
        self.NAMESCROLLSPEED = 40
        self.TILESCROLLSPEED = 40
        self.MAXNAMEOFFSET = 20
        self.lockOffset = -20
        self.currentSheetScroll = 0
        self.currentTileScroll = 0

    def renderSheetNames(self):
        self.sheetnameSurf.fill(self.COLOR)

        for sheetname in self.sheets.sheets:
            if sheetname == self.sheetLock or sheetname == self.currentSheet:
                self.sheetnameSurf.blit(self.sheets.sheets[sheetname][4][1], (self.sheets.sheets[sheetname][1].x + self.nameOffsets[sheetname], self.sheets.sheets[sheetname][1].y))
                if sheetname == self.sheetLock:
                    self.activeFont.render(self.sheetnameSurf, '-', (self.sheets.sheets[sheetname][1].x + self.lockOffset, self.sheets.sheets[sheetname][1].y))
            else:
                self.sheetnameSurf.blit(self.sheets.sheets[sheetname][4][0], (self.sheets.sheets[sheetname][1].x + self.nameOffsets[sheetname], self.sheets.sheets[sheetname][1].y))


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
        self.currentSheetScroll = max(0, self.currentSheetScroll + self.NAMESCROLLSPEED * direction)
        self.currentSheetScroll = min(self.sheets.NAMESCROLLBOUND, self.currentSheetScroll)

    def selectSheet(self, cursor, lock=False):
        self.currentSheet = None
        for sheetname in self.sheets.sheets:
            if self.sheets.sheets[sheetname][1].colliderect(cursor):
                self.currentSheet = sheetname
                if lock and self.sheetLock != sheetname:
                    self.lockOffset = -20
                    self.sheetLock = self.currentSheet
                    self.tileLock = None
                    self.currentTileScroll = 0

    def renderTiles(self):
        self.tilerenderSurf.fill(self.COLOR)

        if self.sheetLock:
            for i, row in enumerate(self.sheets.sheets[self.sheetLock][0]):
                for j, tile in enumerate(row):
                    if tile == self.currentTile or tile == self.tileLock:
                        whiteMask = pygame.mask.from_surface(tile).to_surface(unsetcolor=(0, 0, 0, 0))
                        for x, y in [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                            self.tilerenderSurf.blit(whiteMask, (self.sheets.sheets[self.sheetLock][2][i][j].x + x, self.sheets.sheets[self.sheetLock][2][i][j].y + y))
                    self.tilerenderSurf.blit(tile, self.sheets.sheets[self.sheetLock][2][i][j])

        self.display.blit(pygame.transform.scale(self.tilerenderSurf, (self.width, int(self.display.get_height() * .8))), (0, self.display.get_height() * .2))

    def updateTileRects(self):
        if self.sheetLock:
            for i, row in enumerate(self.sheets.sheets[self.sheetLock][0]):
                for j, tile in enumerate(row):
                    self.sheets.sheets[self.sheetLock][2][i][j].y -= (self.sheets.sheets[self.sheetLock][2][i][j].y - (self.tileOrigins[self.sheetLock][i][j] - self.currentTileScroll)) * self.clock.dt // 2

    def adjustTileScroll(self, direction):
        self.currentTileScroll = max(0, self.currentTileScroll + self.TILESCROLLSPEED * direction)
        self.currentTileScroll = min(self.sheets.sheets[self.sheetLock][3], self.currentTileScroll)

    def selectTile(self, cursor, lock=False):
        zeroMousePos = list(cursor)
        zeroMousePos[1] -= self.divider.centery
        zeroMousePos = zeroMousePos[0] * self.tileSurfRatio[0], zeroMousePos[1] * self.tileSurfRatio[1]

        if self.sheetLock:
            self.currentTile = None
            for i, row in enumerate(self.sheets.sheets[self.sheetLock][0]):
                for j, tile in enumerate(row):
                    if self.sheets.sheets[self.sheetLock][2][i][j].collidepoint(zeroMousePos):
                        self.currentTile = tile
                        if lock and self.tileLock != tile:
                            self.tileLock = tile

    def render(self):
        self.display.fill(self.COLOR)

        self.updateSheetRects()
        self.renderSheetNames()

        self.updateTileRects()
        self.renderTiles()

        pygame.draw.rect(self.display, self.COLOR, self.dividerPad)
        pygame.draw.rect(self.display, (202, 210, 197), self.divider)

        self.window.window.blit(self.display, (0, 0))

    def getAsset(self):
        pass

    def swapSheets(self):
        pass
