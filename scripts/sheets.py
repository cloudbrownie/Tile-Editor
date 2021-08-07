import pygame
import os
import json

class Sheets:
    def __init__(self, toolbar):
        # for use of other classes of the toolbar
        self.toolbar = toolbar

        # init an empty sheet dictionary that will store all sheets and their loaded textures
        # example: {'name':[[2D asset list], namerect, [assetrects], maxassetscroll, [namerenders]]
        self.sheets = {
        }

        # init the config, will be a dictionary of 2D lists of offsets to their corresponding tiles
        # example: {'name':[[2D list of cnfg per asset]]}
        self.config = {
        }

        # constants for sheet name rendering in the toolbar and vars used for scrolling
        self.YSPACE = 7
        self.XSPACE = 5
        self.NAMESCROLLBOUND = 0

        # create an input folder if it doesn't exist
        if not os.path.isdir('input/'):
            os.mkdir('input/')

    def loadSheets(self):

        # load from all sheets in the input folder (any .pngs)
        sheetnameY = self.YSPACE * 2
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
            size = self.toolbar.inactiveFont.size(sheetname)
            rect = pygame.Rect((self.XSPACE, sheetnameY), size)
            sheetnameY += size[1] + self.YSPACE

            # create the name renders to store in a cache
            inactiveRender = pygame.Surface(size)
            self.toolbar.inactiveFont.render(inactiveRender, sheetname, (0, 0))
            inactiveRender.set_colorkey((0, 0, 0))
            activeRender = pygame.Surface(size)
            self.toolbar.activeFont.render(activeRender, sheetname, (0, 0))
            activeRender.set_colorkey((0, 0, 0))

            # create asset rects
            assetRects = []
            assetRectY = self.toolbar.dividerPad.h // 4 + self.YSPACE
            for row in assets:
                assetRectX = self.XSPACE
                assetRow = []
                for asset in row:
                    assetRow.append(pygame.Rect(assetRectX, assetRectY, asset.get_width(), asset.get_height()))
                    assetRectX += asset.get_width() + self.XSPACE
                    if assetRectX > self.toolbar.tilerenderSurf.get_width():
                        assetRectX = asset.get_width() + self.XSPACE * 3
                        assetRectY += max([rect.height for rect in assetRow]) + self.YSPACE
                        assetRow[-1].x = self.XSPACE * 2
                        assetRow[-1].y = assetRectY
                assetRectY += max([rect.height for rect in assetRow]) + self.YSPACE
                assetRects.append(assetRow)
            assetRectY += assetRects[-1][-1].h

            scrollBound = max(0, assetRectY - self.toolbar.tilerenderSurf.get_height() - self.toolbar.dividerPad.h // 2)

            # store data in the dict
            self.sheets[sheetname] = [assets, rect, assetRects, scrollBound, [inactiveRender, activeRender]]

        if self.sheets != {}:
            self.NAMESCROLLBOUND = max(0, sheetnameY - self.toolbar.sheetnameSurf.get_height() + self.YSPACE + self.toolbar.dividerPad.h // 2)

    def loadConfig(self):
        # check if there is a config.json in the input folder, exit the method if there is no config
        files = [file for file in os.listdir('input/') if file.endswith('.json')]
        if 'config.json' not in files:
            return

        # otherwise, just load the .json data into the config
        with open('input/config.json') as readFile:
            self.config = json.load(readFile)
