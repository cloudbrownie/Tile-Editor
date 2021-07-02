import pygame
import math

"""
other classes use the editor pointer to access necessary vars in other classes.
this class will not do so as this class will also be used in games and such that will not have the other classes
"""
class Chonky:
    def __init__(self, editor):
        # this will change depending on the project
        self.editor = editor

        self.layer = 0
        self.TILESIZE = 16
        self.CHUNKSIZE = 8
        self.chunks = {}

        self.sheetReferences = {

        }
        self.sheetID = 0

    def update(self):
        return

    """
    used by the rendering class to render the bg, tiles, and foreground.
    rendering class handles this stuff rather than the chunk class since the player images in-game
        will be between the bg and the tile layer
    """
    def getRenderList(self, camRect, scroll):
        # get the visible chunks
        chunks = self.getVisibleChunks(camRect, scroll)

        # store all tile surfs and their blit location
        tileSurfs = []

        # iterate through the visible chunks
        for chunk in chunks:
            data = self.chunks[chunk]['img'], (chunk[0] * self.TILESIZE * self.CHUNKSIZE, chunk[1] * self.TILESIZE * self.CHUNKSIZE)
            tileSurfs.append(data)

        return tileSurfs

    def getVisibleChunks(self, camRect, scroll):
        # start a list of chunks to return
        chunks = []
        # calculate the amount of horizontal and vertical chunks
        horizontalChunks = int(math.ceil(camRect.w / (self.TILESIZE * self.CHUNKSIZE)))
        verticalChunks = int(math.ceil(camRect.h / (self.TILESIZE * self.CHUNKSIZE)))

        # iterate through the amount of horizontal and vertical chunks
        for i in range(horizontalChunks):
            for j in range(verticalChunks):

                # apply the scroll to the location
                chunkx = i + int(math.ceil(scroll[0] / (self.TILESIZE * self.CHUNKSIZE)))
                chunky = j + int(math.ceil(scroll[1] / (self.TILESIZE * self.CHUNKSIZE)))

                # skip the chunk id if it doesnt exist
                if (chunkx, chunky)not in self.chunks:
                    continue

                # append this new id
                chunks.append((chunkx, chunky))

        return chunks

    def addChunk(self, chunkID):
        # add a new chunk and fill it with the default info
        self.chunks[chunkID] = {
            'tiles':{

            },
            'decor':{
                'bg':[],
                'fg':[]
            },
            'img':None
        }

    def getChunkID(self, location, tile=True):
        # unpack the x, y locations
        x, y = location
        # find the chunk id, different equation if looking for tile's
        if tile:
            return x // self.CHUNKSIZE, y // self.CHUNKSIZE
        else:
            return x // (self.CHUNKSIZE * self.TILESIZE), y // (self.CHUNKSIZE * self.TILESIZE)

    def getTile(self):
        return

    def addTile(self, layer, tiledata, sheets, sheetCnfg):
        # somehow this method adds the tile to all chunks

        # unpack the tile data
        sheetname, sheetLoc, loc = tiledata

        # get the chunk id of the current tile and create the chunk if it doesnt exist
        chunkID = self.getChunkID(loc)
        if chunkID not in self.chunks:
            self.addChunk(chunkID)

        # fix the relative chunk position
        tilex, tiley = loc
        tilex %= self.CHUNKSIZE
        tiley %= self.CHUNKSIZE
        if tilex < 0:
            tilex = self.CHUNKSIZE + tilex
        if tiley < 0:
            tiley = self.CHUNKSIZE + tiley

        # create the layer if the layer does not exist
        if layer not in self.chunks[chunkID]['tiles']:
            self.addLayer(chunkID, layer)

        # update the tile data to use the sheet reference so the saved .json doesn't get bloated with long strings
        updatedTileData = self.getSheetID(sheetname), sheetLoc, (tilex, tiley)
        self.chunks[chunkID]['tiles'][layer].append(updatedTileData)

        # redraw the cached surface
        self.cacheChunkSurf(chunkID, sheets, sheetCnfg)

    def cacheChunkSurf(self, chunkID, sheets, sheetCnfg):
        # get the tiles in the chunk
        layers = self.chunks[chunkID]['tiles'].copy()

        # sort the layers and just place into a list from back to front
        srtdLayers = [layer for layer in sorted(layers)]
        tiles = []
        for layer in srtdLayers:
            tiles.append(layers[layer])

        # get the decor in the chunk
        bg = self.chunks[chunkID]['decor']['bg']
        fg = self.chunks[chunkID]['decor']['fg']

        # create a transparent surface for the tiles
        surf = pygame.Surface((self.TILESIZE * self.CHUNKSIZE, self.TILESIZE * self.CHUNKSIZE))
        surf.set_colorkey((0, 0, 0))

        # blit each tile and apply the configuration if it exists
        for row in tiles:
            for tile in row:
                imgRow, imgCol = tile[1]
                img = sheets[self.sheetReferences[tile[0]]][0][imgRow][imgCol].copy()
                tileX, tileY = tile[2]
                tileX *= self.TILESIZE
                tileY *= self.TILESIZE
                if tile[0] in sheetCnfg:
                    offx, offy = sheetCnfg[tile[0]][imgRow][imgCol]
                    surf.blit(img, (tileX + offx, tileY + offy))
                else:
                    surf.blit(img, (tileX, tileY))

        # cache the surf
        self.chunks[chunkID]['img'] = surf.copy()

    def removeTile(self):
        pass

    def addLayer(self, chunkID, layer):
        # just add a new layer in the dictionary of layers
        self.chunks[chunkID]['tiles'][layer] = []

    def addSheetRef(self, sheetname):
        # increment the current sheet id and create a reference
        self.sheetID += 1
        self.sheetReferences[self.sheetID] = sheetname

    def getSheetID(self, sheetname):
        # iterate through all ID's and match the current sheetname to an ID referenced name
        for id in self.sheetReferences:
            if sheetname == self.sheetReferences[id]:
                return id
        # if method did not return earlier, create a new sheet ref and recursively get the ID referenced name
        self.addSheetRef(sheetname)
        # gotta carry the value upwards to the first call of the method since itll only return the found id in the recursively called method and then return None since the first call didnt find it
        id = self.getSheetID(sheetname)
        return id

    def autoTile(self):
        pass

    def flood(self):
        pass
