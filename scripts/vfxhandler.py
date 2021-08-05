import pygame

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

    def addRemove(self, location):
        pass

    def addChunkAdd(self, chunk):
        self.effects.append(ChunkCreation(self.editor, chunk))

    def addChunkRemove(self, chunk):
        self.effects.append(ChunkRemoval(self.editor, chunk))

