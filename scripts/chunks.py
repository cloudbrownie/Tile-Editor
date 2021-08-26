import pygame
import math
import copy

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
        self.CACHEIMGPADDING = 3
        self.CACHEIMGSIZE = self.CHUNKPX + self.CACHEIMGPADDING * 2, self.CHUNKPX + self.CACHEIMGPADDING * 2
        self.chunks = {

        }

        self.sheetReferences = {

        }
        self.sheetID = 0

        # for future use of implementing a way to undo certain things
        self.prevActions = []

    @property
    def currentChunks(self):
        '''
        returns a list of all current chunks in the chunk system
        '''
        return [chunk for chunk in self.chunks]

    @property
    def cleanData(self):
        '''
        used during saving to obtain the chunk data without the cached images since the cached images can't be stored in .jsons
        '''
        newChunkData = {}
        for chunk in self.chunks:
            newChunkData[chunk] = {
            'tiles':copy.deepcopy(self.chunks[chunk]['tiles']),
            'decor':copy.deepcopy(self.chunks[chunk]['decor'])
            }
        return newChunkData

    def getRenderList(self, rect):
        '''
        used by the rendering class to render the bg, tiles, and foreground.
        rendering class handles this stuff rather than the chunk class since the player images in-game will be between the bg and the tile layer
        returns a dictionary with blit information
        '''
        # get the visible chunks
        chunks = self.getVisibleChunks(rect)

        # store all tile surfs and their blit location
        tileSurfs = []

        # iterate through the visible chunks
        for chunk in chunks:
            chunkx, chunky = self.deStringifyID(chunk)
            data = {
                'chunkpos':(chunkx * self.CHUNKPX - self.CACHEIMGPADDING, chunky * self.CHUNKPX - self.CACHEIMGPADDING), 
                'bg img':self.chunks[chunk]['imgs']['bg']['img'], 
                'fg img':self.chunks[chunk]['imgs']['fg']['img'],
                'bg subs':self.chunks[chunk]['imgs']['bg']['subs'],
                'fg subs':self.chunks[chunk]['imgs']['fg']['subs']
                }
            tileSurfs.append(data)

        return tileSurfs

    def getVisibleChunks(self, rect, keepAllChunks=False):
        '''
        returns all chunks within the specified rect and scroll. can ignore chunks that don't already exist
        '''
        # start a list of chunks to return
        chunks = []
        # calculate the amount of horizontal and vertical chunks
        horizontalChunks = int(math.ceil(rect.w / (self.CHUNKPX))) + 1
        verticalChunks = int(math.ceil(rect.h / (self.CHUNKPX))) + 1

        # iterate through the amount of horizontal and vertical chunks
        for i in range(horizontalChunks):
            for j in range(verticalChunks):

                # apply the scroll to the location
                chunkx = i + int(math.ceil(rect.x / (self.CHUNKPX))) - 1
                chunky = j + int(math.ceil(rect.y / (self.CHUNKPX))) - 1

                # stringify the chunk id
                chunkID = self.stringifyID(chunkx, chunky)

                # skip the chunk id if it doesnt exist
                if chunkID not in self.chunks and not keepAllChunks:
                    continue

                # append this new id
                chunks.append(self.stringifyID(chunkx, chunky))

        return chunks

    def deStringifyID(self, id):
        '''
        used to turn a chunk id string into an int tuple of the chunkx and chunky. returns a tuple of chunkx, chunky
        '''
        listified = id.split(';')
        return int(listified[0]), int(listified[1])

    def stringifyID(self, chunkx, chunky):
        '''
        used to format a chunk id using the inputted chunkx and chunky. returns a string of the formatted chunk id
        '''
        return f'{chunkx};{chunky}'

    def validID(self, arg):
        '''
        used to convert a tuple chunk format into the string format if not already string format. returns formatted string chunk id
        '''
        if isinstance(arg, tuple):
            return self.stringifyID(arg[0], arg[1])
        return arg

    def addChunk(self, chunkID):
        '''
        adds a new chunk to the class's chunk variable with the default information. input can be either chunkx and chunky or pre formatted chunk id. returns none
        '''
        chunkID = self.validID(chunkID)
        # add a new chunk and fill it with the default info
        self.chunks[chunkID] = {
            'tiles':{

            },
            'decor':{
                'bg':[],
                'fg':[]
            },
            'imgs':{
                'bg':{
                    'img':None,
                    'subs':[]
                },
                'fg':{
                    'img':None,
                    'subs':[]
                }
            }
        }

    def removeChunk(self, chunkID):
        '''
        removes the chunk from the chunk system and deletes it from memory. returns none.
        '''
        if chunkID in self.chunks:
            del self.chunks[chunkID]

    def removeEmptyChunks(self):
        '''
        simply removes all chunks that are completely empty
        '''
        removedChunks = []
        for chunk in self.chunks:
            empty = True
            for layer in self.chunks[chunk]['tiles']:
                if len(self.chunks[chunk]['tiles'][layer]) > 0:
                    empty = False
            for layer in self.chunks[chunk]['decor']:
                if len(self.chunks[chunk]['decor'][layer]) > 0:
                    empty = False
            if empty:
                removedChunks.append(chunk)

        for chunk in removedChunks:
            self.removeChunk(chunk)

        return removedChunks
            
    def removeEmptyLayers(self, chunkID):
        '''
        removes the empty layers from a specifed chunk
        '''
        tileLayers = []
        for layer in self.chunks[chunkID]['tiles']:
            if not len(self.chunks[chunkID]['tiles'][layer]) > 0:
                tileLayers.append(layer)
        for layer in tileLayers:
            del self.chunks[chunkID]['tiles'][layer]
        return tileLayers

    def getChunkID(self, location, tile=True, string=True):
        '''
        intakes a location which is specified to be either a tile position or an exact position and returns the chunk id as either a string or a tuple of ints, specified by the string arg
        '''
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
            return self.stringifyID(x, y)
        else:
            return x, y

    def getTiles(self, loc):
        '''
        returns a list of tiles in a certain location but in different layers. loc arg is not chunk relative
        '''
        # used to get tiles through multiple layers if all tiles are in the same spot
        tiles = []
        for layer in self.chunks[self.getChunkID(loc)]['tiles']:
            for tile in layer:
                if tile[2] == self.getTileLocation(loc):
                    tiles.append(tile)
        return tiles

    def getTileInLayer(self, loc, layer):
        '''
        returns a single tile at a given location and layer. loc arg is not chunk relative
        '''
        # used to get a single tile in a given layer
        for tile in self.chunks[self.getChunkID(loc)]['tiles'][layer]:
            if tile[2] == self.getTileLocation(loc):
                return tile

    def convertExactToTilePosition(self, loc):
        '''
        loc arg is not a tile location and is not a chunk relative position. returns a non chunk relative tile position
        '''
        # returned loc will not be chunk relative
        return loc[0] // self.TILESIZE, loc[1] // self.TILESIZE

    def getRelativeTileLocation(self, loc):
        '''
        loc arg is a non chunk relative tile position. returns a chunk relative tile position
        '''
        # loc is not chunk relative
        tilex, tiley = loc
        tilex %= self.CHUNKSIZE
        tiley %= self.CHUNKSIZE
        if tilex < 0:
            tilex = self.CHUNKSIZE + tilex
        if tiley < 0:
            tiley = self.CHUNKSIZE + tiley
        return tilex, tiley

    def addTile(self, layer, tiledata, sheets, sheetCnfg, flood=False):
        '''
        used to add a tile to the chunk system at a certain layer in a chunk. 
        location of the tile is given in the tile data arg which needs to be formatted as: (sheetname, asset location in sheet, non chunk relative tile position).
        needs the sheets and sheetcnfg args for chunk img caching, but wont chunk img cache if this method is used while flood filling.
        returns the chunk id of the added tile
        '''
        # unpack the tile data
        sheetname, sheetLoc, loc = tiledata

        # get the chunk id of the current tile and create the chunk if it doesnt exist
        chunkID = self.getChunkID(loc)
        if chunkID not in self.chunks:
            self.addChunk(chunkID)

        # fix the relative chunk position
        tilex, tiley = self.getRelativeTileLocation(loc)

        # create the layer if the layer does not exist
        if layer not in self.chunks[chunkID]['tiles']:
            self.addLayer(chunkID, layer)

        # update the tile data to use the sheet reference so the saved .json doesn't get bloated with long strings
        updatedTileData = self.getSheetID(sheetname), sheetLoc, (tilex, tiley)

        validPlace = True

        # check if a tile exists in this exact location already, if so, overwrite it
        for i, tile in enumerate(self.chunks[chunkID]['tiles'][layer]):
            if tile == updatedTileData:
                validPlace = False
            elif tile[2] == updatedTileData[2]:
                validPlace = True
                self.chunks[chunkID]['tiles'][layer].pop(i)

        if validPlace:
            self.chunks[chunkID]['tiles'][layer].append(updatedTileData)

            # redraw the cached surface
            if not flood:
                self.cacheChunkSurf(chunkID, sheets, sheetCnfg)

        return chunkID, updatedTileData, validPlace

    def removeTile(self, layer, loc, sheets, sheetCnfg, bulk=False):
        '''
        used to remove a tile from the chunk system at a certain layer at a certain location.
        location of the tile is given as a non chunk relative tile position.
        needs the sheets and sheetcnfg args for chunk img caching, but wont chunk img cache if this method is used while bulk deleting.
        '''
        # init a var to store the removed tile if there was one removed to return it
        tileData = None

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
                        tileData = tile

                # redraw the chunk surf to update it if the chunk changed
                if changed:
                    self.cacheChunkSurf(chunkID, sheets, sheetCnfg)

            # remove the layer if empty
            self.removeEmptyLayers(chunkID)

            # remove the chunk if empty
            self.removeEmptyChunks()

        return chunkID, tileData

    def findSpillChunks(self, chunk, size, loc):
        '''
        used to find all chunks that an object collides with, given the original chunk, the size of the object, and the topleft location of the object.
        returns a list of all collided chunks as tuples of ints.
        '''
        # unpack chunkx and chunky
        chunkx, chunky = chunk

        # unpack the size
        width, height = size

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

        return spillOverChunks

    def addDecor(self, layer, decordata, sheets, sheetCnfg):
        '''
        used to add a decoration to the chunk system in either the bg or fg in a chunk. 
        location of the decoration is given in the decoration data arg which needs to be formatted as: (sheetname, asset location in sheet, exact position of the topleft point of the decoration).
        needs the sheets and sheetcnfg args for chunk img caching.
        '''
        # unpack the decordata
        sheet, sheetLoc, loc = decordata
        sheetrow, sheetcol = sheetLoc

        # grab a copy of the decoration surface
        decorSurf = sheets[sheet][0][sheetrow][sheetcol].copy()

        # grab the dimensions of the decoration surface
        width, height = decorSurf.get_size()

        # find the string chunk id
        chunkx, chunky = self.getChunkID(loc, tile=False, string=False)
        stringifiedChunkID = self.stringifyID(chunkx, chunky)

        # find the relative blit location of the decor
        blitx = loc[0] - chunkx * self.CHUNKPX
        blity = loc[1] - chunky * self.CHUNKPX

        # add the original chunk if the original chunk doesn't exist
        if stringifiedChunkID not in self.chunks:
            self.addChunk(stringifiedChunkID)

        spillOverChunks = self.findSpillChunks((chunkx, chunky), (width, height), loc)

        # create the new chunks if they don't exist
        for chunk in spillOverChunks:
            chunkStr = self.stringifyID(chunk[0], chunk[1])
            if chunkStr not in self.chunks:
                self.addChunk(chunkStr)

        horizontalSpillOver = max(width - (chunkx * self.CHUNKPX + self.CHUNKPX - loc[0]), 0)
        verticalSpillOver = max(height - (chunky * self.CHUNKPX + self.CHUNKPX - loc[1]), 0)

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
                infoPerChunk[self.stringifyID(spillChunkx, spillChunky)] = [(relativeBlitx, relativeBlity), (decorClipRect.x, decorClipRect.y, decorClipRect.w, decorClipRect.h)]

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

        return [chunk for chunk in infoPerChunk], decordata

    def removeDecor(self, layer, rect, sheets, sheetCnfg, bulk=False):
        # store all effected chunks for recaching later and the decor data if applicable
        effectedChunks = []
        decordata = None

        # use the center of the rect to find the current chunk
        chunkID = self.getChunkID(rect.center, tile=False)
        if chunkID in self.chunks:

            # store all decor to delete
            removeDecor = []
            for i, decor in enumerate(self.chunks[chunkID]['decor'][layer]):
                # make a decor rect from the stored data
                decorRect = pygame.Rect(decor[2][0], decor[2][1], decor[3][2], decor[3][3])

                # since the decor rect is chunk relative, make the rect chunk relative
                relativeRect = rect.copy()
                chunkx, chunky = self.deStringifyID(chunkID)
                relativeRect.x -= chunkx * self.CHUNKPX
                relativeRect.y -= chunky * self.CHUNKPX

                # normalize negative values
                if relativeRect.centerx < 0:
                    relativeRect.centerx = self.CHUNKPX + relativeRect.centerx
                if relativeRect.centery < 0:
                    relativeRect.centery = self.CHUNKPX + relativeRect.centery

                # check if the rects collide
                if relativeRect.colliderect(decorRect):
                    effectedChunks.append(chunkID)

                    # store the decor
                    removeDecor.append(decor)

                    decordata = decor

                    # try to find all decor bits in spill over chunks if they exist
                    sheetID = decor[0]
                    assetLocation = decor[1]
                    width, height = sheets[self.sheetReferences[sheetID]][0][assetLocation[0]][assetLocation[1]].get_size()
                    # if the original dimensions are larger than the current dimensions, then we have spill overs
                    if width > decorRect.w or height > decorRect.h:
                        # find the original topleft placement of the decor to find spill over chunks of the original decor
                        originalTopLeft = chunkx * self.CHUNKPX + decor[2][0] - decor[3][0], chunky * self.CHUNKPX + decor[2][1] - decor[3][1]
                        originalChunk = self.getChunkID(originalTopLeft, tile=False)
                        spillOverChunks = self.findSpillChunks(self.deStringifyID(originalChunk), (width, height), originalTopLeft)
                        # since the spill over chunks contains the original, remove the original from the spill overs
                        spillOverChunks = [chunk for chunk in spillOverChunks if chunk != (chunkx, chunky)]
                        # find each fragment in the spill over chunks
                        for spillChunk in spillOverChunks:
                            # store the relative decor to remove
                            relRemoveDecor = []

                            sChunkx, sChunky = spillChunk
                            # create rects to find the correct rects for the decor through clipping
                            chunkRect = pygame.Rect(sChunkx * self.CHUNKPX, sChunky * self.CHUNKPX, self.CHUNKPX, self.CHUNKPX)
                            chunkRect.normalize()
                            sDecorRect = pygame.Rect(originalTopLeft[0], originalTopLeft[1], width, height)
                            sDecorClip = chunkRect.clip(sDecorRect)

                            # normalize the clipped rect
                            sDecorClip.normalize()

                            # use this clip to find the relative blit location
                            relativeBlitx = sDecorClip.x - sChunkx * self.CHUNKPX
                            relativeBlity = sDecorClip.y - sChunky * self.CHUNKPX

                            # make the topleft coord of the rect relative to the actual decor for the subsurface
                            sDecorClip.x = sDecorClip.x - originalTopLeft[0]
                            sDecorClip.y = sDecorClip.y - originalTopLeft[1]

                            # store the decor to remove in this chunk
                            currentChunk = self.stringifyID(sChunkx, sChunky)
                            for chunkDecor in self.chunks[currentChunk]['decor'][layer]:
                                if chunkDecor[2] == (relativeBlitx, relativeBlity) and chunkDecor[3] == (sDecorClip.x, sDecorClip.y, sDecorClip.w, sDecorClip.h):
                                    relRemoveDecor.append(chunkDecor)

                            if len(relRemoveDecor) > 0:
                                for decor in relRemoveDecor:
                                    self.chunks[currentChunk]['decor'][layer].remove(decor)
                                effectedChunks.append(currentChunk)
            
            for decor in removeDecor:
                self.chunks[chunkID]['decor'][layer].remove(decor)

        if not bulk:
            for chunk in effectedChunks:
                self.cacheChunkSurf(chunk, sheets, sheetCnfg)

        return effectedChunks, decordata

    def cacheChunkSurf(self, chunkID, sheets, sheetCnfg):
        '''
        used to cache an img of the fg and bg layers of a chunk and store the bounding rects of sub surfaces of set pixels in the cached image.
        stores the images in the chunk's data.
        needs the sheets and sheetcnfg.
        '''
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
        fgsurf = pygame.Surface(self.CACHEIMGSIZE)
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
                    fgsurf.blit(img, (tileX + offx + self.CACHEIMGPADDING, tileY + offy + self.CACHEIMGPADDING))
                else:
                    fgsurf.blit(img, (tileX + self.CACHEIMGPADDING, tileY + self.CACHEIMGPADDING))

        # blit each fg decor
        for decor in self.chunks[chunkID]['decor']['fg']:
            imgRow, imgCol = decor[1]
            img = sheets[self.sheetReferences[decor[0]]][0][imgRow][imgCol].copy()
            decorX, decorY = decor[2]
            x, y, w, h = decor[3]
            subsurfRect = pygame.Rect(x, y, w, h)
            subsurface = img.subsurface(subsurfRect)
            fgsurf.blit(subsurface, (decorX + self.CACHEIMGPADDING, decorY + self.CACHEIMGPADDING))

        # create a transparent surface for the bg decor
        bgsurf = pygame.Surface(self.CACHEIMGSIZE)
        bgsurf.set_colorkey((0, 0, 0))

        # blit each bg decor
        for decor in self.chunks[chunkID]['decor']['bg']:
            imgRow, imgCol = decor[1]
            img = sheets[self.sheetReferences[decor[0]]][0][imgRow][imgCol].copy()
            decorX, decorY = decor[2]
            x, y, w, h = decor[3]
            subsurfRect = pygame.Rect(x, y, w, h)
            subsurface = img.subsurface(subsurfRect).copy()
            bgsurf.blit(subsurface, (decorX + self.CACHEIMGPADDING, decorY + self.CACHEIMGPADDING))

        # create the imgs key in the chunk dict if this chunk was originally cleaned
        self.chunks[chunkID]['imgs'] = {
                'bg':{
                    'img':None,
                    'subs':[]
                },
                'fg':{
                    'img':None,
                    'subs':[]
                }
            }

        # cache each surf
        self.chunks[chunkID]['imgs']['fg']['img'] = fgsurf.copy()
        self.chunks[chunkID]['imgs']['bg']['img'] = bgsurf.copy()

        # store the sub surface rects for each chunk using masks
        fgmask = pygame.mask.from_surface(fgsurf)
        fgsubs = fgmask.get_bounding_rects()
        bgmask = pygame.mask.from_surface(bgsurf)
        bgsubs = bgmask.get_bounding_rects()

        self.chunks[chunkID]['imgs']['fg']['subs'] = fgsubs
        self.chunks[chunkID]['imgs']['bg']['subs'] = bgsubs

    def addLayer(self, chunkID, layer):
        '''
        adds a layer in a chunk's tile data.
        '''
        # just add a new layer in the dictionary of layers
        self.chunks[chunkID]['tiles'][layer] = []

    def addSheetRef(self, sheetname):
        # increment the current sheet id and create a reference
        self.sheetID += 1
        self.sheetReferences[self.sheetID] = sheetname

    def getSheetID(self, sheetname):
        '''
        returns the id of a stored sheetname in the chunk's system's sheet reference dictionary.
        if the sheetname is not in the chunk's system's sheet reference dictionary, it is added to the dictionary with a unique integer id and the newly created id is returned.
        '''
        # iterate through all ID's and match the current sheetname to an ID referenced name
        for id in self.sheetReferences:
            if sheetname == self.sheetReferences[id]:
                return id
        # if method did not return earlier, create a new sheet ref and recursively get the ID referenced name
        self.addSheetRef(sheetname)
        # gotta carry the value upwards to the first call of the method since itll only return the found id in the recursively called method and then return None since the first call didnt find it
        id = self.getSheetID(sheetname)
        return id

    def saveCurrentChunks(self):
        '''
        method is called in an input class in order to save the current chunks into the previous actions list for undo-ing.
        also called when flooding, autotiling, and bulk removing
        used in the tile editor to tell the chunks system to save the last action after the user finishes their current action by letting go of left click
        '''
        lastAction = copy.deepcopy(self.cleanData)
        self.prevActions.append(lastAction)

    def undo(self, sheets, sheetCnfg):
        '''
        reverts the chunk system data to a previous version of the chunks, recaches all surfaces since previously saved chunks are stored without cached images.
        cached images can't be stored due to pickling issues with pygame surfaces and rects.
        '''
        if len(self.prevActions) > 0:
            self.chunks = copy.deepcopy(self.prevActions[-1])
            self.prevActions.pop(-1)
            # since the chunks loaded don't have cached surface info from being pickled when saved, must cache each chunk's surface data
            for chunk in self.chunks:
                self.cacheChunkSurf(chunk, sheets, sheetCnfg)

    def autoTile(self, layer, loc, sheets, sheetCnfg, rect=None):
        '''
        used to convert a large amount of tiles into their correct texture based on their neighbors and the configuration set in the sheetcnfg arg.
        if a rect is given, then this method will auto tile all tiles within the rect.
        if a rect is not given, then this method will attempt to auto tile the tile that the location corresponds to, and all other connected tiles of this tile.
        loc arg should be given as a non chunk relative tile location.
        returns none.
        '''
        pass

    def flood(self, layer, tiledata, sheets, sheetCnfg, rect):
        '''
        given a rect for bounding purposes, fills the entire area with tiles of the same texture as given in the tiledata arg. only fills in the given layer.
        creates new chunks.
        needs sheets and sheetcnfg args for caching the images of all affect chunks.
        '''
        # save current chunks into previous actions list for undo feature
        self.saveCurrentChunks()

        # unpack tile data
        sheetname, sheetLoc, loc = tiledata

        # find the current chunks; can just input loc since the tile loc is in tile mode
        originalChunk = self.getChunkID(loc)
        originalTile = self.getRelativeTileLocation(loc)

        # check if a tile in this position already exists; if it does just return
        if originalChunk in self.chunks:
            if layer in self.chunks[originalChunk]['tiles']:
                for tile in self.chunks[originalChunk]['tiles'][layer]:
                    if tile[2] == originalTile:
                        return [], []

        # find the bounding tile positions
        leftBound = self.convertExactToTilePosition(rect.midleft)[0]
        rightBound = self.convertExactToTilePosition(rect.midright)[0]
        topBound = self.convertExactToTilePosition(rect.midtop)[1]
        bottomBound = self.convertExactToTilePosition(rect.midbottom)[1]

        # start the open list and closed list; open list contains the current tile position
        originalChunk = self.deStringifyID(originalChunk)
        currentTile = originalTile[0] + originalChunk[0] * self.CHUNKSIZE, originalTile[1] + originalChunk[1] * self.CHUNKSIZE
        openList = []
        if currentTile[0] > leftBound and currentTile[0] < rightBound and currentTile[1] > topBound and currentTile[1] < bottomBound:
            openList.append(currentTile)
        newTiles = []
        closedList = []

        # find all chunks inside of the rect
        chunks = self.getVisibleChunks(rect)

        # add all existing tiles in the same layer in these chunks if they exist
        for chunk in chunks:
            if layer in self.chunks[chunk]['tiles']:
                for tile in self.chunks[chunk]['tiles'][layer]:
                    currentChunk = self.deStringifyID(chunk)
                    closedTile = tile[2][0] + currentChunk[0] * self.CHUNKSIZE, tile[2][1] + currentChunk[1] * self.CHUNKSIZE
                    closedList.append(closedTile)

        if currentTile not in closedList and currentTile in openList:
            newTiles.append(currentTile)

        while len(openList) > 0:
            # start checking the next available point
            pos = openList[0]
            openList.pop(0)
            # iterate through positions next to the current position in the cardinal directions
            for x, y in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                newpos = pos[0] + x, pos[1] + y
                if newpos in closedList or newpos[0] < leftBound or newpos[0] > rightBound or newpos[1] < topBound or newpos[1] > bottomBound:
                    continue
                if newpos not in openList:
                    openList.append(newpos)
                if newpos not in newTiles:
                    newTiles.append(newpos)
            closedList.append(pos)

        for location in newTiles:
            chunk, _, _ = self.addTile(layer, (sheetname, sheetLoc, location), sheets, sheetCnfg, flood=True)
            if chunk not in chunks:
                chunks.append(chunk)

        for chunk in chunks:
            self.cacheChunkSurf(chunk, sheets, sheetCnfg)

        return chunks, newTiles

    def bulkRemove(self, entityType, layer, sheets, sheetCnfg, rect):
        '''
        deletes all tiles or decor inside a large rect.
        returns a tuple of lists as (chunk list, tile/decor list)
        '''
        # save the chunks for undo feature
        self.saveCurrentChunks()

        # find all chunks inside of the rect
        boundChunks = self.getVisibleChunks(rect)

        # separate action based on type
        if entityType == 'tiles':
            # create the bounding tile positions
            leftBound = self.convertExactToTilePosition(rect.midleft)[0]
            rightBound = self.convertExactToTilePosition(rect.midright)[0]
            topBound = self.convertExactToTilePosition(rect.midtop)[1]
            bottomBound = self.convertExactToTilePosition(rect.midbottom)[1]

            # store all chunks that have been effected for surface recaching
            effectedChunks = []

            # keep track of all unrelative tile locations to remove 
            removeTiles = []
            # iterate through all chunks in bounds
            for chunk in boundChunks:
                # check if the layer exists in the chunk
                if layer in self.chunks[chunk]['tiles']:
                    # iterate through each tile in the layer
                    for tile in self.chunks[chunk]['tiles'][layer]:
                        # convert the tile location to an unrelative tile location and then store it if the location is in bounds
                        chunkx, chunky = self.deStringifyID(chunk)
                        unrelativeTileLocation = tile[2][0] + chunkx * self.CHUNKSIZE, tile[2][1] + chunky * self.CHUNKSIZE
                        if unrelativeTileLocation[0] < leftBound or unrelativeTileLocation[0] > rightBound or unrelativeTileLocation[1] < topBound or unrelativeTileLocation[1] > bottomBound:
                            continue    
                        removeTiles.append(unrelativeTileLocation)


            # store removed tiles
            removedTiles = []

            # remove the tiles outside of iteration because removing during iteration causes issues in this case
            for tileLocation in removeTiles:
                chunk, tile = self.removeTile(layer, tileLocation, sheets, sheetCnfg, bulk=True)
                if tile != None:
                    removedTiles.append(tile)
                if chunk not in effectedChunks:
                    effectedChunks.append(chunk)

            # remove empty chunks
            self.removeEmptyChunks()

            # iterate through effected chunks and recache their surfaces
            for i, chunk in enumerate(effectedChunks):
                if chunk in self.chunks:
                    self.cacheChunkSurf(chunk, sheets, sheetCnfg)
                else:
                    effectedChunks.pop(i)

            return effectedChunks, removedTiles

        elif entityType == 'decorations':
            # store all clip rects 
            clipRects = []
            
            # iterate through each chunk and create a clip rect for each chunk
            for chunk in boundChunks:
                chunkx, chunky = self.deStringifyID(chunk)
                chunkRect = pygame.Rect(chunkx * self.CHUNKPX, chunky * self.CHUNKPX, self.CHUNKPX, self.CHUNKPX)
                clipRect = chunkRect.clip(rect)

                clipRects.append(clipRect)

            # store all effected chunks and removed decor
            effectedChunks = []
            removedDecor = []

            # iterate through all clip rects and call the remove decor method using each clip rect
            for clipRect in clipRects:
                chunks, decor = self.removeDecor(layer, clipRect, sheets, sheetCnfg, bulk=True)
                removedDecor.append(decor)
                if chunk not in effectedChunks:
                    effectedChunks.extend(chunks)

            # remove empty chunks
            self.removeEmptyChunks()

            # iterate throguh effected chunks and recache their surface
            for i, chunk in enumerate(effectedChunks):
                if chunk in self.chunks:
                    self.cacheChunkSurf(chunk, sheets, sheetCnfg)
                else:
                    effectedChunks.pop(i)

            return effectedChunks, removedDecor
