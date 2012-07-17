from lib2d.ui.element import Element
import pygame, collections


class Packer(Element):
    def __init__(self):
        self._rect = None
        self.elements = collections.OrderedDict()
        self.freespace = collections.OrderedDict()


    def getElements(self):
        return itertools.chain(self.elements.keys(), self.freespace.keys())


    def getRect(self, element):
        if self.elements.has_key(element):
            return self.elements[element]

        if self.freespace.has_key(element):
            return self.freespace[element]


    def setRect(self, element, rect):
        if self.elements.has_key(element):
            self.elements[element] = rect
            return

        if self.freespace.has_key(element):
            self.freespace[element] = rect
            return


    def add(self, element, rect=None):
        if rect:
            self.freespace[element] = rect
        else:
            self.elements[rect] = None


    def remove(self, element):
        try:
            del self.elements[element]
        except:
            pass

        try:
            del self.freespace[element]
        except:
            pass


    def getRects(self):
        """ Return a list of rects that represents the area of this """
        raise NotImplementedError


    def getLayout(self, rect=None):
        if (not self._rect == rect) and (rect is not None):
            self.onResize(rect)
            self._rect = pygame.Rect(rect)

        items = self.elements.items()
        items.extend(self.freespace.items())
        return items


    def onResize(self, rect):
        raise NotImplementedError


    def getPosition(self, element):
        return self.elements[element]


class OpenPacker(Packer):
    """
    allows for freeform positioning of ui elements
    """

    def add(self, element, rect):
        self.elements[element] = rect

    def remove(self, element):
        del self.elements[element]

    def getRects(self):
        return self.elements.values()

    def onResize(self, rect):
        self._rect = rect


class GridPacker(Packer):
    """
    positions widgets in a grid
    """

    def __init__(self):
        Packer.__init__(self)
        self.order = []


    def add(self, element, rect=None):
        if rect:
            self.freespace[element] = rect
        else:
            self.order.append(element)
            self.elements[element] = None


    def remove(self, element):
        super(GridPacker, self).remove(element)
        try:
            self.order.remove(element)
        except:
            pass


    def getRects(self):
        return list(self.order)


    def onResize(self, rect):
        """ resize the rects for the panes """

        if len(self.elements) == 1:
            self.elements[self.order[0]] = pygame.Rect(rect)

        elif len(self.elements) == 2:
            w, h = self.rect.size
            self.elements[self.order[0]] = pygame.Rect((0,0,w,h/2))
            self.elements[self.order[1]] = pygame.Rect((0,h/2,w,h/2))

        elif len(self.elements) == 3:
            w, h = self.rect.size
            self.elements[self.order[0]] = pygame.Rect((0,0,w,h/2))
            self.elements[self.order[1]] = pygame.Rect((0,h/2,w/2,h/2))
            self.elements[self.order[2]] = pygame.Rect((w/2,h/2,w/2,h/2))

        elif len(self.elements) == 4:
            w = self.rect.width / 2
            h = self.rect.height / 2
            self.elements[self.order[0]] = pygame.Rect((0,0,w,h))
            self.elements[self.order[1]] = pygame.Rect((w,0,w,h))
            self.elements[self.order[2]] = pygame.Rect((0,h,w,h))
            self.elements[self.order[3]] = pygame.Rect((w,h,w,h))

