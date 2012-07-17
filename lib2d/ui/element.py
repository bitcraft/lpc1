import pygame


class Element(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.enabled = False
        self._rect = None


    def setParent(self, parent):
        self.parent = parent


    def draw(self, surface, rect):
        if (not self._rect == rect) and (rect is not None):
            self.onResize(rect)
            self._rect = pygame.Rect(rect)
        return self.onDraw(surface, rect)


    def onResize(self, rect):
        pass        


    def getUI(self):
        parent = self.parent
        while not isinstance(parent, UserInterface):
            parent = parent.parent
        return parent


    def handle_commandlist(self, cmdlist):
        pass


    def onDraw(self, surface, rect):
        pass


    def onClick(self, point, button):
        pass


    def onBeginHover(self, point):
        pass

    def onEndHover(self, point):
        pass

