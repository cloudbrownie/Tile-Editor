import pygame
from .font import Font

class GUI:
    def __init__(self, window):
        self.window = window

        self.scale = self.window.scale
        self.font = Font(self.scale)

    def render(self, input):

        # add on the asset type
        assetText =  f'[W] Current Asset Type: {input.currentAssetType}'

        # add on the layer text
        if input.currentAssetType == 'tiles':
            layerText = f'[-] Layer {input.currentLayer} [+]'
        elif input.currentAssetType == 'decorations':
            layerText =  f'[-] {input.currentDecorationLayer} [+]'

        # add on the pen position info
        penText = f'Pen Position: {input.penPosition}'

        # add on the current tool text
        toolText = f'Current Tool: {input.currentToolType}'

        # add on the available tools and their respective shortcut keys
        toolKeyText = '[1] Draw\n[2] Erase\n[3] Select'

        # render the text
        xRender = self.window.window.get_width() * .2 + 2
        yRender = 2
        yRender += self.font.render(self.window.window, str(self.window.editor.clock.fps), (xRender, yRender))[1]
        yRender += self.font.render(self.window.window, assetText, (xRender, yRender))[1]
        yRender += self.font.render(self.window.window, layerText, (xRender, yRender))[1]
        yRender += self.font.render(self.window.window, penText, (xRender, yRender))[1]
        yRender += self.font.render(self.window.window, toolText, (xRender, yRender))[1]
        yRender += self.font.render(self.window.window, toolKeyText, (xRender, yRender))[1]



        # update the font's cache
        self.font.update()
