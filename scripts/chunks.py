import pygame


class Chonky:
    def __init__(self, editor):
        self.editor = editor

        self.layer = 0
        self.tileSize = 16
        self.chunks = {
            'tiles':{

            },
            'decor':{
                'bg':[],
                'fg':[]
            }
        }

        self.sheetReferences = {

        }
        self.sheetID = 0

    def update(self):
        return

    def render(self):
        pass

    def addChunk(self, location):
        pass

    def getVisibleChunks(self):
        return

    def getTile(self):
        return

    def addTile(self, layer, tiledata):
        sheetname, sheetLoc, chunkLoc = tiledata

        if layer not in self.chunks['tiles']:
            self.addLayer(layer)

        if tiledata[0] not in self.sheetReferences:
            self.addSheetRef(sheetname)

        updatedTileData = self.getSheetID(sheetname), sheetLoc, chunkLoc
        self.chunks['tiles'][layer].append(updatedTileData)

    def removeTile(self):
        pass

    def addLayer(self, layer):
        self.chunks['tiles'][layer] = []

    def addSheetRef(self, sheetname):
        self.sheetID += 1
        self.sheetReferences[self.sheetID] = sheetname

    def getSheetID(self, sheetname):
        # iterate through all ID's and match the current sheetname to an ID referenced name
        for ID in self.sheetReferences:
            if sheetname == self.sheetReferences[ID]:
                return ID
        # if method did not return earlier, create a new sheet ref and recursively get the ID referenced name
        self.addSheetRef(sheetname)
        self.getSheetID(sheetname)

    def autoTile(self):
        pass

    def flood(self):
        pass
