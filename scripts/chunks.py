import pygame


class Chonky:
    def __init__(self, editor):
        self.layer = 0
        self.tileSize = 16
        self.chunks = {
            'tiles':[],
            'decor':{
                'bg':[],
                'fg':[]
            }
        }

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

    def addTile(self):
        pass

    def removeTile(self):
        pass

    def addLayer(self):
        pass

    def autoTile(self):
        pass

    def flood(self):
        pass
