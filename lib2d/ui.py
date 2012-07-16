"""
the mouse api is generally as follows:

if the client has a onClick, onHover, or onDrag method, the
'point' argument will be relative to the rect of the object,
not the screen.  The point passed will be a vec.Vec2d object

"""

"""
this module strives to NOT be a replacement for more fucntional draw toolkits.
this is a bare-bones simple draw toolkit for mouse use only.
"""

from lib2d.buttons import *
from lib2d import res, draw, vec
import pygame



class UIElement(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.enabled = False
        self._rect = None


    def setParent(self, parent):
        self.parent = parent


    def draw(self, surface, rect):
        if not self._rect == rect:
            self._rect = rect
            self.onResize(rect)
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


class Packer(UIElement):
    def __init__(self):
        self._rect = None
        self.elements = {}


    def getRects(self):
        """ Return a list of rects that represents the area of this """
        raise NotImplementedError


    def getLayout(self, rect=None):
        if (not self._rect == rect) and (rect is not None):
            self.onResize(rect)
        return self.elements.items()


    def onResize(self, rect):
        raise NotImplementedError



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


    def add(self, element):
        self.elements[element] = None
        self.order.append(element)


    def getRects(self):
        return list(self.order)


    def onResize(self, rect):
        """ resize the rects for the panes """

        self._rect = pygame.Rect(rect)

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


class MouseTool(object):
    toole_image = None
    cursor_image = None


    def onClick(self, element, point, button):
        pass


    def onDrag(self, element, point, button, origin):
        pass


    def onBeginHover(self, element, point):
        element.onBeginHover(point)


    def onEndHover(self, element, point):
        element.onEndHover(point)


class GraphicIcon(UIElement):
    """
    Clickable Icon

    TODO: cache the image so it isn't duplicated in memory
    """

    def __init__(self, filename, func, arg=[], kwarg={}, uses=1):
        UIElement.__init__(self)
        self.filename = filename
        self.func = (func, arg, kwarg)
        self.uses = uses
        self.image = None
        self.originalImage = None
        self.load()


    def load(self):
        if self.image is None:
            image = res.loadImage(self.filename)
            self.originalImage = pygame.transform.scale(image, (16,16))
            self.image = self.originalImage.copy()
            self.enabled = True


    def unload(self):
        self.image = None
        self.func = None
        self.enabled = False


    def onClick(self, point, button):
        if self.uses > 0 and self.enabled:
            self.func[0](*self.func[1], **self.func[2])
            self.uses -= 1
            if self.uses == 0:
                self.unload()


    def onDrag(self, point, button, origin):
        pass


    def onBeginHover(self, point):
        self.image.fill((96,96,96), special_flags=pygame.BLEND_ADD)


    def onEndHover(self, point):
        self.image = self.originalImage.copy()


    def onDraw(self, surface, rect):
        return surface.blit(self.image, rect.topleft)


class RoundMenu(UIElement):
    """
    menu that 'explodes' from a center point and presents a group of menu
    options as a circle of GraphicIcon objects
    """

    def __init__(self, parent):
        UIElement.__init__(self, parent)
        self.icons = []


    def setIcons(self, icons):
        self.icons = icons
        for i in icons:
            i.load()


    def open(self, point):
        """ start the animation of the menu """
        self.enabled = True
        rect = pygame.Rect(point-(32,8), (16,16))
        for i, icon in enumerate(self.icons):
            self.parent.freeSpace.add(icon, rect.move(16*i,0))
  
 
    def close(self):
        self.enabled = False
        for i in self.icons:
            self.parent.freeSpace.remove(i)
            i.unload()

 
    def onDraw(self, surface, rect):
        pass


class PanTool(MouseTool, UIElement):
    def __init__(self, parent):
        MouseTool.__init__(self)
        UIElement.__init__(self, parent)
        self.drag_origin = None
        self.openMenu = None


    def load(self):
        self.tool_image = res.loadImage("pantool.png")


    def onClick(self, element, point, button):
        if isinstance(element, VirtualMapElement):
            self.drag_origin = None
            self.openMenu = testMenu(self.parent)
            self.openMenu.open(point)
        else:
            element.onClick(point, button)


    def onDrag(self, element, point, button, origin):
        print "drag", element, point
        if isinstance(element, VirtualMapElement):
            if self.drag_origin is None:
                x = element.parent._rect.width / 2
                y = element.parent._rect.height / 2
                self.drag_origin = element.camera.surfaceToWorld((x, y))

            x, y, z = self.drag_origin
            dy, dx = point[0] - origin[0], point[1] - origin[1]
            element.camera.center((x-dx, y-dy, z))


class Frame(UIElement):
    def __init__(self, parent, packer):
        UIElement.__init__(self, parent)
        self.packer = packer
        self.elements = []
        self.areas = []


    def setPacker(self, packer):
        self.packer = packer


    def addElement(self, other, rect=None):
        self.elements.append(other)
        self.packer.add(other)


    def removeElement(self, other):
        self.elements.remove(other)
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


class UserInterface(Frame):
    """
    Standard UI controls mouse interaction, drawing the maps, and UI
    elements such as menus
    """

    height = 20
    color = pygame.Color(196, 207, 214)
    transparent = pygame.Color(1,2,3)

    background = (109, 109, 109)
    foreground = (0, 0, 0)

    drag_sensitivity = 4

    def __init__(self):
        self.blank = True
        self.packer = GridPacker()
        self.elements = []
        self.rect = None

        self.tools = [ PanTool(self) ]
        for tool in self.tools:
            tool.load()

        self.mouseTool = self.tools[0]

        # ugh, i really suck at making gui toolkits!
        self.freeSpace = OpenPacker()

        #mouse hack
        self.drag_origin = None
        self.drag_el = None
        self.hovered = None


    def buildInterface(self, rect):
        """
        pass the rect of the screen surface and the interface will be
        proportioned correctly.
        """

        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.border = draw.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = draw.GraphicBox("dialog2.png")
        self.paneManager = None

        x, y, w, h = rect
        w = x+int((w*.30))
        s = pygame.Surface((w, self.height))
        s.fill(self.transparent)
        s.set_colorkey(self.transparent, pygame.RLEACCEL)

        pygame.draw.circle(s, (128,128,128), (self.height, 1), self.height)
        pygame.draw.rect(s, (128, 128, 128), (self.height, 1, w, self.height))

        pygame.draw.circle(s, self.color, (self.height+1, 0), self.height)
        pygame.draw.rect(s, self.color, (self.height+1, 0, w-self.height, self.height))
        
        self.buttonbar = s


    def draw(self, surface):
        surface_rect = surface.get_rect()
        self.rect = surface.get_rect()

        for element, rect in self.packer.getLayout(surface_rect):
            element.draw(surface, rect)

        x, y, w, h = surface_rect
        back_width = x+int((w*.70))
        self.buildInterface((x, y, w, h))
        surface.blit(self.buttonbar, (x+int(w*.70)+1,0))

        for element, rect in self.freeSpace.getLayout(surface_rect):
            element.draw(surface, rect)


    def handle_commandlist(self, cmdlist):
        for e in self.elements:
            e.handle_commandlist(cmdlist)


    def findElement(self, point):
        """
        return a clicked element, ignoring frames
        """

        def searchPacker(packer):
            layout = packer.getLayout()
            while layout:
                element, rect = layout.pop()
                if rect.collidepoint(point):
                    if isinstance(element, Frame):
                        layout.extend(element.packer.getLayout())
                    else:
                        return element, rect                

            return None, None


        search = (self.freeSpace, self.packer)
        for packer in search:
            element, rect = searchPacker(packer)
            if element:
                return element, rect

        return None, None


    # handles all mouse interaction
    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if cmd == CLICK1:
                state, pos = arg
                if pos is None: return
                el, rect = self.findElement(pos)
                if el:
                    pos = vec.Vec2d(pos[0] - rect.left, pos[1] - rect.top)
                    if state == BUTTONDOWN:
                        self.drag_origin = pos
                        self.drag_el = el

                    if state == BUTTONUP:
                        d = abs(sum(pos - self.drag_origin))
                        if d < self.drag_sensitivity:
                            self.mouseTool.onClick(el, pos, 1)

                    elif state == BUTTONHELD:
                        d = abs(sum(pos - self.drag_origin))
                        if el == self.drag_el and d > self.drag_sensitivity:
                            self.mouseTool.onDrag(el, pos, 1, self.drag_origin)

            elif cmd == CLICK2:
                pass
            elif cmd == MOUSEPOS:
                el, rect = self.findElement(arg)
                if el and not self.hovered:
                    pos = (arg[0] - rect.left, arg[1] - rect.top)
                    self.mouseTool.onBeginHover(el, pos)
                    self.hovered = el

                if (not el == self.hovered) and (el is not None):
                    pos = (arg[0] - rect.left, arg[1] - rect.top)
                    self.hovered.onEndHover(pos)
                    self.hovered = None


def testMenu(parent):
    def func(menu):
        menu.close()

    m = RoundMenu(parent)
    a = GraphicIcon("grasp.png", func, [m])
    b = GraphicIcon("grasp.png", func, [m])
    c = GraphicIcon("grasp.png", func, [m])
    d = GraphicIcon("grasp.png", func, [m])
    m.setIcons([a,b,c,d])
    return m


class VirtualAvatarElement(UIElement):
    def __init__(self, parent, avatar):
        UIElement.__init__(self, parent)
        self.avatar = avatar

    def onClick(self, point, button):
        print "clicked", self.avatar


class VirtualMapElement(UIElement):
    def __init__(self, parent, camera):
        UIElement.__init__(self, parent)
        self.camera = camera

    def onClick(self, point, button):
        print "clicked", self.viewport
        

class ViewPort(Frame):
    """
    the ViewPort is a Frame that draws an area to the screen (or other surface)
    
    Elements can be added to the pane and expect to be loacated in world
    coordinates (so elements move with the map when scrolled)
    """

    loadedAreas = []


    def __init__(self, area, parent=None):
        Frame.__init__(self, parent, OpenPacker())
        self.area = area
        self.camera = None
        self.elements = {}

        self.virtualElements = {}

        if area not in self.loadedAreas:
            self.loadedAreas.append(area)
            area.load()

            # load the children
            for child in area.getChildren():
                child.load()

            # load sounds from area
            #for filename in element.area.soundFiles:
            #    SoundMan.loadSound(filename)

    def addElement(self, element, rect):
        x, y, w, h = rect
        self.elements[element] = pygame.Rect(y, x, h, w)

    def onResize(self, rect):
        from lib.renderer import LevelCamera
        self.camera = LevelCamera(self.area, rect)
        self.map_element = VirtualMapElement(self, self.camera)
        self.packer.elements = {}
        self.packer.elements[self.map_element] = self._rect

    def onDraw(self, surface, rect):
        dirty = self.camera.draw(surface, rect)
        for element, rect in self.elements.items():
            dx, dy = self.camera.extent.topleft
            x, y, w, h = rect.move(-dx, -dy)
            dirty.append(element.draw(surface, pygame.Rect(y, x, h, w)))

        # create elements that overlay avatars, so that they are clickable
        # giant hack
        ao = [ i for i in self.area.bodies.keys() if hasattr(i, "avatar")]

        for a in ao:
            bbox = self.area.getBBox(a)
            x, y, z, d, w, h = bbox
            x, y = self.camera.worldToSurface((x, y, z))
            x = x - self.camera.extent.top + rect.top
            y = y - self.camera.extent.left + rect.left
            e = VirtualAvatarElement(self, a)
            #self.packer.elements[e] = pygame.Rect(x, y, w, h)

        return dirty



