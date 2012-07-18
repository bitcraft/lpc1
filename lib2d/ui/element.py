import pygame



class Element(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.enabled = False
        self._rect = None


    @property
    def rect(self):
        if self._rect: return self._rect
        msg = "Element: {0} does not have it's rect set.  Crashing."
        raise AttributeError, msg.format(self)


    @rect.setter
    def rect(self, rect):
        self._rect = pygame.Rect(rect)
        self.resize()


    def draw(self, surface):
        print "DEBUG: {} has no draw()".format(self.__class__.__name__)


    def resize(self):
        """ call this in case the class does stuff to resize """
        #print "DEBUG: resizing {0}".format(self)
        pass


    def getUI(self):
        parent = self.parent
        while not isinstance(parent, UserInterface):
            parent = parent.parent
        return parent


    def handle_commandlist(self, cmdlist):
        pass


    def onClick(self, point, button):
        pass


    def onBeginHover(self, point):
        pass


    def onEndHover(self, point):
        pass
