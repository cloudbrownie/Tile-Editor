import pygame


class Chonky:
    def __init__(self, editor):
        self.editor = editor

        self.layer = 0
        self.TILESIZE = 16
        self.CHUNKSIZE = 8
        self.DEFAULTCHUNKINFO = {
            'tiles':{

            },
            'decor':{
                'bg':[],
                'fg':[]
            }
        }
        self.chunks = {}

        self.sheetReferences = {

        }
        self.sheetID = 0

    def update(self):
        return

    def render(self):
        pass

    def addChunk(self, chunkID, tile=True):
        self.chunks[chunkID] = self.DEFAULTCHUNKINFO

    def getChunkID(self, location, tile=True):
        x, y = location
        if tile:
            chunkID = x // self.CHUNKSIZE, y // self.CHUNKSIZE
        else:
            chunkID = x // (self.CHUNKSIZE * self.TILESIZE), y // (self.CHUNKSIZE * self.TILESIZE)
        return chunkID

    def getVisibleChunks(self):
        return

    def getTile(self):
        return

    def addTile(self, layer, tiledata):
        sheetname, sheetLoc, loc = tiledata

        chunkID = self.getChunkID(loc)
        if chunkID not in self.chunks:
            self.addChunk(chunkID)

        if layer not in self.chunks[chunkID]['tiles']:
            self.addLayer(chunkID, layer)

        if tiledata[0] not in self.sheetReferences:
            self.addSheetRef(sheetname)

        updatedTileData = self.getSheetID(sheetname), sheetLoc, loc
        self.chunks[chunkID]['tiles'][layer].append(updatedTileData)

    def removeTile(self):
        pass

    def addLayer(self, chunkID, layer):
        self.chunks[chunkID]['tiles'][layer] = []

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
