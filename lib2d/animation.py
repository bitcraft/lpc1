from objects import GameObject
import res

from collections import namedtuple
import math, itertools


pi2 = math.pi * 2

box = namedtuple('Box', 'width height')
frame = namedtuple('Frame', 'box image')


"""
animations may be used by a class that does not need the images, but may need
to know when an animation finishes, where it is at, etc (such as a server).
"""

def calcFrameSize(filename, frames, directions):
    """
    load the images for the animation and set the size of each frame
    """

    width, height = res.loadImage(filename, 0,0,1).get_size()
    return (width / frames, height / directions)


class Animation(GameObject):
    """
    Animation is a collection of frames with a few control variables and useful
    methods to control it.

    Animations can store multiple directions and are picklable.

    each set of animation added will count as a seperate direction.
    1 animation  = no rotations
    2 animations = left and right (or up and down)
    4 animations = left, right, up, down
    6 animations = up, down, nw, ne, sw, se (for hex maps)
    and so on.

    The animation loader expects the image to be in a specific format.
    Loader only supports animations where each frame is the same size.

    TODO: implement some sort of timing, rather than relying on frames
    """

    def __init__(self, filename, name, frames, directions=1, timing=100):

        GameObject.__init__(self)

        self.filename = filename
        self.name = name
        self.images = None
        self.directions = directions

        # TODO: some checking to make sure inputs are the correct length
        if isinstance(frames, int):
            self.frames = tuple(range(0, frames))
        else:
            self.frames = tuple(frames)

        self.real_frames = len(set(self.frames))

        if isinstance(timing, int):
            self.timing = tuple([timing] * len(self.frames))
        else:
            self.timing = tuple(timing)

        self.iterator = iter(self)


    def __iter__(self):
        return itertools.cycle(zip(self.timing, self.frames))


    def returnNew(self):
        return self


    def load(self, force=False):
        """
        load the images for use with pygame
        returns a new Animation Object
        """

        if (self.images is not None) and (not force):
            return

        image = res.loadImage(self.filename, 0, 0, 1)

        iw, ih = image.get_size()
        tw = iw / self.real_frames
        th = ih / self.directions
        self.images = [None] * (self.directions * self.real_frames)
      
        d = 0
        for y in range(0, ih, th):
            #if d == ih/th: d = 0
            for x in range(0, iw, tw):
                try:
                    frame = image.subsurface((x, y, tw, th))
                except ValueError as e:
                    raise ValueError, self.filename
                self.images[(x/tw)+d*self.real_frames] = frame
            d += 1


    def unload(self):
        self.images = []


    def advance(self):
        return self.iterator.next()


    def getImage(self, number,  direction=0):
        """
        return the frame by number with the correct image for the direction
        direction should be expressed in radians
        """

        if self.images == []:
            raise Exception, "Avatar hasn't loaded images yet"

        if direction < 0:
            direction = pi + (pi - abs(direction))
        d = int(math.ceil(direction / pi2 * (self.directions - 1)))

        try:
            return self.images[number+d*self.real_frames]
        except IndexError:
            msg="{} cannot find image for animation ({}/{})"
            raise IndexError, msg.format(self, number+d*self.real_frames,
                                         len(self.images))


    def __repr__(self):
        return "<Animation %s: \"%s\">" % (id(self), self.filename)


class StaticAnimation(Animation):
    """
    Animation that only supports one frame
    Immutable
    """

    def __init__(self, filename, name, tile=None, size=None):
        GameObject.__init__(self)

        self.filename = filename
        self.name = name
        self.tile = tile
        self.size = size
        self.image = None


    def loaded(self):
        """
        load the images for use with pygame
        """

        image = res.loadImage(self.filename, 0, 0, 1)
      
        if self.tile:
            x, y = self.tile
            x *= self.size[0]
            y *= self.size[1]
            ck = image.get_colorkey()
            self.image = pygame.Surface(self.size)
            self.image.blit(image,(0,0),area=(x,y, self.size[0], self.size[1]))
            image.set_colorkey(ck, pygame.RELACCEL) 

        else:
            self.image = image

        self.frames = [self.image]


    def returnNew(self):
        return self


    def unload(self):
        self.image = None


    def getTTL(self, number):
        return -1


    def getImage(self, number, direction=0):
        """
        return the frame by number with the correct image for the direction
        direction should be expressed in radians
        """

        return self.image

    def __repr__(self):
        return "<Animation %s: \"%s\">" % (id(self), self.filename)

