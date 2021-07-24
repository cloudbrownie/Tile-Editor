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
        self.CHUNKPX = self.TILESIZE * self.CHUNKSIZE
        self.chunks = {}

        self.sheetReferences = {

        }
        self.sheetID = 0

    @property
    def currentChunks(self):
        return [chunk for chunk in self.chunks]

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
            data = self.chunks[str(chunk)]['imgs']['fg'], (chunk[0] * self.CHUNKPX, chunk[1] * self.CHUNKPX)
            tileSurfs.append(data)

        return tileSurfs

    def getVisibleChunks(self, camRect, scroll):
        # start a list of chunks to return
        chunks = []
        # calculate the amount of horizontal and vertical chunks
        horizontalChunks = int(math.ceil(camRect.w / (self.CHUNKPX)))
        verticalChunks = int(math.ceil(camRect.h / (self.CHUNKPX)))

        # iterate through the amount of horizontal and vertical chunks
        for i in range(horizontalChunks):
            for j in range(verticalChunks):

                # apply the scroll to the location
                chunkx = i + int(math.ceil(scroll[0] / (self.CHUNKPX)))
                chunky = j + int(math.ceil(scroll[1] / (self.CHUNKPX)))

                # stringify the chunk id
                chunkID = f'({chunkx}, {chunky})'

                # skip the chunk id if it doesnt exist
                if chunkID not in self.chunks:
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
            'imgs':{
                'bg':None,
                'fg':None
            }
        }

    def getChunkID(self, location, tile=True, string=True):
        # unpack the x, y locations
        x, y = location
        # find the chunk id, different equation if looking for tile's
        if tile:
            x = int(x // self.CHUNKSIZE)
            y = int(y // self.CHUNKSIZE)
        else:
            x = int(x // (self.CHUNKPX))
            y = int(y // (self.CHUNKPX))
        if string:
            return f'({x}, {y})'
        else:
            return x, y

    def getTile(self):
        return

    def addTile(self, layer, tiledata, sheets, sheetCnfg):
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

        # check if a tile exists in this exact location already, if so, overwrite it
        for i, tile in enumerate(self.chunks[chunkID]['tiles'][layer]):
            if tile[2] == updatedTileData[2]:
                self.chunks[chunkID]['tiles'][layer].pop(i)

        self.chunks[chunkID]['tiles'][layer].append(updatedTileData)

        # redraw the cached surface
        self.cacheChunkSurf(chunkID, sheets, sheetCnfg)

    def removeTile(self, layer, loc, sheets, sheetCnfg):
        # find the current chunk
        chunkID = self.getChunkID(loc)
        if chunkID in self.chunks:

            # get the list of tiles of the selected layer
            if layer in self.chunks[chunkID]['tiles']:
                tiles = self.chunks[chunkID]['tiles'][layer]

                # fix the relative chunk position
                tilex, tiley = loc
                tilex %= self.CHUNKSIZE
                tiley %= self.CHUNKSIZE
                if tilex < 0:
                    tilex = self.CHUNKSIZE + tilex
                if tiley < 0:
                    tiley = self.CHUNKSIZE + tiley
                loc = tilex, tiley

                # store a boolean of whether or not the chunk has changed in order to see if re caching the chunk is necessary
                changed = False

                # iterate through the tiles and remove the tile that matches the given grid position
                for i, tile in enumerate(tiles):
                    if tile[2] == loc:
                        tiles.pop(i)
                        changed = True

                # redraw the chunk surf to update it if the chunk changed
                if changed:
                    self.cacheChunkSurf(chunkID, sheets, sheetCnfg)

    def addDecor(self, layer, decordata, sheets, sheetCnfg):
        # unpack the decordata
        sheet, sheetLoc, loc = decordata
        sheetrow, sheetcol = sheetLoc

        # grab a copy of the decoration surface
        decorSurf = sheets[sheet][0][sheetrow][sheetcol].copy()

        # grab the dimensions of the decoration surface
        width, height = decorSurf.get_size()

        # find the string chunk id
        chunkx, chunky = self.getChunkID(loc, tile=False, string=False)
        stringifiedChunkID = f'({chunkx}, {chunky})'
        
        # find the relative blit location of the decor
        blitx = loc[0] - chunkx * self.CHUNKPX
        blity = loc[1] - chunky * self.CHUNKPX

        # add the original chunk if the original chunk doesn't exist
        if stringifiedChunkID not in self.chunks:
            self.addChunk(stringifiedChunkID)
        
        # find the horizontal and vertical spill over
        horizontalSpillOver = max(width - (chunkx * self.CHUNKPX + self.CHUNKPX - loc[0]), 0)
        verticalSpillOver = max(height - (chunky * self.CHUNKPX + self.CHUNKPX - loc[1]), 0)

        # find how many more chunks the spill over spills into
        chunksToTheRight = math.ceil(horizontalSpillOver / (self.CHUNKPX))
        chunksToTheBottom = math.ceil(verticalSpillOver / (self.CHUNKPX))

        # THIS NEXT PART DOES NOT WORK SINCE IF THERE ARE NO CHUNKS TO THE RIGHT OR TO THE BOTTOM, NO NEW CHUNKS WILL BE CREATED
        rightChunks = []
        # find chunks to the right of the original chunk
        for i in range(chunksToTheRight):
            newChunkx = chunkx + i + 1
            newChunk = newChunkx, chunky
            rightChunks.append(newChunk)
        # find chunks to the bottom of the original chunk and to the bottom of the spill over chunks on the right
        rightChunks.append((chunkx, chunky))
        bottomChunks = []
        for i in range(chunksToTheBottom):
            for chunk in rightChunks:
                newChunky = chunky + i + 1
                newChunk = chunk[0], newChunky
                # these chunks are kept separate for now since it would just continually add new chunks with no end
                bottomChunks.append(newChunk)
        # merge the chunk lists
        spillOverChunks = rightChunks + bottomChunks
        # create the new chunks if they don't exist
        for chunk in spillOverChunks:
            if str(chunk) not in self.chunks:
                self.addChunk(str(chunk))

        # for each chunk, find the subsurface coordinates needed to properly cut out the decoration for the chunk; init the info dict with the current chunk's info
        infoPerChunk = {
        stringifiedChunkID:[(blitx, blity), (0, 0, width - horizontalSpillOver, height - verticalSpillOver)]
        }
        for chunk in spillOverChunks:
            spillChunkx, spillChunky = chunk

            # create rects to find the correct rects for the decor through clipping
            chunkRect = pygame.Rect(spillChunkx * self.CHUNKPX, spillChunky * self.CHUNKPX, self.CHUNKPX, self.CHUNKPX)
            chunkRect.normalize()
            decorRect = pygame.Rect(loc[0], loc[1], width, height)

            decorClipRect = chunkRect.clip(decorRect)
            
            # use this clip to find the relative blit location
            relativeBlitx = decorClipRect.x - spillChunkx * self.CHUNKPX
            relativeBlity = decorClipRect.y - spillChunky * self.CHUNKPX

            # normalize the clipped rect
            decorClipRect.normalize()

            # make the topleft coord of the rect relative to the actual decor for the subsurface
            decorClipRect.x = decorClipRect.x - loc[0]
            decorClipRect.y = decorClipRect.y - loc[1]

            if decorClipRect.x >= 0 and decorClipRect.y >= 0:
                infoPerChunk[f'({spillChunkx}, {spillChunky})'] = [(relativeBlitx, relativeBlity), (decorClipRect.x, decorClipRect.y, decorClipRect.w, decorClipRect.h)]

        # for each chunk, add the decoration to the chunk's appropriate layer in the decoration dict
        for chunk in infoPerChunk:
            data = self.getSheetID(sheet), sheetLoc, infoPerChunk[chunk][0], infoPerChunk[chunk][1]
            # check if this exact decor data exists in the current chunk and layer; if so, overwrite it
            for i, decor in enumerate(self.chunks[chunk]['decor'][layer]):
                if decor[2] == data[2]:
                    self.chunks[chunk]['decor'][layer].pop(i)

            self.chunks[chunk]['decor'][layer].append(data)
            # redraw each cached image for each affected chunk
            self.cacheChunkSurf(chunk, sheets, sheetCnfg)

    def removeDecor(self, layer, loc, sheets, sheetCnfg):
        # find the current chunk
        chunkID = self.getChunkID(loc, tile=False)
        if chunkID in self.chunks:

            # store a boolean of whether or not the chunk has changed in order to see if re caching the chunk is necessary
            changed = False

            # get the list of decor in the selected layer
            decors = self.chunks[chunkID]['decor'][layer]
            for i, decor in enumerate(decors):
                # make a decor rect fro mthe stored decor data
                decorRect = decor[2][0], decor[2][1], decor[3][2], decor[3][3] 

                # since the decorRect is relative to the current chunk, make the location relative to the current chunk
                loc = [loc[0] - (loc[0] // self.CHUNKPX), loc[1] - (loc[1] // self.CHUNKPX)]

                # normalize negative values
                if loc[0] < 0:
                    loc[0] = self.CHUNKPX + loc[0]
                if loc[1] < 0:
                    loc[1] = self.CHUNKPX + loc[1]

                # check if the point is inside of the decor rect
                if pygame.Rect(decorRect).collidepoint(loc):
                    decors.pop(i)
                    changed = True

            # redraw the chunk surf to update it if the chunk changed
            if changed:
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

        # create a transparent surface for the tiles and fg decor
        fgsurf = pygame.Surface((self.CHUNKPX, self.CHUNKPX))
        fgsurf.set_colorkey((0, 0, 0))

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
                    fgsurf.blit(img, (tileX + offx, tileY + offy))
                else:
                    fgsurf.blit(img, (tileX, tileY))

        # blit each fg decor 
        for decor in self.chunks[chunkID]['decor']['fg']:
            imgRow, imgCol = decor[1]
            img = sheets[self.sheetReferences[decor[0]]][0][imgRow][imgCol].copy()
            decorX, decorY = decor[2]
            x, y, w, h = decor[3]
            subsurfRect = pygame.Rect(x, y, w, h)
            subsurface = img.subsurface(subsurfRect)
            fgsurf.blit(subsurface, (decorX, decorY))

        # create a transparent surface for the bg decor
        bgsurf = pygame.Surface((self.CHUNKPX, self.CHUNKPX))
        bgsurf.set_colorkey((0, 0, 0))

        # blit each bg decor
        for decor in self.chunks[chunkID]['decor']['bg']:
            imgRow, imgCol = decor[1]
            img = sheets[self.sheetReferences[decor[0]]][0][imgRow][imgCol].copy()
            decorX, decorY = decor[2]
            x, y, w, h = decor[3]
            subsurfRect = pygame.Rect(x, y, w, h)
            subsurface = img.subsurface(subsurfRect).copy()
            bgsurf.blit(subsurface, (decorX, decorY))

        # cache each surf
        self.chunks[chunkID]['imgs']['fg'] = fgsurf.copy()
        self.chunks[chunkID]['imgs']['bg'] = bgsurf.copy()

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

    '''
    used during saving to obtain the chunk data without the cached images since the cached images can't be stored in .jsons
    '''
    @property
    def cleanData(self):
        newChunkData = {}
        for chunk in self.chunks:
            newChunkData[chunk] = {
            'tiles':self.chunks[chunk]['tiles'],
            'decor':self.chunks[chunk]['decor']
            }
        return newChunkData
