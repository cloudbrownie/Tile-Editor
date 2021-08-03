import pygame
import sys
import shutil
import os
import json

# store keybinds
DRAW = pygame.K_1
ERASE = pygame.K_2
SELECT = pygame.K_3
INCREMENTLAYER = pygame.K_EQUALS
DECREMENTLAYER = pygame.K_MINUS
QUIT = pygame.K_ESCAPE
SAVE = pygame.K_s
UNDO = pygame.K_z
TYPESWAP = pygame.K_w
AUTOTILE = pygame.K_a
FLOOD = pygame.K_f
BULKREMOVE = pygame.K_r

class Input:
    def __init__(self, editor):
        self.editor = editor

        self.mouseposition = 0, 0
        self.TILESIZE = self.editor.chunks.TILESIZE
        self.DECORERASERSIZE = 32

        self.penToolTypes = ['draw', 'erase', 'select']
        self.penToolIndex = 0

        self.assetTypes = ['tiles', 'decorations']
        self.assetIndex = 0

        self.currentLayer = 0
        self.holding = False

        self.decoLayers = ['Background', 'Foreground']
        self.decoLayerIndex = 0

        self.selectionBox = {
            '1':None,
            '2':None
        }
        self.MINIMUMSBOXAREA = self.editor.chunks.TILESIZE ** 2
        self.SELECTIONBOXCOLOR = 255, 255, 255

        self.cursor = pygame.Rect(0, 0, 5, 5)

    @property
    def penPosition(self):
        mx = (self.mouseposition[0] - self.editor.window.toolbar.width) * self.editor.window.camera.ratio[0]
        my = self.mouseposition[1] * self.editor.window.camera.ratio[1]
        if self.currentAssetType == 'decorations':
            return int(mx * self.editor.window.camera.zoom + self.editor.window.camera.scroll[0]), int(my * self.editor.window.camera.zoom + self.editor.window.camera.scroll[1])
        elif self.currentAssetType == 'tiles':
            return int((mx * self.editor.window.camera.zoom + self.editor.window.camera.scroll[0]) // self.TILESIZE), int((my * self.editor.window.camera.zoom + self.editor.window.camera.scroll[1]) // self.TILESIZE)

    @property
    def decorEraser(self):
        return pygame.Rect(self.penPosition[0] - self.DECORERASERSIZE / 2, self.penPosition[1] - self.DECORERASERSIZE / 2, self.DECORERASERSIZE, self.DECORERASERSIZE).copy()

    @property
    def currentChunk(self):
        return self.editor.chunks.getChunkID(self.penPosition, tile=(self.currentAssetType == 'tiles'))

    @property
    def exactPosition(self):
        mx = (self.mouseposition[0] - self.editor.window.toolbar.width) * self.editor.window.camera.ratio[0]
        my = self.mouseposition[1] * self.editor.window.camera.ratio[1] 
        return int(mx * self.editor.window.camera.zoom + self.editor.window.camera.scroll[0]), int(my * self.editor.window.camera.zoom + self.editor.window.camera.scroll[1])

    @property
    def currentToolType(self):
        return self.penToolTypes[self.penToolIndex]

    @property
    def currentAssetType(self):
        return self.assetTypes[self.assetIndex]

    @property
    def currentDecorationLayer(self):
        if self.decoLayerIndex == 0:
            return 'fg'
        elif self.decoLayerIndex == 1:
            return 'bg'

    def resetSBox(self):
        self.selectionBox = {
            '1':None,
            '2':None
        }

    def normalizeSBox(self):
        # normalize the coordinates easily using pygame's built in rect normalize function
        if self.selectionBox['1'] and self.selectionBox['2']:
            x1, y1 = self.selectionBox['1']
            x2, y2 = self.selectionBox['2']
            rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
            rect.normalize()
            self.selectionBox['1'] = rect.topleft
            self.selectionBox['2'] = rect.bottomright
            return True
        return False

    def getSBoxArea(self):
        if self.normalizeSBox():
            return (self.selectionBox['2'][0] - self.selectionBox['1'][0]) * (self.selectionBox['2'][1] - self.selectionBox['1'][1])
        return 0

    @property
    def selectionBoxRect(self):
        self.normalizeSBox()
        return pygame.Rect(self.selectionBox['1'], (self.selectionBox['2'][0] - self.selectionBox['1'][0], self.selectionBox['2'][1] - self.selectionBox['1'][1]))

    @property
    def validSBox(self):
        return self.getSBoxArea() > self.MINIMUMSBOXAREA

    def update(self):
        # get the mouse position
        self.mouseposition = pygame.mouse.get_pos()
        self.cursor.center = self.mouseposition

        # handle inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
                    elif self.mouseposition[0] > self.editor.window.toolbar.width and self.currentToolType != 'select':
                        self.editor.chunks.saveCurrentChunks()
                        self.holding = True
                    elif self.mouseposition[0] > self.editor.window.toolbar.width and self.currentToolType == 'select':
                        if not self.selectionBox['1']:
                            self.selectionBox['1'] = self.exactPosition
                        elif self.selectionBox['1']:
                            self.resetSBox()
                            self.selectionBox['1'] = self.exactPosition

                elif event.button == 2:
                    if self.mouseposition[0] > self.editor.window.toolbar.width:
                        self.editor.window.camera.setScrollBoolean(True)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.holding = False
                    if self.mouseposition[0] > self.editor.window.toolbar.width and self.currentToolType == 'select' and self.selectionBox['1']:
                        self.selectionBox['2'] = self.exactPosition

                elif event.button == 2:
                    if self.mouseposition[0] > self.editor.window.toolbar.width:
                        self.editor.window.camera.setScrollBoolean(False)

            elif event.type == pygame.KEYDOWN:
                # changing pen tools
                if event.key == DRAW:
                    self.penToolIndex = 0
                elif event.key == ERASE:
                    self.penToolIndex = 1
                elif event.key == SELECT:
                    self.penToolIndex = 2
                # changing layers
                elif event.key == INCREMENTLAYER:
                    if self.currentAssetType == 'tiles':
                        self.currentLayer += 1
                    elif self.currentAssetType == 'decorations':
                        self.decoLayerIndex = (self.decoLayerIndex + 1) % len(self.decoLayers)
                elif event.key == DECREMENTLAYER:
                    if self.currentAssetType == 'tiles':
                        self.currentLayer -= 1
                    elif self.currentAssetType == 'decorations':
                        self.decoLayerIndex = (self.decoLayerIndex - 1) % len(self.decoLayers)
                # quit event
                elif event.key == QUIT:
                    self.editor.stop()
                # saving
                elif event.key == SAVE:
                    self.save()
                # undo 
                elif event.key == UNDO:
                    sheets = self.editor.window.toolbar.sheets.sheets
                    cnfg = self.editor.window.toolbar.sheets.config
                    self.editor.chunks.undo(sheets, cnfg)
                # changing between tiles and decorations
                elif event.key == TYPESWAP:
                    self.assetIndex = (self.assetIndex + 1) % len(self.assetTypes)
                # auto tiling 
                elif event.key == AUTOTILE:
                    if self.currentAssetType == 'tiles' and self.currentToolType == 'select':
                        self.editor.chunks.autoTile()
                # flood filling 
                elif event.key == FLOOD:
                    if self.currentAssetType == 'tiles':
                        if self.validSBox:
                            layer = self.currentLayer
                            sheet = self.editor.window.toolbar.sheetLock
                            sheetLoc = self.editor.window.toolbar.tileLockLocation
                            loc = self.penPosition
                            sheets = self.editor.window.toolbar.sheets.sheets
                            cnfg = self.editor.window.toolbar.sheets.config
                            rect = self.selectionBoxRect
                            self.editor.chunks.flood(layer, (sheet, sheetLoc, loc), sheets, cnfg, rect)
                        else:
                            layer = self.currentLayer
                            sheet = self.editor.window.toolbar.sheetLock
                            sheetLoc = self.editor.window.toolbar.tileLockLocation
                            loc = self.penPosition
                            sheets = self.editor.window.toolbar.sheets.sheets
                            cnfg = self.editor.window.toolbar.sheets.config
                            rect = self.editor.window.camera.cameraRect.copy()
                            self.editor.chunks.flood(layer, (sheet, sheetLoc, loc), sheets, cnfg, rect)
                # bulk removing
                elif event.key == BULKREMOVE:
                    if self.currentAssetType == 'tiles' and self.validSBox:
                        entityType = self.currentAssetType
                        layer = self.currentLayer
                        sheets = self.editor.window.toolbar.sheets.sheets
                        cnfg = self.editor.window.toolbar.sheets.config
                        rect = self.selectionBoxRect
                        self.editor.chunks.bulkRemove(entityType, layer, sheets, cnfg, rect)
                    elif self.currentAssetType == 'decor' and self.validSBox:
                        pass

        # since holding is only used for the editing tools, make holding false when in the toolbar or if the mouse goes out of the window
        if self.mouseposition[0] < self.editor.window.toolbar.width or not pygame.mouse.get_focused():
            self.holding = False

        # call the editing methods
        if self.holding:
            # adding tiles
            if self.currentToolType == 'draw' and self.currentAssetType == 'tiles' and self.editor.window.toolbar.tileLock:
                sheet = self.editor.window.toolbar.sheetLock
                sheetLoc = self.editor.window.toolbar.tileLockLocation
                loc = self.penPosition
                sheets = self.editor.window.toolbar.sheets.sheets
                cnfg = self.editor.window.toolbar.sheets.config
                self.editor.chunks.addTile(self.currentLayer, (sheet, sheetLoc, loc), sheets, cnfg)
            # removing tiles
            elif self.currentToolType == 'erase' and self.currentAssetType == 'tiles' and self.editor.window.toolbar.tileLock:
                loc = self.penPosition
                sheets = self.editor.window.toolbar.sheets.sheets
                cnfg = self.editor.window.toolbar.sheets.config
                self.editor.chunks.removeTile(self.currentLayer, loc, sheets, cnfg)
            # adding decor
            elif self.currentToolType == 'draw' and self.currentAssetType == 'decorations' and self.editor.window.toolbar.tileLock:
                layer = self.currentDecorationLayer
                sheet = self.editor.window.toolbar.sheetLock
                sheetLoc = self.editor.window.toolbar.tileLockLocation
                locx, locy = self.penPosition
                loc = locx - self.editor.window.toolbar.tileLock.get_width() // 2, locy - self.editor.window.toolbar.tileLock.get_height() // 2
                sheets = self.editor.window.toolbar.sheets.sheets
                sheetCnfg = self.editor.window.toolbar.sheets.config
                self.editor.chunks.addDecor(layer, (sheet, sheetLoc, loc), sheets, sheetCnfg)
            # removing decor
            elif self.currentToolType == 'erase' and self.currentAssetType == 'decorations' and self.editor.window.toolbar.tileLock:
                layer = self.currentDecorationLayer
                loc = self.penPosition
                sheets = self.editor.window.toolbar.sheets.sheets
                sheetCnfg = self.editor.window.toolbar.sheets.config
                self.editor.chunks.removeDecor(layer, loc, sheets, sheetCnfg)

        # when selecting, if the selection box area is too small, just destroy the selection box
        if self.selectionBox['1'] and self.selectionBox['2'] and (not self.validSBox or self.currentToolType != 'select'):
            self.resetSBox()

        # update the selected sheet name
        self.editor.window.toolbar.selectSheet(self.cursor)

        # update the selected tile
        self.editor.window.toolbar.selectTile(self.mouseposition)

        # stop scrolling if the mouse goes into the toolbar
        if self.mouseposition[0] < self.editor.window.toolbar.width:
            self.editor.window.camera.setScrollBoolean(False)

        # update the camera scroll in here since it only updates based on inputs anyways
        self.editor.window.camera.updateScroll()

    """
    create a new folder with all of the current chunk data in a .json file, copies of each of the spritesheets, and a copy of the config for each of the spritesheets
    """
    def save(self):
        # save the path to the folder
        path = f'output/{self.editor.clock.getDate()}'

        # create a folder in the output folder to store all the data in
        os.mkdir(path)

        # clean the chunk data from the imgs
        chunkData = self.editor.chunks.cleanData

        # store only the config data of the sheets in use
        cnfg = {}
        for sheet in self.editor.window.toolbar.sheets.config:
            for key in self.editor.chunks.sheetReferences:
                if sheet == self.editor.chunks.sheetReferences[key]:
                    cnfg[sheet] == self.editor.window.toolbar.sheets.config[sheet]

        # the .json stores sheet reference dict, the config data dict, and the chunk data dict, stored in that order in a single dict
        data = {
        'refs':self.editor.chunks.sheetReferences,
        'config':cnfg,
        'chunks':chunkData
        }

        # write the data to the .json
        with open(f'{path}/data.json', 'w') as writeFile:
            json.dump(data, writeFile)

        # gather the paths of all used sheets
        sheets = []
        for id in self.editor.chunks.sheetReferences:
            sheets.append(f'input/{self.editor.chunks.sheetReferences[id]}')

        # copy all sheets over into the new folder
        for sheet in sheets:
            shutil.copy(sheet, path)
