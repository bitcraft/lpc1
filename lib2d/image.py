from lib2d import res
import pygame



class Image(object):
    """
    Surface class that is pickable.  :)
    """

    def __init__(self, filename, alpha=False, colorkey=False):
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

    def __init__(self, filename, tile, tilesize):
        self.image = Image(filename)
        self.tile = tile
        self.tilesize = tilesize

    def load(self):
        self.loaded = True
        if self.image.loaded:
            surface = self.image.load()
        else:
            surface = self.image.load()
        temp = pygame.Surface(self.tilesize).convert(surface)
        temp.blit(surface, (0,0),
                  ((self.tilesize[0] * self.tile[0],
                    self.tilesize[1] * self.tile[1]),
                    self.tilesize))
        return temp
