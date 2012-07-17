from lib2d.ui.element import Element



class Frame(Element):
    def __init__(self, parent, packer):
        Element.__init__(self, parent)
        self.packer = packer
        self.areas = []


    def setPacker(self, packer):
        self.packer = packer


    def addElement(self, other, rect=None):
        self.packer.add(other, rect)


    def removeElement(self, other):
        self.packer.remove(other)


    def addViewPort(self, element):
        if isinstance(element, ViewPort):
            self.packer.add(element)


    def onDraw(self, surface, rect):
        dirty = []
        for element, rect in self.packer.getLayout(rect):
            dirty.extend(element.draw(surface, rect))

        #for rect in self.packer.getRects():
        #    self.border.draw(surface, rect.inflate(6,6))

        return dirty
