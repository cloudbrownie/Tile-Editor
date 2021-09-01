import pygame
import time
import random

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

class TilePlace(Effect):
    '''
    effect used for tile and decor placements.
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

class DecorPlace(Effect):
    '''
    effect used for decor placements.
    '''
    def __init__(self, editor, topleft, asset):
        super().__init__(editor)
        self.location = topleft
        self.mask = pygame.mask.from_surface(asset)
        self.w, self.h = asset.get_size()
        self.scale = 1
        self.mxscale = 1.75
        self.grwRate = .075
        self.innerscale = .75

    def update(self):
        outSize = self.w * self.scale, self.h * self.scale
        surface = pygame.Surface(outSize)
        surface.set_colorkey((0, 0, 0))
        whitemask = self.mask.to_surface(unsetcolor=(0, 0, 0, 0))
        intsize = int(outSize[0]), int(outSize[1])
        surface.blit(pygame.transform.scale(whitemask, intsize), (0, 0))

        inSize = int(self.w * self.innerscale), int(self.h * self.innerscale)
        alphamask = self.mask.to_surface(setcolor=(0, 0, 0))
        surface.blit(pygame.transform.scale(alphamask, inSize), ((outSize[0] - inSize[0]) / 2, (outSize[0] - inSize[0]) / 2))

        blitx = self.location[0] - (outSize[0] - self.w) / 2
        blity = self.location[1] - (outSize[1] - self.h) / 2

        self.scale = min(self.scale + self.grwRate * self.clock.dt, self.mxscale)
        self.innerscale = min(self.innerscale + self.grwRate * self.clock.dt, self.scale)
        if self.innerscale == self.scale:
            self.dead = True

        return surface, (blitx, blity)

class Remove(Effect):
    '''
    effect used for tile and decor removals.
    '''
    def __init__(self, editor, location, color):
        super().__init__(editor)
        self.decayRate = random.uniform(.05, .15)
        self.radius = random.randint(2, 5)
        self.location = location
        self.color = color
        self.vels = random.uniform(-1, 1), random.uniform(-1, 1)

    def update(self):
        surface = pygame.Surface((self.radius, self.radius))
        surface.fill(self.color)
        
        self.location[0] += self.vels[0] * self.clock.dt
        self.location[1] += self.vels[1] * self.clock.dt

        self.radius -= self.decayRate * self.clock.dt
        if self.radius <= 0:
            self.dead = True

        return surface, self.location

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