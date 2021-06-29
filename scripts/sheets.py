import pygame
import os
import json

class Sheets:
    def __init__(self, toolbar):
        # for use of other classes of the toolbar
        self.toolbar = toolbar

        # init an empty sheet dictionary that will store all sheets and their loaded textures
        # example: {'name':[[2D asset list], namerect, [assetrects], maxassetscroll]
        self.sheets = {
        }

        # init the config, will be a dictionary of 2D lists of offsets to their corresponding tiles
        self.config = {
        }

        # constants for sheet name rendering in the toolbar and vars used for scrolling
        self.YSPACE = 5
        self.XSPACE = 5
        self.NAMESCROLLBOUND = 0

    def loadSheets(self):

        # load from all sheets in the input folder (any .pngs)
        sheetnameY = self.YSPACE
        for sheetname in [file for file in os.listdir('input/') if file.endswith('.png')]:

            # load the sheet and textures
            sheet = pygame.image.load(f'input/{sheetname}').convert()
            assets = []
            for i in range(sheet.get_height()):
                if sheet.get_at((0, i)) == (166, 255, 0, 255):
                    row = []
                    for j in range(sheet.get_width()):
                        if sheet.get_at((j, i)) == (255, 41, 250, 255):
                            w, h = 0, 0
                            for x in range(j + 1, sheet.get_width()):
                                if sheet.get_at((x, i)) == (0, 255, 255, 255):
                                    w = x - j - 1
                                    break
                            for y in range(i + 1, sheet.get_height()):
                                if sheet.get_at((j, y)) == (0, 255, 255, 255):
                                    h = y - i - 1
                                    break
                            asset = pygame.Surface((w, h))
                            asset.blit(sheet, (0, 0), (j + 1, i + 1, w, h))
                            asset.set_colorkey((0, 0, 0))
                            row.append(asset.copy())
                    assets.append(row)

            # create the sheet name rect
            size = self.toolbar.font.size(sheetname)
            rect = pygame.Rect((self.XSPACE, sheetnameY), size)
            sheetnameY += size[1] + self.YSPACE

            # create asset rects
            assetRects = []
            assetRectY = self.toolbar.dividerPad.h // 2 + self.YSPACE
            for row in assets:
                assetRectX = self.XSPACE
                assetRow = []
                for asset in row:
                    assetRow.append(pygame.Rect(assetRectX, assetRectY, asset.get_width(), asset.get_height()))
                    assetRectX += asset.get_width() + self.XSPACE
                    if assetRectX > self.toolbar.width:
                        assetRectX = asset.get_width() + self.XSPACE * 3
                        assetRectY += max([rect.height for rect in assetRow]) + self.YSPACE
                        assetRow[-1].x = self.XSPACE * 2
                        assetRow[-1].y = assetRectY
                assetRectY += max([rect.height for rect in assetRow]) + self.YSPACE
                assetRects.append(assetRow)

            scrollBound = max(0, assetRectY - self.toolbar.tilerenderSurf.get_height() - self.toolbar.dividerPad.bottom)

            # store data in the dict
            self.sheets[sheetname] = [assets, rect, assetRects, scrollBound, 0]

        if self.sheets != {}:
            self.NAMESCROLLBOUND = max(0, sheetnameY - self.toolbar.sheetnameSurf.get_height() + self.YSPACE + self.toolbar.dividerPad.h // 2)

    def loadConfig(self, filename):
        # skip the method if there is no config
        if not filename:
            return
