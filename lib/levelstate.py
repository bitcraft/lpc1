from renderer import LevelCamera
from misc import Lift

from lib2d.gamestate import GameState
from lib2d.statedriver import driver as sd
from lib2d.buttons import *
from lib2d.signals import *
#from lib2d.ui import *
from lib2d.vec import Vec2d
from lib2d.quadtree import QuadTree, FrozenRect
from lib2d import res, gui
import pytmx

from random import randint
from math import sqrt, atan2
from operator import itemgetter
from itertools import ifilter
import pygame
import os.path

import time


debug = 1

movt_fix = 1/sqrt(2)


def getNearby(thing, d):
    p = thing.parent
    body = p.getBody(thing)
    bbox = body.bbox.inflate(64,d,d)
    x1, y1, z1 = body.bbox.center
    nearby = []
    for other in p.testCollideObjects(bbox, skip=[body]): 
        x2, y2, z2 = other.bbox.center
        dist = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
        nearby.append((d, (other.parent, other)))

    return [ i[1] for i in sorted(nearby) ]


class SoundManager(object):
    def __init__(self):
        self.sounds = {}
        self.last_played = {}

    def loadSound(self, filename):
        self.sounds[filename] = res.loadSound(filename)
        self.last_played[filename] = 0

    def play(self, filename, volume=1.0):
        now = time.time()
        if self.last_played[filename] + .05 <= now:
            self.last_played[filename] = now
            sound = self.sounds[filename]
            sound.set_volume(volume)
            sound.play()

    def unload(self):
        self.sounds = {}
        self.last_played = {}


SoundMan = SoundManager()


# GLOBAL LEET SKILLS
hero_body = None
state = None


"""
the mouse api is generally as follows:

if the client has a onClick, onHover, or onDrag method, the
'point' argument will be relative to the rect of the object,
not the screen.  The point passed will be a Vec2d object

"""

"""
this module strives to NOT be a replacement for more fucntional gui toolkits.
this is a bare-bones simple gui toolkit for mouse use only.
"""
from renderer import LevelCamera
from lib2d.buttons import *
from lib2d import res, gui
import pygame



class UserInterface(object):
    pass


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


    def update(self, time):
        pass


class Packer(UIElement):
    def __init__(self):
        self._rect = None
        self.elements = {}


    def getRects(self):
        """ Return a list of rects that represents the area of this """
        raise NotImplementedError


    def getLayout(self, rect):
        if not self._rect == rect:
            self.onResize(rect)
        return self.elements.items()


    def onResize(self, rect):
        raise NotImplementedError


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

        self.rect = pygame.Rect(rect)

        if len(self.elements) == 1:
            self.elements[self.order[0]] = pygame.Rect(rect)

        elif len(self.elements) == 2:
            w, h = self.rect.size
            self.elements[self.order[0]] = pygame.Rect((0,0,w,h/2))
            self.elements[self.order[1]] = pygame.Rect((0,h/2,w,h/2))

        elif len(self.elements) == 3:
            w = self.rect.width / 2
            h = self.rect.height / 2
            rect = self.rect.copy()
            # WARNING!!!! 3 panes does not work

        elif len(self.elements) == 4:
            w = self.rect.width / 2
            h = self.rect.height / 2
            self.elements[self.order[0]] = pygame.Rect((0,0,w,h))
            self.elements[self.order[1]] = pygame.Rect((w,0,w,h))
            self.elements[self.order[2]] = pygame.Rect((0,h,w,h))
            self.elements[self.order[3]] = pygame.Rect((w,h,w,h))


class Pane(UIElement):
    """
    object capable of interacting with the mouse
    """
    pass


class MouseTool(object):
    toole_image = None
    cursor_image = None


    def onClick(self, pane, point, button):
        pass


    def onDrag(self, pane, point, button, origin):
        pass


    def onHover(self, pane, point):
        pass


class GraphicIcon(object):
    """
    Clickable Icon

    TODO: cache the image so it isn't duplicated in memory
    """

    def __init__(self, filename, func, arg=[], kwarg={}, uses=1):
        self.filename = filename
        self.func = (func, arg, kwarg)
        self.uses = uses
        self.image = None
        self.load()


    def load(self):
        if self.image == None:
            self.image = res.loadImage(self.filename)
            self.enabled = True

    def unload(self):
        self.image = None

    def onClick(self, point, button, origin):
        if self.uses > 0 and self.enabled:
            self.func[0](*self.func[1], **self.func[2])
            self.uses -= 1
            if self.uses == 0:
                self.unload()
                self.func = None

    def onDrag(self, point, button, origin):
        pass

    def onHover(self, point):
        pass

    def onDraw(self, surface, rect):
        return surface.blit(self.image, rect.topleft)


class RoundMenu(UIElement):
    """
    menu that 'explodes' from a center point and presents a group of menu
    options as a circle of GraphicIcon objects
    """

    def __init__(self, items):
        self.items = []
        for i in items:
            i.load()
            i.enabled = False


    def open(self):
        """ start the animation of the menu """
        self.enabled = True
        for i in self.items:
            i.enabled = False
    
    def onDraw(self, surface, rect):
        dirty = []
        for i, item in enumerate(self.items):
            x = i*32
            y = 10
            dirty.append(item.draw(surface, (x,y)))
        return dirty


class PanTool(MouseTool, UIElement):
    def __init__(self, parent):
        MouseTool.__init__(self)
        UIElement.__init__(self, parent)
        self.drag_origin = None


    def load(self):
        self.tool_image = res.loadImage("pantool.png")


    def onClick(self, pane, point, button):
        self.drag_origin = None
        m = testMenu()
        #self.getUI().addElement(m)
        #self.getUI().setRect(m, (pos, (32, 32)))
        m.open()


    def onDrag(self, pane, point, button, origin):
        if isinstance(pane, ViewPort):
            if self.drag_origin == None:
                x, y = pane._rect.width / 2, pane._rect.height / 2
                self.drag_origin = pane.camera.surfaceToWorld((x, y))

            x, y, z = self.drag_origin
            dy, dx = point[0] - origin[0], point[1] - origin[1]
            pane.camera.center((x-dx, y-dy, z))


class StandardUI(UserInterface):
    """
    Standard UI controls mouse interaction, drawing the maps, and UI
    elements such as menus
    """

    height = 20
    color = pygame.Color(196, 207, 214)
    transparent = pygame.Color(1,2,3)

    background = (109, 109, 109)
    foreground = (0, 0, 0)


    def __init__(self):
        self.blank = True
        self.packer = GridPacker()
        self.elements = []
        self.rect = None


    def setPacker(self, packer):
        self.packer = packer


    def addElement(self, other):
        self.elements.append(other)
        self.packer.add(other)


    def buildInterface(self, rect):
        """
        pass the rect of the screen surface and the interface will be
        proportioned correctly.
        """

        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
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
        """
        when asking clients to draw(), you must call _draw().  the client will
        then automatically adjust to changes in screen size or position, then
        call the draw() method on its own.
        """

        surface_rect = surface.get_rect()

        for e, rect in self.packer.getLayout(surface_rect):
            e.draw(surface, rect)

        x, y, w, h = surface_rect
        back_width = x+int((w*.70))
        self.buildInterface((x, y, w, h))
        surface.blit(self.buttonbar, (x+int(w*.70)+1,0))


    def handle_commandlist(self, cmdlist):
        for e in self.elements:
            e.handle_commandlist(cmdlist)


    def update(self, time):
        [ i.update(time) for i in self.elements ]


def testMenu():
    def func():
        pass

    g = GraphicIcon("grasp.png", func) 
    m = RoundMenu([g, g, g, g])
    return m



class ViewPort(UIElement):
    """
    the ViewPort is a Pane that draws a area to the screen (or other
    surface)
    """

    def __init__(self, area, parent=None):
        UIElement.__init__(self, parent)
        self.area = area
        self.camera = None

    def onResize(self, rect):
        self.camera = LevelCamera(self.area, rect)

    def onDraw(self, surface, rect):
        return self.camera.draw(surface, rect)

    def update(self, time):
        self.camera.update(time)


class ViewPortManager(UIElement):
    drag_sensitivity = 2


    def __init__(self, parent):
        UIElement.__init__(self, parent)
        self.elements = []
        self.areas = []
        self.packer = GridPacker()

        self.tools = [ PanTool(self) ]

        for tool in self.tools:
            tool.load()

        self.mouse_tool = self.tools[0]

        #mouse hack
        self.drag_origin = None
        self.drag_vp = None


    def add(self, element):
        if isinstance(element, ViewPort):
            self.packer.add(element)

            if element.area not in self.areas:
                self.areas.append(element.area)
                element.area.load()

                # load the children
                for child in element.area.getChildren():
                    child.load()

                # load sounds from area
                for filename in element.area.soundFiles:
                    SoundMan.loadSound(filename)


    def onDraw(self, surface, rect):
        dirty = []
        for element, rect in self.packer.getLayout(rect):
            dirty.extend(element.draw(surface, rect))

        #for rect in self.packer.getRects():
        #    self.border.draw(surface, rect.inflate(6,6))

        return dirty


    def update(self, time):
        [ vp.update(time) for vp in self.elements ]
        [ area.update(time) for area in self.areas ]
        

    def findViewport(self, point):
        for element, rect in self.packer.getLayout(self._rect):
            if rect.collidepoint(point):
                return element, rect


    # handles all mouse interaction
    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if cmd == CLICK1:
                state, pos = arg
                vp, rect = self.findViewport(pos)
                if vp:
                    pos = Vec2d(pos[0] - rect.left, pos[1] - rect.top)
                    if state == BUTTONDOWN:
                        self.drag_origin = pos
                        self.drag_vp = vp
                        self.mouse_tool.onClick(vp, pos, 1)

                    elif state == BUTTONHELD:
                        d = abs(sum(pos - self.drag_origin))
                        if vp == self.drag_vp and d > self.drag_sensitivity:
                            self.mouse_tool.onDrag(vp, pos, 1, self.drag_origin)

            elif cmd == CLICK2:
                pass
            elif cmd == MOUSEPOS:
                vp, rect = self.findViewport(arg)
                if vp:
                    pos = (arg[0] - rect.left, arg[1] - rect.top)
                    self.mouse_tool.onHover(vp, pos)






"""============================================================================`
"""

class LevelState(GameState):
    """
    This state is where the player will move the hero around the map
    interacting with npcs, other players, objects, etc.

    much of the work doen here is in the Standard UI class.
    """

    def __init__(self, area, startPosition=None):
        GameState.__init__(self)
        self.area = area


    def activate(self):
        self.ui = StandardUI()
        vpm = ViewPortManager(self.ui)
        vpm.add(ViewPort(self.area))
        vpm.add(ViewPort(self.area))
        self.ui.addElement(vpm)


    def draw(self, surface):
        self.ui.draw(surface)


    def update(self, time):
        self.ui.update(time)


    def handle_commandlist(self, cmdlist):
        self.ui.handle_commandlist(cmdlist)


@receiver(emitText)
def displayText(sender, **kwargs):
    x1, y1, z1 = kwargs['position']
    x2, y2, z2 = hero_body.bbox.origin
    d = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
    state.updateText = True


@receiver(emitSound)
def playSound(sender, **kwargs):
    x1, y1, z1 = kwargs['position']
    x2, y2, z2 = hero_body.bbox.origin
    d = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2))
    try:
        vol = 1/d * 20 
    except ZeroDivisionError:
        vol = 1.0
    if vol > .02:
        SoundMan.play(kwargs['filename'], volume=vol)


@receiver(bodyAbsMove)
def bodyMove(sender, **kwargs):
    area = sender
    body = kwargs['body']
    position = kwargs['position']
    state = kwargs['caller']

    if state == None:
        return


@receiver(bodyWarp)
def bodyWarp(sender, **kwargs):
    area = sender
    body = kwargs['body']
    destination = kwargs['destination']
    state = kwargs['caller']

    if state == None:
        return

    if body == state.hero:
        sd.push(WorldState(destination))
        sd.done()


