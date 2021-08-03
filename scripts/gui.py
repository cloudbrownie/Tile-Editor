import pygame
from .font import Font

class GUI:
    def __init__(self, window):
        self.window = window

        self.scale = self.window.scale
        self.font = Font(self.scale)

    def render(self, input):

        # start the gui text with the fps
        texts = [str(self.window.editor.clock.avgFPS)]

        # add on the asset type
        texts.append(f'[W] Current Asset Type: {input.currentAssetType}')

        # add on the layer text
        if input.currentAssetType == 'tiles':
            texts.append(f'[-] Layer {input.currentLayer} [+]')
        elif input.currentAssetType == 'decorations':
            texts.append(f'[-] {input.currentDecorationLayer} [+]')

        # add on the pen position info
        texts.append(f'Pen Position: {input.penPosition}')

        texts.append(f'Chunk: {input.currentChunk}')

        # add on the current tool text
        texts.append(f'Current Tool: {input.currentToolType}')

        # add on the available tools and their respective shortcut keys
        texts.append('[1] Draw\n[2] Erase\n[3] Select')

        # render the text
        xRender = self.window.window.get_width() * .2 + 2
        yRender = 2 + self.font.size('A')[1]
        for i, text in enumerate(texts):
            self.font.render(self.window.window, text, (xRender, yRender * i))


        # update the font's cache
        self.font.update()
