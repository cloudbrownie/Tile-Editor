import pygame
from .font import Font

class GUI:
    def __init__(self, window):
        self.window = window

        self.scale = self.window.scale
        self.font = Font(self.scale)

    def render(self, input):
        # making the render text
        renderText = ''

        # add on the asset type
        renderText += f'[W] Current Asset Type: {input.currentAssetType}\n'

        # add on the layer text
        if input.currentAssetType == 'tiles':
            renderText += f'[-] Layer {input.currentLayer} [+]\n'
        elif input.currentAssetType == 'decorations':
            renderText +=  f'[-] {input.currentDecorationLayer} [+]\n'

        # add on the pen position info

        # add on the current tool text
        renderText += f'\nCurrent Tool: {input.currentToolType}\n'

        # add on the available tools and their respective shortcut keys
        renderText += '[1] Draw\n'
        renderText += '[2] Erase\n'

        # render the text
        self.font.render(self.window.window, renderText, (self.window.window.get_width() * .2 + 2, 2))

        # update the font's cache
        self.font.update()
