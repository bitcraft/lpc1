from lib2d import res
import pygame



class Image(object):
    """
    Surface class that is pickable.  :)
    """

    def __init__(self, filename, alpha=None, colorkey=None):
        self.filename = filename
        self.alpha = alpha
        self.colorkey = colorkey
        self.loaded = False

    def load(self):
        self.loaded = True
        return res.loadImage(self.filename, self.alpha, self.colorkey)


class ImageTile(object):
    """
    Allows you to easily pull tiles from other images
    """

    def __init__(self, parent, tileSize, tileLocation):
        self.parent = parent
        self.tileSize = tileSize
        self.tileLocation = tileLocation

    def load(self):
        self.loaded = True
        if self.parent.loaded:
            surface = self.parent.load()
        else:
            surface = self.parent.load()
        temp = pygame.Surface(tilesize).convert(surface)
        temp.blit(parent, (0,0),
                  ((self.tileSize[0] * self.tileLocation[0],
                    self.tileSize[1] * self.tileLocation[1]),
                    self.tileSize))
        return temp
