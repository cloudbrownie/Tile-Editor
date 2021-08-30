import pygame
import random

from .vfx import Place, Remove, ChunkCreation, ChunkRemoval

class VFXHandler:
    def __init__(self, window):
        '''
        initialize class vars such as a surface cache, a list for effects, etc
        '''
        self.editor = window.editor
        self.surfCache = []
        self.effects = []
        self.effectData = []

    def handleEffects(self):
        '''
        iterates through all effects stored and updates them all
        '''
        effectData = []

        for i, effect in enumerate(self.effects):
            if effect.dead:
                self.effects.pop(i)
            else:
                data = effect.update()
                effectData.append(data)

        self.effectData = effectData

    def addPlace(self, location):
        self.effects.append(Place(self.editor, location))

    def addRemove(self, location, asset):
        width, height = asset.get_size()

        for i in range(random.randint(1, 5)):
            pxLocation = random.randint(0, width - 1), random.randint(0, height - 1)
            effectLocation = [location[0] + pxLocation[0], location[1] + pxLocation[1]]
            color = asset.get_at(pxLocation)
            self.effects.append(Remove(self.editor, effectLocation, color))

    def addChunkAdd(self, chunk):
        self.effects.append(ChunkCreation(self.editor, chunk))

    def addChunkRemove(self, chunk):
        self.effects.append(ChunkRemoval(self.editor, chunk))

