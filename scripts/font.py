import pygame


class Font:
    def __init__(self, scale):
        # used to scale the font size
        self.scale = scale

        # load the font sheet
        fontsheet = pygame.image.load('assets/font.png').convert()

        # chars in the font sheet
        chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
        'q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H',
        'I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
        '1','2','3','4','5','6','7','8','9','0','!','@','#','%','^','(',')','-',
        '_','+','=','[',']','{','}','/',':',';',"'",'"','.',',','<','>','?']
        self.characters = {}

        # these letters have parts that go below the writing line
        self.twoPixels = 'g', 'j', 'p', 'q', 'y'
        self.onePixel = ','

        # cut out each character from the sheet and save them in the dictionary
        width = 0
        index = 0
        for i in range(fontsheet.get_width()):
            if index < len(chars):
                if fontsheet.get_at((i, 0)) == (255, 0, 0, 255):
                    charHeight = fontsheet.get_height() - 2
                    if chars[index] in self.twoPixels:
                        charHeight += 2
                    elif chars[index] in self.onePixel:
                        charHeight += 1
                    charSurf = fontsheet.subsurface(pygame.Rect(i - width, 0, width, charHeight)).copy()
                    self.characters[chars[index]] = pygame.transform.scale(charSurf.copy(), (charSurf.get_width() * self.scale, charSurf.get_height() * self.scale))
                    index += 1
                    width = 0
                else:
                    width += 1

        # constants used for rendering
        self.SPACEWIDTH = int(self.characters['a'].get_width())
        self.SPACING = self.scale
        self.NEWLINEHEIGHT = int(self.characters[self.twoPixels[0]].get_height()) + 2 * self.scale

        # make each letter's background transparent, (the transparency is set to 1, 1, 1, so that the characters can be recolored to black easily using 0, 0, 0)
        for char in self.characters:
            for i in range(self.characters[char].get_width()):
                for j in range(self.characters[char].get_height()):
                    if self.characters[char].get_at((i, j)) == (0, 0, 0):
                        self.characters[char].set_at((i, j), (1, 1, 1))
            self.characters[char].set_colorkey((1, 1, 1))

    def render(self, surface, text, loc, centered=False, alignCenter=False, alignRight=False):
        # fix the location if center is true (doesn't work well with text with new lines)
        if centered:
            width, height = self.size(text)
            loc = loc[0] - width // 2, loc[1] - height // 2

        # align center and right require the list of widths
        if alignCenter or alignRight:
            alignWidths, height = self.size(text, notAlignLeft=True)

        # offsets for rendering characters properly
        xOff = 0
        yOff = 0

        # this method will return the size of the rendered text
        width = 0
        height = self.NEWLINEHEIGHT
        widths = []
        line = 0

        # iterate through characters
        for char in text:
            if char == '\n':
                # move the offset values based on alignments
                xOff = 0
                yOff += self.NEWLINEHEIGHT
                # record the dimensions
                height += self.NEWLINEHEIGHT
                widths.append(width)
                width = 0
                line += 1
            elif char == ' ':
                xOff += self.SPACEWIDTH + self.SPACING
                width += self.SPACEWIDTH + self.SPACING
            else:
                # change the way it blits based on the alignment
                if alignCenter:
                    surface.blit(self.characters[char], (loc[0] + (max(alignWidths) - alignWidths[line]) // 2 + xOff, loc[1] + yOff))
                elif alignRight:
                    surface.blit(self.characters[char], (loc[0] + (max(alignWidths) - alignWidths[line]) + xOff, loc[1] + yOff))
                else:
                    surface.blit(self.characters[char], (loc[0] + xOff, loc[1] + yOff))
                xOff += self.characters[char].get_width() + self.SPACING
                width += self.characters[char].get_width() + self.SPACING
                if char in self.twoPixels:
                    height += 2 * self.scale
                elif char in self.onePixel:
                    height += 1 * self.scale

        # return the size
        if widths == []:
            return width, height

        return max(widths), height

    def recolor(self, color):
        # skip if the color changing to is the transparent color
        if color != (1, 1, 1):
            updatedChars = self.characters.copy()
            # iterate through each character, then through each pixel, changing the non transparent into the new color
            for char in updatedChars:
                for i in range(updatedChars[char].get_width()):
                    for j in range(updatedChars[char].get_height()):
                        if updatedChars[char].get_at((i, j)) != (1, 1, 1):
                            updatedChars[char].set_at((i, j), color)

        # store the update characters
        self.characters = updatedChars.copy()

    def size(self, text, notAlignLeft=False):
        # since sizing is already implemented in the render method, just copy those steps without blitting anythhing (widths is used in the case of text with new line characters)
        width = 0
        height = self.NEWLINEHEIGHT
        widths = []

        # iterate through each character and adjust the dimensions accordingly
        for char in text:
            if char == '\n':
                height += self.NEWLINEHEIGHT
                widths.append(width)
                width = 0
            elif char == ' ':
                width += self.SPACEWIDTH + self.SPACING
            else:
                width += self.characters[char].get_width() + self.SPACING
        widths.append(width)

        # return the correct dimensions
        if widths == []:
            return width, height

        # return the list of widths if the text is supposed to aligned with the center
        elif notAlignLeft:
            return widths, height

        return max(widths), height
