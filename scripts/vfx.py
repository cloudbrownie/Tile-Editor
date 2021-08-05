import pygame
import time

class Effect:
    '''
    base effect class for all other effects.
    '''

    def __init__(self, editor):
        '''
        base initialize method for non specific class vars.
        take in the editor arg to give effects access to any needed vars.
        '''
        self.dead = False
        self.editor = editor
        self.clock = editor.clock

    def update(self):
        '''
        base method to ensure all effects have this method.
        '''
        pass

class Place(Effect):
    '''
    effect used for tile and decor placements, except for flood cases.
    '''
    def __init__(self, editor, topleft):
        super().__init__(editor)
        self.center = topleft[0] + editor.chunks.TILESIZE / 2, topleft[1] + editor.chunks.TILESIZE / 2
        self.outerRadius = editor.chunks.TILESIZE
        self.innerRadius = self.outerRadius / 2
        self.maxRadius = self.outerRadius * 2
        self.growSpeed = 1

    def update(self):        
        surface = pygame.Surface((self.outerRadius, self.outerRadius))
        surface.set_colorkey((0, 0, 0))
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, self.outerRadius, self.outerRadius))
        pygame.draw.rect(surface, (0, 0, 0), ((self.outerRadius - self.innerRadius) / 2, (self.outerRadius - self.innerRadius) / 2, self.innerRadius, self.innerRadius))
        
        blitLoc = self.center[0] - surface.get_width() / 2, self.center[1] - surface.get_height() / 2

        # grow the two radiuses
        self.outerRadius += self.growSpeed * self.clock.dt
        self.innerRadius += self.growSpeed * self.clock.dt
        # cap the radiuses
        self.outerRadius = min(self.outerRadius, self.maxRadius)
        self.innerRadius = min(self.innerRadius, self.maxRadius)
        if self.innerRadius >= self.maxRadius:
            self.dead = True

        return surface, blitLoc

class Remove(Effect):
    '''
    effect used for tile and decor removals.
    '''
    def __init__(self, editor):
        super().__init__(editor)

    def update(self):
        pass

class ChunkCreation(Effect):
    '''
    effect used for chunk creation
    '''
    def __init__(self, editor, chunk):
        super().__init__(editor)
        self.rect = pygame.Rect(chunk[0] * self.editor.chunks.CHUNKPX, chunk[1] * self.editor.chunks.CHUNKPX, self.editor.chunks.CHUNKPX, self.editor.chunks.CHUNKPX)
        self.green = 255
        self.decayRate = 10
        self.width = 3

    def update(self):
        surface = pygame.Surface(self.rect.size)
        surface.set_colorkey((0, 0, 0))
        relativeRect = self.rect.copy()
        relativeRect.topleft = 0, 0
        pygame.draw.rect(surface, (0, self.green, 0), relativeRect, self.width)

        self.green -= self.decayRate * self.clock.dt
        self.green = max(0, self.green)
        if self.green == 0:
            self.dead = True

        return surface, self.rect.topleft

class ChunkRemoval(Effect):
    '''
    effect used for chunk removal
    '''
    def __init__(self, editor, chunk):
        super().__init__(editor)
        self.rect = pygame.Rect(chunk[0] * self.editor.chunks.CHUNKPX, chunk[1] * self.editor.chunks.CHUNKPX, self.editor.chunks.CHUNKPX, self.editor.chunks.CHUNKPX)
        self.red = 255
        self.decayRate = 10
        self.width = 3

    def update(self):
        surface = pygame.Surface(self.rect.size)
        surface.set_colorkey((0, 0, 0))
        relativeRect = self.rect.copy()
        relativeRect.topleft = 0, 0
        pygame.draw.rect(surface, (self.red, 0, 0), relativeRect, self.width)

        self.red -= self.decayRate * self.clock.dt
        self.red = max(0, self.red)
        if self.red == 0:
            self.dead = True

        return surface, self.rect.topleft