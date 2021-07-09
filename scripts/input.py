import pygame
import sys
import shutil
import os
import json

class Input:
    def __init__(self, editor):
        self.editor = editor

        self.mouseposition = 0, 0
        self.TILESIZE = self.editor.chunks.TILESIZE

        self.penPositionTypes = ['exact', 'grid']
        self.penPositionIndex = 0

        self.penToolTypes = ['draw', 'erase']
        self.penToolIndex = 0

        self.assetTypes = ['tiles', 'decorations']
        self.assetIndex = 0

        self.currentLayer = 0
        self.holding = False

        self.decoLayers = ['Foreground', 'Background']
        self.decoLayerIndex = 0

        self.cursor = pygame.Rect(0, 0, 5, 5)

    @property
    def penPosition(self):
        mx = (self.mouseposition[0] - self.editor.window.toolbar.width) * self.editor.window.camera.ratio[0]
        my = self.mouseposition[1] * self.editor.window.camera.ratio[1]
        if self.penPositionTypes[self.penPositionIndex] == 'exact':
            return mx * self.editor.window.camera.zoom + self.editor.window.camera.scroll[0], my * self.editor.window.camera.zoom + self.editor.window.camera.scroll[1]
        elif self.penPositionTypes[self.penPositionIndex] == 'grid':
            return (mx * self.editor.window.camera.zoom + self.editor.window.camera.scroll[0]) // self.TILESIZE, (my * self.editor.window.camera.zoom + self.editor.window.camera.scroll[1]) // self.TILESIZE

    @property
    def penPositionInfo(self):
        return f'{self.penPositionTypes[self.penPositionIndex]} {self.penPosition}'

    @property
    def currentPositionType(self):
        return self.penPositionTypes[self.penPositionIndex]

    @property
    def currentToolType(self):
        return self.penToolTypes[self.penToolIndex]

    @property
    def currentAssetType(self):
        return self.assetTypes[self.assetIndex]

    @property
    def currentDecorationLayer(self):
        return self.decoLayers[self.decoLayerIndex]

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
                    elif self.mouseposition[0] > self.editor.window.toolbar.width:
                        self.holding = True

                elif event.button == 2:
                    if self.mouseposition[0] > self.editor.window.toolbar.width:
                        self.editor.window.camera.setScrollBoolean(True)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.holding = False

                elif event.button == 2:
                    if self.mouseposition[0] > self.editor.window.toolbar.width:
                        self.editor.window.camera.setScrollBoolean(False)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.penToolIndex = 0
                elif event.key == pygame.K_2:
                    self.penToolIndex = 1
                elif event.key == pygame.K_q:
                    self.penPositionIndex = (self.penPositionIndex + 1) % len(self.penPositionTypes)
                elif event.key == pygame.K_EQUALS:
                    if self.currentAssetType == 'tiles':
                        self.currentLayer += 1
                    elif self.currentAssetType == 'decorations':
                        self.decoLayerIndex = (self.decoLayerIndex + 1) % len(self.decoLayers)
                elif event.key == pygame.K_MINUS:
                    if self.currentAssetType == 'tiles':
                        self.currentLayer -= 1
                    elif self.currentAssetType == 'decorations':
                        self.decoLayerIndex = (self.decoLayerIndex - 1) % len(self.decoLayers)
                elif event.key == pygame.K_ESCAPE:
                    self.editor.stop()
                elif event.key == pygame.K_s:
                    self.save()
                elif event.key == pygame.K_w:
                    self.assetIndex = (self.assetIndex + 1) % len(self.assetTypes)

        # since holding is only used for the editing tools, make holding false when in the toolbar or if the mouse goes out of the window
        if self.mouseposition[0] < self.editor.window.toolbar.width or not pygame.mouse.get_focused():
            self.holding = False

        # call the editing methods
        if self.holding:
            # adding tiles
            if self.currentToolType == 'draw' and self.currentAssetType == 'tiles' and self.currentPositionType == 'grid' and self.editor.window.toolbar.tileLock:
                sheet = self.editor.window.toolbar.sheetLock
                sheetLoc = self.editor.window.toolbar.tileLockLocation
                loc = self.penPosition
                sheets = self.editor.window.toolbar.sheets.sheets
                cnfg = self.editor.window.toolbar.sheets.config
                self.editor.chunks.addTile(self.currentLayer, (sheet, sheetLoc, loc), sheets, cnfg)
            # removing tiles
            elif self.currentToolType == 'erase' and self.currentAssetType == 'tiles' and self.currentPositionType == 'grid' and self.editor.window.toolbar.tileLock:
                loc = self.penPosition
                sheets = self.editor.window.toolbar.sheets.sheets
                cnfg = self.editor.window.toolbar.sheets.config
                self.editor.chunks.removeTile(self.currentLayer, loc, sheets, cnfg)
            # adding decor
            elif self.currentToolType == 'draw' and self.currentAssetType == 'decorations' and self.editor.window.toolbar.tileLock:
                layer = self.currentDecorationLayer
                sheet = self.editor.window.toolbar.sheetLock
                sheetLoc = self.editor.window.toolbar.tileLockLocation
                loc = self.penPosition
                sheetCnfg = self.editor.window.toolbar.sheet.config
                self.editor.chunks.addDecor(layer, (sheet, sheetLoc, loc), sheets, sheetCnfg)
            # removing decor
            elif self.currentToolType == 'draw' and self.currentAssetType == 'decorations' and self.editor.window.toolbar.tileLock:
                pass


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
