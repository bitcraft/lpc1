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

from lib2d.ui.packer import GridPacker
from lib2d.ui import Element, Frame
from lib2d.buttons import *
from lib2d import res, draw, vec
import pygame



class GraphicIcon(Element):
    """
    Clickable Icon

    TODO: cache the image so it isn't duplicated in memory
    """

    def __init__(self, surface, func, arg=[], kwarg={}, uses=1):
        Element.__init__(self)
        self.func = (func, arg, kwarg)
        self.uses = uses
        self.image = None
        self.originalImage = pygame.transform.scale(surface, (16, 16))
        self.image = self.originalImage.copy()
        self.load()


    def load(self):
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


class RoundMenu(Element):
    """
    menu that 'explodes' from a center point and presents a group of menu
    options as a circle of GraphicIcon objects
    """

    def __init__(self, parent):
        Element.__init__(self, parent)
        self.icons = []
        self.anchor = None


    def setIcons(self, icons):
        self.icons = icons
        for i in icons:
            i.load()


    def open(self, point):
        """ start the animation of the menu """
        self.enabled = True
        self.anchor = point
        w = 16 * len(self.icons)
        rect = pygame.Rect(point-(w/2,8), (16,16))
        for i, icon in enumerate(self.icons):
            self.parent.addElement(icon, rect.move(16*i,0))  

 
    def close(self):
        self.enabled = False
        for i in self.icons:
            i.unload()
            self.parent.removeElement(i)

 
    def onDraw(self, surface, rect):
        pass



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

    drag_sensitivity = 2

    def __init__(self):
        from lib2d.mouse.tools import PanTool

        self.blank = True
        self.packer = GridPacker()
        self.rect = None

        self.tools = [ PanTool(self) ]
        for tool in self.tools:
            tool.load()

        self.mouseTool = self.tools[0]

        #mouse hack
        self.drag_origin = None
        self.drag_element = None
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


    def handle_commandlist(self, cmdlist):
        for e in self.packer.getElements():
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


        element, rect = searchPacker(self.packer)
        if element:
            return element, rect
        else:
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
                        self.drag_element = el

                    elif state == BUTTONUP:
                        d = abs(sum(pos - self.drag_origin))
                        if d < self.drag_sensitivity:
                            self.mouseTool.onClick(el, pos, 1)

                    elif state == BUTTONHELD:
                        d = abs(sum(pos - self.drag_origin))
                        if el == self.drag_element and d > self.drag_sensitivity:
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


class VirtualAvatarElement(Element):
    def __init__(self, parent, avatar):
        Element.__init__(self, parent)
        self.avatar = avatar

    def onClick(self, point, button):
        print "clicked", self.avatar


class VirtualMapElement(Element):
    def __init__(self, parent, camera):
        Element.__init__(self, parent)
        self.camera = camera

    def onClick(self, point, button):
        print "clicked", self.viewport
        

class ScrollingGridPacker(GridPacker):
    def getLayout(self, rect=None):
        items = []
        dy, dx = self.camera.extent.topleft
        for element, rect in super(ScrollingGridPacker, self).getLayout(rect):
            if isinstance(element, VirtualMapElement):
                items.append((element, rect))
            else:
                items.append((element, rect.move(-dx, -dy)))
                
        return items


    def setCamera(self, camera):
        self.camera = camera


    def getRect(self, element):
        rect = super(ScrollingGridPacker, self).getRect(element)
        if rect:
            dy, dx = self.camera.extent.topleft
            return rect.move(-dx, -dy)


class ViewPort(Frame):
    """
    the ViewPort is a Frame that draws an area to the screen (or other surface)
    
    Elements can be added to the pane and expect to be loacated in world
    coordinates (so elements move with the map when scrolled)
    """

    loadedAreas = []


    def __init__(self, area, parent=None):
        Frame.__init__(self, parent, ScrollingGridPacker())
        self.area = area
        self.camera = None
        self.map_element = None

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

    def onResize(self, rect):
        from lib.renderer import LevelCamera

        self.camera = LevelCamera(self.area, rect)
        self.packer.setCamera(self.camera)
        if self.map_element is not None:
            self.packer.remove(self.map_element)

        self.map_element = VirtualMapElement(self, self.camera)
        self.packer.add(self.map_element, self._rect)


    def addElement(self, element, rect):
        dy, dx = self.camera.extent.topleft
        rect = rect.move(dx, dy)
        super(ViewPort, self).addElement(element, rect)        


    def onDraw(self, surface, surface_rect):
        dirty = self.camera.draw(surface, surface_rect)

        # big hacks, right here
        for element, rect in self.packer.getLayout(surface_rect):
            dirty.append(element.draw(surface, rect))

        # create elements that overlay avatars, so that they are clickable
        # giant hack
        ao = [ i for i in self.area.bodies.keys() if hasattr(i, "avatar")]

        for a in ao:
            bbox = self.area.getBBox(a)
            x, y, z, d, w, h = bbox
            x, y = self.camera.worldToSurface((x, y, z))
            x = x - surface_rect.top
            y = y - surface_rect.left
            try:
                e = self.virtualElements[a]
            except KeyError:
                e = VirtualAvatarElement(self, a)
                self.virtualElements[a] = e
            else:
                self.packer.elements[e] = pygame.Rect(x, y, w, h)

            pygame.draw.rect(surface, (0,255,0), (x, y, w, h), 1) 

        return dirty



